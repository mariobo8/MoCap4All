// src/components/CameraView/CameraContainer.jsx
import React from 'react';
import CameraView from './CameraView';
import './CameraContainer.css';

const CameraContainer = () => {
  // Function to send pattern movement commands via API
  const movePattern = (direction) => {
    fetch(`http://localhost:8000/api/camera/pattern/move?direction=${direction}&amount=10`, {
      method: 'POST'
    })
      .then(response => response.json())
      .then(data => console.log('Pattern moved:', data))
      .catch(err => console.error('Error sending pattern move command:', err));
  };

  return (
    <div className="camera-container">
      <h2 className="camera-container-title">Motion Capture Camera Feeds</h2>
      
      <div className="camera-grid">
        <div className="camera-grid-item">
          <CameraView cameraId="1" title="Camera 1 - Front View" />
        </div>
        <div className="camera-grid-item">
          <CameraView cameraId="2" title="Camera 2 - Side View" />
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
    </div>
  );
};

export default CameraContainer;