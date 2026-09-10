import { useState } from "react";
import "./App.css";

function App() {
  const [page, setPage] = useState("dashboard");
  const [selectedImage, setSelectedImage] = useState(null);
  const [analysis, setAnalysis] = useState(false);
  const [compliance, setCompliance] = useState(false);

  return (
    <div className="app">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="logo">
          <div className="logo-icon">🔷</div>

          <div>
            <strong>LegalScan</strong>
            <small>Legal Metrology Compliance</small>
          </div>
        </div>

        <nav>

          <div
            className={`nav-item ${page === "dashboard" ? "active" : ""}`}
            onClick={() => setPage("dashboard")}
          >
            🏠 Dashboard
          </div>

          <div
            className={`nav-item ${page === "scan" ? "active" : ""}`}
            onClick={() => setPage("scan")}
          >
            📷 Scan Product
          </div>

          <div className="nav-item">
            🕘 History
          </div>

          <div className="nav-item">
            📄 Reports
          </div>

          <div className="nav-item">
            🔔 Notifications
          </div>

          <div className="nav-item">
            👤 Profile
          </div>

        </nav>

        <div className="logout">
          ↪ Logout
        </div>

      </aside>


      {/* MAIN CONTENT */}
      <div className="content">

        {/* TOP BAR */}
        <header className="topbar">

          <div>
            <h2>
              {page === "dashboard"
                ? "Dashboard"
                : "Scan Product"}
            </h2>

            <p>
              Legal Metrology Compliance System
            </p>
          </div>

          <div className="user">
            🔔
            <div className="avatar">A</div>
            <span>Team Alpha</span>
            {compliance && (
  <section className="analysis-page">
    <button
      className="back-button"
      onClick={() => setCompliance(false)}
    >
      ← Back to Analysis
    </button>

    <div className="analysis-card">
      <h1>Compliance Result</h1>
      <p>Legal Metrology compliance assessment</p>

      <div className="compliance-status">
        <div className="status-icon">✓</div>
        <div>
          <h2>Compliant</h2>
          <p>No major violations detected in this demo analysis.</p>
        </div>
      </div>

      <h2>Compliance Checklist</h2>
      <div className="info-row">
  <span>Manufacturer / Packer / Importer Details</span>
  <strong>✓ Detected</strong>
</div>

<div className="info-row">
  <span>Common / Generic Name</span>
  <strong>✓ Detected</strong>
</div>

<div className="info-row">
  <span>Net Quantity</span>
  <strong>✓ Detected</strong>
</div>

<div className="info-row">
  <span>Maximum Retail Price (MRP)</span>
  <strong>✓ Detected</strong>
</div>

<div className="info-row">
  <span>Country of Origin</span>
  <strong>✓ Detected</strong>
</div>

<div className="info-row">
  <span>Manufacturing / Packing Information</span>
  <strong>✓ Detected</strong>
</div>

<div className="info-row">
  <span>Best Before / Use By</span>
  <strong>✓ Detected</strong>
</div>

<div className="info-row">
  <span>Consumer Care Details</span>
  <strong>✓ Detected</strong>
</div>

<div className="info-row">
  <span>Unit Sale Price</span>
  <strong>✓ Detected</strong>
    </div>

      <button
        className="primary-button"
        onClick={() => alert("Report generation will be added next.")}
      >
        📄 Generate Compliance Report
      </button>
    </div>
   </section>
  )}
          </div>

        </header>


        {/* PAGE CONTENT */}

        {page === "dashboard" && (

          <main>

            <section className="hero">

              <div>

                <div className="eyebrow">
                  AI-POWERED INSPECTION
                </div>

                <h1>
                  Check Packaged Commodity
                  <br />
                  Compliance
                </h1>

                <p className="hero-text">
                  Scan product labels and automatically
                  verify required declarations under
                  Legal Metrology rules.
                </p>

                <button
                  className="primary-button"
                  onClick={() => setPage("scan")}
                >
                  📷 Scan Product
                </button>

                <button className="secondary-button">
                  ⓘ How It Works
                </button>

              </div>

              <div className="hero-visual">

                <div className="scan-corners"></div>

                📦

              </div>

            </section>


            {/* STATISTICS */}

            <section className="stats">

              <div className="stat-card">
                <span>📦</span>
                <div>
                  <small>Total Scans</small>
                  <strong>1,248</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>✅</span>
                <div>
                  <small>Compliant</small>
                  <strong>842</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>❌</span>
                <div>
                  <small>Non-Compliant</small>
                  <strong>406</strong>
                </div>
              </div>

              <div className="stat-card">
                <span>📊</span>
                <div>
                  <small>Compliance Rate</small>
                  <strong>67.6%</strong>
                </div>
              </div>

            </section>


            {/* FEATURES */}

            <h2 className="section-title">
              Inspection Tools
            </h2>

            <section className="feature-grid">

              <div className="feature-card">

                <div className="feature-icon">
                  📷
                </div>

                <h3>Instant Scan</h3>

                <p>
                  Scan product labels using
                  camera or upload an image.
                </p>

                <button
                  className="card-button"
                  onClick={() => setPage("scan")}
                >
                  Start Scan →
                </button>

              </div>


              <div className="feature-card">

                <div className="feature-icon">
                  🤖
                </div>

                <h3>AI Analysis</h3>

                <p>
                  Extract product information
                  from the package label.
                </p>

              </div>


              <div className="feature-card">

                <div className="feature-icon">
                  ✓
                </div>

                <h3>Compliance Check</h3>

                <p>
                  Check declarations against
                  Legal Metrology requirements.
                </p>

              </div>


              <div className="feature-card">

                <div className="feature-icon">
                  📄
                </div>

                <h3>Detailed Report</h3>

                <p>
                  Generate a report showing
                  violations and recommendations.
                </p>

              </div>

            </section>


            {/* RECENT */}

            <section className="recent">

              <div className="section-header">

                <h2>Recent Inspections</h2>

                <button className="view-button">
                  View All →
                </button>

              </div>

              <div className="table">

                <div className="table-row header-row">
                  <span>Product</span>
                  <span>Status</span>
                  <span>Date</span>
                </div>

                <div className="table-row">
                  <span>Sample Product</span>
                  <span className="success">
                    ✓ Compliant
                  </span>
                  <span>Today</span>
                </div>

              </div>

            </section>

          </main>

        )}


        {/* SCAN PAGE */}

        {page === "scan" && (

          <main>

            <button
              className="back-button"
              onClick={() => setPage("dashboard")}
            >
              ← Back to Dashboard
            </button>

            <section className="scan-page">

              <div className="scan-header">

                <h1>
                  Upload or Capture Product Image
                </h1>

                <p>
                  Upload a clear image of the product
                  package or label to begin analysis.
                </p>

              </div>


              <div className="scan-options">

                <div className="scan-option active-option">
                  📁 Upload Image
                </div>

                <div className="scan-option">
                  📷 Capture Image
                </div>

              </div>


              <div className="upload-box">
            {!selectedImage ? (
    <>
      <div className="cloud-icon">
        ☁️
      </div>

      <h2>
        Drag & Drop Product Image
      </h2>

      <p>
        or
      </p>

      <label className="browse-button">

        Browse File

        <input
          type="file"
          accept="image/*"
          hidden
          onChange={(event) => {
            const file = event.target.files[0];

            if (file) {
              setSelectedImage(
                URL.createObjectURL(file)
              );
            }
          }}
        />

      </label>

      <p className="file-info">
        Supported formats: JPG, PNG, JPEG
        (Maximum 10 MB)
      </p>
    </>
  ) : (
    <>
      <h2>Product Image Preview</h2>

      <img
        src={selectedImage}
        alt="Selected product"
        className="product-preview"
      />

      <div className="preview-actions">

        <button
          className="secondary-button"
          onClick={() => setSelectedImage(null)}
        >
          Choose Another
        </button>

        <button
          className="primary-button"
          onClick={() => setAnalysis("True")}
        >
          🤖 Analyze Image
        </button>
        
        </div>
        </>
      )}
   </div>

      


              <div className="tip-box">

                💡 <strong>Tip:</strong> Make sure the
                product label is clear and all required
                information is visible.

              </div>

            </section>

          </main>

        )}

      {analysis && (
  <section className="analysis-page">

    <button
      className="back-button"
      onClick={() => setAnalysis(false)}
    >
      ← Back
    </button>

    <div className="analysis-card">

      <h1>AI Analysis Results</h1>

      <p>
        Information extracted from the product label
      </p>

      <div className="analysis-layout">

        <div className="image-section">

          <img
            src={selectedImage}
            alt="Product"
            className="analysis-image"
          />

          <div className="quality-box">
            🟢 Image Quality: Good
          </div>

        </div>

        <div className="information-section">

          <h2>Extracted Information</h2>

          <div className="info-row">
            <span>Product Name</span>
            <strong>Potato Chips</strong>
          </div>

          <div className="info-row">
            <span>Net Quantity</span>
            <strong>50 g</strong>
          </div>

          <div className="info-row">
            <span>MRP</span>
            <strong>₹20</strong>
          </div>

          <div className="info-row">
            <span>Batch No.</span>
            <strong>B12345</strong>
          </div>

          <div className="info-row">
            <span>Manufacturing Date</span>
            <strong>01/05/2026</strong>
          </div>

          <div className="info-row">
            <span>Use By</span>
            <strong>30/10/2026</strong>
          </div>

          <div className="info-row">
            <span>Manufacturer</span>
            <strong>ABC Foods Pvt. Ltd.</strong>
          </div>

          <div className="info-row">
            <span>FSSAI License</span>
            <strong>10012022000123</strong>
          </div>

        </div>

      </div>
      <button
      className="primary-button"
      onClick={() => setCompliance(true)}
      >
      ✓ Check Compliance
    </button>
      
     </div>

    </section>
  )}

      </div>

    </div>
  );
}

export default App