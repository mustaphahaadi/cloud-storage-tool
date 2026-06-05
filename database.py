import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_FILE = "storage_allocation.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create storage_tiers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS storage_tiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cost_per_gb REAL NOT NULL,
        sla_availability REAL NOT NULL,
        access_latency REAL NOT NULL
    )
    """)
    
    # Create allocations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        required_size REAL NOT NULL,
        availability_req REAL NOT NULL,
        latency_req REAL NOT NULL,
        budget REAL,
        alpha REAL DEFAULT 0.5,
        beta REAL DEFAULT 0.5,
        recommended_tier_id INTEGER,
        cost_estimate REAL NOT NULL,
        availability_prediction REAL NOT NULL,
        latency_prediction REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (recommended_tier_id) REFERENCES storage_tiers(id)
    )
    """)
    
    conn.commit()
    
    # Seed default tiers if empty
    cursor.execute("SELECT COUNT(*) FROM storage_tiers")
    if cursor.fetchone()[0] == 0:
        default_tiers = [
            ('Block Storage', 0.15, 99.999, 2.0),
            ('File Storage', 0.08, 99.99, 10.0),
            ('Object Storage', 0.02, 99.0, 50.0)
        ]
        cursor.executemany(
            "INSERT INTO storage_tiers (name, cost_per_gb, sla_availability, access_latency) VALUES (?, ?, ?, ?)",
            default_tiers
        )
        conn.commit()
        
    conn.close()

def get_storage_tiers():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM storage_tiers", conn)
    conn.close()
    return df

def save_allocation(required_size, availability_req, latency_req, budget, alpha, beta, tier_id, cost_estimate, availability_prediction, latency_prediction):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO allocations 
        (required_size, availability_req, latency_req, budget, alpha, beta, recommended_tier_id, cost_estimate, availability_prediction, latency_prediction, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (required_size, availability_req, latency_req, budget, alpha, beta, tier_id, cost_estimate, availability_prediction, latency_prediction, created_at))
    conn.commit()
    conn.close()

def get_allocation_history():
    conn = get_connection()
    query = """
        SELECT a.id, a.required_size, a.availability_req, a.latency_req, a.budget, a.alpha, a.beta,
               t.name as recommended_tier, a.cost_estimate, a.availability_prediction, a.latency_prediction, a.created_at
        FROM allocations a
        LEFT JOIN storage_tiers t ON a.recommended_tier_id = t.id
        ORDER BY a.created_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Initialize DB on load
if not os.path.exists(DB_FILE):
    init_db()
else:
    # Ensure tables exist even if file exists
    init_db()
