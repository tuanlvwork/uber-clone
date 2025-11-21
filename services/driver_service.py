"""
Driver Service - Manages driver availability and location updates
Publishes driver location and availability to Kafka
"""
import sys
import os
import threading
import logging
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.kafka_config import KafkaProducerWrapper, KafkaConsumerWrapper, TOPICS
from models.database import SessionLocal, Driver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DriverService:
    """Service to manage drivers"""
    
    def __init__(self):
        self.producer = KafkaProducerWrapper()
        logger.info("Driver Service initialized")
    
    def update_driver_availability(self, driver_id, is_online):
        """Update driver online/offline status"""
        db = SessionLocal()
        
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if driver:
                driver.is_online = is_online
                db.commit()
                
                # Publish to Kafka
                message = {
                    'driver_id': driver_id,
                    'is_online': is_online,
                    'timestamp': time.time()
                }
                
                self.producer.send_message(
                    TOPICS['DRIVER_AVAILABILITY'],
                    message,
                    key=str(driver_id)
                )
                
                logger.info(f"Driver {driver_id} is now {'online' if is_online else 'offline'}")
                return True
        except Exception as e:
            logger.error(f"Error updating driver availability: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def update_driver_location(self, driver_id, lat, lon):
        """Update driver location"""
        db = SessionLocal()
        
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if driver:
                driver.current_lat = lat
                driver.current_lon = lon
                db.commit()
                
                # Publish to Kafka if driver is online
                if driver.is_online:
                    message = {
                        'driver_id': driver_id,
                        'lat': lat,
                        'lon': lon,
                        'vehicle_type': driver.vehicle_type,
                        'timestamp': time.time()
                    }
                    
                    self.producer.send_message(
                        TOPICS['DRIVER_LOCATIONS'],
                        message,
                        key=str(driver_id)
                    )
                    
                    logger.info(f"Driver {driver_id} location updated: ({lat}, {lon})")
                return True
        except Exception as e:
            logger.error(f"Error updating driver location: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def accept_ride(self, driver_id, ride_id):
        """Driver accepts a ride"""
        try:
            message = {
                'ride_id': ride_id,
                'driver_id': driver_id,
                'status': 'accepted',
                'timestamp': time.time()
            }
            
            self.producer.send_message(
                TOPICS['RIDE_UPDATES'],
                message,
                key=str(ride_id)
            )
            
            logger.info(f"Driver {driver_id} accepted ride {ride_id}")
            return True
        except Exception as e:
            logger.error(f"Error accepting ride: {e}")
            return False
    
    def start_ride(self, driver_id, ride_id):
        """Driver starts the ride"""
        try:
            message = {
                'ride_id': ride_id,
                'driver_id': driver_id,
                'status': 'started',
                'timestamp': time.time()
            }
            
            self.producer.send_message(
                TOPICS['RIDE_UPDATES'],
                message,
                key=str(ride_id)
            )
            
            logger.info(f"Driver {driver_id} started ride {ride_id}")
            return True
        except Exception as e:
            logger.error(f"Error starting ride: {e}")
            return False
    
    def complete_ride(self, driver_id, ride_id, fare):
        """Driver completes the ride"""
        try:
            message = {
                'ride_id': ride_id,
                'driver_id': driver_id,
                'status': 'completed',
                'fare': fare,
                'timestamp': time.time()
            }
            
            self.producer.send_message(
                TOPICS['RIDE_UPDATES'],
                message,
                key=str(ride_id)
            )
            
            logger.info(f"Driver {driver_id} completed ride {ride_id} with fare ${fare}")
            return True
        except Exception as e:
            logger.error(f"Error completing ride: {e}")
            return False
    
    def start(self):
        """Start the driver service"""
        logger.info("Driver Service started")
        
        try:
            # Keep service running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down Driver Service...")
            self.producer.close()


if __name__ == '__main__':
    service = DriverService()
    service.start()
