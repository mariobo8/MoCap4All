import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

// Define the server URL. Make sure this matches the host and port of your Python backend.
const SERVER_URL = 'http://localhost:5000';

const VideoStream = () => {
  // 'videoFrame' will hold the base64 encoded image string from the backend.
  const [videoFrame, setVideoFrame] = useState('');

  useEffect(() => {
    // 1. Establish a connection to the SocketIO server.
    const socket = io(SERVER_URL);

    // This runs when the component mounts.
    console.log(`Connecting to server at ${SERVER_URL}...`);
    socket.on('connect', () => {
      console.log('Successfully connected to the server!');
    });

    // 2. Set up a listener for the 'video_feed' event.
    // When a message is received on this event, we update our state.
    socket.on('video_feed', (data) => {
      // The data from the backend is an object like { image: "base64string..." }
      setVideoFrame(data.image);
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from the server.');
    });

    // 3. This is a cleanup function.
    // It runs when the component unmounts to prevent memory leaks.
    return () => {
      console.log('Disconnecting socket...');
      socket.disconnect();
    };
  }, []); // The empty array [] means this effect runs only once when the component mounts.

  return (
    <div className="video-container">
      <h2>Live Camera Feed</h2>
      {videoFrame ? (
        // 4. Display the image. The src attribute is formatted for base64 encoded JPEGs.
        <img src={`data:image/jpeg;base64,${videoFrame}`} alt="Live Stream" />
      ) : (
        // Show a message if no frame has been received yet.
        <p>Connecting to video stream...</p>
      )}
    </div>
  );
};

export default VideoStream;