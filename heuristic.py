from database import get_storage_tiers

def suggest_workload_size(workload_category, params):
    """
    Automatically calculates suggested storage capacity (in GB) based on workload profiles.
    Applies empirical growth models across enterprise workload categories.
    """
    if workload_category == "Enterprise Relational Database (OLTP)":
        users = params.get("users", 1000)
        transactions = params.get("transactions", 50000)
        # Base 20GB + 0.05GB per user + 0.0001GB per transaction
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
        total_mb = employees * docs_per_emp * avg_doc_mb
        return round(total_mb / 1024.0, 2)
        
    elif workload_category == "Cold Backup & System Archive":
        snapshot_gb = params.get("snapshot_gb", 500.0)
        retention_count = params.get("retention_count", 6)
        return round(snapshot_gb * retention_count, 2)
        
    return 100.0

def allocate_first_fit(tiers_df, required_size, availability_req, latency_req):
    eligible_tiers = tiers_df[
        (tiers_df['sla_availability'] >= availability_req) &
        (tiers_df['access_latency'] <= latency_req)
    ]
    if eligible_tiers.empty:
        return None
    best_tier = eligible_tiers.iloc[0]
    return {
        "tier_name": best_tier['name'],
        "cost_estimate": float(best_tier['cost_per_gb'] * required_size),
        "availability_prediction": float(best_tier['sla_availability']),
        "latency_prediction": float(best_tier['access_latency'])
    }

def allocate_best_fit(tiers_df, required_size, availability_req, latency_req):
    eligible_tiers = tiers_df[
        (tiers_df['sla_availability'] >= availability_req) &
        (tiers_df['access_latency'] <= latency_req)
    ].copy()
    if eligible_tiers.empty:
        return None
    eligible_tiers['excess_avail'] = eligible_tiers['sla_availability'] - availability_req
    best_tier = eligible_tiers.loc[eligible_tiers['excess_avail'].idxmin()]
    return {
        "tier_name": best_tier['name'],
        "cost_estimate": float(best_tier['cost_per_gb'] * required_size),
        "availability_prediction": float(best_tier['sla_availability']),
        "latency_prediction": float(best_tier['access_latency'])
    }

def allocate_worst_fit(tiers_df, required_size, availability_req, latency_req):
    eligible_tiers = tiers_df[
        (tiers_df['sla_availability'] >= availability_req) &
        (tiers_df['access_latency'] <= latency_req)
    ].copy()
    if eligible_tiers.empty:
        return None
    eligible_tiers['excess_avail'] = eligible_tiers['sla_availability'] - availability_req
    best_tier = eligible_tiers.loc[eligible_tiers['excess_avail'].idxmax()]
    return {
        "tier_name": best_tier['name'],
        "cost_estimate": float(best_tier['cost_per_gb'] * required_size),
        "availability_prediction": float(best_tier['sla_availability']),
        "latency_prediction": float(best_tier['access_latency'])
    }

def allocate_storage(required_size, availability_req, latency_req, budget=None, alpha=0.5, beta=0.5):
    """
    Heuristic alpha-beta dual-objective scoring algorithm to allocate storage based on requirements.
    Balances cost optimization and SLA availability deviation using a weighted scoring model.
    """
    tiers_df = get_storage_tiers()
    
    eligible_tiers = tiers_df[
        (tiers_df['sla_availability'] >= availability_req) &
        (tiers_df['access_latency'] <= latency_req)
    ].copy()
    
    if eligible_tiers.empty:
        return {
            "success": False,
            "message": "No single storage tier meets both the Availability and Latency requirements."
        }
        
    eligible_tiers['total_cost'] = eligible_tiers['cost_per_gb'] * required_size
    
    if budget is not None and budget > 0:
        budget_eligible = eligible_tiers[eligible_tiers['total_cost'] <= budget]
        if budget_eligible.empty:
            min_cost_tier = eligible_tiers.loc[eligible_tiers['total_cost'].idxmin()]
            return {
                "success": False,
                "message": f"No storage tier meets requirements within budget. Closest option: {min_cost_tier['name']} at ${min_cost_tier['total_cost']:.2f}"
            }
        eligible_tiers = budget_eligible.copy()
        
    eligible_tiers['unavailability'] = 1.0 - (eligible_tiers['sla_availability'] / 100.0)
    
    min_cost = eligible_tiers['total_cost'].min()
    max_cost = eligible_tiers['total_cost'].max()
    min_unavail = eligible_tiers['unavailability'].min()
    max_unavail = eligible_tiers['unavailability'].max()
    
    cost_range = max_cost - min_cost
    unavail_range = max_unavail - min_unavail
    
    scores = []
    for idx, row in eligible_tiers.iterrows():
        c_norm = (row['total_cost'] - min_cost) / cost_range if cost_range > 0 else 0.0
        u_norm = (row['unavailability'] - min_unavail) / unavail_range if unavail_range > 0 else 0.0
        scores.append(alpha * c_norm + beta * u_norm)
        
    eligible_tiers['score'] = scores
    best_tier = eligible_tiers.loc[eligible_tiers['score'].idxmin()]
    
    baselines = {
        "heuristic": {
            "tier_name": best_tier['name'],
            "cost_estimate": float(best_tier['total_cost']),
            "availability_prediction": float(best_tier['sla_availability']),
            "latency_prediction": float(best_tier['access_latency'])
        },
        "first_fit": allocate_first_fit(tiers_df, required_size, availability_req, latency_req),
        "best_fit": allocate_best_fit(tiers_df, required_size, availability_req, latency_req),
        "worst_fit": allocate_worst_fit(tiers_df, required_size, availability_req, latency_req)
    }
    
    return {
        "success": True,
        "tier_id": int(best_tier['id']),
        "tier_name": best_tier['name'],
        "cost_estimate": float(best_tier['total_cost']),
        "availability_prediction": float(best_tier['sla_availability']),
        "latency_prediction": float(best_tier['access_latency']),
        "baselines": baselines
    }
