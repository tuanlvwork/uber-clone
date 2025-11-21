"""
Matching Service - Matches ride requests with available drivers
Consumes ride requests and finds the nearest available driver
"""
import sys
import os
import threading
import logging
import math

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.kafka_config import KafkaProducerWrapper, KafkaConsumerWrapper, TOPICS
from models.database import SessionLocal, Driver, Ride

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingService:
    """Service to match riders with drivers"""
    
    def __init__(self):
        self.producer = KafkaProducerWrapper()
        logger.info("Matching Service initialized")
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def find_nearest_driver(self, pickup_lat, pickup_lon, vehicle_type):
        """Find the nearest available driver"""
        db = SessionLocal()
        
        try:
            # Get all online drivers with matching vehicle type
            drivers = db.query(Driver).filter(
                Driver.is_online == True,
                Driver.vehicle_type == vehicle_type,
                Driver.current_lat.isnot(None),
                Driver.current_lon.isnot(None)
            ).all()
            
            if not drivers:
                logger.warning(f"No available drivers found for vehicle type: {vehicle_type}")
                return None
            
            # Find nearest driver
            nearest_driver = None
            min_distance = float('inf')
            
            for driver in drivers:
                distance = self.calculate_distance(
                    pickup_lat, pickup_lon,
                    driver.current_lat, driver.current_lon
                )
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_driver = driver
            
            if nearest_driver:
                logger.info(f"Found nearest driver {nearest_driver.id} at {min_distance:.2f} km away")
                return {
                    'driver_id': nearest_driver.id,
                    'driver_name': nearest_driver.name,
                    'distance': round(min_distance, 2),
                    'vehicle_type': nearest_driver.vehicle_type,
                    'rating': nearest_driver.rating
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding nearest driver: {e}")
            return None
        finally:
            db.close()
    
    def calculate_fare(self, pickup_lat, pickup_lon, dest_lat, dest_lon, vehicle_type):
        """Calculate ride fare based on distance and vehicle type"""
        distance = self.calculate_distance(pickup_lat, pickup_lon, dest_lat, dest_lon)
        
        # Base fare structure
        base_fares = {
            'bike': 2.0,
            'sedan': 3.5,
            'suv': 5.0
        }
        
        per_km_rates = {
            'bike': 0.5,
            'sedan': 1.0,
            'suv': 1.5
        }
        
        base_fare = base_fares.get(vehicle_type, 3.5)
        per_km = per_km_rates.get(vehicle_type, 1.0)
        
        total_fare = base_fare + (distance * per_km)
        return round(total_fare, 2), round(distance, 2)
    
    def handle_ride_request(self, message):
        """Handle incoming ride request"""
        try:
            ride_id = message['ride_id']
            pickup_lat = message['pickup_lat']
            pickup_lon = message['pickup_lon']
            destination_lat = message['destination_lat']
            destination_lon = message['destination_lon']
            vehicle_type = message['vehicle_type']
            
            logger.info(f"Processing ride request {ride_id}")
            
            # Find nearest driver
            driver_match = self.find_nearest_driver(pickup_lat, pickup_lon, vehicle_type)
            
            if driver_match:
                # Calculate fare
                fare, distance = self.calculate_fare(
                    pickup_lat, pickup_lon,
                    destination_lat, destination_lon,
                    vehicle_type
                )
                
                # Update ride in database
                db = SessionLocal()
                try:
                    ride = db.query(Ride).filter(Ride.id == ride_id).first()
                    if ride:
                        ride.fare = fare
                        ride.distance = distance
                        db.commit()
                except Exception as e:
                    logger.error(f"Error updating ride fare: {e}")
                    db.rollback()
                finally:
                    db.close()
                
                # Publish match to Kafka
                match_message = {
                    'ride_id': ride_id,
                    'driver_id': driver_match['driver_id'],
                    'driver_name': driver_match['driver_name'],
                    'distance_to_pickup': driver_match['distance'],
                    'estimated_fare': fare,
                    'ride_distance': distance,
                    'vehicle_type': vehicle_type
                }
                
                self.producer.send_message(
                    TOPICS['RIDE_MATCHES'],
                    match_message,
                    key=str(ride_id)
                )
                
                logger.info(f"Ride {ride_id} matched with driver {driver_match['driver_id']}")
            else:
                logger.warning(f"No driver found for ride {ride_id}")
                
        except Exception as e:
            logger.error(f"Error handling ride request: {e}")
    
    def start(self):
        """Start consuming ride requests"""
        consumer = KafkaConsumerWrapper(
            TOPICS['RIDE_REQUESTS'],
            'matching-service-group',
            self.handle_ride_request
        )
        
        logger.info("Matching Service started and consuming from Kafka")
        
        try:
            consumer.start_consuming()
        except KeyboardInterrupt:
            logger.info("Shutting down Matching Service...")
            consumer.stop_consuming()
            self.producer.close()


if __name__ == '__main__':
    service = MatchingService()
    service.start()
