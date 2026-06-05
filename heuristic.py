from database import get_storage_tiers

def allocate_first_fit(tiers_df, required_size, availability_req, latency_req):
    # First Fit scans tiers in database order (Block, File, Object) and picks the first matching tier
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
    # Best Fit selects the tier that meets requirements and minimizes availability slack
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
    # Worst Fit selects the tier that meets requirements and maximizes availability slack (over-provisioning)
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
    
    # Filter by availability SLA and access latency
    eligible_tiers = tiers_df[
        (tiers_df['sla_availability'] >= availability_req) &
        (tiers_df['access_latency'] <= latency_req)
    ].copy()
    
    if eligible_tiers.empty:
        return {
            "success": False,
            "message": "No single storage tier meets both the Availability and Latency requirements."
        }
        
    # Calculate estimated cost
    eligible_tiers['total_cost'] = eligible_tiers['cost_per_gb'] * required_size
    
    # Filter by budget if provided
    if budget is not None and budget > 0:
        budget_eligible = eligible_tiers[eligible_tiers['total_cost'] <= budget]
        if budget_eligible.empty:
            min_cost_tier = eligible_tiers.loc[eligible_tiers['total_cost'].idxmin()]
            return {
                "success": False,
                "message": f"No storage tier meets the requirements within budget. Closest option: {min_cost_tier['name']} at ${min_cost_tier['total_cost']:.2f}"
            }
        eligible_tiers = budget_eligible.copy()
        
    # Compute normalized objectives for the multi-objective scoring
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
        score = alpha * c_norm + beta * u_norm
        scores.append(score)
        
    eligible_tiers['score'] = scores
    
    # Select the tier that minimizes the weighted score
    best_tier = eligible_tiers.loc[eligible_tiers['score'].idxmin()]
    
    # Run comparative baseline algorithms for comparison
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
