"""
API Gateway - FastAPI-based gateway for frontend communication
Provides REST API for rider and driver applications
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime
import asyncio
import threading

from models.database import SessionLocal, Driver, Rider, Ride, init_db
from services.ride_service import RideService
from services.driver_service import DriverService
from services.websocket_service import manager
from config.kafka_config import KafkaConsumerWrapper, TOPICS

# Initialize FastAPI app
app = FastAPI(title="Uber Clone API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Instrumentation
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)

# Initialize services
ride_service = RideService()
driver_service = DriverService()


# Pydantic models for request/response
class RiderCreate(BaseModel):
    name: str
    email: str
    phone: str


class DriverCreate(BaseModel):
    name: str
    email: str
    phone: str
    vehicle_type: str
    vehicle_number: str


class RideRequest(BaseModel):
    rider_id: int
    pickup_lat: float
    pickup_lon: float
    pickup_address: str
    destination_lat: float
    destination_lon: float
    destination_address: str
    vehicle_type: str


class LocationUpdate(BaseModel):
    driver_id: int
    lat: float
    lon: float


class DriverAvailability(BaseModel):
    driver_id: int
    is_online: bool


class RideAction(BaseModel):
    driver_id: int
    ride_id: int
    fare: Optional[float] = None


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Rider endpoints
@app.post("/api/riders")
async def create_rider(rider: RiderCreate, db=Depends(get_db)):
    """Create a new rider"""
    new_rider = Rider(
        name=rider.name,
        email=rider.email,
        phone=rider.phone
    )
    db.add(new_rider)
    db.commit()
    db.refresh(new_rider)
    
    return {
        "id": new_rider.id,
        "name": new_rider.name,
        "email": new_rider.email,
        "phone": new_rider.phone
    }


@app.get("/api/riders/{rider_id}")
async def get_rider(rider_id: int, db=Depends(get_db)):
    """Get rider details"""
    rider = db.query(Rider).filter(Rider.id == rider_id).first()
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    
    return {
        "id": rider.id,
        "name": rider.name,
        "email": rider.email,
        "phone": rider.phone,
        "rating": rider.rating
    }


# Driver endpoints
@app.post("/api/drivers")
async def create_driver(driver: DriverCreate, db=Depends(get_db)):
    """Create a new driver"""
    new_driver = Driver(
        name=driver.name,
        email=driver.email,
        phone=driver.phone,
        vehicle_type=driver.vehicle_type,
        vehicle_number=driver.vehicle_number
    )
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    
    return {
        "id": new_driver.id,
        "name": new_driver.name,
        "email": new_driver.email,
        "vehicle_type": new_driver.vehicle_type
    }


@app.get("/api/drivers/{driver_id}")
async def get_driver(driver_id: int, db=Depends(get_db)):
    """Get driver details"""
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return {
        "id": driver.id,
        "name": driver.name,
        "email": driver.email,
        "phone": driver.phone,
        "vehicle_type": driver.vehicle_type,
        "vehicle_number": driver.vehicle_number,
        "rating": driver.rating,
        "is_online": driver.is_online
    }


@app.post("/api/drivers/availability")
async def update_driver_availability(data: DriverAvailability):
    """Update driver online/offline status"""
    success = driver_service.update_driver_availability(data.driver_id, data.is_online)
    if success:
        return {"message": "Availability updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update availability")


@app.post("/api/drivers/location")
async def update_driver_location(data: LocationUpdate):
    """Update driver location"""
    success = driver_service.update_driver_location(data.driver_id, data.lat, data.lon)
    if success:
        return {"message": "Location updated successfully"}
    raise HTTPException(status_code=500, detail="Failed to update location")


# Ride endpoints
@app.post("/api/rides")
async def request_ride(ride_request: RideRequest):
    """Request a new ride"""
    ride_id = ride_service.create_ride_request(ride_request.dict())
    if ride_id:
        return {"ride_id": ride_id, "message": "Ride requested successfully"}
    raise HTTPException(status_code=500, detail="Failed to create ride request")


@app.get("/api/rides/{ride_id}")
async def get_ride(ride_id: int, db=Depends(get_db)):
    """Get ride details"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    
    return {
        "id": ride.id,
        "rider_id": ride.rider_id,
        "driver_id": ride.driver_id,
        "pickup_address": ride.pickup_address,
        "destination_address": ride.destination_address,
        "status": ride.status,
        "fare": ride.fare,
        "distance": ride.distance,
        "requested_at": ride.requested_at.isoformat() if ride.requested_at else None,
        "completed_at": ride.completed_at.isoformat() if ride.completed_at else None
    }


