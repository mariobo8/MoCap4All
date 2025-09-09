# backend/app.py

import cv2
import numpy as np
import base64
from threading import Lock

from flask import Flask
from flask_socketio import SocketIO

# Import our custom modules
from camera_manager import camera_manager
from processing import detect_markers

# --- Flask & SocketIO App Initialization ---
app = Flask(__name__)
# The secret key is used for session management, though we don't use sessions here.
app.config['SECRET_KEY'] = 'secret!' 
# Initialize SocketIO, allowing all origins for easy development
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Background Thread for Real-time Processing ---
# A lock to ensure that the background thread is started only once.
thread = None
thread_lock = Lock()

def background_task():
    """
    The main background task that continuously processes camera frames and emits data.
    """
    print("Background task started.")
    while True:
        # Get the latest processed frames from all cameras.
        frames = camera_manager.get_processed_frames()
        if not frames:
            socketio.sleep(0.1) # Wait a bit if no frames are available
            continue

        all_cameras_marker_data = []
        display_frames = []

        # Process each camera frame individually
        for i, frame in enumerate(frames):
            # Run marker detection
            marker_coords = detect_markers(frame, threshold_value=200) # Using a fixed threshold for now
            all_cameras_marker_data.append(marker_coords)
            
            # Draw detected markers on a copy of the frame for the video feed
            display_frame = frame.copy()
            for (x, y) in marker_coords:
                cv2.circle(display_frame, (x, y), 5, (0, 255, 0), 2)
            display_frames.append(display_frame)

        # --- Prepare Data for Emission ---
        # 1. Video Feed: Stitch frames together and encode as JPEG
        combined_frame = np.hstack(display_frames)
        _, buffer = cv2.imencode('.jpg', combined_frame)
        # Encode the JPEG image to a Base64 string for easy transport over WebSocket
        image_str = base64.b64encode(buffer).decode('utf-8')

        # 2. Marker Data: The raw coordinates
        # We can enhance this later to be a more structured dictionary
        marker_data = {'markers': all_cameras_marker_data}
        
        # --- Emit Data to Clients ---
        socketio.emit('video_feed', {'image': image_str})
        socketio.emit('marker_data', marker_data)
        
        # Control the update rate (e.g., 20 FPS)
        socketio.sleep(1 / 20)

@socketio.on('connect')
def handle_connect():
    """
    This function is called when a new client connects to the SocketIO server.
    It starts the background task if it's not already running.
    """
    global thread
    print("Client connected")
    with thread_lock:
        if thread is None:
            # Start the background task in a separate thread managed by SocketIO
            thread = socketio.start_background_task(target=background_task)

# --- Main Execution Block ---
if __name__ == '__main__':
    try:
        # First, start the camera capture thread. This is crucial.
        camera_manager.start_capture()
        if camera_manager.num_cameras == 0:
            print("No cameras detected. The server will run, but no feed will be available.")
        
        # Then, run the Flask-SocketIO server.
        print("Starting Flask-SocketIO server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)

    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        # Ensure camera resources are always released on exit.
        print("Releasing camera resources.")
        camera_manager.stop_capture()