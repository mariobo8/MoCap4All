# app/routers/camera.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
import json
import asyncio
import logging
from typing import Optional
from app.services.mock_camera import get_mock_camera_service

router = APIRouter()

# Connection manager to handle WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections = {}
        self.mock_camera = get_mock_camera_service()
        self.is_camera_started = False

    async def connect(self, websocket: WebSocket, camera_id: str):
        await websocket.accept()
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = []
        self.active_connections[camera_id].append(websocket)
        logging.info(f"Client connected to camera {camera_id}. Total connections: {len(self.active_connections[camera_id])}")
        
        # Start the mock camera service if not already started
        if not self.is_camera_started:
            await self.mock_camera.start()
            self.is_camera_started = True
            logging.info("Mock camera service started")
        
        # Register callback for this camera
        self.mock_camera.register_callback(camera_id, lambda frame: self.send_frame_to_all(frame, camera_id))

    def disconnect(self, websocket: WebSocket, camera_id: str):
        if camera_id in self.active_connections:
            if websocket in self.active_connections[camera_id]:
                self.active_connections[camera_id].remove(websocket)
            if not self.active_connections[camera_id]:
                self.mock_camera.unregister_callback(camera_id)
                del self.active_connections[camera_id]
            logging.info(f"Client disconnected from camera {camera_id}")
        
        # If no active connections at all, stop the camera service
        if not self.active_connections:
            self.mock_camera.stop()
            self.is_camera_started = False
            logging.info("Mock camera service stopped - no active connections")

    async def send_frame_to_all(self, frame: str, camera_id: str):
        """Send frame to all connected clients for a specific camera."""
        if camera_id in self.active_connections:
            disconnected_websockets = []
            message = json.dumps({
                "type": "frame",
                "camera_id": camera_id,
                "frame": frame,
                "timestamp": None
            })
            
            for connection in self.active_connections[camera_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logging.error(f"Error sending frame to client: {e}")
                    disconnected_websockets.append(connection)
            
            # Clean up any disconnected WebSockets
            for ws in disconnected_websockets:
                self.disconnect(ws, camera_id)

# Create a singleton instance of ConnectionManager
manager = ConnectionManager()

# This is the route that will be registered in main.py
async def websocket_endpoint(websocket: WebSocket, camera_id: str):
    """WebSocket endpoint for camera streams."""
    await manager.connect(websocket, camera_id)
    try:
        while True:
            # Just keep the connection alive and let the callback handle sending frames
            data = await websocket.receive_text()
            # Handle commands from the client if needed
            try:
                command = json.loads(data)
                if command.get("type") == "move_pattern":
                    direction = command.get("direction")
                    amount = command.get("amount", 10)
                    manager.mock_camera.move_pattern(direction, amount)
                elif command.get("type") == "toggle_marker_detection":
                    enable = command.get("enable", False)
                    is_enabled = manager.mock_camera.toggle_marker_detection(enable)
                    # Send confirmation back to the client
                    await websocket.send_text(json.dumps({
                        "type": "marker_detection_status",
                        "enabled": is_enabled
                    }))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, camera_id)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, camera_id)

@router.post("/camera/pattern/move")
async def move_pattern(direction: str, amount: int = 10):
    """API endpoint to move the pattern."""
    valid_directions = ["left", "right", "up", "down", "forward", "backward"]
    if direction not in valid_directions:
        raise HTTPException(status_code=400, detail=f"Invalid direction. Use one of: {valid_directions}")
    
    mock_camera = get_mock_camera_service()
    mock_camera.move_pattern(direction, amount)
    return {"success": True, "message": f"Pattern moved {direction} by {amount} units"}