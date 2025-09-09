# backend/processing.py

import cv2
import numpy as np

def detect_markers(frame, threshold_value=200):
    """
    Detects bright markers in a single video frame.

    Args:
        frame (np.array): A single BGR video frame from a camera.
        threshold_value (int): The brightness cutoff for a pixel to be considered
                               part of a marker (0-255).

    Returns:
        list: A list of tuples, where each tuple is the (x, y) coordinate
              of a detected marker's center.
    """
    # 1. Convert the frame to grayscale. This simplifies the thresholding process.
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. Apply a binary threshold. Pixels brighter than threshold_value will be set
    #    to 255 (white), and all others to 0 (black). The markers should become
    #    white blobs.
    _, threshold_img = cv2.threshold(gray_frame, threshold_value, 255, cv2.THRESH_BINARY)

    # 3. Find contours in the thresholded image. A contour is the outline of a shape.
    #    cv2.RETR_EXTERNAL is used to only find the outermost contours.
    contours, _ = cv2.findContours(threshold_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    marker_centers = []
    
    # 4. Loop over all the contours that were found.
    for contour in contours:
        # 5. Filter out noise by checking the area of the contour. If it's too small,
        #    it's likely just a random bright pixel, not a real marker.
        #    This is a key parameter to tune.
        if cv2.contourArea(contour) > 2: # Adjust this area threshold as needed
            
            # 6. Calculate the "moments" of the contour to find its center.
            M = cv2.moments(contour)
            if M["m00"] != 0:
                # Calculate the center x, y coordinates (the centroid)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                marker_centers.append((cX, cY))

    return marker_centers