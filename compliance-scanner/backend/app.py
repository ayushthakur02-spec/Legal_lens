from flask import Flask

from paddleocr import PaddleOCR

app = Flask(__name__)

# Initialize PaddleOCR
ocr = PaddleOCR(
    lang="en"
)


@app.route("/")
def home():
    return "LegalScan Backend is running!"


if __name__ == "__main__":
    app.run(debug=True)