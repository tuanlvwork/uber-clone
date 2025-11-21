# 📱 Uber Clone - User Guide

This guide walks you through the complete flow of the Uber Clone application, from a driver going online to a rider completing a trip.

## 🚀 Getting Started

### 1. Open the Applications
For the best experience, open these two files in separate browser windows and place them **side-by-side**.

- **Driver App**: `frontend/driver.html`
- **Rider App**: `frontend/rider.html`

You can open them directly from your terminal:
```bash
open frontend/driver.html
open frontend/rider.html
```

---

## 🚕 The Driver Flow (Start Here)

**Goal**: Make a driver available to receive ride requests.

1. **Login**:
   - Select **"John Doe"** (Sedan) or **"Jane Smith"** (SUV) from the dropdown.
   - Click **"Login as Driver"**.

2. **Go Online**:
   - You will see your dashboard with a map and status panel.
   - Toggle the switch labeled **"You are Offline"** to **ON**.
   - **Result**: Status changes to *"Looking for rides..."* and the map starts updating your location.

   > ⚠️ **Important**: You MUST be online to receive ride requests!

---

## 🙋‍♀️ The Rider Flow

**Goal**: Request a ride and get matched with a driver.

1. **Login**:
   - Select **"Alice Brown"** or **"Bob Wilson"** from the dropdown.
   - Click **"Login as Rider"**.

2. **Request a Ride**:
   - **Pickup Location**: Default is Times Square (40.7580, -73.9855).
   - **Destination**: Default is Central Park (40.7829, -73.9654).
   - **Vehicle Type**: Select **"Sedan"** (if you chose John Doe) or **"SUV"** (if you chose Jane Smith).
   - Click **"Request Ride"**.

3. **Matching Process**:
   - The app will show *"Finding a driver..."*.
   - Behind the scenes, the **Matching Service** calculates the nearest available driver using the Haversine formula.

---

## ✨ The Interaction (Real-Time)

This is where the magic happens via Kafka!

1. **Driver Notification**:
   - Within seconds, the **Driver App** will show a popup: **"New Ride Request!"**.
   - It displays the pickup address and estimated fare.

2. **Accepting the Ride**:
   - **Driver**: Click **"Accept Ride"**.
   - **Rider**: Screen immediately updates to *"Driver Accepted"* and shows the driver's name and vehicle details.

3. **The Journey**:
   - **Driver**: Click **"Start Ride"** when you "arrive" at the pickup.
   - **Rider**: Status updates to *"Ride Started"*.
   - **Driver**: Click **"Complete Ride"** when you reach the destination.

4. **Completion**:
   - Both screens show a **Ride Summary** with the final fare.
   - The driver is automatically made available for new rides.

---

## 🔍 Troubleshooting

**"No drivers available" error?**
- Ensure the Driver App is open.
- Ensure the driver is toggled **"Online"**.
- Ensure the **Vehicle Type** matches (e.g., don't request an SUV if only a Sedan driver is online).

**"Failed to load driver info"?**
- The API Gateway might be down. Run `./start.sh` again.
- Check if the API is running on port 8001: `curl http://localhost:8001/docs`

**Nothing happens when I request a ride?**
- Check the Kafka services: `docker ps`
- Ensure all Python services are running.
