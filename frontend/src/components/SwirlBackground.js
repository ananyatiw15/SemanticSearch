import React, { useEffect, useRef } from "react";
import { createNoise2D } from "simplex-noise";

const SwirlBackground = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const noise2D = createNoise2D();

    let width, height;
    let particles = [];

    const resizeCanvas = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
      createParticles();
    };

    const createParticles = () => {
      particles = Array.from({ length: 500 }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * 3 + 1,
        speed: Math.random() * 1.5 + 0.3,
        life: Math.random() * 200 + 100,
        hue: 220 + Math.random() * 60,
      }));
    };

    const drawParticles = () => {
      ctx.clearRect(0, 0, width, height);
      particles.forEach((p) => {
        const angle = noise2D(p.x * 0.002, p.y * 0.002) * Math.PI * 2;
        p.x += Math.cos(angle) * p.speed;
        p.y += Math.sin(angle) * p.speed;
        p.life -= 1;

        if (p.life <= 0 || p.x > width || p.x < 0 || p.y > height || p.y < 0) {
          p.x = Math.random() * width;
          p.y = Math.random() * height;
          p.life = Math.random() * 200 + 100;
        }

        ctx.fillStyle = `hsla(${p.hue}, 100%, 85%, 0.6)`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      });

      requestAnimationFrame(drawParticles);
    };

    resizeCanvas();
    drawParticles();

    window.addEventListener("resize", resizeCanvas);
    return () => window.removeEventListener("resize", resizeCanvas);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full z-[-10] pointer-events-none
                 bg-gradient-to-br from-[#0a0f1f] to-[#121826]"
    />
  );
};

export default SwirlBackground;
