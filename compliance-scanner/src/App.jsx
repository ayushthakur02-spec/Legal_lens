import React, { useEffect, useState } from "react";
import OCRScanner from "./assets/components/OCRScanner";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";


// ============================================================
// DASHBOARD
// ============================================================

function Dashboard({ inspections, onScan }) {
  const total = inspections.length;

  const passed = inspections.filter(
    (item) => item.overall_status === "PASS"
  ).length;

  const review = inspections.filter(
    (item) => item.overall_status === "REVIEW"
  ).length;

  return (
    <div className="dashboard-page">

      <section className="dashboard-hero">
        <div className="hero-content">
          <div className="hero-label">
            AI-POWERED COMPLIANCE ASSISTANT
          </div>

          <h1>
            Packaged Commodity
            <br />
            Compliance Made Simple
          </h1>

          <p>
            Scan product labels, extract important declarations,
            and perform a preliminary Legal Metrology compliance check.
          </p>

          <button
            className="upload-button"
            onClick={onScan}
          >
            Scan Product
          </button>
        </div>
      </section>


      <section className="stats-grid">

        <div className="stat-card">
          <div className="feature-icon">📦</div>
          <h2>{total}</h2>
          <p>Total Inspections</p>
        </div>

        <div className="stat-card">
          <div className="feature-icon">✓</div>
          <h2>{passed}</h2>
          <p>Passed</p>
        </div>

        <div className="stat-card">
          <div className="feature-icon">⚠</div>
          <h2>{review}</h2>
          <p>Needs Review</p>
        </div>

      </section>


      <section className="feature-grid">

        <div className="feature-card">
          <div className="feature-icon">📷</div>
          <h3>Smart Scanning</h3>
          <p>
            Upload a product image and automatically analyze
            the visible package declarations.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🔎</div>
          <h3>OCR Extraction</h3>
          <p>
            Important label information can be converted into
            structured product fields.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">⚖</div>
          <h3>Compliance Check</h3>
          <p>
            Check important declarations and identify
            PASS, REVIEW or FAIL conditions.
          </p>
        </div>

      </section>


      <section className="recent-section">

        <div className="section-title">
          <h2>Recent Inspections</h2>
        </div>

        {inspections.length === 0 ? (

          <p>No inspections yet. Scan a product to create one.</p>

        ) : (

          <div className="recent-table">

            <div className="recent-row recent-head">
              <span>Product</span>
              <span>MRP</span>
              <span>Status</span>
              <span>Date</span>
            </div>

            {inspections.slice(0, 5).map((item) => (

              <div
                className="recent-row"
                key={item.id}
              >

                <span>
                  {item.product_name || "Unknown Product"}
                </span>

                <span>
                  {item.mrp || "—"}
                </span>

                <span>
                  {item.overall_status || "REVIEW"}
                </span>

                <span>
                  {item.inspection_time || "—"}
                </span>

              </div>

            ))}

          </div>

        )}

      </section>


      <div className="disclaimer">
        <strong>Important:</strong> PackCheck AI is an
        AI-assisted preliminary screening tool. It does not
        replace inspection or certification by an authorised
        Legal Metrology officer.
      </div>

    </div>
  );
}


// ============================================================
// RESULTS
// ============================================================

function Results({ result, onScan }) {

  if (!result) {

    return (
      <div className="analysis-page">

        <div className="analysis-card">

          <h1>No Inspection Result</h1>

          <p>
            Scan a packaged commodity first to view its
            compliance analysis.
          </p>

          <button
            className="upload-button"
            onClick={onScan}
          >
            Scan Product
          </button>

        </div>

      </div>
    );
  }


  const fields = result.fields || {};

  const compliance = result.compliance || {};

  const checks = compliance.checks || [];

  const status =
    compliance.overallStatus ||
    "REVIEW";


  return (
    <div className="analysis-page">

      <div className="analysis-card">

        <div className="compliance-status">

          <div className="status-icon">
            {status === "PASS"
              ? "✓"
              : status === "FAIL"
              ? "✕"
              : "!"}
          </div>

          <div>
            <h1>
              {status}
            </h1>

            <p>
              Preliminary Compliance Result
            </p>
          </div>

        </div>


        <h2>Extracted Product Information</h2>

        <div className="fields-grid">

          {Object.entries(fields)
            .filter(
              ([, value]) =>
                value !== null &&
                value !== undefined &&
                String(value).trim() !== ""
            )
            .map(([key, value]) => (

              <div
                className="field-card"
                key={key}
              >

                <strong>
                  {formatFieldName(key)}
                </strong>

                <span>
                  {value}
                </span>

              </div>

            ))}

        </div>


        <h2>Compliance Checks</h2>

        <div className="checks-list">

          {checks.length === 0 ? (

            <p>
              No individual compliance checks available.
            </p>

          ) : (

            checks.map((check, index) => (

              <div
                className="check-row"
                key={index}
              >

                <div>
                  <strong>
                    {check.field || "Compliance Check"}
                  </strong>

                  <p>
                    {check.message || ""}
                  </p>
                </div>

                <span className="check-status">
                  {check.status || "REVIEW"}
                </span>

              </div>

            ))

          )}

        </div>


        {result.inspectionId && (

          <p style={{ marginTop: "20px" }}>
            <strong>Inspection ID:</strong>{" "}
            #{result.inspectionId}
          </p>

        )}


        <div className="result-actions">

          <button
            className="upload-button"
            onClick={onScan}
          >
            Scan Another Product
          </button>

        </div>


        <div className="disclaimer">
          This result is an AI-assisted preliminary screening
          and should be verified by an authorised inspector.
        </div>

      </div>

    </div>
  );
}


