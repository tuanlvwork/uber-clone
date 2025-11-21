#!/usr/bin/env python3
"""
Quick test to update a few driver locations
"""
import requests
import time

API_URL = "http://localhost:8001/api"

# Sample NYC locations
locations = [
    {"name": "Times Square", "lat": 40.7580, "lon": -73.9855},
    {"name": "Central Park", "lat": 40.7829, "lon": -73.9654},
    {"name": "Brooklyn Bridge", "lat": 40.7061, "lon": -73.9969},
]

def set_driver_online(driver_id):
    """Set driver online"""
    url = f"{API_URL}/drivers/availability"
    data = {"driver_id": driver_id, "is_online": True}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"✓ Driver {driver_id} is now online")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
    return False

def update_location(driver_id, location):
    """Update driver location"""
    url = f"{API_URL}/drivers/location"
    data = {
        "driver_id": driver_id,
        "lat": location["lat"],
        "lon": location["lon"]
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"✓ Driver {driver_id} at {location['name']}")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
    return False

if __name__ == "__main__":
    print("🚗 Quick Driver Location Test")
    print("=" * 50)
    
    # Set 3 drivers online and update their locations
    for i in range(1, 4):
        driver_id = i
        location = locations[i - 1]
        
        print(f"\nDriver {driver_id}:")
        set_driver_online(driver_id)
        time.sleep(0.5)
        update_location(driver_id, location)
        time.sleep(0.5)
    
    print("\n✅ Done! Check the tracking page:")
    print("   http://localhost:8080/tracking.html")
