import re

def field(value,confidence,evidence):
    return {"value":value,"confidence":round(float(confidence),4),"evidence":evidence,"source":"ocr"}

def confidence(evidence,ocr):
    for img in ocr.get("images",[]):
        for line in img.get("lines",[]):
            if line["text"].lower()==evidence.lower(): return line["confidence"]
    return ocr.get("overall_confidence",0.0)

def find(lines,patterns):
    for line in lines:
        for p in patterns:
            m=re.search(p,line,re.I)
            if m:return m.group(1).strip(),line
    return None,None

def extract_fields(text,ocr):
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    f={}
    patterns={
      "product_name":[r"^(?:product name|common name|product)\s*[:\-]\s*(.+)$"],
      "manufacturer":[r"(?:manufactured by|manufacturer|packed by|packer|imported by|importer)\s*[:\-]?\s*(.+)$"],
      "address":[r"(?:address|registered office)\s*[:\-]?\s*(.+)$"],
      "net_quantity":[r"(?:net\s*(?:quantity|weight|wt|volume))\s*[:\-]?\s*([\d.,]+\s*(?:kg|g|mg|l|ml|cl))"],
      "mrp":[r"(?:mrp|maximum retail price)\s*[:\-]?\s*(?:rs\.?|₹)?\s*([\d,]+(?:\.\d{1,2})?)"],
      "manufacture_or_pack_date":[r"(?:mfg|manufactured|pkd|packed|packing date|date of manufacture)\s*[:\-]?\s*([\w./-]+)"],
      "best_before":[r"(?:best before|use by|expiry|expires)\s*[:\-]?\s*(.+)$"],
      "consumer_care":[r"(?:customer care|consumer care|helpline|toll free|contact)\s*[:\-]?\s*(.+)$"],
      "country_of_origin":[r"(?:country of origin|made in|product of)\s*[:\-]?\s*(.+)$"],
      "unit_sale_price":[r"(?:unit sale price|price per)\s*[:\-]?\s*(.+)$"]
    }
    for name,ps in patterns.items():
        v,e=find(lines,ps)
        if v:f[name]=field(("₹"+v) if name=="mrp" and not v.startswith("₹") else v,
                            confidence(e,ocr),e)
    return f
