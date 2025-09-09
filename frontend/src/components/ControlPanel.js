import React, { useState, useEffect } from 'react';
import socket from '../socket';
import './Controls.css';

const ControlPanel = () => {
  const [status, setStatus] = useState('Connecting...');
  const [isDetecting, setIsDetecting] = useState(false);
  
  // States for sliders
  const [exposure, setExposure] = useState(100);
  const [gain, setGain] = useState(10);
  const [threshold, setThreshold] = useState(200);

  useEffect(() => {
    socket.on('status_update', (data) => {
      setStatus(data.status);
    });
    return () => {
      socket.off('status_update');
    };
  }, []);

  const handleToggleDetection = () => {
    const newIsDetecting = !isDetecting;
    setIsDetecting(newIsDetecting);
    socket.emit('toggle_detection', { value: newIsDetecting });
  };

  const handleCameraSettingChange = (newExposure, newGain) => {
    setExposure(newExposure);
    setGain(newGain);
    socket.emit('update_camera_settings', { exposure: newExposure, gain: newGain });
  };

  const handleThresholdChange = (event) => {
    const newThreshold = event.target.value;
    setThreshold(newThreshold);
    socket.emit('update_threshold', { value: newThreshold });
  };

  return (
    <div className="control-panel">
      <div className="status-indicator">
        <h3>STATUS: <span>{status}</span></h3>
      </div>

      <div className="panel-section">
        <h4>Live Tracking</h4>
        <button onClick={handleToggleDetection} className={`control-button ${isDetecting ? 'active' : ''}`}>
          {isDetecting ? 'Stop Detection' : 'Start Detection'}
        </button>
      </div>
      
      {/* The Calibration panel section has been removed */}
      
      <div className="panel-section">
        <h4>Camera Settings</h4>
        <div className="control-item">
          <label htmlFor="exposure">Exposure: {exposure}</label>
          <input id="exposure" type="range" min="0" max="255" value={exposure} onChange={(e) => handleCameraSettingChange(e.target.value, gain)} />
        </div>
        <div className="control-item">
          <label htmlFor="gain">Gain: {gain}</label>
          <input id="gain" type="range" min="0" max="63" value={gain} onChange={(e) => handleCameraSettingChange(exposure, e.target.value)} />
        </div>
        <div className="control-item">
          <label htmlFor="threshold">Dot Threshold: {threshold}</label>
          <input id="threshold" type="range" min="0" max="255" value={threshold} onChange={handleThresholdChange} />
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;