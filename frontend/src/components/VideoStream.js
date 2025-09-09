import React, { useState, useEffect } from 'react';
import socket from '../socket'; // Import the centralized socket

const VideoStream = () => {
  const [videoFrame, setVideoFrame] = useState('');
  // --- NEW: State to manage the collapsed/expanded view ---
  const [isCollapsed, setIsCollapsed] = useState(false); // false = open by default

  useEffect(() => {
    socket.on('video_feed', (data) => {
      setVideoFrame(data.image);
    });

    return () => {
      socket.off('video_feed');
    };
  }, []);

  // --- NEW: Handler to toggle the collapsed state ---
  const handleToggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    // Add a 'collapsed' class to the container when the state is true
    <div className={`video-container ${isCollapsed ? 'collapsed' : ''}`}>
      {/* --- NEW: A header to hold the title and the toggle button --- */}
      <div className="panel-header">
        <h2>Live Camera Feed</h2>
        <button onClick={handleToggleCollapse} className="collapse-button">
          {isCollapsed ? '+' : '−'}
        </button>
      </div>
      
      {/* --- MODIFIED: Conditionally render the content --- */}
      {!isCollapsed && (
        <div className="video-content">
          {videoFrame ? (
            <img src={`data:image/jpeg;base64,${videoFrame}`} alt="Live Stream" />
          ) : (
            <p>Connecting to video stream...</p>
          )}
        </div>
      )}
    </div>
  );
};

export default VideoStream;