@app.get("/api/rides/rider/{rider_id}")
async def get_rider_rides(rider_id: int, db=Depends(get_db)):
    """Get all rides for a rider"""
    rides = db.query(Ride).filter(Ride.rider_id == rider_id).order_by(Ride.requested_at.desc()).all()
    
    return [{
        "id": ride.id,
        "driver_id": ride.driver_id,
        "pickup_address": ride.pickup_address,
        "destination_address": ride.destination_address,
        "status": ride.status,
        "fare": ride.fare,
        "distance": ride.distance,
        "requested_at": ride.requested_at.isoformat() if ride.requested_at else None
    } for ride in rides]


@app.get("/api/rides/driver/{driver_id}")
async def get_driver_rides(driver_id: int, db=Depends(get_db)):
    """Get all rides for a driver"""
    rides = db.query(Ride).filter(Ride.driver_id == driver_id).order_by(Ride.requested_at.desc()).all()
    
    return [{
        "id": ride.id,
        "rider_id": ride.rider_id,
        "pickup_address": ride.pickup_address,
        "destination_address": ride.destination_address,
        "status": ride.status,
        "fare": ride.fare,
        "distance": ride.distance,
        "requested_at": ride.requested_at.isoformat() if ride.requested_at else None
    } for ride in rides]


@app.post("/api/rides/accept")
async def accept_ride(action: RideAction):
    """Driver accepts a ride"""
    success = driver_service.accept_ride(action.driver_id, action.ride_id)
    if success:
        return {"message": "Ride accepted successfully"}
    raise HTTPException(status_code=500, detail="Failed to accept ride")


@app.post("/api/rides/start")
async def start_ride(action: RideAction):
    """Driver starts a ride"""
    success = driver_service.start_ride(action.driver_id, action.ride_id)
    if success:
        return {"message": "Ride started successfully"}
    raise HTTPException(status_code=500, detail="Failed to start ride")


@app.post("/api/rides/complete")
async def complete_ride(action: RideAction):
    """Driver completes a ride"""
    if not action.fare:
        raise HTTPException(status_code=400, detail="Fare is required")
    
    success = driver_service.complete_ride(action.driver_id, action.ride_id, action.fare)
    if success:
        return {"message": "Ride completed successfully"}
    raise HTTPException(status_code=500, detail="Failed to complete ride")


