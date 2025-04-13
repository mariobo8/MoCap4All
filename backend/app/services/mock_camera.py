# app/services/mock_camera.py
import numpy as np
import cv2 as cv
import math
import base64
import threading
import time
import asyncio
import logging
from typing import Dict, Callable, Any, Optional

# Import the marker detector
from app.services.marker_detection import get_marker_detector

class MockCameraService:
    def __init__(self):
        # Window settings
        self.width, self.height = 640, 480
        
        # Camera settings
        self.focal_length = 300
        self.center_x = self.width / 2
        self.center_y = self.height / 2
        
        # Define camera views
        self.views = [
            {'id': '1', 'x': -223.6, 'y': -180, 'z': -359.4, 'yaw': -25, 'pitch': 25},  # View 1
            {'id': '2', 'x': 278, 'y': -140, 'z': -319.44, 'yaw': 30, 'pitch': 25},     # View 2
        ]
        
        # Pattern position (can be moved)
        self.pattern_x = 0
        self.pattern_y = 0
        self.pattern_z = 0
        
        # Create the 3D pattern
        self.create_pattern()
        
        # Callbacks for when frames are generated
        self.callbacks = {}
        
        # Running flag
        self.running = False
        self.frame_rate = 30  # FPS
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Marker detection flag
        self.enable_marker_detection = False
        
        # Get marker detector
        self.marker_detector = get_marker_detector()
        
        logging.info("Mock camera service initialized")
    
    def create_pattern(self):
        """Create the 3D calibration pattern."""
        self.base_pattern_3d = []
        
        # Parameters for pattern positioning
        x_spacing = 60
        
        # First row, first group (5 dots)
        for i in range(5):
            self.base_pattern_3d.append({"X": -120 + i*x_spacing, "Y": -40, "Z": 0})
        
        # First row, second group (1 dot)
        self.base_pattern_3d.append({"X": 200, "Y": -40, "Z": 0})
        
        # Second row, first group (4 dots)
        for i in range(4):
            self.base_pattern_3d.append({"X": -120 + i*x_spacing, "Y": 40, "Z": 0})
        
        # Second row, second group (2 dots)
        self.base_pattern_3d.append({"X": 180, "Y": 40, "Z": 0})
        self.base_pattern_3d.append({"X": 240, "Y": 40, "Z": 0})
    
    def get_pattern_3d(self):
        """Get the pattern with the current offset applied."""
        pattern_3d = []
        for point in self.base_pattern_3d:
            pattern_3d.append({
                "X": point["X"] + self.pattern_x,
                "Y": point["Y"] + self.pattern_y,
                "Z": point["Z"] + self.pattern_z
            })
        return pattern_3d
    
    def render_view(self, camera_x, camera_y, camera_z, camera_yaw, camera_pitch):
        """Render the view from the given camera position and orientation."""
        # Create black background
        image = np.zeros((self.height, self.width), dtype=np.uint8)
        
        # Get current pattern position
        pattern_3d = self.get_pattern_3d()
        
        # Create transformation matrices
        sin_yaw = math.sin(math.radians(camera_yaw))
        cos_yaw = math.cos(math.radians(camera_yaw))
        sin_pitch = math.sin(math.radians(camera_pitch))
        cos_pitch = math.cos(math.radians(camera_pitch))
        
        # Project all 3D points to 2D
        for point in pattern_3d:
            # Translate point relative to camera
            x = point["X"] - camera_x
            y = point["Y"] - camera_y
            z = point["Z"] - camera_z
            
            # Apply yaw rotation (around Y axis)
            x_rot = x * cos_yaw + z * sin_yaw
            z_rot = -x * sin_yaw + z * cos_yaw
            
            # Apply pitch rotation (around X axis)
            y_rot = y * cos_pitch - z_rot * sin_pitch
            z_rot_final = y * sin_pitch + z_rot * cos_pitch
            
            # Perspective projection
            if z_rot_final > 0:  # Only render points in front of camera
                u = int(self.focal_length * x_rot / z_rot_final + self.center_x)
                v = int(self.focal_length * y_rot / z_rot_final + self.center_y)
                
                if 0 <= u < self.width and 0 <= v < self.height:
                    # Size based on distance
                    size = max(2, int(8 * self.focal_length / z_rot_final))
                    cv.circle(image, (u, v), size, 255, -1)
        
        # Convert to color for better visualization
        image_color = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
        
        return image_color
    
    def encode_frame(self, frame):
        """Encode frame to base64 for WebSocket transmission."""
        _, buffer = cv.imencode('.jpg', frame, [cv.IMWRITE_JPEG_QUALITY, 80])
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        return jpg_as_text
    
    def register_callback(self, camera_id, callback):
        """Register a callback for when a frame is captured."""
        self.callbacks[camera_id] = callback
        logging.info(f"Callback registered for camera {camera_id}")
    
    def unregister_callback(self, camera_id):
        """Unregister a callback."""
        if camera_id in self.callbacks:
            del self.callbacks[camera_id]
            logging.info(f"Callback unregistered for camera {camera_id}")
    
    def move_pattern(self, direction, amount=10):
        """Move the pattern in the specified direction."""
        with self.lock:
            if direction == 'left':
                self.pattern_x -= amount
            elif direction == 'right':
                self.pattern_x += amount
            elif direction == 'up':
                self.pattern_y -= amount
            elif direction == 'down':
                self.pattern_y += amount
            elif direction == 'forward':
                self.pattern_z += amount
            elif direction == 'backward':
                self.pattern_z -= amount
        logging.info(f"Pattern moved {direction} by {amount} units")
    
    def toggle_marker_detection(self, enable: bool) -> bool:
        """
        Toggle marker detection on/off.
        
        Args:
            enable: True to enable marker detection, False to disable
            
        Returns:
            Current state of marker detection
        """
        self.enable_marker_detection = enable
        logging.info(f"Marker detection {'enabled' if enable else 'disabled'}")
        return self.enable_marker_detection
    
    async def capture_loop(self):
        """Main capture loop that generates frames."""
        self.running = True
        logging.info("Mock camera capture loop started")
        
        while self.running:
            start_time = time.time()
            
            # Generate frames for each view
            for view in self.views:
                camera_id = view['id']
                if camera_id in self.callbacks:
                    # Render the frame
                    with self.lock:
                        frame = self.render_view(
                            view['x'], view['y'], view['z'], 
                            view['yaw'], view['pitch']
                        )
                    
                    # Process frame for marker detection if enabled
                    encoded_frame = self.encode_frame(frame)
                    
                    if self.enable_marker_detection:
                        # Process frame with marker detector
                        encoded_frame, _ = self.marker_detector.detect_markers(encoded_frame, camera_id)
                    
                    # Send via callback
                    await self.callbacks[camera_id](encoded_frame)
            
            # Calculate time to maintain frame rate
            elapsed = time.time() - start_time
            sleep_time = max(0, 1.0/self.frame_rate - elapsed)
            await asyncio.sleep(sleep_time)
    
    async def start(self):
        """Start the capture loop."""
        if not self.running:
            asyncio.create_task(self.capture_loop())
            logging.info("Mock camera service started")
    
    def stop(self):
        """Stop the capture loop."""
        self.running = False
        logging.info("Mock camera service stopped")


# Singleton instance
_instance = None

def get_mock_camera_service():
    """Get or create the mock camera service singleton."""
    global _instance
    if _instance is None:
        _instance = MockCameraService()
    return _instance