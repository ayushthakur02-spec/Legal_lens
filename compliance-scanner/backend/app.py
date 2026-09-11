from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import os
import cv2
import numpy as np

# ============================================================
# PACKCHECK AI - FAST SIH DEMO BACKEND
# ============================================================

app = Flask(__name__)
CORS(app)

FAST_DEMO_MODE = os.getenv(
    "PACKCHECK_FAST_DEMO",
    "true"
).lower() == "true"


# ============================================================
# DATABASE
# ============================================================

try:
    from database import (
        init_database,
        save_inspection,
        get_inspections
    )

    init_database()
    DATABASE_READY = True
    print("Database: READY")

except Exception as e:
    DATABASE_READY = False

    print("Database: NOT AVAILABLE ->", e)

    def save_inspection(result):
        return None

    def get_inspections():
        return []


# ============================================================
# OPTIONAL REAL OCR
# ============================================================

ocr = None

try:
    from paddleocr import PaddleOCR

    ocr = PaddleOCR(lang="en")

    print("PaddleOCR: READY")

except Exception as e:

    print("PaddleOCR: NOT AVAILABLE ->", e)


# ============================================================
# EXTRACTOR
# ============================================================

try:

    from extractor import extract_fields

    print("Extractor: READY")

except Exception as e:

    extract_fields = None

    print("Extractor: NOT AVAILABLE ->", e)


# ============================================================
# IMAGE OPTIMIZATION
# ============================================================

def optimize_image(image, max_side=1200):

    h, w = image.shape[:2]

    longest = max(h, w)

    if longest <= max_side:
        return image

    scale = max_side / float(longest)

    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    return cv2.resize(
        image,
        (new_w, new_h),
        interpolation=cv2.INTER_AREA
    )


# ============================================================
# PADDLE OCR PARSER
# ============================================================

def parse_paddle_result(result):

    texts = []

    try:

        if isinstance(result, list):

            for item in result:

                if isinstance(item, dict):

                    rec_texts = item.get(
                        "rec_texts",
                        []
                    )

                    if rec_texts:

                        texts.extend(
                            [str(x) for x in rec_texts]
                        )

                elif isinstance(item, list):

                    for row in item:

                        try:

                            if (
                                isinstance(
                                    row,
                                    (list, tuple)
                                )
                                and len(row) >= 2
                                and isinstance(
                                    row[1],
                                    (list, tuple)
                                )
                            ):

                                txt = row[1][0]

                                if txt:
                                    texts.append(
                                        str(txt)
                                    )

                        except Exception:
                            pass

        if not texts:

            items = (
                result
                if isinstance(
                    result,
                    (list, tuple)
                )
                else [result]
            )

            for item in items:

                rec_texts = getattr(
                    item,
                    "rec_texts",
                    None
                )

                if rec_texts:

                    texts.extend(
                        [str(x) for x in rec_texts]
                    )

    except Exception as e:

        print(
            "OCR parsing warning:",
            e
        )

    return texts


# ============================================================
# REAL OCR
# ============================================================

def run_real_ocr(image):

    if ocr is None:
        return []

    image = optimize_image(
        image,
        1200
    )

    try:

        result = ocr.predict(image)

        return parse_paddle_result(
            result
        )

    except Exception as e:

        print(
            "OCR error:",
            e
        )

        return []


# ============================================================
# FAST DEMO DATA
# ============================================================

def fast_demo_result():

    return {

        "productName":
            "ARHAR DAL",

        "netQuantity":
            "1 kg",

        "mrp":
            "₹249.00",

        "batchNumber":
            "AHRAR560125 B",

        "packagingDate":
            "05/05/2026",

        "useBy":
            "04/05/2027",

        "fssaiLicense":
            "100130210005",

        "countryOfOrigin":
            "India",

        "manufacturer":
            "Sample Food Products",

        "customerCare":
            "1800-123-4567"
    }


# ============================================================
# BASIC EXTRACTION
# ============================================================

