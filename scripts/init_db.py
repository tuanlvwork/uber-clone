"""
Database Initialization Script
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import init_db, SessionLocal, Driver, Rider
from config.kafka_config import create_kafka_topics


def create_sample_data():
    """Create sample drivers and riders"""
    db = SessionLocal()
    
    try:
        # Create sample drivers
        drivers = [
            Driver(
                name="John Doe",
                email="john@example.com",
                phone="+1234567890",
                vehicle_type="sedan",
                vehicle_number="ABC-1234",
                current_lat=40.7128,
                current_lon=-74.0060,
                is_online=True
            ),
            Driver(
                name="Jane Smith",
                email="jane@example.com",
                phone="+1234567891",
                vehicle_type="suv",
                vehicle_number="XYZ-5678",
                current_lat=40.7580,
                current_lon=-73.9855,
                is_online=True
            ),
            Driver(
                name="Mike Johnson",
                email="mike@example.com",
                phone="+1234567892",
                vehicle_type="bike",
                vehicle_number="MNO-9012",
                current_lat=40.7489,
                current_lon=-73.9680,
                is_online=True
            ),
        ]
        
        for driver in drivers:
            db.add(driver)
        
        # Create sample riders
        riders = [
            Rider(
                name="Alice Brown",
                email="alice@example.com",
                phone="+1234567893"
            ),
            Rider(
                name="Bob Wilson",
                email="bob@example.com",
                phone="+1234567894"
            ),
        ]
        
        for rider in riders:
            db.add(rider)
        
        db.commit()
        print("✓ Sample data created successfully")
        print(f"  - Created {len(drivers)} drivers")
        print(f"  - Created {len(riders)} riders")
        
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    print("Initializing Uber Clone Database...")
    print("-" * 50)
    
    # Initialize database
    print("Creating database tables...")
    init_db()
    print("✓ Database tables created")
    
    # Create Kafka topics
    print("\nCreating Kafka topics...")
    create_kafka_topics()
    print("✓ Kafka topics created")
    
    # Create sample data
    print("\nCreating sample data...")
    create_sample_data()
    
    print("\n" + "=" * 50)
    print("Database initialization complete!")
    print("=" * 50)
