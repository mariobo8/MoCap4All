import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import socket from '../socket';
import CameraFrustum from './CameraFrustum';

const ThreeScene = () => {
  const [poses, setPoses] = useState([]);

  useEffect(() => {
    // Listen for pose updates from the backend
    const handlePoseUpdate = (data) => {
      console.log("Received camera poses:", data.poses);
      setPoses(data.poses);
    };
    
    socket.on('camera_poses_update', handlePoseUpdate);

    // --- NEW: Also listen to the main camera status event ---
    // If the success flag is false, it means cameras were disconnected, so we clear the poses.
    const handleCameraStatus = (data) => {
        if (!data.success) {
            setPoses([]);
        }
    };

    socket.on('cameras_initialized_status', handleCameraStatus);

    return () => {
      socket.off('camera_poses_update', handlePoseUpdate);
      socket.off('cameras_initialized_status', handleCameraStatus); // Clean up the new listener
    };
  }, []);

  return (
    <div className="scene-container">
      <h4>3D Scene View</h4>
      <Canvas camera={{ position: [0, 3, 8], fov: 50 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        <Grid infiniteGrid={true} cellSize={1} sectionSize={5} />
        
        {poses.map((pose, index) => (
          <CameraFrustum key={index} position={pose.position} rotation={pose.rotation} />
        ))}

        <OrbitControls />
      </Canvas>
    </div>
  );
};

export default ThreeScene;