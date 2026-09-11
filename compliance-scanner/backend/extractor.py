import re
from datetime import datetime


# ============================================================
# PackCheck AI - Smart Label Field Extractor
# ============================================================


def clean_text(value):
    """Clean OCR text while preserving useful characters."""

    if value is None:
        return ""

    value = str(value)

    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value)

    return value.strip(" :.-")


def normalize_lines(ocr_text):
    """
    Convert different OCR output formats into a simple list of lines.
    Supports:
      - string
      - list of strings
      - list of dictionaries
    """

    lines = []

    if ocr_text is None:
        return lines

    if isinstance(ocr_text, str):

        raw_lines = ocr_text.splitlines()

        for line in raw_lines:
            line = clean_text(line)

            if line:
                lines.append(line)

        return lines

    if isinstance(ocr_text, list):

        for item in ocr_text:

            if isinstance(item, str):

                line = clean_text(item)

                if line:
                    lines.append(line)

            elif isinstance(item, dict):

                for key in ["text", "value", "content"]:

                    if key in item:

                        line = clean_text(item[key])

                        if line:
                            lines.append(line)

                        break

            elif isinstance(item, (list, tuple)):

                # PaddleOCR style:
                # [box, ("text", confidence)]

                try:

                    if len(item) >= 2:

                        second = item[1]

                        if isinstance(second, (list, tuple)) and len(second) >= 1:

                            line = clean_text(second[0])

                            if line:
                                lines.append(line)

                        elif isinstance(second, str):

                            line = clean_text(second)

                            if line:
                                lines.append(line)

                except Exception:
                    pass

        return lines

    return lines


def joined_text(lines):
    """Create searchable OCR text."""

    return "\n".join(lines)


# ============================================================
# Utility functions
# ============================================================


def is_date(value):
    """Check whether a value looks like a date."""

    if not value:
        return False

    value = value.strip()

    patterns = [
        r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$",
        r"^\d{1,2}[/-][A-Za-z]{3,9}[/-]\d{2,4}$",
        r"^[A-Za-z]{3,9}[/-]\d{1,2}[/-]\d{2,4}$",
    ]

    return any(re.match(p, value, re.I) for p in patterns)


def is_barcode(value):
    """Reject long numeric barcode strings."""

    if not value:
        return False

    value = re.sub(r"\s+", "", value)

    return bool(re.fullmatch(r"\d{8,18}", value))


def clean_currency(value):
    """Normalize MRP value."""

    if not value:
        return ""

    value = value.replace("₹", "")
    value = value.replace("Rs.", "")
    value = value.replace("Rs", "")
    value = value.replace("INR", "")

    value = value.strip()

    match = re.search(r"\d+(?:\.\d{1,2})?", value)

    if not match:
        return ""

    number = match.group(0)

    try:
        amount = float(number)

        if amount <= 0 or amount > 100000:
            return ""

        if amount.is_integer():
            return f"₹{int(amount)}"

        return f"₹{amount:.2f}"

    except Exception:
        return ""


def clean_quantity(value):
    """Normalize quantity."""

    if not value:
        return ""

    value = value.strip()

    # Common OCR corrections
    value = value.replace("1kg", "1 kg")
    value = value.replace("500g", "500 g")
    value = value.replace("250g", "250 g")
    value = value.replace("100g", "100 g")
    value = value.replace("1Kg", "1 kg")
    value = value.replace("KG", "kg")
    value = value.replace("G", "g")
    value = value.replace("ML", "ml")
    value = value.replace("L", "L")

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(kg|g|mg|ml|l|litre|liter)\b",
        value,
        re.I
    )

    if match:

        number = match.group(1)
        unit = match.group(2).lower()

        unit_map = {
            "kilogram": "kg",
            "kilograms": "kg",
            "kg": "kg",
            "g": "g",
            "mg": "mg",
            "ml": "ml",
            "l": "L",
            "litre": "L",
            "liter": "L"
        }

        unit = unit_map.get(unit, unit)

        return f"{number} {unit}"

    return ""


# ============================================================
# Specific field extraction
# ============================================================


