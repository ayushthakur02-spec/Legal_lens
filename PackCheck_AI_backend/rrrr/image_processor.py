import cv2
from pathlib import Path

def preprocess_image(input_path,output_path):
    image=cv2.imread(input_path)
    if image is None: return {"ok":False,"error":"Cannot read image"}
    h,w=image.shape[:2]
    if w>1800:
        s=1800/w
        image=cv2.resize(image,(int(w*s),int(h*s)),interpolation=cv2.INTER_AREA)
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray=cv2.fastNlMeansDenoising(gray,None,8,7,21)
    clahe=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    enhanced=clahe.apply(gray)
    Path(output_path).parent.mkdir(parents=True,exist_ok=True)
    cv2.imwrite(output_path,enhanced,[cv2.IMWRITE_JPEG_QUALITY,95])
    return {"ok":True,"path":output_path}
