KEYWORDS={
 "food":["ingredients","nutrition","fssai","calories","protein","serving size"],
 "cosmetic":["shampoo","cream","lotion","cosmetic","conditioner","soap"],
 "electrical":["voltage","watt","frequency","input","output"],
 "household":["detergent","cleaner","dishwash"]
}
def classify_product(text,requested_category="auto",imported=False):
    if requested_category in {"general","food","cosmetic","electrical","household"}:
        return {"category":requested_category,"imported":bool(imported),
                "reason":"Category selected by user."}
    t=text.lower()
    scores={c:sum(k in t for k in ks) for c,ks in KEYWORDS.items()}
    best=max(scores,key=scores.get) if scores else "general"
    if scores.get(best,0)==0: best="general"; reason="No strong category keyword detected."
    else: reason=f"Inferred from {scores[best]} keyword match(es)."
    return {"category":best,"imported":bool(imported),"reason":reason}
