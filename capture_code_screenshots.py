import os
import time
from playwright.sync_api import sync_playwright

CODE_SNIPPETS = {
    "fig_4_5_code_db.png": {
        "title": "Code Module 4.1: Database Persistence Layer & Initialization (database.py)",
        "code": """def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create storage_tiers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS storage_tiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cost_per_gb REAL NOT NULL,
        sla_availability REAL NOT NULL,
        access_latency REAL NOT NULL
    )
    ''')
    
    # Create allocations table with foreign key linkage
    cursor.execute('''
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
    ''')
    conn.commit()
    conn.close()"""
    },
    "fig_4_6_code_suggest.png": {
        "title": "Code Module 4.2: Workload Storage Size Sizing Engine (heuristic.py)",
        "code": """def suggest_workload_size(workload_category, params):
    \"\"\"
    Calculates storage capacity (GB) based on enterprise workload profiles.
    \"\"\"
    if workload_category == "Enterprise Relational Database (OLTP)":
        users = params.get("users", 1000)
        transactions = params.get("transactions", 50000)
        return round(20.0 + (users * 0.05) + (transactions * 0.0001), 2)
        
    elif workload_category == "HD Video & Media Streaming":
        media_count = params.get("media_count", 200)
        avg_file_gb = params.get("avg_file_gb", 2.5)
        return round(media_count * avg_file_gb, 2)
        
    elif workload_category == "IoT Sensor & Log Analytics":
        devices = params.get("devices", 500)
        daily_log_mb = params.get("daily_log_mb", 50.0)
        retention_days = params.get("retention_days", 90)
        total_mb = devices * daily_log_mb * retention_days
        return round(total_mb / 1024.0, 2)
        
    elif workload_category == "Document & Content Management (CMS)":
        employees = params.get("employees", 250)
        docs_per_emp = params.get("docs_per_emp", 400)
        avg_doc_mb = params.get("avg_doc_mb", 5.0)
        return round((employees * docs_per_emp * avg_doc_mb) / 1024.0, 2)
        
    elif workload_category == "Cold Backup & System Archive":
        snapshot_gb = params.get("snapshot_gb", 500.0)
        retention_count = params.get("retention_count", 6)
        return round(snapshot_gb * retention_count, 2)
        
    return 100.0"""
    },
    "fig_4_7_code_heuristic.png": {
        "title": "Code Module 4.3: Dual-Objective Multi-Tier Heuristic Engine (heuristic.py)",
        "code": """def allocate_storage(required_size, availability_req, latency_req, budget=None, alpha=0.5, beta=0.5):
    tiers_df = get_storage_tiers()
    
    # 1. Hard constraint pre-filtering phase
    eligible_tiers = tiers_df[
        (tiers_df['sla_availability'] >= availability_req) &
        (tiers_df['access_latency'] <= latency_req)
    ].copy()
    
    if eligible_tiers.empty:
        return {"success": False, "message": "No tier meets SLA & Latency criteria."}
        
    # 2. Cost calculation & Budget verification
    eligible_tiers['total_cost'] = eligible_tiers['cost_per_gb'] * required_size
    if budget is not None and budget > 0:
        budget_eligible = eligible_tiers[eligible_tiers['total_cost'] <= budget]
        if budget_eligible.empty:
            return {"success": False, "message": "Budget constraint exceeded."}
        eligible_tiers = budget_eligible.copy()
        
    # 3. Min-Max Normalization & Dual-Objective Scoring
    eligible_tiers['unavailability'] = 1.0 - (eligible_tiers['sla_availability'] / 100.0)
    min_c, max_c = eligible_tiers['total_cost'].min(), eligible_tiers['total_cost'].max()
    min_u, max_u = eligible_tiers['unavailability'].min(), eligible_tiers['unavailability'].max()
    
    cost_range = max_c - min_c
    unavail_range = max_u - min_u
    
    scores = []
    for idx, row in eligible_tiers.iterrows():
        c_norm = (row['total_cost'] - min_c) / cost_range if cost_range > 0 else 0.0
        u_norm = (row['unavailability'] - min_u) / unavail_range if unavail_range > 0 else 0.0
        scores.append(alpha * c_norm + beta * u_norm)
        
    eligible_tiers['score'] = scores
    best_tier = eligible_tiers.loc[eligible_tiers['score'].idxmin()]
    return {"success": True, "tier_name": best_tier['name'], "cost_estimate": float(best_tier['total_cost'])}"""
    },
    "fig_4_8_code_baselines.png": {
        "title": "Code Module 4.4: Baseline Allocation Algorithm Routines (heuristic.py)",
        "code": """def allocate_first_fit(tiers_df, required_size, availability_req, latency_req):
    eligible = tiers_df[(tiers_df['sla_availability'] >= availability_req) & (tiers_df['access_latency'] <= latency_req)]
    if eligible.empty: return None
    best = eligible.iloc[0] # Select first matching tier in database order
    return {"tier_name": best['name'], "cost_estimate": float(best['cost_per_gb'] * required_size)}

def allocate_best_fit(tiers_df, required_size, availability_req, latency_req):
    eligible = tiers_df[(tiers_df['sla_availability'] >= availability_req) & (tiers_df['access_latency'] <= latency_req)].copy()
    if eligible.empty: return None
    eligible['excess_avail'] = eligible['sla_availability'] - availability_req
    best = eligible.loc[eligible['excess_avail'].idxmin()] # Minimize excess SLA slack
    return {"tier_name": best['name'], "cost_estimate": float(best['cost_per_gb'] * required_size)}

def allocate_worst_fit(tiers_df, required_size, availability_req, latency_req):
    eligible = tiers_df[(tiers_df['sla_availability'] >= availability_req) & (tiers_df['access_latency'] <= latency_req)].copy()
    if eligible.empty: return None
    eligible['excess_avail'] = eligible['sla_availability'] - availability_req
    best = eligible.loc[eligible['excess_avail'].idxmax()] # Maximize excess SLA slack
    return {"tier_name": best['name'], "cost_estimate": float(best['cost_per_gb'] * required_size)}"""
    },
    "fig_4_9_code_ui.png": {
        "title": "Code Module 4.5: Streamlit Interactive Simulation Controller (modules/allocation.py)",
        "code": """category = st.selectbox("Select Workload Profile Category", options=[
    "Enterprise Relational Database (OLTP)",
    "HD Video & Media Streaming",
    "IoT Sensor & Log Analytics",
    "Document & Content Management (CMS)",
    "Cold Backup & System Archive"
])

# Capture parameter scale inputs
params = {}
if category == "IoT Sensor & Log Analytics":
    params["devices"] = st.number_input("Connected IoT Devices", value=750)
    params["daily_log_mb"] = st.number_input("Daily Log Output per Device (MB)", value=40.0)
    params["retention_days"] = st.number_input("Retention Period (Days)", value=120)

suggested_gb = heuristic.suggest_workload_size(category, params)
st.info(f"💡 **Automated Storage Recommendation**: **{suggested_gb:,.2f} GB** calculated for **{category}**.")

# Form controls with pre-filled storage size recommendation
with st.form("allocation_form"):
    required_size = st.number_input("Required Storage Size (GB)", value=float(suggested_gb))
    latency_req = st.number_input("Max Tolerable Access Latency (ms)", value=15.0)
    availability_req = st.selectbox("Availability Requirement (SLA %)", options=[99.0, 99.9, 99.99, 99.999])
    alpha = st.slider("Cost Optimization Weight (α)", min_value=0.0, max_value=1.0, value=0.5)
    submit_button = st.form_submit_button("Generate Storage Recommendation")"""
    }
}

