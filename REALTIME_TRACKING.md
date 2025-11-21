# Real-Time Location Tracking Implementation

## Overview

This document describes the implementation of real-time location tracking for the Uber Clone application using WebSocket connections and Kafka event streaming.

## Architecture

### Components

1. **WebSocket Service** (`services/websocket_service.py`)
   - Manages WebSocket connections for riders and drivers
   - Maintains in-memory cache of driver locations
   - Provides connection management and broadcasting capabilities

2. **API Gateway** (`services/api_gateway.py`)
   - WebSocket endpoints for real-time communication
   - REST endpoints for driver location queries
   - Kafka consumers for broadcasting updates

3. **Frontend Tracking Page** (`frontend/tracking.html`)
   - Interactive Leaflet map showing live driver locations
   - Real-time statistics and updates
   - WebSocket client for receiving location updates

## Features

### ✅ Real-Time Location Updates
- **WebSocket Connections**: Persistent connections for instant updates
- **Sub-second Latency**: Location updates appear in real-time
- **Auto-Reconnect**: Automatic reconnection if connection drops

### ✅ Interactive Map
- **Leaflet Integration**: Beautiful, interactive map interface
- **Live Driver Markers**: Real-time driver positions with vehicle icons
- **Nearby Driver Search**: Find drivers within specified radius
- **Click-to-Focus**: Click on driver to zoom and view details

### ✅ Comprehensive Statistics
- **Online Drivers**: Count of currently active drivers
- **Update Metrics**: Total updates and average latency
- **Recent Activity**: Log of recent location updates

## WebSocket API

### Endpoints

#### 1. Rider WebSocket
```
ws://localhost:8001/ws/rider/{rider_id}
```
Receives real-time updates about assigned rides and driver locations.

**Incoming Messages:**
```json
{
  "type": "ride_update",
  "ride_id": 123,
  "status": "accepted",
  "driver_id": 1,
  "timestamp": 1234567890.123
}
```

#### 2. Driver WebSocket
```
ws://localhost:8001/ws/driver/{driver_id}
```
Receives real-time updates about ride requests and status changes.

**Incoming Messages:**
```json
{
  "type": "location_updated",
  "lat": 40.7128,
  "lon": -74.0060,
  "timestamp": 1234567890.123
}
```

#### 3. Ride WebSocket
```
ws://localhost:8001/ws/ride/{ride_id}
```
Receives updates about a specific ride.

**Incoming Messages:**
```json
{
  "type": "ride_update",
  "ride_id": 123,
  "status": "started",
  "timestamp": 1234567890.123
}
```

#### 4. Nearby Drivers WebSocket
```
ws://localhost:8001/ws/nearby-drivers
```
Real-time stream of all driver locations and nearby driver queries.

**Outgoing Messages:**
```json
{
  "type": "get_nearby",
  "lat": 40.7128,
  "lon": -74.0060,
  "radius": 5
}
```

**Incoming Messages:**
```json
{
  "type": "nearby_drivers",
  "drivers": [
    {
      "driver_id": 1,
      "location": {
        "lat": 40.7128,
        "lon": -74.0060,
        "vehicle_type": "sedan",
        "timestamp": 1234567890.123
      },
      "distance": 1.23
    }
  ],
  "count": 1
}
```

```json
{
  "type": "all_driver_locations",
  "drivers": [...],
  "timestamp": "2025-11-22T01:28:58+07:00"
}
```

## REST API

### Get Nearby Drivers
```
GET /api/drivers/nearby?lat={latitude}&lon={longitude}&radius={km}
```

**Response:**
```json
{
  "drivers": [
    {
      "driver_id": 1,
      "location": {
        "lat": 40.7128,
        "lon": -74.0060,
        "vehicle_type": "sedan",
        "timestamp": 1234567890.123
      },
      "distance": 1.23
    }
  ],
  "count": 1
}
```

## Data Flow

### Location Update Flow

```
1. Driver updates location
   └─> POST /api/drivers/location
       └─> Driver Service
           └─> Kafka: driver-locations topic
               ├─> Location Service (stores in-memory)
               └─> API Gateway Kafka Consumer
                   └─> WebSocket broadcast to:
                       ├─> Connected riders
                       ├─> Live tracking page
                       └─> Driver's own connection
```

### Real-Time Tracking Page Flow

```
1. User opens tracking.html
   └─> WebSocket connection to /ws/nearby-drivers
       └─> Receives all current driver locations
           └─> Displays on Leaflet map
               └─> Continuously receives updates
                   └─> Updates map markers in real-time
```

## Kafka Topics Used

### `driver-locations`
- **Producer**: Driver Service
- **Consumers**: Location Service, API Gateway
- **Message Format**:
  ```json
  {
    "driver_id": 1,
    "lat": 40.7128,
    "lon": -74.0060,
    "vehicle_type": "sedan",
    "timestamp": 1234567890.123
  }
  ```

### `driver-availability`
- **Producer**: Driver Service
- **Consumers**: Location Service, API Gateway
- **Message Format**:
  ```json
  {
    "driver_id": 1,
    "is_online": true,
    "timestamp": 1234567890.123
  }
  ```

