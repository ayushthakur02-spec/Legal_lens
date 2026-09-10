import { useState } from "react";
import Tesseract from "tesseract.js";

function extractFields(text) {
  const fields = {
    mrp: "",
    netQuantity: "",
    batchNumber: "",
    manufacturingDate: "",
    useBy: "",
  };

  const mrpMatch = text.match(
    /(?:MRP|M\.R\.P\.?)\s*[:\-]?\s*(?:₹|Rs\.?|INR)?\s*([0-9]+(?:\.[0-9]+)?)/i
  );

  const quantityMatch = text.match(
    /(?:Net\s*(?:Qty|Quantity)|Net\s*Wt\.?)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)\s*(g|kg|ml|l|mg)/i
  );

  const batchMatch = text.match(
    /(?:Batch\s*(?:No\.?|Number)|Lot\s*No\.?)\s*[:\-]?\s*([A-Z0-9\-\/]+)/i
  );

  const dateMatch = text.match(
    /(?:Mfg\.?|Mfd\.?|Manufactured|Manufacturing)\s*(?:Date)?\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i
  );

  const useByMatch = text.match(
    /(?:Use\s*By|Best\s*Before|Expiry|Exp\.?)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i
  );

  if (mrpMatch) fields.mrp = mrpMatch[1];
  if (quantityMatch) fields.netQuantity = quantityMatch[0];
  if (batchMatch) fields.batchNumber = batchMatch[1];
  if (dateMatch) fields.manufacturingDate = dateMatch[1];
  if (useByMatch) fields.useBy = useByMatch[1];

  return fields;
}
function OCRScanner() {
  const [image, setImage] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleImage = (event) => {
    const file = event.target.files[0];

    if (file) {
      setImage(URL.createObjectURL(file));
      setText("");
    }
  };
   
  const runOCR = async () => {
  if (!image) return;

  setLoading(true);
  setText("");

  try {
    const img = new Image();

    img.onload = async () => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      const scale = 3;

      canvas.width = img.width * scale;
      canvas.height = img.height * scale;

      ctx.drawImage(
        img,
        0,
        0,
        canvas.width,
        canvas.height
      );

      const imageData = ctx.getImageData(
        0,
        0,
        canvas.width,
        canvas.height
      );

      const data = imageData.data;

      for (let i = 0; i < data.length; i += 4) {
        const gray =
  0.299 * data[i] +
  0.587 * data[i + 1] +
  0.114 * data[i + 2];

 const threshold = gray;

data[i] = threshold;
data[i + 1] = threshold;
data[i + 2] = threshold;
      }

      ctx.putImageData(imageData, 0, 0);

      const processedImage = canvas.toDataURL("image/png");

      const result = await Tesseract.recognize(
        processedImage,
        "eng",
        {
          logger: (info) => {
            console.log(info);
          },
          tesseract_pageseg_mode: "6",
        }
      );

      setText(result.data.text);
      setLoading(false);
    };

    img.src = image;
  } catch (error) {
    console.error(error);
    setText("Unable to read the image.");
    setLoading(false);
  }
};

  return (
    <div className="ocr-scanner">
      <h2>Product Label OCR</h2>

      <p>
        Upload a product label image and extract its text.
      </p>

      <input
        type="file"
        accept="image/*"
        onChange={handleImage}
      />

      {image && (
        <div>
          <img
            src={image}
            alt="Product label"
            className="product-preview"
          />

          <button
            className="primary-button"
            onClick={runOCR}
            disabled={loading}
          >
            {loading ? "Reading Image..." : "Extract Text"}
          </button>
        </div>
      )}

      {text && (
        <div className="information-section">
          <h3>Extracted Text</h3>
          <pre>{text}</pre>
        </div>
      )}
    </div>
  );
}

export default OCRScanner;