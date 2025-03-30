// src/App.jsx
import React, { useState } from 'react';
import CameraContainer from './components/CameraView/CameraContainer';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home');
  
  // Render the appropriate component based on currentView
  const renderView = () => {
    switch(currentView) {
      case 'cameras':
        return <CameraContainer />;
      case 'calibration':
        return (
          <div className="placeholder-view">
            <h2>Calibration</h2>
            <p>Camera calibration tools will be available here.</p>
          </div>
        );
      case 'recordings':
        return (
          <div className="placeholder-view">
            <h2>Recordings</h2>
            <p>Your motion capture recordings will be listed here.</p>
          </div>
        );
      case 'settings':
        return (
          <div className="placeholder-view">
            <h2>Settings</h2>
            <p>Configure your motion capture system settings here.</p>
          </div>
        );
      default:
        return (
          <div className="welcome-container">
            <h2>Welcome to MoCap4All</h2>
            <p>A motion capture system designed specifically for robotics applications.</p>
            <div className="feature-list">
              <div className="feature-item">
                <h3>Multi-Camera Support</h3>
                <p>Capture motion from multiple angles for precise tracking</p>
              </div>
              <div className="feature-item">
                <h3>Real-time Visualization</h3>
                <p>View captured motion data as it happens</p>
              </div>
              <div className="feature-item">
                <h3>Robotics Integration</h3>
                <p>Export motion data in formats compatible with robotics systems</p>
              </div>
            </div>
            <button 
              className="start-button"
              onClick={() => setCurrentView('cameras')}
            >
              Get Started
            </button>
          </div>
        );
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>MoCap4All</h1>
        <p>Motion Capture System for Robotics</p>
      </header>
      
      <div className="app-content">
        <nav className="app-nav">
          <ul>
            <li>
              <a 
                href="#" 
                className={currentView === 'home' ? 'active' : ''}
                onClick={(e) => {e.preventDefault(); setCurrentView('home');}}
              >
                Dashboard
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={currentView === 'cameras' ? 'active' : ''}
                onClick={(e) => {e.preventDefault(); setCurrentView('cameras');}}
              >
                Camera Views
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={currentView === 'calibration' ? 'active' : ''}
                onClick={(e) => {e.preventDefault(); setCurrentView('calibration');}}
              >
                Calibration
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={currentView === 'recordings' ? 'active' : ''}
                onClick={(e) => {e.preventDefault(); setCurrentView('recordings');}}
              >
                Recordings
              </a>
            </li>
            <li>
              <a 
                href="#" 
                className={currentView === 'settings' ? 'active' : ''}
                onClick={(e) => {e.preventDefault(); setCurrentView('settings');}}
              >
                Settings
              </a>
            </li>
          </ul>
        </nav>
        
        <main className="app-main">
          {renderView()}
        </main>
      </div>
    </div>
  );
}

export default App;