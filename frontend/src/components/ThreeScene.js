import React, { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
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

    // If cameras are disconnected, clear the poses from the scene
    const handleCameraStatus = (data) => {
        if (!data.success) {
            setPoses([]);
        }
    };

    socket.on('cameras_initialized_status', handleCameraStatus);

    return () => {
      socket.off('camera_poses_update', handlePoseUpdate);
      socket.off('cameras_initialized_status', handleCameraStatus);
    };
  }, []);

  // --- NEW: Define constants for our custom axes ---
  const AXIS_LENGTH = 1;
  const AXIS_THICKNESS = 0.035;

  return (
    <div className="scene-container">
      <h4>3D Scene View</h4>
      <Canvas 
        camera={{ 
          position: [10, -10, 8], 
          fov: 50,
          up: [0, 0, 1] 
        }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        
        <gridHelper 
          args={[30, 30]} 
          rotation={[-Math.PI / 2, 0, 0]} 
        />

        {/* --- REPLACED axesHelper WITH THICKER MESHES --- */}
        {/* X-axis (Red) */}
        <mesh position={[AXIS_LENGTH / 2, 0, 0]}>
          <boxGeometry args={[AXIS_LENGTH, AXIS_THICKNESS, AXIS_THICKNESS]} />
          <meshStandardMaterial color="red" />
        </mesh>
        {/* Y-axis (Green) */}
        <mesh position={[0, AXIS_LENGTH / 2, 0]}>
          <boxGeometry args={[AXIS_THICKNESS, AXIS_LENGTH, AXIS_THICKNESS]} />
          <meshStandardMaterial color="green" />
        </mesh>
        {/* Z-axis (Blue) */}
        <mesh position={[0, 0, AXIS_LENGTH / 2]}>
          <boxGeometry args={[AXIS_THICKNESS, AXIS_THICKNESS, AXIS_LENGTH]} />
          <meshStandardMaterial color="blue" />
        </mesh>
        
        {poses.map((pose, index) => (
          <CameraFrustum key={index} position={pose.position} rotation={pose.rotation} />
        ))}

        <OrbitControls />
      </Canvas>
    </div>
  );
};

export default ThreeScene;