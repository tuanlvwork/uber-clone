#!/usr/bin/env python3
"""
Real-Time Location Tracking Test Script
Simulates multiple drivers updating their locations to test the tracking system
"""
import asyncio
import aiohttp
import random
import time
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:8001/api"

# Predefined locations in New York City
NYC_LOCATIONS = [
    {"name": "Times Square", "lat": 40.7580, "lon": -73.9855},
    {"name": "Central Park", "lat": 40.7829, "lon": -73.9654},
    {"name": "Brooklyn Bridge", "lat": 40.7061, "lon": -73.9969},
    {"name": "Statue of Liberty", "lat": 40.6892, "lon": -74.0445},
    {"name": "Empire State Building", "lat": 40.7484, "lon": -73.9857},
    {"name": "Wall Street", "lat": 40.7074, "lon": -74.0113},
]

async def update_driver_location(session, driver_id, location):
    """Update a driver's location"""
    url = f"{API_URL}/drivers/location"
    data = {
        "driver_id": driver_id,
        "lat": location["lat"],
        "lon": location["lon"]
    }
    
    try:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                print(f"✓ Driver {driver_id} location updated to {location['name']}")
                return True
            else:
                print(f"✗ Failed to update driver {driver_id}: {response.status}")
                return False
    except Exception as e:
        print(f"✗ Error updating driver {driver_id}: {e}")
        return False

async def set_driver_online(session, driver_id, is_online):
    """Set driver online/offline status"""
    url = f"{API_URL}/drivers/availability"
    data = {
        "driver_id": driver_id,
        "is_online": is_online
    }
    
    try:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                status = "online" if is_online else "offline"
                print(f"✓ Driver {driver_id} is now {status}")
                return True
            else:
                print(f"✗ Failed to update driver {driver_id} availability: {response.status}")
                return False
    except Exception as e:
        print(f"✗ Error updating driver {driver_id} availability: {e}")
        return False

async def simulate_driver(session, driver_id, duration=60):
    """Simulate a driver moving around the city"""
    print(f"\n🚗 Starting simulation for Driver {driver_id}")
    
    # Set driver online
    await set_driver_online(session, driver_id, True)
    
    # Simulate movement
    start_time = time.time()
    location_index = driver_id % len(NYC_LOCATIONS)
    
    while time.time() - start_time < duration:
        # Get current location
        location = NYC_LOCATIONS[location_index].copy()
        
        # Add small random variation to simulate movement
        location["lat"] += random.uniform(-0.01, 0.01)
        location["lon"] += random.uniform(-0.01, 0.01)
        
        # Update location
        await update_driver_location(session, driver_id, location)
        
        # Wait before next update
        await asyncio.sleep(random.uniform(3, 7))
        
        # Move to next location occasionally
        if random.random() < 0.3:
            location_index = (location_index + 1) % len(NYC_LOCATIONS)
    
    # Set driver offline
    await set_driver_online(session, driver_id, False)
    print(f"\n🏁 Simulation ended for Driver {driver_id}")

async def main():
    """Main function to run the simulation"""
    print("=" * 60)
    print("Real-Time Location Tracking Test")
    print("=" * 60)
    print("\nThis script will simulate multiple drivers updating their")
    print("locations in real-time. Open the tracking page to watch:")
    print("  http://localhost:8080/tracking.html\n")
    print("=" * 60)
    
    # Get user input
    try:
        num_drivers = int(input("\nHow many drivers to simulate? (1-10): ") or "3")
        num_drivers = max(1, min(10, num_drivers))
        
        duration = int(input(f"Duration in seconds? (default 60): ") or "60")
        duration = max(10, min(300, duration))
    except ValueError:
        num_drivers = 3
        duration = 60
    
    print(f"\n📊 Simulating {num_drivers} drivers for {duration} seconds...")
    print("=" * 60)
    
    # Create HTTP session
    async with aiohttp.ClientSession() as session:
        # Create tasks for each driver
        tasks = [
            simulate_driver(session, driver_id + 1, duration)
            for driver_id in range(num_drivers)
        ]
        
        # Run all drivers concurrently
        await asyncio.gather(*tasks)
    
    print("\n" + "=" * 60)
    print("✅ Simulation completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user")
        sys.exit(0)