// ============================================================
// FIELD NAME FORMATTER
// ============================================================

function formatFieldName(key) {

  const names = {
    productName: "Product Name",
    netQuantity: "Net Quantity",
    mrp: "Maximum Retail Price",
    batchNumber: "Batch / Lot Number",
    packagingDate: "Date of Packaging",
    useBy: "Use By / Best Before",
    fssaiLicense: "FSSAI License",
    countryOfOrigin: "Country of Origin",
    manufacturer: "Manufacturer",
    customerCare: "Consumer Care"
  };

  return (
    names[key] ||
    key
      .replace(/([A-Z])/g, " $1")
      .replace(/^./, (str) => str.toUpperCase())
  );
}


// ============================================================
// APP
// ============================================================

export default function App() {

  const [page, setPage] = useState(
    window.location.pathname === "/scan"
      ? "scan"
      : window.location.pathname === "/results"
      ? "results"
      : "dashboard"
  );


  const [result, setResult] = useState(() => {

    try {

      const saved =
        localStorage.getItem("packcheck_result");

      return saved
        ? JSON.parse(saved)
        : null;

    } catch {

      return null;

    }

  });


  const [inspections, setInspections] = useState([]);


  // ----------------------------------------------------------
  // LOAD DATABASE HISTORY
  // ----------------------------------------------------------

  const loadInspections = async () => {

    try {

      const response =
        await fetch(`${API_URL}/api/inspections`);

      const data =
        await response.json();

      if (data.success) {

        setInspections(
          data.inspections || []
        );

      }

    } catch (error) {

      console.log(
        "Unable to load inspection history."
      );

    }

  };


  useEffect(() => {

    loadInspections();

  }, []);


  // ----------------------------------------------------------
  // NAVIGATION
  // ----------------------------------------------------------

  const navigate = (target) => {

    const path =
      target === "dashboard"
        ? "/"
        : `/${target}`;

    window.history.pushState(
      {},
      "",
      path
    );

    setPage(target);

    if (target === "dashboard") {
      loadInspections();
    }

  };


  // ----------------------------------------------------------
  // HANDLE NEW RESULT
  // ----------------------------------------------------------

  const handleResult = (data) => {

    setResult(data);

    localStorage.setItem(
      "packcheck_result",
      JSON.stringify(data)
    );

    loadInspections();

    navigate("results");

  };


  // ----------------------------------------------------------
  // SIDEBAR
  // ----------------------------------------------------------

  return (

    <div className="app">

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-icon">
            ✓
          </div>

          <div>
            <strong>
              PackCheck AI
            </strong>

            <small>
              Compliance Assistant
            </small>
          </div>

        </div>


        <nav className="sidebar-nav">

          <button
            className={
              `nav-item ${
                page === "dashboard"
                  ? "active"
                  : ""
              }`
            }
            onClick={() =>
              navigate("dashboard")
            }
          >
            🏠
            <span>
              Dashboard
            </span>
          </button>


          <button
            className={
              `nav-item ${
                page === "scan"
                  ? "active"
                  : ""
              }`
            }
            onClick={() =>
              navigate("scan")
            }
          >
            📷
            <span>
              Scan Product
            </span>
          </button>


          <button
            className={
              `nav-item ${
                page === "results"
                  ? "active"
                  : ""
              }`
            }
            onClick={() =>
              navigate("results")
            }
          >
            📋
            <span>
              Results
            </span>
          </button>

        </nav>


        <div className="sidebar-bottom">

          <div className="sidebar-info">
            <strong>
              SIH 2026 Prototype
            </strong>

            <span>
              AI-assisted preliminary
              compliance screening
            </span>
          </div>

        </div>

      </aside>


      <main className="main-content">

        <header className="topbar">

          <div>
            <strong>
              PackCheck AI
            </strong>
          </div>

          <div className="user-area">

            <div className="user-icon">
              👤
            </div>

          </div>

        </header>


        {page === "dashboard" && (

          <Dashboard
            inspections={inspections}
            onScan={() =>
              navigate("scan")
            }
          />

        )}


        {page === "scan" && (

          <OCRScanner
            onResult={handleResult}
          />

        )}


        {page === "results" && (

          <Results
            result={result}
            onScan={() =>
              navigate("scan")
            }
          />

        )}

      </main>

    </div>

  );
}