def basic_extract(texts):

    full = "\n".join(texts)

    result = {}

    def first(patterns):

        for pattern in patterns:

            match = re.search(
                pattern,
                full,
                re.I
            )

            if match:

                return match.group(1).strip()

        return None


    result["productName"] = first([
        r"(?:product\s*name|name\s*of\s*product)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z][A-Za-z ]{2,40})"
    ])


    result["netQuantity"] = first([
        r"(?:net\s*(?:quantity|wt|weight)|quantity)"
        r"\s*[:\-]?\s*"
        r"([0-9]+(?:\.[0-9]+)?\s*"
        r"(?:kg|g|mg|l|ml))"
    ])


    result["mrp"] = first([
        r"(?:mrp|maximum\s*retail\s*price)"
        r"\s*[:\-]?\s*"
        r"(?:₹|rs\.?|inr)?\s*"
        r"([0-9]+(?:\.[0-9]{1,2})?)"
    ])


    result["batchNumber"] = first([
        r"(?:batch\s*(?:no|number)?|"
        r"lot\s*(?:no|number)?)"
        r"\s*[:\-]?\s*"
        r"([A-Z0-9][A-Z0-9\- ]{2,25})"
    ])


    result["packagingDate"] = first([
        r"(?:date\s*of\s*packaging|"
        r"packed\s*on|packaging\s*date)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
    ])


    result["manufacturingDate"] = first([
        r"(?:date\s*of\s*manufacture|"
        r"manufactured\s*on|mfg\.?\s*date)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
    ])


    result["useBy"] = first([
        r"(?:use\s*by|best\s*before|expiry|expires?)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
    ])


    result["fssaiLicense"] = first([
        r"(?:fssai(?:\s*license)?|"
        r"lic(?:ence)?\s*no\.?)"
        r"\s*[:\-]?\s*"
        r"(\d{10,14})"
    ])


    result["countryOfOrigin"] = first([
        r"(?:country\s*of\s*origin|made\s*in)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z ]{2,30})"
    ])


    result["customerCare"] = first([
        r"(?:customer\s*care|helpline|contact)"
        r"\s*[:\-]?\s*"
        r"(\+?\d[\d \-]{8,16})"
    ])


    result["manufacturer"] = first([
        r"(?:manufactured\s*by|manufacturer)"
        r"\s*[:\-]?\s*"
        r"([A-Za-z0-9&.,() \-]{3,80})"
    ])


    return {
        k: v
        for k, v in result.items()
        if v
    }


# ============================================================
# COMPLIANCE ENGINE
# ============================================================

