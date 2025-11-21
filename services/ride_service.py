"""
Ride Service - Handles ride requests from customers
Publishes ride requests to Kafka for matching service
"""
import sys
import os
import threading
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.kafka_config import KafkaProducerWrapper, KafkaConsumerWrapper, TOPICS
from models.database import SessionLocal, Ride, Rider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RideService:
    """Service to handle ride requests"""
    
    def __init__(self):
        self.producer = KafkaProducerWrapper()
        logger.info("Ride Service initialized")
    
    def create_ride_request(self, ride_data):
        """Create a new ride request"""
        db = SessionLocal()
        
        try:
            # Create ride in database
            ride = Ride(
                rider_id=ride_data['rider_id'],
                pickup_lat=ride_data['pickup_lat'],
                pickup_lon=ride_data['pickup_lon'],
                pickup_address=ride_data['pickup_address'],
                destination_lat=ride_data['destination_lat'],
                destination_lon=ride_data['destination_lon'],
                destination_address=ride_data['destination_address'],
                vehicle_type=ride_data['vehicle_type'],
                status='requested'
            )
            
            db.add(ride)
            db.commit()
            db.refresh(ride)
            
            # Publish to Kafka
            message = {
                'ride_id': ride.id,
                'rider_id': ride.rider_id,
                'pickup_lat': ride.pickup_lat,
                'pickup_lon': ride.pickup_lon,
                'pickup_address': ride.pickup_address,
                'destination_lat': ride.destination_lat,
                'destination_lon': ride.destination_lon,
                'destination_address': ride.destination_address,
                'vehicle_type': ride.vehicle_type,
                'requested_at': ride.requested_at.isoformat()
            }
            
            self.producer.send_message(
                TOPICS['RIDE_REQUESTS'],
                message,
                key=str(ride.id)
            )
            
            logger.info(f"Ride request created: {ride.id}")
            return ride.id
            
        except Exception as e:
            logger.error(f"Error creating ride request: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    def handle_ride_match(self, message):
        """Handle ride match from matching service"""
        db = SessionLocal()
        
        try:
            ride_id = message['ride_id']
            driver_id = message['driver_id']
            
            ride = db.query(Ride).filter(Ride.id == ride_id).first()
            if ride:
                ride.driver_id = driver_id
                ride.status = 'matched'
                ride.matched_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Ride {ride_id} matched with driver {driver_id}")
        except Exception as e:
            logger.error(f"Error handling ride match: {e}")
            db.rollback()
        finally:
            db.close()
    
    def handle_ride_update(self, message):
        """Handle ride status updates"""
        db = SessionLocal()
        
        try:
            ride_id = message['ride_id']
            status = message['status']
            
            ride = db.query(Ride).filter(Ride.id == ride_id).first()
            if ride:
                ride.status = status
                
                if status == 'accepted':
                    ride.accepted_at = datetime.utcnow()
                elif status == 'started':
                    ride.started_at = datetime.utcnow()
                elif status == 'completed':
                    ride.completed_at = datetime.utcnow()
                    if 'fare' in message:
                        ride.fare = message['fare']
                
                db.commit()
                logger.info(f"Ride {ride_id} status updated to {status}")
        except Exception as e:
            logger.error(f"Error handling ride update: {e}")
            db.rollback()
        finally:
            db.close()
    
    def start(self):
        """Start consuming from Kafka topics"""
        # Start Prometheus metrics server
        from prometheus_client import start_http_server
        start_http_server(8002)
        logger.info("Prometheus metrics server started on port 8002")

        # Consume ride matches
        match_consumer = KafkaConsumerWrapper(
            TOPICS['RIDE_MATCHES'],
            'ride-service-group',
            self.handle_ride_match
        )
        
        # Consume ride updates
        update_consumer = KafkaConsumerWrapper(
            TOPICS['RIDE_UPDATES'],
            'ride-service-group',
            self.handle_ride_update
        )
        
        # Start consumers in separate threads
        match_thread = threading.Thread(target=match_consumer.start_consuming)
        update_thread = threading.Thread(target=update_consumer.start_consuming)
        
        match_thread.start()
        update_thread.start()
        
        logger.info("Ride Service started and consuming from Kafka")
        
        # Keep main thread alive
        try:
            match_thread.join()
            update_thread.join()
        except KeyboardInterrupt:
            logger.info("Shutting down Ride Service...")
            match_consumer.stop_consuming()
            update_consumer.stop_consuming()
            self.producer.close()


if __name__ == '__main__':
    service = RideService()
    service.start()
