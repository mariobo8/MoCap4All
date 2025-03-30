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
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>MoCap4All</h1>
      </header>
      
      <div className="app-content">
        <nav className="app-nav">
          <ul>
            <li>
              <a 
                href="#" 
                className={currentView === 'cameras' ? 'active' : ''}
                onClick={(e) => {e.preventDefault(); setCurrentView('cameras');}}
              >
                Camera Views
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