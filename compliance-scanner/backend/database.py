import sqlite3
from datetime import datetime

DATABASE = "packcheck.db"


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            net_quantity TEXT,
            mrp TEXT,
            batch_number TEXT,
            packaging_date TEXT,
            use_by TEXT,
            fssai_license TEXT,
            country_of_origin TEXT,
            manufacturer TEXT,
            customer_care TEXT,
            overall_status TEXT,
            inspection_time TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_inspection(result):
    fields = result.get("fields", {})
    compliance = result.get("compliance", {})

    conn = get_connection()

    cursor = conn.execute("""
        INSERT INTO inspections (
            product_name,
            net_quantity,
            mrp,
            batch_number,
            packaging_date,
            use_by,
            fssai_license,
            country_of_origin,
            manufacturer,
            customer_care,
            overall_status,
            inspection_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        fields.get("productName", ""),
        fields.get("netQuantity", ""),
        fields.get("mrp", ""),
        fields.get("batchNumber", ""),
        fields.get("packagingDate", ""),
        fields.get("useBy", ""),
        fields.get("fssaiLicense", ""),
        fields.get("countryOfOrigin", ""),
        fields.get("manufacturer", ""),
        fields.get("customerCare", ""),
        compliance.get("overallStatus", "REVIEW"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    inspection_id = cursor.lastrowid
    conn.close()

    return inspection_id


def get_inspections():
    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM inspections
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]