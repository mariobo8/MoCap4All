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
    cameras_initialized = False
    is_detecting = False
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

@socketio.on('initialize_cameras')
def handle_initialize_cameras():
    global thread
    with thread_lock:
        if not AppSettings.cameras_initialized:
            print("Received request to initialize cameras...")
            camera_manager.start_capture()
            if camera_manager.num_cameras > 0:
                AppSettings.cameras_initialized = True
                camera_manager.edit_settings(AppSettings.exposure, AppSettings.gain)
                if thread is None:
                    thread = socketio.start_background_task(target=background_task)
                socketio.emit('cameras_initialized_status', {
                    'success': True, 
                    'message': f'Successfully initialized {camera_manager.num_cameras} cameras.'
                })
            else:
                socketio.emit('cameras_initialized_status', {
                    'success': False, 
                    'message': 'Failed to initialize cameras. Check connections.'
                })

# --- NEW: Handler for the "Disconnect Cameras" button ---
@socketio.on('disconnect_cameras')
def handle_disconnect_cameras():
    global thread
    with thread_lock:
        if AppSettings.cameras_initialized:
            print("Received request to disconnect cameras...")
            # This flag will stop the background task's while loop
            AppSettings.cameras_initialized = False
            # Wait a moment for the background thread to finish its current loop and exit
            socketio.sleep(0.1) 
            
            # Stop the camera hardware capture thread
            camera_manager.stop_capture()
            
            # Reset the thread variable so it can be restarted later
            thread = None
            
            # Send confirmation back to the frontend
            socketio.emit('cameras_initialized_status', {
                'success': False, 
                'message': 'Cameras disconnected successfully.'
            })

def get_status():
    if not AppSettings.cameras_initialized:
        return "Cameras Off"
    if AppSettings.is_detecting:
        return "Detecting Markers"
    return "Idle"

def background_task():
    print("Background processing task started.")
    # The loop will now automatically exit when cameras_initialized becomes False
    while AppSettings.cameras_initialized:
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
    print("Background processing task stopped.")

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    # --- MODIFIED: Emit the current camera status to the new client ---
    # This ensures the UI is correct if a user refreshes the page.
    socketio.emit('cameras_initialized_status', {'success': AppSettings.cameras_initialized})

if __name__ == '__main__':
    try:
        print("Starting Flask-SocketIO server, waiting for client to initialize cameras...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        print("Releasing camera resources.")
        camera_manager.stop_capture()