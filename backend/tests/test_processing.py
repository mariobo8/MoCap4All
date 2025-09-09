# backend/tests/test_processing.py

import cv2
import time
import numpy as np

from backend.camera_manager import camera_manager
# Import our new marker detection function
from backend.processing import detect_markers

# A simple class to hold our trackbar value
class Settings:
    threshold = 200 # Initial threshold value

def on_trackbar(val):
    """Callback function for the trackbar."""
    Settings.threshold = val

def run_test():
    """
    Tests the marker detection pipeline on the live camera feeds.
    """
    print("Starting camera manager for processing test...")
    camera_manager.start_capture()

    if camera_manager.num_cameras == 0:
        print("Camera manager failed to find any cameras. Aborting test.")
        camera_manager.stop_capture()
        return

    print(f"Manager started with {camera_manager.num_cameras} camera(s).")
    time.sleep(2)

    window_name = 'Marker Detection Test'
    cv2.namedWindow(window_name)
    
    # Create a trackbar to adjust the threshold in real-time
    cv2.createTrackbar('Threshold', window_name, Settings.threshold, 255, on_trackbar)
    
    print("\nStarting test. Adjust the 'Threshold' slider. Press 'q' to quit.")

    try:
        while True:
            frames = camera_manager.get_processed_frames()

            if not frames:
                time.sleep(0.1)
                continue
            
            display_frames = []
            for frame in frames:
                # Make a copy to draw on, so we don't alter the original
                display_frame = frame.copy()
                
                # --- This is the core of the test ---
                # Run marker detection on the current frame
                marker_coords = detect_markers(display_frame, Settings.threshold)
                
                # Draw the results on the display frame
                for (x, y) in marker_coords:
                    # Draw a green circle at the center of each detected marker
                    cv2.circle(display_frame, (x, y), 5, (0, 255, 0), 2)
                
                display_frames.append(display_frame)
            
            # Combine all frames into a single window
            combined_frame = np.hstack(display_frames)
            cv2.imshow(window_name, combined_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        print("Stopping camera capture...")
        camera_manager.stop_capture()
        cv2.destroyAllWindows()
        print("Test finished.")

if __name__ == "__main__":
    run_test()