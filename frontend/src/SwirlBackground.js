import React, { useEffect, useRef } from 'react';

// Utility functions
const { PI, cos, sin, abs, random } = Math;
const TAU = 2 * PI;
const rand = n => n * random();
const randRange = n => n - rand(2 * n);
const fadeInOut = (t, m) => {
  let hm = 0.5 * m;
  return abs((t + hm) % m - hm) / (hm);
};
const lerp = (n1, n2, speed) => (1 - speed) * n1 + speed * n2;

const SwirlBackground = () => {
  const containerRef = useRef(null);
  const canvasARef = useRef(null);
  const canvasBRef = useRef(null);
  const ctxARef = useRef(null);
  const ctxBRef = useRef(null);
  
  useEffect(() => {
    // Constants
    const particleCount = 700;
    const particlePropCount = 9;
    const particlePropsLength = particleCount * particlePropCount;
    const rangeY = 100;
    const baseTTL = 50;
    const rangeTTL = 150;
    const baseSpeed = 0.1;
    const rangeSpeed = 2;
    const baseRadius = 1;
    const rangeRadius = 4;
    const baseHue = 220;
    const rangeHue = 100;
    const noiseSteps = 8;
    const xOff = 0.00125;
    const yOff = 0.00125;
    const zOff = 0.0005;
    const backgroundColor = 'hsla(260,40%,5%,1)';

    let center = [];
    let tick = 0;
    let particleProps;

    // Initialize canvases
    const canvasA = canvasARef.current;
    const canvasB = canvasBRef.current;
    const ctxA = canvasA.getContext('2d');
    const ctxB = canvasB.getContext('2d');
    ctxARef.current = ctxA;
    ctxBRef.current = ctxB;

    // Setup SimplexNoise
    const simplex = new SimplexNoise();

    const initParticle = (i) => {
      let x, y, vx, vy, life, ttl, speed, radius, hue;

      x = rand(canvasA.width);
      y = center[1] + randRange(rangeY);
      vx = 0;
      vy = 0;
      life = 0;
      ttl = baseTTL + rand(rangeTTL);
      speed = baseSpeed + rand(rangeSpeed);
      radius = baseRadius + rand(rangeRadius);
      hue = baseHue + rand(rangeHue);

      particleProps.set([x, y, vx, vy, life, ttl, speed, radius, hue], i);
    };

    const drawParticle = (x, y, x2, y2, life, ttl, radius, hue) => {
      ctxA.save();
      ctxA.lineCap = 'round';
      ctxA.lineWidth = radius;
      ctxA.strokeStyle = `hsla(${hue},100%,60%,${fadeInOut(life, ttl)})`;
      ctxA.beginPath();
      ctxA.moveTo(x, y);
      ctxA.lineTo(x2, y2);
      ctxA.stroke();
      ctxA.closePath();
      ctxA.restore();
    };

    const updateParticle = (i) => {
      let i2=1+i, i3=2+i, i4=3+i, i5=4+i, i6=5+i, i7=6+i, i8=7+i, i9=8+i;
      let n, x, y, vx, vy, life, ttl, speed, x2, y2, radius, hue;

      x = particleProps[i];
      y = particleProps[i2];
      n = simplex.noise3D(x * xOff, y * yOff, tick * zOff) * noiseSteps * TAU;
      vx = lerp(particleProps[i3], cos(n), 0.5);
      vy = lerp(particleProps[i4], sin(n), 0.5);
      life = particleProps[i5];
      ttl = particleProps[i6];
      speed = particleProps[i7];
      x2 = x + vx * speed;
      y2 = y + vy * speed;
      radius = particleProps[i8];
      hue = particleProps[i9];

      drawParticle(x, y, x2, y2, life, ttl, radius, hue);

      life++;

      particleProps[i] = x2;
      particleProps[i2] = y2;
      particleProps[i3] = vx;
      particleProps[i4] = vy;
      particleProps[i5] = life;

      (checkBounds(x, y) || life > ttl) && initParticle(i);
    };

    const checkBounds = (x, y) => {
      return (
        x > canvasA.width ||
        x < 0 ||
        y > canvasA.height ||
        y < 0
      );
    };

    const drawParticles = () => {
      for (let i = 0; i < particlePropsLength; i += particlePropCount) {
        updateParticle(i);
      }
    };

    const init = () => {
      tick = 0;
      particleProps = new Float32Array(particlePropsLength);

      for (let i = 0; i < particlePropsLength; i += particlePropCount) {
        initParticle(i);
      }
    };

    const draw = () => {
      tick++;

      ctxA.clearRect(0, 0, canvasA.width, canvasA.height);

      ctxB.fillStyle = backgroundColor;
      ctxB.fillRect(0, 0, canvasA.width, canvasA.height);

      drawParticles();
      renderGlow();
      renderToScreen();

      requestAnimationFrame(draw);
    };

    const renderGlow = () => {
      ctxB.save();
      ctxB.filter = 'blur(8px) brightness(200%)';
      ctxB.globalCompositeOperation = 'lighter';
      ctxB.drawImage(canvasA, 0, 0);
      ctxB.restore();

      ctxB.save();
      ctxB.filter = 'blur(4px) brightness(200%)';
      ctxB.globalCompositeOperation = 'lighter';
      ctxB.drawImage(canvasA, 0, 0);
      ctxB.restore();
    };

    const renderToScreen = () => {
      ctxB.save();
      ctxB.globalCompositeOperation = 'lighter';
      ctxB.drawImage(canvasA, 0, 0);
      ctxB.restore();
    };

    const resize = () => {
      const { innerWidth, innerHeight } = window;
      
      canvasA.width = innerWidth;
      canvasA.height = innerHeight;

      ctxA.drawImage(canvasB, 0, 0);

      canvasB.width = innerWidth;
      canvasB.height = innerHeight;
      
      ctxB.drawImage(canvasA, 0, 0);

      center[0] = 0.5 * canvasA.width;
      center[1] = 0.5 * canvasA.height;
    };

    // Initialize everything
    resize();
    init();
    draw();

    // Event listeners
    window.addEventListener('resize', resize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <div ref={containerRef} className="content--canvas">
      <canvas ref={canvasARef} style={{ display: 'none' }} />
      <canvas
        ref={canvasBRef}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%'
        }}
      />
    </div>
  );
};

export default SwirlBackground;