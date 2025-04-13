# app/services/marker_detection.py
import cv2 as cv
import numpy as np
import base64
import logging
from typing import List, Tuple, Dict, Optional

class MarkerDetector:
    def __init__(self):
        self.detected_markers: Dict[str, List[Tuple[int, int]]] = {}
        self.marker_sizes: Dict[str, List[float]] = {}
        self.matches: List[Tuple[int, int]] = []
        self.is_initialized = False
        logging.info("Marker detector initialized")

    def detect_markers(self, image_data: str, camera_id: str) -> Tuple[str, List[Tuple[int, int]]]:
        """
        Detect markers in the base64 encoded image and return annotated image and marker positions.
        
        Args:
            image_data: Base64 encoded image string
            camera_id: Camera identifier
            
        Returns:
            Tuple containing:
                - Base64 encoded annotated image
                - List of detected marker centers (x, y)
        """
        # Decode the base64 image
        img_bytes = base64.b64decode(image_data)
        img_np = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv.imdecode(img_np, cv.IMREAD_COLOR)
        
        if img is None:
            logging.error(f"Failed to decode image for camera {camera_id}")
            return image_data, []
            
        # Detect white dots
        centers, sizes, img_with_markers = self._detect_white_dots(img)
        
        # Store detected markers for this camera
        self.detected_markers[camera_id] = centers
        self.marker_sizes[camera_id] = sizes
        
        # Match markers if we have detections from multiple cameras but haven't matched yet
        if not self.is_initialized and len(self.detected_markers) >= 2:
            self._match_markers()
            self.is_initialized = True
            logging.info("Marker matching initialized")
        
        # Annotate the image with markers and their IDs
        img_annotated = self._annotate_image(img.copy(), camera_id)
        
        # Encode the annotated image back to base64
        _, buffer = cv.imencode('.jpg', img_annotated, [cv.IMWRITE_JPEG_QUALITY, 80])
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        
        return jpg_as_text, centers
    
    def _detect_white_dots(self, img: np.ndarray) -> Tuple[List[Tuple[int, int]], List[float], np.ndarray]:
        """
        Detect white dots in the image using blob detection.
        
        Args:
            img: Input image in BGR format
            
        Returns:
            Tuple containing:
                - List of center coordinates (x, y)
                - List of marker sizes
                - Image with detected markers drawn
        """
        # Convert BGR to grayscale
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        # Apply threshold to isolate white/bright areas
        _, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)
        
        # Apply morphological operations to clean up the mask
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
        binary = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel)
        binary = cv.morphologyEx(binary, cv.MORPH_CLOSE, kernel)
        
        # Set up blob detector parameters
        params = cv.SimpleBlobDetector_Params()
        
        # Change thresholds
        params.minThreshold = 200
        params.maxThreshold = 255
        
        # Filter by color (255 = light, 0 = dark)
        params.filterByColor = True
        params.blobColor = 255  # White blobs on black background
        
        # Filter by area
        params.filterByArea = True
        params.minArea = 10
        params.maxArea = 100000
        
        # Filter by circularity
        params.filterByCircularity = True
        params.minCircularity = 0.3
        
        # Filter by convexity
        params.filterByConvexity = True
        params.minConvexity = 0.1
        
        # Filter by inertia (how circular vs. elliptical)
        params.filterByInertia = True
        params.minInertiaRatio = 0.2
        
        # Create detector
        detector = cv.SimpleBlobDetector_create(params)
        
        # Detect blobs
        keypoints = detector.detect(binary)
        
        # Extract coordinates and sizes
        centers = [(int(k.pt[0]), int(k.pt[1])) for k in keypoints]
        sizes = [k.size for k in keypoints]
        
        # If blob detector didn't work well, try alternative approach
        if len(centers) < 6:  # We expect at least 6 dots
            centers, sizes, img_with_keypoints, _ = self._detect_white_dots_alternative(img)
            logging.info(f"Using alternative detection method, found {len(centers)} markers")
        else:
            # Visualize detection
            img_with_keypoints = cv.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255), 
                                                cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            
        return centers, sizes, img_with_keypoints
    
    def _detect_white_dots_alternative(self, img: np.ndarray) -> Tuple[List[Tuple[int, int]], List[float], np.ndarray, np.ndarray]:
        """
        Alternative method to detect white dots using contour detection.
        
        Args:
            img: Input image in BGR format
            
        Returns:
            Tuple containing:
                - List of center coordinates (x, y)
                - List of marker sizes
                - Image with detected markers drawn
                - Binary threshold image
        """
        # Convert to grayscale
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv.threshold(gray, 230, 255, cv.THRESH_BINARY)
        
        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
        thresh = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and shape
        centers = []
        sizes = []
        for contour in contours:
            area = cv.contourArea(contour)
            if area < 50 or area > 5000:  # Filter by area
                continue
                
            # Calculate circularity
            perimeter = cv.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            if circularity < 0.5:  # Filter by circularity (circle = 1)
                continue
                
            # Calculate center
            M = cv.moments(contour)
            if M["m00"] > 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centers.append((cX, cY))
                
                # Estimate dot size (radius)
                radius = int(np.sqrt(area / np.pi))
                sizes.append(radius * 2)  # Diameter
        
        # Create visualization image
        img_with_keypoints = img.copy()
        return centers, sizes, img_with_keypoints, thresh
    
    def _match_markers(self) -> None:
        """
        Match markers between cameras using fixed manual pattern matching.
        This is called once when we have detections from at least two cameras.
        """
        if len(self.detected_markers) < 2:
            logging.warning("Cannot match markers: need at least 2 camera views")
            return
            
        # Get the first two camera IDs
        camera_ids = list(self.detected_markers.keys())
        points1 = self.detected_markers[camera_ids[0]]
        points2 = self.detected_markers[camera_ids[1]]
        
        logging.info(f"Matching markers between camera {camera_ids[0]} and {camera_ids[1]}")
        logging.info(f"Found {len(points1)} markers in camera {camera_ids[0]}")
        logging.info(f"Found {len(points2)} markers in camera {camera_ids[1]}")
        
        # Convert to numpy arrays
        pts1 = np.array(points1)
        pts2 = np.array(points2)
        
        if len(pts1) < 8 or len(pts2) < 8:
            logging.warning(f"Not enough points for matching: {len(pts1)} and {len(pts2)}")
            # If not enough points, skip matching
            return
        
        # Sort all points by y-coordinate (top to bottom)
        y_sorted_indices1 = np.argsort([p[1] for p in pts1])
        y_sorted_indices2 = np.argsort([p[1] for p in pts2])
        
        # Check if we have enough points for proper splitting
        if len(y_sorted_indices1) < 8 or len(y_sorted_indices2) < 8:
            # Try to split evenly if possible
            half1 = len(y_sorted_indices1) // 2
            half2 = len(y_sorted_indices2) // 2
            top_row1_indices = y_sorted_indices1[:half1]
            bottom_row1_indices = y_sorted_indices1[half1:]
            top_row2_indices = y_sorted_indices2[:half2]
            bottom_row2_indices = y_sorted_indices2[half2:]
        else:
            # Try to follow the pattern layout: split into top and bottom rows
            top_row1_indices = y_sorted_indices1[:6]
            bottom_row1_indices = y_sorted_indices1[6:]
            top_row2_indices = y_sorted_indices2[:6]
            bottom_row2_indices = y_sorted_indices2[6:]
        
        # For each row, sort by x-coordinate (left to right)
        def sort_indices_by_x(indices, points):
            return sorted(indices, key=lambda i: points[i][0])
        
        # Sort each row by x-coordinate
        top_row1_x_sorted = sort_indices_by_x(top_row1_indices, pts1)
        bottom_row1_x_sorted = sort_indices_by_x(bottom_row1_indices, pts1)
        top_row2_x_sorted = sort_indices_by_x(top_row2_indices, pts2)
        bottom_row2_x_sorted = sort_indices_by_x(bottom_row2_indices, pts2)
        
        # Apply the matching rules based on the pattern
        matches = []
        
        # Top row: first 5 points + last point (if available)
        for i in range(min(5, len(top_row1_x_sorted), len(top_row2_x_sorted))):
            idx1 = top_row1_x_sorted[i]
            idx2 = top_row2_x_sorted[i]
            matches.append((idx1, idx2))
        
        # Last point in top row (if available)
        if len(top_row1_x_sorted) >= 6 and len(top_row2_x_sorted) >= 6:
            idx1 = top_row1_x_sorted[-1]
            idx2 = top_row2_x_sorted[-1]
            matches.append((idx1, idx2))
        
        # Bottom row: first 4 points + last 2 points (if available)
        for i in range(min(4, len(bottom_row1_x_sorted), len(bottom_row2_x_sorted))):
            idx1 = bottom_row1_x_sorted[i]
            idx2 = bottom_row2_x_sorted[i]
            matches.append((idx1, idx2))
        
        # Last 2 points in bottom row (if available)
        if len(bottom_row1_x_sorted) >= 6 and len(bottom_row2_x_sorted) >= 6:
            # Second to last point
            idx1 = bottom_row1_x_sorted[-2]
            idx2 = bottom_row2_x_sorted[-2]
            matches.append((idx1, idx2))
            
            # Last point
            idx1 = bottom_row1_x_sorted[-1]
            idx2 = bottom_row2_x_sorted[-1]
            matches.append((idx1, idx2))
        
        self.matches = matches
        logging.info(f"Matched {len(matches)} markers between cameras")
    
    def _annotate_image(self, img: np.ndarray, camera_id: str) -> np.ndarray:
        """
        Annotate the image with markers and their IDs.
        
        Args:
            img: Input image to annotate
            camera_id: Camera identifier
            
        Returns:
            Annotated image
        """
        if camera_id not in self.detected_markers:
            return img
            
        centers = self.detected_markers[camera_id]
        sizes = self.marker_sizes.get(camera_id, [10] * len(centers))
        
        # If we have matches, use them to draw numbered markers
        if self.is_initialized and len(self.matches) > 0:
            # Get camera indices
            camera_ids = list(self.detected_markers.keys())
            cam_idx = camera_ids.index(camera_id)
            
            # Draw each marker with its match ID
            for i, (center, size) in enumerate(zip(centers, sizes)):
                # Default marker ID is its index
                marker_id = i
                
                # Check if this marker is part of a match
                for match_idx, match in enumerate(self.matches):
                    if cam_idx == 0 and match[0] == i:
                        marker_id = match_idx
                        break
                    elif cam_idx == 1 and match[1] == i:
                        marker_id = match_idx
                        break
                
                # Draw circle and label
                cv.circle(img, center, int(size/2), (0, 0, 255), 2)
                cv.putText(img, str(marker_id), (center[0]-10, center[1]-10), 
                          cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        else:
            # If no matches yet, just draw circles
            for center, size in zip(centers, sizes):
                cv.circle(img, center, int(size/2), (0, 0, 255), 2)
        
        return img

# Singleton instance
_marker_detector_instance = None

def get_marker_detector():
    """Get or create the marker detector singleton."""
    global _marker_detector_instance
    if _marker_detector_instance is None:
        _marker_detector_instance = MarkerDetector()
    return _marker_detector_instance