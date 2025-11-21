"""
Location Service - Tracks and broadcasts real-time driver locations
Consumes driver location updates from Kafka
"""
import sys
import os
import threading
import logging
from collections import defaultdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.kafka_config import KafkaConsumerWrapper, TOPICS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocationService:
    """Service to track driver locations"""
    
    def __init__(self):
        # Store driver locations in memory
        self.driver_locations = {}
        self.driver_status = {}
        logger.info("Location Service initialized")
    
    def handle_location_update(self, message):
        """Handle driver location updates"""
        try:
            driver_id = message['driver_id']
            lat = message['lat']
            lon = message['lon']
            vehicle_type = message.get('vehicle_type', 'sedan')
            timestamp = message['timestamp']
            
            # Store location
            self.driver_locations[driver_id] = {
                'lat': lat,
                'lon': lon,
                'vehicle_type': vehicle_type,
                'timestamp': timestamp
            }
            
            logger.info(f"Updated location for driver {driver_id}: ({lat}, {lon})")
            
        except Exception as e:
            logger.error(f"Error handling location update: {e}")
    
    def handle_availability_update(self, message):
        """Handle driver availability updates"""
        try:
            driver_id = message['driver_id']
            is_online = message['is_online']
            
            self.driver_status[driver_id] = is_online
            
            if not is_online and driver_id in self.driver_locations:
                # Remove location when driver goes offline
                del self.driver_locations[driver_id]
            
            logger.info(f"Driver {driver_id} is now {'online' if is_online else 'offline'}")
            
        except Exception as e:
            logger.error(f"Error handling availability update: {e}")
    
    def get_nearby_drivers(self, lat, lon, radius_km=5):
        """Get all drivers within a certain radius"""
        import math
        
        nearby_drivers = []
        
        for driver_id, location in self.driver_locations.items():
            # Simple distance calculation
            R = 6371  # Earth's radius in km
            
            lat1_rad = math.radians(lat)
            lat2_rad = math.radians(location['lat'])
            delta_lat = math.radians(location['lat'] - lat)
            delta_lon = math.radians(location['lon'] - lon)
            
            a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c
            
            if distance <= radius_km:
                nearby_drivers.append({
                    'driver_id': driver_id,
                    'location': location,
                    'distance': round(distance, 2)
                })
        
        return nearby_drivers
    
    def start(self):
        """Start consuming location and availability updates"""
        # Consumer for location updates
        location_consumer = KafkaConsumerWrapper(
            TOPICS['DRIVER_LOCATIONS'],
            'location-service-group',
            self.handle_location_update
        )
        
        # Consumer for availability updates
        availability_consumer = KafkaConsumerWrapper(
            TOPICS['DRIVER_AVAILABILITY'],
            'location-service-group',
            self.handle_availability_update
        )
        
        # Start consumers in separate threads
        location_thread = threading.Thread(target=location_consumer.start_consuming)
        availability_thread = threading.Thread(target=availability_consumer.start_consuming)
        
        location_thread.start()
        availability_thread.start()
        
        logger.info("Location Service started and consuming from Kafka")
        
        try:
            location_thread.join()
            availability_thread.join()
        except KeyboardInterrupt:
            logger.info("Shutting down Location Service...")
            location_consumer.stop_consuming()
            availability_consumer.stop_consuming()


if __name__ == '__main__':
    service = LocationService()
    service.start()
