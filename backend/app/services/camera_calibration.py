# app/services/camera_calibration.py
import numpy as np
import cv2 as cv
from typing import List, Dict, Tuple, Optional, Any
import logging
from scipy.spatial.transform import Rotation
import base64

class CameraCalibrationService:
    def __init__(self):
        """Initialize the camera calibration service."""
        self.camera_poses = None
        self.intrinsic_matrices = [
            np.array([
                [600, 0, 320],
                [0, 600, 240],
                [0, 0, 1]
            ]),
            np.array([
                [600, 0, 320],
                [0, 600, 240],
                [0, 0, 1]
            ])
        ]
        logging.info("Camera calibration service initialized")

    def calibrate_from_frames(self, frames: List[str]) -> Dict[str, Any]:
        """
        Calibrate cameras using frames from multiple views.
        
        Args:
            frames: List of base64 encoded frame images
            
        Returns:
            Dictionary containing camera poses and other calibration data
        """
        if len(frames) < 2:
            logging.error("Need at least 2 frames for calibration")
            return {"success": False, "message": "Need at least 2 frames for calibration"}

        try:
            # Decode frames
            decoded_frames = []
            for frame in frames:
                img_bytes = base64.b64decode(frame)
                img_np = np.frombuffer(img_bytes, dtype=np.uint8)
                img = cv.imdecode(img_np, cv.IMREAD_COLOR)
                if img is None:
                    raise ValueError("Failed to decode image")
                decoded_frames.append(img)
            
            # Detect features in both frames
            camera_poses = self._calibrate_cameras(decoded_frames)
            self.camera_poses = camera_poses
            
            # Convert to serializable format for output
            serializable_poses = self._camera_pose_to_serializable(camera_poses)
            
            logging.info(f"Camera calibration successful: {serializable_poses}")
            return {
                "success": True,
                "camera_poses": serializable_poses
            }
        
        except Exception as e:
            logging.error(f"Error during camera calibration: {e}")
            return {"success": False, "message": f"Calibration error: {str(e)}"}

    def _calibrate_cameras(self, frames: List[np.ndarray]) -> List[Dict[str, np.ndarray]]:
        """
        Calculate camera poses using Structure from Motion.
        
        Args:
            frames: List of decoded image frames
            
        Returns:
            List of camera poses (rotation matrices and translation vectors)
        """
        # Convert images to grayscale
        gray_frames = [cv.cvtColor(frame, cv.COLOR_BGR2GRAY) for frame in frames]
        
        # Feature detection and extraction (use SIFT or ORB)
        sift = cv.SIFT_create()
        keypoints = []
        descriptors = []
        
        for gray in gray_frames:
            kp, des = sift.detectAndCompute(gray, None)
            keypoints.append(kp)
            descriptors.append(des)
        
        # Match features between frames
        bf = cv.BFMatcher()
        matches = bf.knnMatch(descriptors[0], descriptors[1], k=2)
        
        # Apply ratio test
        good_matches = []
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good_matches.append(m)
        
        # Extract matched points
        pts1 = np.float32([keypoints[0][m.queryIdx].pt for m in good_matches])
        pts2 = np.float32([keypoints[1][m.trainIdx].pt for m in good_matches])
        
        # Calculate essential matrix
        E, mask = cv.findEssentialMat(pts1, pts2, self.intrinsic_matrices[0], 
                                      method=cv.RANSAC, prob=0.999, threshold=1.0)
        
        # Recover rotation and translation from essential matrix
        _, R, t, mask = cv.recoverPose(E, pts1, pts2, self.intrinsic_matrices[0])
        
        # Set camera poses (first camera is at origin)
        camera_poses = [
            {"R": np.eye(3), "t": np.zeros((3, 1))},
            {"R": R, "t": t}
        ]
        
        # Print relative position for debugging
        print("Camera Calibration Results:")
        print(f"Camera 1 position: [0, 0, 0]")
        print(f"Camera 2 position: {t.flatten()}")
        print(f"Camera 2 rotation matrix:\n{R}")
        
        # Convert rotation matrix to Euler angles for easier interpretation
        euler_angles = Rotation.from_matrix(R).as_euler('xyz', degrees=True)
        print(f"Camera 2 rotation (Euler angles xyz): {euler_angles}")
        
        return camera_poses

    def _camera_pose_to_serializable(self, camera_poses: List[Dict[str, np.ndarray]]) -> List[Dict[str, List]]:
        """Convert camera poses to JSON serializable format."""
        serializable_poses = []
        for pose in camera_poses:
            serializable_pose = {
                "R": pose["R"].tolist(),
                "t": pose["t"].flatten().tolist()
            }
            serializable_poses.append(serializable_pose)
        return serializable_poses

    def get_camera_poses(self) -> Optional[List[Dict[str, np.ndarray]]]:
        """Get the current camera poses."""
        return self.camera_poses

# Singleton instance
_calibration_service_instance = None

def get_camera_calibration_service():
    """Get or create the camera calibration service singleton."""
    global _calibration_service_instance
    if _calibration_service_instance is None:
        _calibration_service_instance = CameraCalibrationService()
    return _calibration_service_instance