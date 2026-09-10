from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False
)


image_path = input("Enter image path: ")

result = ocr.predict(image_path)

for res in result:
    res.print()
