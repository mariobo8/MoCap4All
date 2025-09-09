import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import './Controls.css'; 

const SERVER_URL = 'http://localhost:5000';

const VideoStream = () => {
  const [videoFrame, setVideoFrame] = useState('');
  // --- NEW: Add state for all our controls ---
  const [threshold, setThreshold] = useState(200);
  const [exposure, setExposure] = useState(100);
  const [gain, setGain] = useState(10);
  const [isDetecting, setIsDetecting] = useState(false);

  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = io(SERVER_URL);
    const socket = socketRef.current;

    socket.on('connect', () => console.log('Successfully connected to the server!'));
    socket.on('video_feed', (data) => setVideoFrame(data.image));
    socket.on('disconnect', () => console.log('Disconnected from the server.'));

    return () => {
      console.log('Disconnecting socket...');
      socket.disconnect();
    };
  }, []);

  const handleThresholdChange = (event) => {
    const newThreshold = event.target.value;
    setThreshold(newThreshold);
    socketRef.current.emit('update_threshold', { value: newThreshold });
  };
  
  // --- NEW: Handler for Exposure and Gain sliders ---
  // We'll update them together in one event
  const handleCameraSettingChange = (newExposure, newGain) => {
    setExposure(newExposure);
    setGain(newGain);
    socketRef.current.emit('update_camera_settings', { exposure: newExposure, gain: newGain });
  };
  
  // --- NEW: Handler for the detection toggle button ---
  const handleToggleDetection = () => {
    const newIsDetecting = !isDetecting;
    setIsDetecting(newIsDetecting);
    socketRef.current.emit('toggle_detection', { value: newIsDetecting });
  };

  return (
    <div className="video-container">
      <h2>Live Camera Feed</h2>
      {videoFrame ? (
        <img src={`data:image/jpeg;base64,${videoFrame}`} alt="Live Stream" />
      ) : (
        <p>Connecting to video stream...</p>
      )}

      <div className="controls-panel">
        {/* --- NEW: Detection Toggle Button --- */}
        <div className="control-item full-width">
           <button onClick={handleToggleDetection} className={`control-button ${isDetecting ? 'active' : ''}`}>
             {isDetecting ? 'Stop Detection' : 'Start Detection'}
           </button>
        </div>

        {/* --- NEW: Camera Settings Sliders --- */}
        <div className="control-item">
          <label htmlFor="exposure">Exposure: {exposure}</label>
          <input
            id="exposure"
            type="range"
            min="0"
            max="255"
            step="1"
            value={exposure}
            onChange={(e) => handleCameraSettingChange(e.target.value, gain)}
          />
        </div>
        <div className="control-item">
          <label htmlFor="gain">Gain: {gain}</label>
          <input
            id="gain"
            type="range"
            min="0"
            max="63" // Max gain for PS Eye camera
            step="1"
            value={gain}
            onChange={(e) => handleCameraSettingChange(exposure, e.target.value)}
          />
        </div>
        
        {/* Detection Threshold Slider */}
        <div className="control-item">
          <label htmlFor="threshold">Dot Threshold: {threshold}</label>
          <input
            id="threshold"
            type="range"
            min="0"
            max="255"
            value={threshold}
            onChange={handleThresholdChange}
          />
        </div>
      </div>
    </div>
  );
};

export default VideoStream;