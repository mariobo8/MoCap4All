# app/routers/marker_detection.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import logging
from app.services.marker_detection import get_marker_detector
from app.services.mock_camera import get_mock_camera_service

router = APIRouter()

class ImageData(BaseModel):
    camera_id: str
    image: str  # base64 encoded image

@router.post("/marker-detection/detect")
async def detect_markers(data: ImageData):
    """
    Detect markers in the provided image.
    
    Args:
        data: ImageData containing camera_id and base64 encoded image
        
    Returns:
        Dictionary with annotated image and detected markers
    """
    try:
        # Get marker detector
        marker_detector = get_marker_detector()
        
        # Process image
        annotated_image, markers = marker_detector.detect_markers(data.image, data.camera_id)
        
        return {
            "success": True,
            "image": annotated_image,
            "markers": [{"x": m[0], "y": m[1]} for m in markers]
        }
    except Exception as e:
        logging.error(f"Error detecting markers: {e}")
        raise HTTPException(status_code=500, detail=f"Error detecting markers: {str(e)}")

@router.post("/marker-detection/toggle")
async def toggle_marker_detection(enable: bool = True):
    """API endpoint to toggle marker detection."""
    mock_camera = get_mock_camera_service()
    is_enabled = mock_camera.toggle_marker_detection(enable)
    return {
        "success": True, 
        "enabled": is_enabled,
        "message": f"Marker detection {'enabled' if is_enabled else 'disabled'}"
    }