import React, { useEffect } from 'react';
import './App.css';
import socket from './socket';
import VideoStream from './components/VideoStream';
import ControlPanel from './components/ControlPanel';
import ThreeScene from './components/ThreeScene'; // Keep the import here

function App() {
  useEffect(() => {
    socket.connect();
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
        {/* --- NEW: A dedicated column for visual components --- */}
        <div className="main-content-area">
          <VideoStream />
          <ThreeScene />
        </div>
        {/* The control panel is now a sibling, acting as the right column */}
        <ControlPanel />
      </main>
    </div>
  );
}

export default App;