def generate_html(title, code):
    lines = code.split('\n')
    line_numbers = '\n'.join([str(i+1) for i in range(len(lines))])
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #F8FAFC;
            margin: 0;
            padding: 20px;
        }}
        .card {{
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            max-width: 950px;
            margin: 0 auto;
        }}
        .header {{
            background: #0F172A;
            color: #FFFFFF;
            padding: 12px 20px;
            font-size: 14px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        .code-container {{
            display: flex;
            padding: 16px 0;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
            background: #FFFFFF;
        }}
        .line-numbers {{
            padding: 0 16px;
            color: #94A3B8;
            text-align: right;
            user-select: none;
            border-right: 1px solid #E2E8F0;
        }}
        .code-text {{
            padding: 0 16px;
            color: #0F172A;
            white-space: pre;
            overflow-x: auto;
        }}
        .kw {{ color: #0284C7; font-weight: bold; }}
        .str {{ color: #0D9488; }}
        .cmnt {{ color: #64748B; font-style: italic; }}
        .num {{ color: #D97706; }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">{title}</div>
        <div class="code-container">
            <div class="line-numbers"><pre>{line_numbers}</pre></div>
            <div class="code-text"><pre>{code}</pre></div>
        </div>
    </div>
</body>
</html>"""
    return html_content

def capture_code_screenshots():
    images_dir = os.path.join(os.path.dirname(__file__), 'docs', 'images')
    os.makedirs(images_dir, exist_ok=True)
    temp_html_path = os.path.join(images_dir, 'temp_code.html')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(device_scale_factor=2)
        page = context.new_page()

        for filename, data in CODE_SNIPPETS.items():
            html_content = generate_html(data["title"], data["code"])
            with open(temp_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            page.goto(f"file://{temp_html_path}")
            time.sleep(0.5)
            element = page.locator(".card")
            output_path = os.path.join(images_dir, filename)
            element.screenshot(path=output_path)
            print(f"Captured code screenshot: {filename}")

        browser.close()
    
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)
    print("All code module screenshots successfully generated!")

if __name__ == "__main__":
    capture_code_screenshots()
