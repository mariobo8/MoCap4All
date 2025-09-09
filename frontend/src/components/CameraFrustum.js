import React, { useMemo } from 'react';
import * as THREE from 'three';

// Convert degrees to radians for Three.js
const toRadians = (degrees) => degrees * (Math.PI / 180);

const CameraFrustum = ({ position = [0, 0, 0], rotation = [0, 0, 0] }) => {
  // useMemo is a React hook that prevents re-calculating this on every render
  const eulerRotation = useMemo(() => new THREE.Euler(
    toRadians(rotation[0]),
    toRadians(rotation[1]),
    toRadians(rotation[2]),
    'YXZ' // A common rotation order for cameras
  ), [rotation]);

  // We also memoize the geometry so it's not recreated on every render
  const pyramidGeometry = useMemo(() => new THREE.ConeGeometry(0.4, 0.8, 4, 1), []);

  return (
    <group position={position} rotation={eulerRotation}>
      {/*
        THIS IS THE CORRECTED PART:
        The <coneGeometry> is now passed as an argument ('args') to <edgesGeometry>.
        This is the correct way to create a wireframe from a shape.
      */}
      <lineSegments rotation={[-Math.PI / 2, 0, 0]}>
        <edgesGeometry attach="geometry" args={[pyramidGeometry]} />
        <lineBasicMaterial color="white" attach="material" />
      </lineSegments>
    </group>
  );
};

export default CameraFrustum;