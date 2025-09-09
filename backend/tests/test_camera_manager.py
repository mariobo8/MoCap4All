# backend/tests/test_camera_manager.py

import cv2
import time
import numpy as np

# This import works when run as a module from the project root
from backend.camera_manager import camera_manager

def run_test():
    """
    Tests the updated CameraManager by displaying the processed feeds.
    """
    # 1. Start the camera manager's capture thread.
    print("Attempting to start camera manager...")
    camera_manager.start_capture()

    # Check if initialization was successful
    if camera_manager.num_cameras == 0:
        print("Camera manager failed to find any cameras. Aborting test.")
        camera_manager.stop_capture()
        return

    print(f"Manager started with {camera_manager.num_cameras} camera(s).")
    print("Waiting for 2 seconds for cameras to warm up...")
    time.sleep(2)

    print("\nStarting camera feed test. Press 'q' on the video window to quit.")
    
    try:
        window_name = 'All Processed Camera Feeds'
        while True:
            # 2. Get the list of processed frames.
            # This method now handles rotation, undistortion, filtering, etc.
            processed_frames = camera_manager.get_processed_frames()

            if processed_frames:
                # 3. Stitch all frames together horizontally into a single image.
                combined_frame = np.hstack(processed_frames)
                
                # 4. Display the combined frame.
                cv2.imshow(window_name, combined_frame)
            else:
                print("Waiting for frames...")
                time.sleep(0.5)

            # 5. Check for the 'q' key to quit the loop.
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("'q' pressed, exiting.")
                break
    
    except Exception as e:
        print(f"An error occurred during the test: {e}")
    
    finally:
        # 6. VERY IMPORTANT: Always stop the capture and clean up.
        print("Stopping camera capture...")
        camera_manager.stop_capture()
        cv2.destroyAllWindows()
        print("Test finished and resources released.")

if __name__ == "__main__":
    run_test()