def compliance_check(fields):

    checks = []

    required = {

        "Product Name":
            "productName",

        "Net Quantity":
            "netQuantity",

        "MRP":
            "mrp",

        "Batch/Lot":
            "batchNumber",

        "Date of Packaging":
            "packagingDate",

        "Use By":
            "useBy",

        "FSSAI":
            "fssaiLicense",

        "Country of Origin":
            "countryOfOrigin",

        "Manufacturer":
            "manufacturer"
    }


    for label, key in required.items():

        value = fields.get(key)

        if value:

            checks.append({

                "name": label,

                "status": "PASS",

                "message":
                    "Required declaration detected."

            })

        else:

            checks.append({

                "name": label,

                "status": "REVIEW",

                "message":
                    "Declaration not detected; manual verification recommended."

            })


    failed = sum(
        1
        for item in checks
        if item["status"] == "FAIL"
    )

    review = sum(
        1
        for item in checks
        if item["status"] == "REVIEW"
    )

    passed = sum(
        1
        for item in checks
        if item["status"] == "PASS"
    )


    if failed:

        overall = "FAIL"

    elif review:

        overall = "REVIEW"

    else:

        overall = "PASS"


    return {

        "overallStatus":
            overall,

        "status":
            overall,

        "checks":
            checks,

        "summary": {

            "passed":
                passed,

            "review":
                review,

            "failed":
                failed,

            "total":
                len(checks)
        }
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    return jsonify({

        "success":
            True,

        "message":
            "PackCheck AI backend is running",

        "ocr_available":
            ocr is not None,

        "extractor_available":
            extract_fields is not None,

        "database_available":
            DATABASE_READY,

        "fast_demo_mode":
            FAST_DEMO_MODE
    })


# ============================================================
# SCAN PRODUCT
# ============================================================

@app.post("/api/scan")
def scan():

    try:

        upload = (

            request.files.get("image")

            or request.files.get("file")

            or request.files.get("photo")

            or request.files.get("productImage")

            or request.files.get("upload")
        )


        print(
            "Received fields:",
            list(request.files.keys())
        )


        if upload is None:

            return jsonify({

                "success":
                    False,

                "error":
                    "No image uploaded."
            }), 400


        raw = upload.read()


        if not raw:

            return jsonify({

                "success":
                    False,

                "error":
                    "Uploaded image is empty."
            }), 400


        # ====================================================
        # FAST DEMO MODE
        # ====================================================

        if FAST_DEMO_MODE:

            fields = fast_demo_result()

            compliance = compliance_check(
                fields
            )

            result = {

                "success":
                    True,

                "mode":
                    "FAST_DEMO",

                "message":
                    "Fast prototype analysis completed.",

                "fields":
                    fields,

                "detectedInformation":
                    fields,

                "compliance":
                    compliance,

                "processingTime":
                    "< 1 second"
            }


            # SAVE TO DATABASE

            inspection_id = None

            if DATABASE_READY:

                try:

                    inspection_id = save_inspection(
                        result
                    )

                    print(
                        "Inspection saved:",
                        inspection_id
                    )

                except Exception as db_error:

                    print(
                        "Database save error:",
                        db_error
                    )


            result["inspectionId"] = inspection_id

            return jsonify(result)


        # ====================================================
        # REAL OCR MODE
        # ====================================================

        image_array = np.frombuffer(
            raw,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )


        if image is None:

            return jsonify({

                "success":
                    False,

                "error":
                    "Could not decode uploaded image."
            }), 400


        texts = run_real_ocr(
            image
        )


        if extract_fields is not None:

            try:

                fields = extract_fields(
                    texts
                )

            except Exception as e:

                print(
                    "Extractor error:",
                    e
                )

                fields = basic_extract(
                    texts
                )

        else:

            fields = basic_extract(
                texts
            )


        cleaned = {}


        for key, value in fields.items():

            if value is None:
                continue

            value = str(value).strip()

            if not value:
                continue

            if value.lower() in {

                "not detected",

                "not found",

                "unknown",

                "n/a",

                "na"
            }:

                continue

            cleaned[key] = value


        compliance = compliance_check(
            cleaned
        )


        result = {

            "success":
                True,

            "mode":
                "REAL_OCR",

            "message":
                "Real OCR analysis completed.",

            "ocrText":
                texts,

            "fields":
                cleaned,

            "detectedInformation":
                cleaned,

            "compliance":
                compliance
        }


        # SAVE REAL INSPECTION

        inspection_id = None

        if DATABASE_READY:

            try:

                inspection_id = save_inspection(
                    result
                )

            except Exception as db_error:

                print(
                    "Database save error:",
                    db_error
                )


        result["inspectionId"] = inspection_id


        return jsonify(result)


    except Exception as e:

        print(
            "SCAN ERROR:",
            e
        )


        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# INSPECTION HISTORY
# ============================================================

@app.get("/api/inspections")
def inspections():

    try:

        rows = get_inspections()

        return jsonify({

            "success":
                True,

            "count":
                len(rows),

            "inspections":
                rows
        })

    except Exception as e:

        print(
            "History error:",
            e
        )

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# SINGLE INSPECTION
# ============================================================

@app.get("/api/inspections/<int:inspection_id>")
def inspection_detail(
    inspection_id
):

    try:

        rows = get_inspections()

        for row in rows:

            if int(row.get("id", 0)) == inspection_id:

                return jsonify({

                    "success":
                        True,

                    "inspection":
                        row
                })


        return jsonify({

            "success":
                False,

            "error":
                "Inspection not found."
        }), 404


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():

    return jsonify({

        "name":
            "PackCheck AI",

        "status":
            "running",

        "mode":
            "FAST_DEMO"
            if FAST_DEMO_MODE
            else "REAL_OCR",

        "scan_endpoint":
            "/api/scan",

        "history_endpoint":
            "/api/inspections"
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "PACKCHECK AI BACKEND"
    )

    print(
        "Backend: http://127.0.0.1:5000"
    )

    print(
        "Fast Demo Mode:",
        FAST_DEMO_MODE
    )

    print(
        "OCR:",
        "READY"
        if ocr is not None
        else "NOT AVAILABLE"
    )

    print(
        "Extractor:",
        "READY"
        if extract_fields is not None
        else "NOT AVAILABLE"
    )

    print(
        "Database:",
        "READY"
        if DATABASE_READY
        else "NOT AVAILABLE"
    )

    print("=" * 60)


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False,

        threaded=True
    )