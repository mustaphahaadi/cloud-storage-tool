import database
import heuristic
import random
from datetime import datetime, timedelta

def generate_mock_data():
    database.init_db()
    
    # We will generate 20 random allocations spread over the last 30 days
    now = datetime.now()
    
    for _ in range(20):
        # Random inputs
        req_size = random.choice([50, 100, 500, 1000, 2000, 5000])
        latency = random.choice([5.0, 15.0, 60.0])
        availability = random.choice([99.0, 99.9, 99.99, 99.999])
        budget = random.choice([0, 50, 100, 500]) # 0 means no budget
        
        result = heuristic.allocate_storage(req_size, availability, latency, budget if budget > 0 else None)
        
        if result["success"]:
            # Random date within last 30 days
            days_ago = random.randint(1, 30)
            created_at = now - timedelta(days=days_ago)
            
            # Save manually to override created_at
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO allocations 
                (required_size, availability_req, latency_req, budget, recommended_tier_id, cost_estimate, availability_prediction, latency_prediction, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (req_size, availability, latency, budget if budget > 0 else None, 
                  result["tier_id"], result["cost_estimate"], result["availability_prediction"], result["latency_prediction"], created_at.isoformat()))
            conn.commit()
            conn.close()

if __name__ == "__main__":
    generate_mock_data()
    print("Mock data generated.")
