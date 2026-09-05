import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

interface Architectural3DProps {
  className?: string;
  variant?: 'compact' | 'hero' | 'floating' | 'dense';
  interactive?: boolean;
}

export const Architectural3D: React.FC<Architectural3DProps> = ({
  className = '',
  variant = 'compact',
  interactive = true,
}) => {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 300;
    const height = container.clientHeight || 300;

    const scene = new THREE.Scene();
    
    const camera = new THREE.PerspectiveCamera(36, width / height, 0.1, 1000);
    camera.position.set(26, 20, 30);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const rootGroup = new THREE.Group();
    scene.add(rootGroup);

    const darkSlabMat = new THREE.MeshStandardMaterial({
      color: 0x0A0D28,
      roughness: 0.8,
      metalness: 0.1,
    });

    const crimsonLineMat = new THREE.LineBasicMaterial({
      color: 0xE63946,
      linewidth: 1.5,
      transparent: true,
      opacity: 0.85,
    });

    const pinkLineMat = new THREE.LineBasicMaterial({
      color: 0xF5A9B8,
      linewidth: 1.2,
      transparent: true,
      opacity: 0.7,
    });

    const gridLineMat = new THREE.LineBasicMaterial({
      color: 0x1C2260,
      linewidth: 1,
      transparent: true,
      opacity: 0.35,
    });

    const gridHelper = new THREE.GridHelper(30, 15, 0xE63946, 0x181F54);
    gridHelper.position.y = -6;
    (gridHelper.material as THREE.Material).transparent = true;
    (gridHelper.material as THREE.Material).opacity = 0.35;
    rootGroup.add(gridHelper);

    const slabsConfig = [
      { w: 14, h: 1.2, d: 14, y: -4.5, rot: 0 },
      { w: 11, h: 1.2, d: 11, y: -2.8, rot: 0.08 },
      { w: 8.5, h: 1.4, d: 8.5, y: -1.0, rot: -0.06 },
      { w: 6.2, h: 2.0, d: 6.2, y: 1.5, rot: 0.12 },
      { w: 3.8, h: 2.8, d: 3.8, y: 4.6, rot: -0.1 },
    ];

    slabsConfig.forEach((cfg, i) => {
      const geom = new THREE.BoxGeometry(cfg.w, cfg.h, cfg.d);
      const mesh = new THREE.Mesh(geom, darkSlabMat);
      mesh.position.y = cfg.y;
      mesh.rotation.y = cfg.rot;

      const edges = new THREE.EdgesGeometry(geom);
      const wire = new THREE.LineSegments(
        edges, 
        i % 2 === 0 ? crimsonLineMat : pinkLineMat
      );
      mesh.add(wire);
      rootGroup.add(mesh);
    });

    const strutGeom = new THREE.BoxGeometry(0.35, 12, 0.35);
    const strutEdges = new THREE.EdgesGeometry(strutGeom);
    
    const positions = [
      [-6, 0.5, -6],
      [6, 0.5, -6],
      [-6, 0.5, 6],
      [6, 0.5, 6],
    ];

    positions.forEach(([x, y, z]) => {
      const strutMesh = new THREE.Mesh(strutGeom, darkSlabMat);
      strutMesh.position.set(x, y, z);
      const wire = new THREE.LineSegments(strutEdges, crimsonLineMat);
      strutMesh.add(wire);
      rootGroup.add(strutMesh);
    });

    const boundingBoxGeom = new THREE.BoxGeometry(16, 14, 16);
    const boundingEdges = new THREE.EdgesGeometry(boundingBoxGeom);
    const boundingWire = new THREE.LineSegments(boundingEdges, gridLineMat);
    boundingWire.position.y = 0.5;
    rootGroup.add(boundingWire);

    const planeGeom = new THREE.PlaneGeometry(16, 16, 4, 4);
    const planeWireGeom = new THREE.WireframeGeometry(planeGeom);
    const scanPlane = new THREE.LineSegments(planeWireGeom, crimsonLineMat);
    scanPlane.rotation.x = Math.PI / 2;
    scanPlane.position.y = 0;
    rootGroup.add(scanPlane);

    const ambientLight = new THREE.AmbientLight(0x222858, 1.4);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xF5A9B8, 0.9);
    dirLight.position.set(20, 30, 20);
    scene.add(dirLight);

    const fillLight = new THREE.DirectionalLight(0xE63946, 0.6);
    fillLight.position.set(-20, -10, -20);
    scene.add(fillLight);

    let targetRotY = 0;
    let targetRotX = 0;
    let currentRotY = 0;
    let currentRotX = 0;

    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive) return;
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width - 0.5;
      const y = (e.clientY - rect.top) / rect.height - 0.5;
      targetRotY = x * 0.6;
      targetRotX = y * 0.35;
    };

    window.addEventListener('mousemove', handleMouseMove);

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    let animationFrameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      currentRotY += (targetRotY - currentRotY) * 0.05;
      currentRotX += (targetRotX - currentRotX) * 0.05;

      rootGroup.rotation.y = elapsed * 0.12 + currentRotY;
      rootGroup.rotation.x = Math.sin(elapsed * 0.25) * 0.03 + currentRotX;

      scanPlane.position.y = Math.sin(elapsed * 1.6) * 5.2;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [interactive, variant]);

  return (
    <div 
      ref={mountRef} 
      className={`relative w-full h-full pointer-events-none select-none ${className}`}
      aria-hidden="true"
    />
  );
};