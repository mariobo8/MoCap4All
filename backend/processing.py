# backend/processing.py

import cv2
import numpy as np

def detect_markers(frame, threshold_value=173):
    """
    Detects bright, circular markers in a single video frame using advanced filtering.

    Args:
        frame (np.array): A single BGR video frame from a camera.
        threshold_value (int): The brightness cutoff for a pixel.

    Returns:
        tuple: A tuple containing:
            - list: A list of (x, y) coordinates for each detected marker's center.
            - np.array: The black and white "mask" image showing only the detected blobs.
    """
    # 1. Convert the frame to grayscale for simpler processing.
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. Apply a binary threshold to get a black and white image.
    _, threshold_img = cv2.threshold(gray_frame, threshold_value, 255, cv2.THRESH_BINARY)

    # 3. Find the outlines (contours) of all white shapes.
    contours, _ = cv2.findContours(threshold_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    marker_centers = []
    
    # Create a blank (black) image to draw the final mask on.
    output_mask = np.zeros_like(gray_frame)

    # 4. Loop over all found contours.
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # --- MODIFICATION START: More robust filtering ---
        
        # 5a. Filter by AREA to remove tiny noise and large bright spots.
        if 2 < area < 500: # Tune these min/max area values as needed.
            perimeter = cv2.arcLength(contour, True)
            
            # Avoid division by zero for invalid contours.
            if perimeter == 0:
                continue
            
            # 5b. Filter by CIRCULARITY to ensure we only get round shapes.
            # A perfect circle has a circularity of 1.
            circularity = 4 * np.pi * (area / (perimeter * perimeter))
            
            if circularity > 0.5: # Tune this circularity threshold as needed.
                # 6. Calculate the center of the valid marker.
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    marker_centers.append((cX, cY))
                    
                    # 7. Draw the valid, filtered contour onto our output mask.
                    # This creates the "white dots only" view.
                    cv2.drawContours(output_mask, [contour], -1, (255), thickness=cv2.FILLED)

        # --- MODIFICATION END ---

    # 8. Return both the list of coordinates and the visual mask.
    return marker_centers, output_mask