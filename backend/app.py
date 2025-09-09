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
    is_detecting = False
    # is_capturing has been removed
    exposure = 100
    gain = 10
    detection_threshold = 200

@socketio.on('update_threshold')
def handle_threshold_update(data):
    AppSettings.detection_threshold = int(data.get('value', AppSettings.detection_threshold))

@socketio.on('toggle_detection')
def handle_detection_toggle(data):
    AppSettings.is_detecting = bool(data.get('value', AppSettings.is_detecting))
    print(f"Marker detection toggled: {'ON' if AppSettings.is_detecting else 'OFF'}")

@socketio.on('update_camera_settings')
def handle_camera_settings(data):
    AppSettings.exposure = int(data.get('exposure', AppSettings.exposure))
    AppSettings.gain = int(data.get('gain', AppSettings.gain))
    camera_manager.edit_settings(AppSettings.exposure, AppSettings.gain)

# The 'toggle_capture' handler has been removed

def get_status():
    """Simplified status helper."""
    if AppSettings.is_detecting:
        return "Detecting Markers"
    return "Idle"

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
            if AppSettings.is_detecting:
                marker_coords, _ = detect_markers(frame, threshold_value=AppSettings.detection_threshold)
                all_cameras_marker_data.append(marker_coords)
                for (x, y) in marker_coords:
                    cv2.circle(display_frame, (x, y), 5, (0, 255, 0), 2)
            else:
                all_cameras_marker_data.append([])

            border_color = (100, 100, 100)
            display_frame_with_border = cv2.copyMakeBorder(display_frame, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=border_color)
            label = f"Camera {i + 1}"
            cv2.putText(display_frame_with_border, label, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            display_frames.append(display_frame_with_border)

        combined_frame = np.hstack(display_frames)
        _, buffer = cv2.imencode('.jpg', combined_frame)
        image_str = base64.b64encode(buffer).decode('utf-8')
        
        socketio.emit('video_feed', {'image': image_str})
        socketio.emit('marker_data', {'markers': all_cameras_marker_data})
        socketio.emit('status_update', {'status': get_status()})
        
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