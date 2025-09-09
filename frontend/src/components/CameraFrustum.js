import React from 'react';
import * as THREE from 'three';

// Convert degrees to radians for Three.js
const toRadians = (degrees) => degrees * (Math.PI / 180);

const CameraFrustum = ({ position = [0, 0, 0], rotation = [0, 0, 0] }) => {
  // Create a group to hold the camera model, so we can easily position/rotate it
  const eulerRotation = new THREE.Euler(
    toRadians(rotation[0]),
    toRadians(rotation[1]),
    toRadians(rotation[2]),
    'YXZ' // A common rotation order for cameras
  );

  return (
    <group position={position} rotation={eulerRotation}>
      {/* Camera Body */}
      <mesh>
        <boxGeometry args={[0.1, 0.1, 0.2]} />
        <meshStandardMaterial color="darkgrey" />
      </mesh>
      
      {/* Lens */}
      <mesh position={[0, 0, 0.1]}>
         <cylinderGeometry args={[0.05, 0.05, 0.05, 16]} />
         <meshStandardMaterial color="black" />
      </mesh>

      {/* Frustum (the camera's field of view) */}
      <lineSegments>
        <edgesGeometry>
            {/* A pyramid shape */}
            <coneGeometry args={[0.4, 0.8, 4, 1]} />
        </edgesGeometry>
        <lineBasicMaterial color="white" />
      </lineSegments>
    </group>
  );
};

export default CameraFrustum;