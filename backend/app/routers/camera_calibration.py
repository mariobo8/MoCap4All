# app/routers/camera_calibration.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
from app.services.camera_calibration import get_camera_calibration_service
from app.services.mock_camera import get_mock_camera_service

router = APIRouter()

class CalibrateRequest(BaseModel):
    """Request model for camera calibration."""
    frames: List[str]

@router.post("/camera-calibration/calibrate")
async def calibrate_cameras(data: CalibrateRequest):
    """
    Calibrate cameras using frames from two different views.
    
    Args:
        data: CalibrateRequest with frames from both cameras
        
    Returns:
        Dictionary with calibration results
    """
    try:
        calibration_service = get_camera_calibration_service()
        result = calibration_service.calibrate_from_frames(data.frames)
        return result
    except Exception as e:
        logging.error(f"Error calibrating cameras: {e}")
        raise HTTPException(status_code=500, detail=f"Error calibrating cameras: {str(e)}")

@router.get("/camera-calibration/status")
async def get_calibration_status():
    """Get the current status of camera calibration."""
    try:
        calibration_service = get_camera_calibration_service()
        camera_poses = calibration_service.get_camera_poses()
        
        return {
            "is_calibrated": camera_poses is not None,
            "camera_poses": calibration_service._camera_pose_to_serializable(camera_poses) if camera_poses else None
        }
    except Exception as e:
        logging.error(f"Error getting calibration status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting calibration status: {str(e)}")