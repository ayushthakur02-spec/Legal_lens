LOW_CONF=0.55

def check_compliance(fields,category,imported,rules,ocr_confidence):
    checks=[]; passed=review=failed=0
    for rule in rules["rules"]:
        cats=rule.get("categories",["*"])
        if "*" not in cats and category not in cats: continue
        if rule.get("imported_only") and not imported: continue
        data=fields.get(rule["field"])
        value=data.get("value") if data else None
        conf=float(data.get("confidence",ocr_confidence)) if data else ocr_confidence

        if value and conf<LOW_CONF:
            status="REVIEW"; reason="Possible declaration detected, but OCR confidence is low."; review+=1
        elif value:
            status="PASS"; reason="Declaration detected."; passed+=1
        elif rule.get("required",True):
            status="FAIL"; reason="Required declaration was not detected."; failed+=1
        else:
            status="REVIEW"; reason="Optional/applicability-dependent declaration was not detected."; review+=1

        checks.append({"rule_id":rule["id"],"field":rule["field"],"title":rule["title"],
                       "required":rule.get("required",True),"status":status,"value":value,
                       "confidence":round(conf,4),"evidence":data.get("evidence") if data else None,
                       "reason":reason,"source":rule.get("source","Configured rule")})
    if failed: overall="FAIL"
    elif review or ocr_confidence<0.35: overall="REVIEW"
    else: overall="PASS"
    return {"overall_status":overall,
            "overall_reason":f"Passed {passed}, review {review}, failed {failed}.",
            "summary":{"passed":passed,"review":review,"failed":failed,"checked":len(checks)},
            "checks":checks,
            "disclaimer":"Preliminary AI-assisted screening only; not legal certification."}
