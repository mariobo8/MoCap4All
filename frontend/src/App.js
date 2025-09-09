import React from 'react';
import './App.css';
import VideoStream from './components/VideoStream'; // Import our new component

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>MoCap For Robotics Dashboard</h1>
      </header>
      <main>
        <VideoStream />
      </main>
    </div>
  );
}

export default App;