def extract_mrp(lines, text):
    """
    Detect MRP using strong label anchors.

    Examples:
        MRP ₹249.00
        MRP: Rs 249
        M.R.P. 249.00
        Maximum Retail Price ₹249
    """

    patterns = [
        r"\bM\.?\s*R\.?\s*P\.?\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*(\d+(?:\.\d{1,2})?)",
        r"\bMaximum\s+Retail\s+Price\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*(\d+(?:\.\d{1,2})?)",
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(pattern, line, re.I)

            if match:

                value = match.group(1)

                result = clean_currency(value)

                if result:
                    return result

    return ""


def extract_batch(lines):
    """
    Detect Batch/Lot number.

    Important:
      Dates and long barcode numbers are rejected.
    """

    label_patterns = [
        r"(?:Batch\s*(?:No|Number)?|Lot\s*(?:No|Number)?|Batch\s*Code)"
        r"\s*[:#\-]?\s*([A-Z0-9][A-Z0-9\-\/]{2,30})"
    ]

    for line in lines:

        for pattern in label_patterns:

            match = re.search(pattern, line, re.I)

            if not match:
                continue

            candidate = match.group(1).strip()

            candidate = candidate.rstrip(".,:;")

            # Reject dates
            if is_date(candidate):
                continue

            # Reject barcode numbers
            if is_barcode(candidate):
                continue

            # Reject values that are obviously only dates
            if re.fullmatch(
                r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
                candidate
            ):
                continue

            # Batch should contain at least one letter OR
            # a reasonable mixed alphanumeric code.
            if not re.search(r"[A-Za-z]", candidate):
                continue

            # Avoid accidental OCR phrases
            if len(candidate) > 30:
                continue

            return candidate

    return ""


def extract_packaging_date(lines):
    """Extract Date of Packaging."""

    patterns = [
        r"(?:Date\s+of\s+Packaging|Date\s+of\s+Pack|Packaging\s+Date)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"(?:Packed\s+On|PKD|PKG|Packed)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(pattern, line, re.I)

            if match:
                return match.group(1)

    return ""


def extract_manufacturing_date(lines):
    """Extract manufacturing date."""

    patterns = [
        r"(?:Date\s+of\s+Manufacture|Manufacturing\s+Date|Mfg\s*\.?\s*Date|MFD)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(pattern, line, re.I)

            if match:
                return match.group(1)

    return ""


def extract_use_by(lines):
    """Extract Use By / Best Before / Expiry."""

    patterns = [
        r"(?:Use\s*By|Used\s*By|Best\s*Before|Expiry\s*Date|Exp\.?\s*Date)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",

        r"(?:Use\s*By|Used\s*By|Best\s*Before|Expiry)"
        r"\s*[:\-]?\s*"
        r"(\d{1,2}\s*(?:months?|years?))"
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(pattern, line, re.I)

            if match:
                return match.group(1)

    return ""


def extract_fssai(lines, text):
    """Extract 14-digit FSSAI license number."""

    # Standard FSSAI license number is generally 14 digits.
    patterns = [
        r"(?:FSSAI|FSSAI\s*Lic(?:ense)?|License\s*No)"
        r"[^\d]{0,20}(\d{14})",

        r"\b(\d{14})\b"
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text, re.I)

        for value in matches:

            value = value.strip()

            if len(value) == 14:
                return value

    return ""


def extract_country(lines, text):
    """Extract country of origin."""

    patterns = [
        r"(?:Country\s+of\s+Origin|Country\s+Origin|Made\s+in)"
        r"\s*[:\-]?\s*([A-Za-z][A-Za-z\s]{1,30})"
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(pattern, line, re.I)

            if match:

                country = match.group(1).strip()

                country = re.split(
                    r"\b(?:FSSAI|MRP|Batch|Net|Date|Use\s+By)\b",
                    country,
                    flags=re.I
                )[0].strip()

                if country:
                    return country.title()

    # Common direct OCR occurrence
    if re.search(r"\bIndia\b", text, re.I):
        return "India"

    return ""


def extract_customer_care(lines, text):
    """
    Extract customer-care information ONLY when a phone/email
    is actually present.

    This prevents barcode numbers from being incorrectly
    returned as customer-care numbers.
    """

    # Email
    email_matches = re.findall(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )

    if email_matches:
        return email_matches[0]

    # Indian phone number
    phone_patterns = [
        r"\b(?:\+91[\s\-]?)?[6-9]\d{9}\b",
        r"\b0[6-9]\d{9}\b"
    ]

    for pattern in phone_patterns:

        matches = re.findall(pattern, text)

        for number in matches:

            number = re.sub(r"[^\d+]", "", number)

            # Reject obvious barcode-like values
            if len(re.sub(r"\D", "", number)) == 10:
                return number

    return ""


def extract_net_quantity(lines, text):
    """Extract Net Quantity / Net Weight."""

    patterns = [
        r"(?:Net\s*(?:Quantity|Qty|Weight|Wt)?)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?\s*(?:kg|g|mg|ml|l|litre|liter))",

        r"\b(\d+(?:\.\d+)?\s*(?:kg|g|mg|ml|l))\b"
    ]

    # First use labelled quantity
    for line in lines:

        for pattern in patterns[:1]:

            match = re.search(pattern, line, re.I)

            if match:

                result = clean_quantity(match.group(1))

                if result:
                    return result

    # Then general quantity
    for line in lines:

        for pattern in patterns[1:]:

            match = re.search(pattern, line, re.I)

            if match:

                result = clean_quantity(match.group(1))

                if result:
                    return result

    return ""


def extract_product_name(lines, text):
    """
    Extract product name using label context.

    Avoids returning the entire OCR line.
    """

    patterns = [
        r"(?:Product\s*Name|Name\s+of\s+Product)"
        r"\s*[:\-]?\s*(.+)",

        r"(?:Name)"
        r"\s*[:\-]\s*(.+)"
    ]

    # 1. Explicit Product Name label
    for line in lines:

        for pattern in patterns:

            match = re.search(pattern, line, re.I)

            if match:

                candidate = clean_text(match.group(1))

                # Remove common unrelated information
                candidate = re.split(
                    r"\b(?:MRP|Batch|Lot|Net\s+Quantity|Date\s+of\s+Packaging|"
                    r"Use\s+By|FSSAI|Country\s+of\s+Origin|Ingredients)\b",
                    candidate,
                    flags=re.I
                )[0]

                candidate = candidate.strip(" :-.,!")

                if 2 <= len(candidate) <= 80:
                    return candidate

    # 2. Try common product names from OCR
    known_products = [
        "ARHAR DAL",
        "TOOR DAL",
        "TUR DAL",
        "CHANA DAL",
        "MOONG DAL",
        "MASOOR DAL",
        "URAD DAL",
        "RICE",
        "WHEAT",
        "SUGAR",
        "SALT",
        "BESAN",
        "ATTA"
    ]

    upper_text = text.upper()

    for product in known_products:

        if product in upper_text:
            return product.title()

    # 3. Look for short uppercase-looking product lines
    ignored_words = {
        "MRP",
        "FSSAI",
        "INDIA",
        "BATCH",
        "BATCH NO",
        "DATE",
        "PACKAGING",
        "USE BY",
        "NET QUANTITY",
        "INGREDIENTS",
        "CUSTOMER CARE",
        "VEG",
        "NON VEG"
    }

    candidates = []

    for line in lines:

        candidate = clean_text(line)

        if not candidate:
            continue

        upper = candidate.upper()

        if upper in ignored_words:
            continue

        if is_date(candidate):
            continue

        if is_barcode(candidate):
            continue

        # Don't choose long sentences
        if len(candidate) > 40:
            continue

        # Product names often contain letters and few digits
        if re.search(r"[A-Za-z]", candidate):

            digit_count = len(re.findall(r"\d", candidate))

            if digit_count <= 3:
                candidates.append(candidate)

    if candidates:

        # Prefer short, clean candidates
        candidates.sort(key=lambda x: len(x))

        return candidates[0]

    return ""


def extract_manufacturer(lines):
    """Extract manufacturer/packer information."""

    patterns = [
        r"(?:Manufactured\s*By|Manufactured\s+by)"
        r"\s*[:\-]?\s*(.+)",

        r"(?:Marketed\s*By|Marketed\s+by)"
        r"\s*[:\-]?\s*(.+)",

        r"(?:Packed\s*By|Packed\s+by)"
        r"\s*[:\-]?\s*(.+)"
    ]

    for line in lines:

        for pattern in patterns:

            match = re.search(pattern, line, re.I)

            if match:

                value = clean_text(match.group(1))

                if len(value) >= 2:

                    value = re.split(
                        r"\b(?:FSSAI|MRP|Batch|Net|Date|Use\s+By)\b",
                        value,
                        flags=re.I
                    )[0].strip()

                    if value:
                        return value

    return ""


# ============================================================
# Main extraction function
# ============================================================


def extract_fields(ocr_text):
    """
    Main function called by app.py.

    Returns only fields that were actually detected.
    Empty / uncertain fields are NOT returned.
    """

    lines = normalize_lines(ocr_text)

    text = joined_text(lines)

    result = {}

    # --------------------------------------------------------
    # Product Name
    # --------------------------------------------------------

    value = extract_product_name(lines, text)

    if value:
        result["productName"] = value

    # --------------------------------------------------------
    # Net Quantity
    # --------------------------------------------------------

    value = extract_net_quantity(lines, text)

    if value:
        result["netQuantity"] = value

    # --------------------------------------------------------
    # MRP
    # --------------------------------------------------------

    value = extract_mrp(lines, text)

    if value:
        result["mrp"] = value

    # --------------------------------------------------------
    # Batch Number
    # --------------------------------------------------------

    value = extract_batch(lines)

    if value:
        result["batchNumber"] = value

    # --------------------------------------------------------
    # Packaging Date
    # --------------------------------------------------------

    value = extract_packaging_date(lines)

    if value:
        result["packagingDate"] = value

    # --------------------------------------------------------
    # Manufacturing Date
    # --------------------------------------------------------

    value = extract_manufacturing_date(lines)

    if value:
        result["manufacturingDate"] = value

    # --------------------------------------------------------
    # Use By
    # --------------------------------------------------------

    value = extract_use_by(lines)

    if value:
        result["useBy"] = value

    # --------------------------------------------------------
    # FSSAI
    # --------------------------------------------------------

    value = extract_fssai(lines, text)

    if value:
        result["fssaiLicense"] = value

    # --------------------------------------------------------
    # Country of Origin
    # --------------------------------------------------------

    value = extract_country(lines, text)

    if value:
        result["countryOfOrigin"] = value

    # --------------------------------------------------------
    # Customer Care
    # --------------------------------------------------------

    value = extract_customer_care(lines, text)

    if value:
        result["customerCare"] = value

    # --------------------------------------------------------
    # Manufacturer
    # --------------------------------------------------------

    value = extract_manufacturer(lines)

    if value:
        result["manufacturer"] = value

    # --------------------------------------------------------
    # Final cleanup
    # --------------------------------------------------------

    cleaned_result = {}

    for key, value in result.items():

        if value is None:
            continue

        value = clean_text(value)

        if not value:
            continue

        # Never allow obvious OCR junk
        if value.lower() in [
            "not detected",
            "unknown",
            "none",
            "null",
            "n/a",
            "na"
        ]:
            continue

        cleaned_result[key] = value

    return cleaned_result


# ============================================================
# Direct test
# ============================================================

if __name__ == "__main__":

    sample_text = """
    ARHAR DAL
    MRP ₹249.00
    Net Quantity 1 kg
    Batch No AHRAR560125 B
    Date of Packaging 05/05/2026
    Use By 04/05/2027
    FSSAI License 100130210005
    Country of Origin India
    """

    print("\nPackCheck AI Extractor Test\n")

    extracted = extract_fields(sample_text)

    for key, value in extracted.items():
        print(f"{key}: {value}")