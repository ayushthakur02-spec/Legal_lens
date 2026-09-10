from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

def generate_pdf_report(data,path):
    doc=SimpleDocTemplate(path,pagesize=A4,leftMargin=12*mm,rightMargin=12*mm,topMargin=12*mm,bottomMargin=12*mm)
    styles=getSampleStyleSheet(); story=[Paragraph("PACKCHECK AI",styles["Title"]),
        Paragraph("Preliminary Packaged Commodity Compliance Report",styles["Heading2"]),Spacer(1,8)]
    p=data.get("product",{}); c=data.get("compliance",{})
    meta=[["Product",str(p.get("name") or "Not detected")],
          ["Category",str(p.get("category","general"))],
          ["Imported","Yes" if p.get("imported") else "No"],
          ["Overall result",c.get("overall_status","REVIEW")]]
    t=Table(meta,colWidths=[45*mm,130*mm]); t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.4,colors.grey),("BACKGROUND",(0,0),(0,-1),colors.whitesmoke)])); story+=[t,Spacer(1,8)]
    story.append(Paragraph("Field-wise checks",styles["Heading2"]))
    rows=[["Rule","Field","Status","Value","Reason"]]
    for x in c.get("checks",[]): rows.append([x["rule_id"],x["title"],x["status"],str(x.get("value") or "Not detected"),x["reason"]])
    t=Table(rows,colWidths=[15*mm,38*mm,22*mm,38*mm,62*mm],repeatRows=1)
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),.3,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("FONTSIZE",(0,0),(-1,-1),7)]))
    story.append(t); story.append(Spacer(1,8))
    story.append(Paragraph(c.get("disclaimer",""),styles["BodyText"]))
    doc.build(story)
    return path
