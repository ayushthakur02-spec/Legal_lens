import React, { useState } from "react";

const API_URL = "http://127.0.0.1:5000/api/scan";

export default function OCRScanner({ onResult }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    setFile(selectedFile);
    setError("");

    const reader = new FileReader();

    reader.onload = (event) => {
      setPreview(event.target.result);
    };

    reader.readAsDataURL(selectedFile);
  };

  const handleChange = (event) => {
    handleFile(event.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please upload a product image first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();

      formData.append("image", file);

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.error || "Unable to analyze the product."
        );
      }

      if (typeof onResult === "function") {
        onResult(data);
      }

      // Also store the result locally
      localStorage.setItem(
        "packcheck_result",
        JSON.stringify(data)
      );

      // Go to results page if the app uses routing
      if (window.location.pathname !== "/results") {
        window.location.href = "/results";
      }
    } catch (err) {
      console.error(err);
      setError(
        err.message ||
          "Backend connection failed. Make sure Flask is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="scan-page">

      <div className="scan-header">
        <h1>Scan Product</h1>
        <p>
          Upload a packaged commodity label to check
          compliance.
        </p>
      </div>

      <div className="scan-options">

        <div className="upload-box">

          {!preview ? (
            <>
              <div className="upload-icon">
                📷
              </div>

              <h2>Upload Product Image</h2>

              <p>
                Select a clear image of the product
                packaging or label.
              </p>

              <label
                htmlFor="product-image"
                className="upload-button"
              >
                Choose Image
              </label>

              <input
                id="product-image"
                type="file"
                accept="image/*"
                onChange={handleChange}
                style={{ display: "none" }}
              />
            </>
          ) : (
            <div className="preview-area">

              <img
                src={preview}
                alt="Product preview"
                className="product-preview"
              />

              <div className="preview-actions">

                <label
                  htmlFor="product-image"
                  className="upload-button"
                >
                  Change Image
                </label>

                <input
                  id="product-image"
                  type="file"
                  accept="image/*"
                  onChange={handleChange}
                  style={{ display: "none" }}
                />

              </div>

            </div>
          )}

        </div>

      </div>

      {error && (
        <div
          style={{
            marginTop: "20px",
            padding: "12px 16px",
            borderRadius: "10px",
            background: "#fee2e2",
            color: "#991b1b",
            fontWeight: "600",
          }}
        >
          {error}
        </div>
      )}

      {file && (
        <div
          style={{
            marginTop: "20px",
            textAlign: "center",
          }}
        >

          <button
            onClick={handleAnalyze}
            disabled={loading}
            style={{
              padding: "14px 32px",
              border: "none",
              borderRadius: "10px",
              background: "#0b4f8a",
              color: "white",
              fontSize: "16px",
              fontWeight: "700",
              cursor: loading
                ? "not-allowed"
                : "pointer",
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading
              ? "Analyzing..."
              : "Analyze Product"}
          </button>

        </div>
      )}

    </div>
  );
}