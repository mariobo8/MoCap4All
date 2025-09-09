import React, { useState, useEffect } from 'react';
import socket from '../socket'; // Import the centralized socket

const VideoStream = () => {
  const [videoFrame, setVideoFrame] = useState('');

  useEffect(() => {
    socket.on('video_feed', (data) => {
      setVideoFrame(data.image);
    });

    // Clean up listener
    return () => {
      socket.off('video_feed');
    };
  }, []);

  return (
    <div className="video-container">
      <h2>Live Camera Feed</h2>
      {videoFrame ? (
        <img src={`data:image/jpeg;base64,${videoFrame}`} alt="Live Stream" />
      ) : (
        <p>Connecting to video stream...</p>
      )}
    </div>
  );
};

export default VideoStream;