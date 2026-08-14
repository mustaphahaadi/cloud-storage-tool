import database
import heuristic
import random
from datetime import datetime, timedelta

def generate_mock_data():
    database.init_db()
    
    now = datetime.now()
    
    # Generate 100 realistic allocations spread over the last 30 days
    for _ in range(100):
        req_size = random.choice([100, 250, 500, 750, 1000, 1500, 2500, 5000])
        latency = random.choice([5.0, 10.0, 15.0, 30.0, 60.0])
        availability = random.choice([99.0, 99.9, 99.99, 99.999])
        budget = random.choice([0, 0, 100, 250, 500]) # 0 means no budget
        
        alpha = random.choice([0.2, 0.4, 0.5, 0.6, 0.8])
        beta = round(1.0 - alpha, 2)
        
        result = heuristic.allocate_storage(req_size, availability, latency, budget if budget > 0 else None, alpha=alpha, beta=beta)
        
        if result["success"]:
            days_ago = random.randint(1, 30)
            created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO allocations 
                (required_size, availability_req, latency_req, budget, alpha, beta, recommended_tier_id, cost_estimate, availability_prediction, latency_prediction, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (req_size, availability, latency, budget if budget > 0 else None, alpha, beta,
                  result["tier_id"], result["cost_estimate"], result["availability_prediction"], result["latency_prediction"], created_at.isoformat()))
            conn.commit()
            conn.close()

if __name__ == "__main__":
    generate_mock_data()
    print("100 mock allocations seeded into database.")
