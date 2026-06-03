from database import get_storage_tiers

def allocate_storage(required_size, workload_iops, availability_req, budget=None):
    """
    Heuristic algorithm to allocate storage based on requirements.
    Selects the most cost-effective tier that meets SLA and IOPS requirements.
    """
    tiers_df = get_storage_tiers()
    
    # Filter by availability SLA and workload IOPS
    eligible_tiers = tiers_df[
        (tiers_df['sla_availability'] >= availability_req) &
        (tiers_df['max_iops'] >= workload_iops)
    ].copy()
    
    if eligible_tiers.empty:
        return {
            "success": False,
            "message": "No single storage tier meets both the Availability and IOPS requirements."
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
        eligible_tiers = budget_eligible
        
    # Select the lowest cost tier
    best_tier = eligible_tiers.loc[eligible_tiers['total_cost'].idxmin()]
    
    return {
        "success": True,
        "tier_id": int(best_tier['id']),
        "tier_name": best_tier['name'],
        "cost_estimate": float(best_tier['total_cost']),
        "availability_prediction": float(best_tier['sla_availability'])
    }
