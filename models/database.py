"""
Database Models for Uber Clone
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///uber.db')
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Driver(Base):
    """Driver model"""
    __tablename__ = 'drivers'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)  # sedan, suv, bike
    vehicle_number = Column(String, nullable=False)
    rating = Column(Float, default=5.0)
    is_online = Column(Boolean, default=False)
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rides = relationship("Ride", back_populates="driver")


class Rider(Base):
    """Rider model"""
    __tablename__ = 'riders'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=False)
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rides = relationship("Ride", back_populates="rider")


class Ride(Base):
    """Ride model"""
    __tablename__ = 'rides'
    
    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey('riders.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=True)
    
    # Pickup location
    pickup_lat = Column(Float, nullable=False)
    pickup_lon = Column(Float, nullable=False)
    pickup_address = Column(String, nullable=False)
    
    # Destination
    destination_lat = Column(Float, nullable=False)
    destination_lon = Column(Float, nullable=False)
    destination_address = Column(String, nullable=False)
    
    # Ride details
    status = Column(String, default='requested')  # requested, matched, accepted, started, completed, cancelled
    vehicle_type = Column(String, nullable=False)
    fare = Column(Float, nullable=True)
    distance = Column(Float, nullable=True)  # in kilometers
    
    # Timestamps
    requested_at = Column(DateTime, default=datetime.utcnow)
    matched_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    rider = relationship("Rider", back_populates="rides")
    driver = relationship("Driver", back_populates="rides")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")
