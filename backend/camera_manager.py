# backend/camera_manager.py

import threading
import time
import json
import os
import cv2
import numpy as np

# A flag to attempt importing the pseyepy library.
try:
    from pseyepy import Camera
    PSEYE_AVAILABLE = True
except ImportError:
    print("WARNING: pseyepy library not found. CameraManager will not be able to connect to PS Eye cameras.")
    PSEYE_AVAILABLE = False

class CameraManager:
    """
    A thread-safe singleton class to manage PS Eye cameras.
    It uses a dedicated thread to continuously capture raw frames and provides
    methods to retrieve processed frames based on the application's state.
    """

    def __init__(self):
        if not PSEYE_AVAILABLE:
            self.cameras = None
            print("ERROR: Cannot initialize CameraManager, pseyepy library not available.")
            return

        # --- Camera Hardware and Frame Buffers ---
        self.cameras = None
        self.num_cameras = 0
        self._latest_raw_frames = {} # Stores raw frames from the capture thread
        self.camera_params = self._load_camera_params() # Stores calibration data

        # --- Threading Primitives ---
        self._frame_lock = threading.Lock()
        self._capture_thread = None
        self._stop_event = threading.Event()

        # --- Application State Flags ---
        self.is_capturing_points = False

    def _load_camera_params(self):
        """
        Loads intrinsic and extrinsic parameters for each camera from a JSON file.
        """
        try:
            # --- THIS IS THE MODIFIED PART ---
            dirname = os.path.dirname(__file__)
            # Point to the 'config' subfolder to find the parameters file.
            filename = os.path.join(dirname, "config", "camera-params.json")
            # --- END OF MODIFICATION ---
            
            with open(filename, 'r') as f:
                params = json.load(f)
            print("Successfully loaded camera parameters from 'config' folder.")
            return params
        except FileNotFoundError:
            print("ERROR: 'backend/config/camera-params.json' not found. Please create it.")
            return []
        except Exception as e:
            print(f"ERROR loading camera parameters: {e}")
            return []

    def _initialize_cameras(self):
        """
        Initializes a connection to all available PS Eye cameras.
        """
        print("Attempting to initialize PS Eye cameras with auto-detection...")
        try:
            self.cameras = Camera(fps=90, resolution=Camera.RES_SMALL, gain=10, exposure=100)
            self.num_cameras = len(self.cameras.exposure)

            if self.num_cameras > 0:
                print(f"Successfully initialized {self.num_cameras} cameras.")
                if len(self.camera_params) < self.num_cameras:
                    print(f"WARNING: Found {self.num_cameras} cameras but only {len(self.camera_params)} parameter sets.")
                return True
            else:
                print("ERROR: No PS Eye cameras were detected.")
                self.cameras = None
                return False
        except Exception as e:
            print(f"ERROR: Failed to initialize cameras. Details: {e}")
            self.cameras = None
            return False

    def start_capture(self):
        """
        Starts the background frame capture thread.
        """
        if self._initialize_cameras():
            self._stop_event.clear()
            self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._capture_thread.start()
            print("Camera capture thread started.")

    def stop_capture(self):
        """
        Stops the capture thread and releases camera resources.
        """
        print("Stopping camera capture...")
        self._stop_event.set()
        if self._capture_thread is not None:
            self._capture_thread.join()
        if self.cameras is not None:
            self.cameras.end()
            print("Camera resources released.")
        self.cameras = None
        self._capture_thread = None

    def _capture_loop(self):
        """
        The core loop of the capture thread. Continuously reads raw frames
        from the cameras and stores them in a thread-safe dictionary.
        """
        while not self._stop_event.is_set():
            if self.cameras:
                try:
                    frames, _ = self.cameras.read()
                    with self._frame_lock:
                        for i, frame in enumerate(frames):
                            self._latest_raw_frames[i] = frame
                except Exception as e:
                    print(f"ERROR in capture loop: {e}")
                    self._stop_event.set()
            time.sleep(1 / 200) # Small sleep to yield CPU time
        print("Capture loop stopped.")

    def get_latest_raw_frames(self):
        """
        Returns a thread-safe copy of the latest raw frames dictionary.
        """
        with self._frame_lock:
            return self._latest_raw_frames.copy()

    def get_processed_frames(self):
        """
        Retrieves the latest raw frames and applies the standard pre-processing pipeline.
        """
        raw_frames_dict = self.get_latest_raw_frames()
        if not raw_frames_dict:
            return None 

        processed_frames = []
        sharpen_kernel = np.array([
            [-2,-1,-1,-1,-2], [-1, 1, 3, 1,-1], [-1, 3, 4, 3,-1],
            [-1, 1, 3, 1,-1], [-2,-1,-1,-1,-2]
        ])

        for i in range(self.num_cameras):
            frame = raw_frames_dict.get(i)
            if frame is None:
                res = Camera.RES_SMALL
                placeholder = np.zeros((res[1], res[0], 3), dtype=np.uint8)
                cv2.putText(placeholder, f"Cam {i} No Signal", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                processed_frames.append(placeholder)
                continue

            params = self.get_camera_params(i)
            
            if params and params.get("rotation", 0) != 0:
                frame = np.rot90(frame, k=params["rotation"])

            if params:
                frame = cv2.undistort(frame, params["intrinsic_matrix"], params["distortion_coef"])

            frame = cv2.GaussianBlur(frame, (9, 9), 0)
            frame = cv2.filter2D(frame, -1, sharpen_kernel)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            processed_frames.append(frame)

        return processed_frames

    def edit_settings(self, exposure, gain):
        """
        Adjusts the exposure and gain for all cameras in real-time.
        """
        if self.cameras:
            try:
                self.cameras.exposure = [exposure] * self.num_cameras
                self.cameras.gain = [gain] * self.num_cameras
                print(f"Set exposure={exposure}, gain={gain} for {self.num_cameras} cameras.")
                return True
            except Exception as e:
                print(f"ERROR setting camera properties: {e}")
                return False
        return False

    def get_camera_params(self, camera_index):
        """
        Safely retrieves the parameter set for a specific camera.
        """
        if camera_index < len(self.camera_params):
            param_set = self.camera_params[camera_index]
            return {
                "intrinsic_matrix": np.array(param_set["intrinsic_matrix"]),
                "distortion_coef": np.array(param_set["distortion_coef"]),
                "rotation": param_set.get("rotation", 0)
            }
        return None

# --- Singleton Instance ---
camera_manager = CameraManager()