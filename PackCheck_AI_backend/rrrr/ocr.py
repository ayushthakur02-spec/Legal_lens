class OCRService:
    def __init__(self):
        self.engine_name="PaddleOCR"
        self.engine=None
        self.error=None
        try:
            from paddleocr import PaddleOCR
            self.engine=PaddleOCR(lang="en")
        except Exception as e:
            self.error=str(e)
            self.engine_name="PaddleOCR unavailable"

    def read_image(self,path,index):
        if self.engine is None:
            return {"image_index":index,"text":"","confidence":0.0,"lines":[],"error":self.error}
        try:
            result=self.engine.predict(path)
            texts=[]; scores=[]
            for item in result if isinstance(result,list) else [result]:
                if hasattr(item,"json"):
                    try: item=item.json()
                    except Exception: pass
                if hasattr(item,"to_dict"):
                    try: item=item.to_dict()
                    except Exception: pass
                if isinstance(item,dict):
                    texts += [str(x) for x in item.get("rec_texts",[])]
                    scores += [float(x) for x in item.get("rec_scores",[])]
            lines=[{"text":t.strip(),"confidence":scores[i] if i<len(scores) else 0.0}
                   for i,t in enumerate(texts) if t.strip()]
            text="\n".join(x["text"] for x in lines)
            conf=sum(x["confidence"] for x in lines)/len(lines) if lines else 0.0
            return {"image_index":index,"text":text,"confidence":round(conf,4),
                    "lines":lines,"error":None}
        except Exception as e:
            return {"image_index":index,"text":"","confidence":0.0,"lines":[],"error":str(e)}

    def read_images(self,paths):
        items=[self.read_image(p,i) for i,p in enumerate(paths,1)]
        vals=[x["confidence"] for x in items if x["text"]]
        return {"engine":self.engine_name,
                "overall_confidence":round(sum(vals)/len(vals),4) if vals else 0.0,
                "images":items}