### `ride-updates`
- **Producer**: Driver Service
- **Consumers**: Ride Service, API Gateway
- **Message Format**:
  ```json
  {
    "ride_id": 123,
    "driver_id": 1,
    "status": "accepted",
    "timestamp": 1234567890.123
  }
  ```

## Frontend Integration

### Using the Live Tracking Page

1. **Open the tracking page**: Navigate to `http://localhost:8080/tracking.html`
2. **View driver locations**: All online drivers appear as markers on the map
3. **Click on drivers**: Click any driver marker to see details
4. **Monitor statistics**: View real-time stats in the top cards
5. **Check recent updates**: See activity log at the bottom

### Map Features

- **Vehicle Icons**: Different emojis for bikes (🏍️), sedans (🚗), and SUVs (🚙)
- **Distance Display**: Shows distance from reference point
- **Auto-refresh**: Updates every 5 seconds automatically
- **Connection Status**: Visual indicator of WebSocket connection

## Performance Considerations

### In-Memory Storage
- Driver locations are cached in-memory for fast access
- Automatically cleaned when drivers go offline
- No database queries needed for location lookups

### WebSocket Efficiency
- Single persistent connection instead of polling
- Reduces server load and network traffic
- Instant updates without delay

### Scalability
- Connection Manager handles multiple concurrent WebSocket connections
- Kafka ensures message delivery even if connections drop
- Can scale horizontally with load balancers

## Testing

### Manual Testing

1. **Start the application**:
   ```bash
   ./start.sh
   ```

2. **Open driver app**:
   - Navigate to `http://localhost:8080/driver.html`
   - Select a driver and go online
   - Update location

3. **Open tracking page**:
   - Navigate to `http://localhost:8080/tracking.html`
   - Verify driver appears on map
   - Check that location updates in real-time

4. **Test multiple drivers**:
   - Open multiple driver apps in different browser windows
   - Set each driver online with different locations
   - Verify all appear on tracking map

### WebSocket Testing

Use a WebSocket client (e.g., `wscat`) to test:

```bash
# Install wscat
npm install -g wscat

# Connect to nearby drivers endpoint
wscat -c ws://localhost:8001/ws/nearby-drivers

# Send request for nearby drivers
> {"type": "get_nearby", "lat": 40.7128, "lon": -74.0060, "radius": 5}

# Receive response
< {"type": "nearby_drivers", "drivers": [...], "count": 1}
```

## Kubernetes Deployment

The real-time location tracking works seamlessly in both local and Kubernetes deployments:

### Updates to K8s Manifests
- WebSocket service is included in the API Gateway deployment
- No additional services needed
- Uses same port 8001 for both HTTP and WebSocket

### Accessing in Kubernetes
```bash
# Get Minikube IP
minikube ip

# Access tracking page
open http://<MINIKUBE_IP>:30080/tracking.html
```

### WebSocket URL Configuration
The frontend automatically detects the environment:
- **Local**: `ws://localhost:8001`
- **Production**: Uses current hostname from browser

## Troubleshooting

### WebSocket Not Connecting

1. **Check API Gateway is running**:
   ```bash
   ps aux | grep api_gateway
   ```

2. **Check Kafka is running**:
   ```bash
   docker ps | grep kafka
   ```

3. **Check browser console** for WebSocket errors

### No Drivers Appearing on Map

1. **Ensure drivers are online**: Check driver app status
2. **Verify location updates**: Check API Gateway logs
3. **Check WebSocket connection**: Look for "Connected" status

### Updates Not Real-Time

1. **Check Kafka consumers**: Ensure they're running in API Gateway
2. **Verify driver location updates**: Check driver service logs
3. **Test with direct REST API**: `GET /api/drivers/nearby`

## Future Enhancements

- [ ] **Route Visualization**: Draw route lines between pickup and destination
- [ ] **Heatmap View**: Show ride density across areas
- [ ] **Historical Playback**: Replay driver movements over time
- [ ] **Geofencing**: Alert when drivers enter/exit specific areas
- [ ] **Advanced Filters**: Filter drivers by vehicle type, rating, etc.
- [ ] **Mobile App**: Native iOS/Android apps with real-time tracking
- [ ] **Push Notifications**: Send location alerts to riders
- [ ] **Trip Sharing**: Share live trip progress with friends

## Security Considerations

### Current Implementation
- WebSocket connections are open (no authentication)
- Suitable for development and demonstration

### Production Recommendations
- [ ] Add JWT-based WebSocket authentication
- [ ] Implement rate limiting on WebSocket connections
- [ ] Use WSS (WebSocket Secure) with TLS
- [ ] Add authorization checks for location data access
- [ ] Implement connection limits per user
- [ ] Add CORS restrictions for WebSocket endpoints

## Performance Metrics

### Expected Performance
- **WebSocket Latency**: < 50ms
- **Location Update Frequency**: 5-10 seconds
- **Map Refresh Rate**: Real-time (immediate)
- **Concurrent Connections**: 1000+ per server instance

### Monitoring
- Prometheus metrics exposed on all services
- Grafana dashboards for visualization
- WebSocket connection counts tracked
- Message delivery latency monitored

---

**Documentation Version**: 1.0  
**Last Updated**: 2025-11-22  
**Author**: Uber Clone Development Team
