"""
API Gateway - FastAPI-based gateway for frontend communication
Provides REST API for rider and driver applications
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
from datetime import datetime

from models.database import SessionLocal, Driver, Rider, Ride, init_db
from services.ride_service import RideService
from services.driver_service import DriverService

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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Uber Clone API with Kafka",
        "version": "1.0.0",
        "endpoints": {
            "riders": "/api/riders",
            "drivers": "/api/drivers",
            "rides": "/api/rides"
        }
    }


if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8001)
