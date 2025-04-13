// src/components/CameraView/CameraContainer.jsx
import React, { useState } from 'react';
import CameraView from './CameraView';
import './CameraContainer.css';

const CameraContainer = () => {
  const [markerDetectionEnabled, setMarkerDetectionEnabled] = useState(false);
  const [isCalibrating, setIsCalibrating] = useState(false);

  // Function to send pattern movement commands via API
  const movePattern = (direction) => {
    fetch(`http://localhost:8000/api/camera/pattern/move?direction=${direction}&amount=10`, {
      method: 'POST'
    })
      .then(response => response.json())
      .then(data => console.log('Pattern moved:', data))
      .catch(err => console.error('Error sending pattern move command:', err));
  };

  // Function to toggle marker detection
  const toggleMarkerDetection = () => {
    const newState = !markerDetectionEnabled;
    fetch(`http://localhost:8000/api/marker-detection/toggle?enable=${newState}`, {
      method: 'POST'
    })
      .then(response => response.json())
      .then(data => {
        console.log('Marker detection toggled:', data);
        setMarkerDetectionEnabled(data.enabled);
      })
      .catch(err => console.error('Error toggling marker detection:', err));
  };

  // Function to perform camera calibration
  const calibrateCameras = async () => {
    setIsCalibrating(true);
    console.log('Starting camera calibration...');
    
    // Get frames from each camera
    try {
      // Get frames from both cameras
      const getFrame = async (cameraId) => {
        // Try to find the corresponding canvas element
        const canvas = document.querySelector(`#camera-canvas-${cameraId}`);
        if (!canvas) {
          throw new Error(`Cannot find canvas for camera ${cameraId}`);
        }
        
        // Get the data URL from the canvas and convert it to base64
        const dataUrl = canvas.toDataURL('image/jpeg');
        return dataUrl.split(',')[1]; // Remove the data:image/jpeg;base64, prefix
      };
      
      // Get frames from both cameras
      const frame1Promise = getFrame('1');
      const frame2Promise = getFrame('2');
      
      const [frame1, frame2] = await Promise.all([frame1Promise, frame2Promise]);
      
      // Send frames to the backend for calibration
      const response = await fetch('http://localhost:8000/api/camera-calibration/calibrate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          frames: [frame1, frame2]
        }),
      });
      
      const data = await response.json();
      console.log('Calibration result:', data);
      
      if (data.success) {
        alert('Camera calibration successful!');
      } else {
        alert(`Camera calibration failed: ${data.message}`);
      }
    } catch (error) {
      console.error('Error during calibration:', error);
      alert(`Calibration error: ${error.message}`);
    } finally {
      setIsCalibrating(false);
    }
  };

  return (
    <div className="camera-container">
      <h2 className="camera-container-title">Motion Capture Camera Feeds</h2>
      
      <div className="camera-grid">
        <div className="camera-grid-item">
          <CameraView 
            cameraId="1" 
            title="Camera 1 - Front View" 
            markerDetectionEnabled={markerDetectionEnabled}
          />
        </div>
        <div className="camera-grid-item">
          <CameraView 
            cameraId="2" 
            title="Camera 2 - Side View"
            markerDetectionEnabled={markerDetectionEnabled}
          />
        </div>
      </div>
      
      <div className="pattern-controls">
        <h3>Pattern Controls</h3>
        <div className="controls-grid">
          <div className="controls-row">
            <div className="spacer"></div>
            <button className="control-button" onClick={() => movePattern('up')}>
              ↑
            </button>
            <div className="spacer"></div>
          </div>
          <div className="controls-row">
            <button className="control-button" onClick={() => movePattern('left')}>
              ←
            </button>
            <button className="control-button" onClick={() => movePattern('down')}>
              ↓
            </button>
            <button className="control-button" onClick={() => movePattern('right')}>
              →
            </button>
          </div>
          <div className="controls-row z-controls">
            <button className="control-button" onClick={() => movePattern('forward')}>
              <span className="z-label">Z+</span>
            </button>
            <button className="control-button" onClick={() => movePattern('backward')}>
              <span className="z-label">Z-</span>
            </button>
          </div>
        </div>
      </div>
      
      <div className="marker-detection-controls">
        <button 
          className={`action-button ${markerDetectionEnabled ? 'active' : ''}`} 
          onClick={toggleMarkerDetection}
        >
          {markerDetectionEnabled ? 'Disable Marker Detection' : 'Enable Marker Detection'}
        </button>
        
        <button 
          className={`action-button calibrate ${isCalibrating ? 'active' : ''}`} 
          onClick={calibrateCameras}
          disabled={isCalibrating}
        >
          {isCalibrating ? 'Calibrating...' : 'Calibrate Cameras'}
        </button>
      </div>
    </div>
  );
};

export default CameraContainer;