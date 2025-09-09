# backend/app.py

import cv2
import numpy as np
import base64
from threading import Lock

from flask import Flask
from flask_socketio import SocketIO

from camera_manager import camera_manager
from processing import detect_markers

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

thread = None
thread_lock = Lock()

class AppSettings:
    detection_threshold = 200
    # --- NEW: Add state for detection toggle and camera settings ---
    is_detecting = False
    exposure = 100
    gain = 10

@socketio.on('update_threshold')
def handle_threshold_update(data):
    new_value = data.get('value')
    if new_value is not None:
        AppSettings.detection_threshold = int(new_value)

# --- NEW: Handler for the Start/Stop Detection button ---
@socketio.on('toggle_detection')
def handle_detection_toggle(data):
    is_on = data.get('value')
    if is_on is not None:
        AppSettings.is_detecting = bool(is_on)
        print(f"Marker detection toggled: {'ON' if AppSettings.is_detecting else 'OFF'}")

# --- NEW: Handler for the Exposure and Gain sliders ---
@socketio.on('update_camera_settings')
def handle_camera_settings(data):
    exposure = data.get('exposure')
    gain = data.get('gain')
    if exposure is not None and gain is not None:
        AppSettings.exposure = int(exposure)
        AppSettings.gain = int(gain)
        # Pass the new settings to the camera manager to apply them to the hardware
        camera_manager.edit_settings(AppSettings.exposure, AppSettings.gain)

def background_task():
    print("Background task started.")
    while True:
        frames = camera_manager.get_processed_frames()
        if not frames:
            socketio.sleep(0.1)
            continue

        all_cameras_marker_data = []
        display_frames = []

        for i, frame in enumerate(frames):
            display_frame = frame.copy()
            
            # --- MODIFIED: Wrap detection logic in an 'if' statement ---
            if AppSettings.is_detecting:
                marker_coords, _ = detect_markers(frame, threshold_value=AppSettings.detection_threshold)
                all_cameras_marker_data.append(marker_coords)
                # Draw markers only if detection is on
                for (x, y) in marker_coords:
                    cv2.circle(display_frame, (x, y), 5, (0, 255, 0), 2)
            else:
                # If detection is off, just append an empty list for this camera's data
                all_cameras_marker_data.append([])

            display_frames.append(display_frame)

        combined_frame = np.hstack(display_frames)
        _, buffer = cv2.imencode('.jpg', combined_frame)
        image_str = base64.b64encode(buffer).decode('utf-8')

        marker_data = {'markers': all_cameras_marker_data}
        
        socketio.emit('video_feed', {'image': image_str})
        socketio.emit('marker_data', marker_data)
        
        socketio.sleep(1 / 20)

@socketio.on('connect')
def handle_connect():
    global thread
    print("Client connected")
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_task)

if __name__ == '__main__':
    try:
        camera_manager.start_capture()
        if camera_manager.num_cameras > 0:
            # --- NEW: Apply default settings on startup ---
            camera_manager.edit_settings(AppSettings.exposure, AppSettings.gain)
        else:
            print("No cameras detected.")
        
        print("Starting Flask-SocketIO server...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)

    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        print("Releasing camera resources.")
        camera_manager.stop_capture()