"""
WebSocket Service - Real-time location tracking and ride updates
Provides WebSocket connections for live updates to riders and drivers
"""
import sys
import os
import asyncio
import json
import logging
from typing import Dict, Set
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import WebSocket, WebSocketDisconnect
from config.kafka_config import KafkaConsumerWrapper, TOPICS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for riders and drivers"""
    
    def __init__(self):
        # Store active connections by rider_id and driver_id
        self.rider_connections: Dict[int, Set[WebSocket]] = {}
        self.driver_connections: Dict[int, Set[WebSocket]] = {}
        # Store connections by ride_id for ride-specific updates
        self.ride_connections: Dict[int, Set[WebSocket]] = {}
        # Store driver locations in memory
        self.driver_locations: Dict[int, dict] = {}
        
    async def connect_rider(self, rider_id: int, websocket: WebSocket):
        """Connect a rider's WebSocket"""
        await websocket.accept()
        if rider_id not in self.rider_connections:
            self.rider_connections[rider_id] = set()
        self.rider_connections[rider_id].add(websocket)
        logger.info(f"Rider {rider_id} connected via WebSocket")
        
    async def connect_driver(self, driver_id: int, websocket: WebSocket):
        """Connect a driver's WebSocket"""
        await websocket.accept()
        if driver_id not in self.driver_connections:
            self.driver_connections[driver_id] = set()
        self.driver_connections[driver_id].add(websocket)
        logger.info(f"Driver {driver_id} connected via WebSocket")
        
    async def connect_ride(self, ride_id: int, websocket: WebSocket):
        """Connect to a specific ride for updates"""
        await websocket.accept()
        if ride_id not in self.ride_connections:
            self.ride_connections[ride_id] = set()
        self.ride_connections[ride_id].add(websocket)
        logger.info(f"Connection established for ride {ride_id}")
        
    def disconnect_rider(self, rider_id: int, websocket: WebSocket):
        """Disconnect a rider's WebSocket"""
        if rider_id in self.rider_connections:
            self.rider_connections[rider_id].discard(websocket)
            if not self.rider_connections[rider_id]:
                del self.rider_connections[rider_id]
        logger.info(f"Rider {rider_id} disconnected")
        
    def disconnect_driver(self, driver_id: int, websocket: WebSocket):
        """Disconnect a driver's WebSocket"""
        if driver_id in self.driver_connections:
            self.driver_connections[driver_id].discard(websocket)
            if not self.driver_connections[driver_id]:
                del self.driver_connections[driver_id]
        logger.info(f"Driver {driver_id} disconnected")
        
    def disconnect_ride(self, ride_id: int, websocket: WebSocket):
        """Disconnect from a ride"""
        if ride_id in self.ride_connections:
            self.ride_connections[ride_id].discard(websocket)
            if not self.ride_connections[ride_id]:
                del self.ride_connections[ride_id]
        logger.info(f"Disconnected from ride {ride_id}")
        
    async def broadcast_to_rider(self, rider_id: int, message: dict):
        """Send message to all connections of a specific rider"""
        if rider_id in self.rider_connections:
            disconnected = set()
            for websocket in self.rider_connections[rider_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to rider {rider_id}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                self.rider_connections[rider_id].discard(websocket)
                
    async def broadcast_to_driver(self, driver_id: int, message: dict):
        """Send message to all connections of a specific driver"""
        if driver_id in self.driver_connections:
            disconnected = set()
            for websocket in self.driver_connections[driver_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to driver {driver_id}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                self.driver_connections[driver_id].discard(websocket)
                
    async def broadcast_to_ride(self, ride_id: int, message: dict):
        """Send message to all connections watching a specific ride"""
        if ride_id in self.ride_connections:
            disconnected = set()
            for websocket in self.ride_connections[ride_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to ride {ride_id}: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                self.ride_connections[ride_id].discard(websocket)
                
    async def broadcast_all_driver_locations(self, websocket: WebSocket):
        """Send all current driver locations to a new connection"""
        message = {
            "type": "all_driver_locations",
            "drivers": [
                {
                    "driver_id": driver_id,
                    **location
                }
                for driver_id, location in self.driver_locations.items()
            ],
            "timestamp": datetime.now().isoformat()
        }
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending all driver locations: {e}")
            
    def update_driver_location(self, driver_id: int, location_data: dict):
        """Update stored driver location"""
        self.driver_locations[driver_id] = {
            "lat": location_data.get("lat"),
            "lon": location_data.get("lon"),
            "vehicle_type": location_data.get("vehicle_type"),
            "timestamp": location_data.get("timestamp", datetime.now().timestamp())
        }
        
    def remove_driver_location(self, driver_id: int):
        """Remove driver location when they go offline"""
        if driver_id in self.driver_locations:
            del self.driver_locations[driver_id]
            
    def get_nearby_drivers(self, lat: float, lon: float, radius_km: float = 5) -> list:
        """Get drivers within a certain radius"""
        import math
        
        nearby_drivers = []
        
        for driver_id, location in self.driver_locations.items():
            # Haversine distance calculation
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
        
        return sorted(nearby_drivers, key=lambda x: x['distance'])


# Global connection manager instance
manager = ConnectionManager()