# FastAPI startup event
@app.on_event("startup")
async def startup_event():
    """Initialize Kafka consumers on startup"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting Kafka consumers for WebSocket broadcasting...")
    start_kafka_consumers()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Uber Clone API with Kafka",
        "version": "1.0.0",
        "endpoints": {
            "riders": "/api/riders",
            "drivers": "/api/drivers",
            "rides": "/api/rides",
            "websocket": {
                "rider": "/ws/rider/{rider_id}",
                "driver": "/ws/driver/{driver_id}",
                "ride": "/ws/ride/{ride_id}",
                "nearby_drivers": "/ws/nearby-drivers"
            }
        }
    }


# WebSocket endpoints
@app.websocket("/ws/rider/{rider_id}")
async def websocket_rider(websocket: WebSocket, rider_id: int):
    """WebSocket connection for rider to receive real-time updates"""
    await manager.connect_rider(rider_id, websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({"type": "heartbeat", "status": "connected"})
    except WebSocketDisconnect:
        manager.disconnect_rider(rider_id, websocket)


@app.websocket("/ws/driver/{driver_id}")
async def websocket_driver(websocket: WebSocket, driver_id: int):
    """WebSocket connection for driver to receive real-time updates"""
    await manager.connect_driver(driver_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "heartbeat", "status": "connected"})
    except WebSocketDisconnect:
        manager.disconnect_driver(driver_id, websocket)


@app.websocket("/ws/ride/{ride_id}")
async def websocket_ride(websocket: WebSocket, ride_id: int):
    """WebSocket connection for ride-specific updates"""
    await manager.connect_ride(ride_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"type": "heartbeat", "status": "connected"})
    except WebSocketDisconnect:
        manager.disconnect_ride(ride_id, websocket)


@app.websocket("/ws/nearby-drivers")
async def websocket_nearby_drivers(websocket: WebSocket):
    """WebSocket connection to get all nearby drivers in real-time"""
    await websocket.accept()
    
    # Send initial driver locations
    await manager.broadcast_all_driver_locations(websocket)
    
    try:
        while True:
            # Wait for location requests from client
            data = await websocket.receive_json()
            if data.get("type") == "get_nearby":
                lat = data.get("lat")
                lon = data.get("lon")
                radius = data.get("radius", 5)
                
                nearby = manager.get_nearby_drivers(lat, lon, radius)
                await websocket.send_json({
                    "type": "nearby_drivers",
                    "drivers": nearby,
                    "count": len(nearby)
                })
            elif data.get("type") == "get_all":
                await manager.broadcast_all_driver_locations(websocket)
    except WebSocketDisconnect:
        pass


@app.get("/api/drivers/nearby")
async def get_nearby_drivers(lat: float, lon: float, radius: float = 5):
    """REST endpoint to get nearby drivers"""
    nearby = manager.get_nearby_drivers(lat, lon, radius)
    return {
        "drivers": nearby,
        "count": len(nearby)
    }


# Kafka consumers for WebSocket broadcasting
def handle_location_update(message: dict):
    """Handle driver location updates from Kafka"""
    driver_id = message.get('driver_id')
    
    # Update stored location
    manager.update_driver_location(driver_id, message)
    
    # Broadcast to all relevant connections
    asyncio.run(manager.broadcast_to_driver(driver_id, {
        "type": "location_updated",
        "lat": message.get('lat'),
        "lon": message.get('lon'),
        "timestamp": message.get('timestamp')
    }))


def handle_availability_update(message: dict):
    """Handle driver availability updates from Kafka"""
    driver_id = message.get('driver_id')
    is_online = message.get('is_online')
    
    if not is_online:
        manager.remove_driver_location(driver_id)
    
    asyncio.run(manager.broadcast_to_driver(driver_id, {
        "type": "availability_updated",
        "is_online": is_online,
        "timestamp": message.get('timestamp')
    }))


def handle_ride_update(message: dict):
    """Handle ride status updates from Kafka"""
    ride_id = message.get('ride_id')
    driver_id = message.get('driver_id')
    status = message.get('status')
    
    # Get ride from database to find rider_id
    db = SessionLocal()
    try:
        ride = db.query(Ride).filter(Ride.id == ride_id).first()
        if ride:
            # Broadcast to rider
            asyncio.run(manager.broadcast_to_rider(ride.rider_id, {
                "type": "ride_update",
                "ride_id": ride_id,
                "status": status,
                "driver_id": driver_id,
                "timestamp": message.get('timestamp')
            }))
            
            # Broadcast to ride-specific connections
            asyncio.run(manager.broadcast_to_ride(ride_id, {
                "type": "ride_update",
                "ride_id": ride_id,
                "status": status,
                "timestamp": message.get('timestamp')
            }))
    finally:
        db.close()


def start_kafka_consumers():
    """Start Kafka consumers in background threads"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Consumer for driver locations
        location_consumer = KafkaConsumerWrapper(
            TOPICS['DRIVER_LOCATIONS'],
            'api-gateway-location-group',
            handle_location_update
        )
        
        # Consumer for driver availability
        availability_consumer = KafkaConsumerWrapper(
            TOPICS['DRIVER_AVAILABILITY'],
            'api-gateway-availability-group',
            handle_availability_update
        )
        
        # Consumer for ride updates
        ride_consumer = KafkaConsumerWrapper(
            TOPICS['RIDE_UPDATES'],
            'api-gateway-ride-group',
            handle_ride_update
        )
        
        # Start consumers in separate threads
        location_thread = threading.Thread(target=location_consumer.start_consuming, daemon=True)
        availability_thread = threading.Thread(target=availability_consumer.start_consuming, daemon=True)
        ride_thread = threading.Thread(target=ride_consumer.start_consuming, daemon=True)
        
        location_thread.start()
        availability_thread.start()
        ride_thread.start()
        
        logger.info("Kafka consumers started for WebSocket broadcasting")
    except Exception as e:
        logger.error(f"Error starting Kafka consumers: {e}")


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Run FastAPI server (Kafka consumers start via @app.on_event("startup"))
    uvicorn.run(app, host="0.0.0.0", port=8001)
