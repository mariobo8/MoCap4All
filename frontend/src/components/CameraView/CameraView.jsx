// src/components/CameraView/CameraView.jsx
import React, { useEffect, useRef, useState } from 'react';
import './CameraView.css';

const CameraView = ({ cameraId, title, markerDetectionEnabled }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);
  const prevMarkerDetectionEnabled = useRef(markerDetectionEnabled);

  useEffect(() => {
    // Connect to WebSocket for camera feed
    const connectWebSocket = () => {
      const ws = new WebSocket(`ws://localhost:8000/ws/camera/${cameraId}`);
      
      ws.onopen = () => {
        console.log(`Connected to camera ${cameraId} WebSocket`);
        setIsConnected(true);
        setError(null);
        
        // Send current marker detection state if connected
        if (markerDetectionEnabled) {
          sendMarkerDetectionCommand(ws, true);
        }
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'frame') {
          // Draw image on canvas when frame is received
          const canvas = canvasRef.current;
          if (canvas) {
            const ctx = canvas.getContext('2d');
            const img = new Image();
            img.onload = () => {
              ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            };
            img.src = `data:image/jpeg;base64,${data.frame}`;
          }
        } else if (data.type === 'marker_detection_status') {
          console.log(`Marker detection status for camera ${cameraId}:`, data.enabled);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Failed to connect to camera feed');
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log(`Camera ${cameraId} WebSocket closed`);
        setIsConnected(false);
        // Try to reconnect after a delay
        setTimeout(connectWebSocket, 3000);
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    // Cleanup WebSocket connection when component unmounts
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [cameraId]);

  // Effect to handle changes to marker detection state
  useEffect(() => {
    if (wsRef.current && isConnected && prevMarkerDetectionEnabled.current !== markerDetectionEnabled) {
      sendMarkerDetectionCommand(wsRef.current, markerDetectionEnabled);
      prevMarkerDetectionEnabled.current = markerDetectionEnabled;
    }
  }, [markerDetectionEnabled, isConnected]);

  // Function to send marker detection command
  const sendMarkerDetectionCommand = (ws, enable) => {
    // Send via WebSocket if connected
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'toggle_marker_detection',
        enable: enable
      }));
    } else {
      // Fallback to REST API
      fetch(`http://localhost:8000/api/marker-detection/toggle?enable=${enable}`, {
        method: 'POST'
      })
        .then(response => response.json())
        .then(data => console.log('Marker detection toggled via API:', data))
        .catch(err => console.error('Error toggling marker detection via API:', err));
    }
  };

  // Function to send pattern movement commands
  const movePattern = (direction) => {
    // Send via WebSocket if connected
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({
        type: 'move_pattern',
        direction: direction,
        amount: 10
      }));
    } else {
      // Fallback to REST API
      fetch(`http://localhost:8000/api/camera/pattern/move?direction=${direction}&amount=10`, {
        method: 'POST'
      }).catch(err => console.error('Error sending pattern move command:', err));
    }
  };

  return (
    <div className="camera-view">
      <div className="camera-header">
        <h3>{title || `Camera ${cameraId}`}</h3>
        <div className="status-container">
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
          {isConnected && markerDetectionEnabled && (
            <div className="detection-status">
              Marker Detection: Active
            </div>
          )}
        </div>
      </div>
      
      <div className="camera-content">
        {error && <div className="error-message">{error}</div>}
        
        <canvas 
          ref={canvasRef} 
          id={`camera-canvas-${cameraId}`}
          width="640" 
          height="480"
          className="camera-canvas"
        />
        
        {!isConnected && !error && (
          <div className="connecting-overlay">
            <div className="spinner"></div>
            <p>Connecting to camera feed...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CameraView;