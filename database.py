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
        max_iops INTEGER NOT NULL
    )
    """)
    
    # Create allocations table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        required_size REAL NOT NULL,
        workload_iops INTEGER NOT NULL,
        availability_req REAL NOT NULL,
        budget REAL,
        recommended_tier_id INTEGER,
        cost_estimate REAL NOT NULL,
        availability_prediction REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (recommended_tier_id) REFERENCES storage_tiers(id)
    )
    """)
    
    conn.commit()
    
    # Seed default tiers if empty
    cursor.execute("SELECT COUNT(*) FROM storage_tiers")
    if cursor.fetchone()[0] == 0:
        default_tiers = [
            ('High-Performance (NVMe)', 0.15, 99.999, 100000),
            ('Standard (SSD)', 0.08, 99.99, 10000),
            ('Capacity (HDD)', 0.03, 99.9, 1000),
            ('Archive (Cold Storage)', 0.01, 99.0, 100)
        ]
        cursor.executemany(
            "INSERT INTO storage_tiers (name, cost_per_gb, sla_availability, max_iops) VALUES (?, ?, ?, ?)",
            default_tiers
        )
        conn.commit()
        
    conn.close()

def get_storage_tiers():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM storage_tiers", conn)
    conn.close()
    return df

def save_allocation(required_size, workload_iops, availability_req, budget, tier_id, cost_estimate, availability_prediction):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO allocations 
        (required_size, workload_iops, availability_req, budget, recommended_tier_id, cost_estimate, availability_prediction, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (required_size, workload_iops, availability_req, budget, tier_id, cost_estimate, availability_prediction, created_at))
    conn.commit()
    conn.close()

def get_allocation_history():
    conn = get_connection()
    query = """
        SELECT a.id, a.required_size, a.workload_iops, a.availability_req, a.budget, 
               t.name as recommended_tier, a.cost_estimate, a.availability_prediction, a.created_at
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
