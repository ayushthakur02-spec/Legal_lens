from pathlib import Path
from flask import Flask, jsonify, request, send_file
from werkzeug.utils import secure_filename
import uuid

from image_processor import preprocess_image
from ocr import OCRService
from extractor import extract_fields
from classifier import classify_product
from rules_loader import load_rules
from compliance import check_compliance
from report import generate_pdf_report

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
PROCESSED = BASE / "processed"
REPORTS = BASE / "reports"
for p in (UPLOADS, PROCESSED, REPORTS): p.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024
ALLOWED = {"jpg","jpeg","png","webp"}
ocr = OCRService()

@app.get("/")
def home():
    return jsonify({"name":"PackCheck AI","status":"running"})

@app.get("/api/health")
def health():
    return jsonify({"status":"ok","ocr_engine":ocr.engine_name})

@app.get("/api/rules")
def rules():
    return jsonify(load_rules())

@app.post("/api/analyze")
def analyze():
    files = request.files.getlist("images")
    if not files: return jsonify({"error":"Upload at least one image using field 'images'"}), 400
    category = request.form.get("category","auto").lower()
    imported = request.form.get("imported","false").lower() in {"1","true","yes","on"}
    job = uuid.uuid4().hex[:12]
    up = UPLOADS/job; pp = PROCESSED/job
    up.mkdir(parents=True); pp.mkdir(parents=True)

    paths = []
    for i, f in enumerate(files,1):
        if not f.filename: continue
        ext = Path(secure_filename(f.filename)).suffix.lower().lstrip(".")
        if ext not in ALLOWED: return jsonify({"error":"Unsupported image type"}),400
        path = up/f"side_{i}.{ext}"; f.save(path); paths.append(path)
    if not paths: return jsonify({"error":"No valid images"}),400

    processed = []
    for i,p in enumerate(paths,1):
        out = pp/f"processed_{i}.jpg"
        r = preprocess_image(str(p),str(out))
        processed.append(Path(r["path"]) if r["ok"] else p)

    ocr_result = ocr.read_images([str(p) for p in processed])
    text = "\n".join(x["text"] for x in ocr_result["images"] if x["text"])
    fields = extract_fields(text, ocr_result)
    cls = classify_product(text, category, imported)
    result = {
        "job_id":job,
        "product":{"name":fields.get("product_name",{}).get("value"),
                   "category":cls["category"],"imported":cls["imported"],
                   "classification_reason":cls["reason"]},
        "ocr":ocr_result,
        "fields":fields
    }
    result["compliance"] = check_compliance(fields, cls["category"], cls["imported"],
                                             load_rules(), ocr_result["overall_confidence"])
    return jsonify(result)

@app.post("/api/report")
def report():
    data = request.get_json(silent=True)
    if not data: return jsonify({"error":"JSON analysis result required"}),400
    path = REPORTS/f"PackCheck_AI_Report_{data.get('job_id','report')}.pdf"
    generate_pdf_report(data,str(path))
    return send_file(path,as_attachment=True,download_name=path.name)

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=5000,debug=True)
