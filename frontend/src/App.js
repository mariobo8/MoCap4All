import React, { useEffect } from 'react';
import './App.css';
import socket from './socket'; // Import the centralized socket
import VideoStream from './components/VideoStream';
import ControlPanel from './components/ControlPanel';

function App() {
  // Use a useEffect hook to manage the socket connection
  useEffect(() => {
    // Manually connect when the app component mounts
    socket.connect();
    
    // Disconnect when the app component unmounts
    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>MoCap For Robotics Dashboard</h1>
      </header>
      <main>
        <VideoStream />
        <ControlPanel />
      </main>
    </div>
  );
}

export default App;