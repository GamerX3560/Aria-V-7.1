import React, { useEffect, useState } from 'react';

const BOOT_LINES = [
  '▸ Initializing ARIA Neural Core...',
  '▸ Loading identity matrix...',
  '▸ Connecting to LLM inference engine...',
  '▸ Mounting skill modules (30+)...',
  '▸ Establishing Telegram bridge...',
  '▸ Starting browser automation stack...',
  '▸ Syncing memory bank...',
  '▸ Calibrating personality vectors...',
  '▸ All systems nominal. Welcome, Commander.',
];

export default function SplashScreen({ onFinish }) {
  const [visibleLines, setVisibleLines] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    const lineTimers = BOOT_LINES.map((_, i) =>
      setTimeout(() => setVisibleLines(i + 1), 200 + i * 250)
    );
    const fadeTimer = setTimeout(() => setFadeOut(true), 200 + BOOT_LINES.length * 250 + 400);
    const finishTimer = setTimeout(onFinish, 200 + BOOT_LINES.length * 250 + 900);
    return () => { lineTimers.forEach(clearTimeout); clearTimeout(fadeTimer); clearTimeout(finishTimer); };
  }, [onFinish]);

  return (
    <div className={`splash-screen-v2 ${fadeOut ? 'fade-out' : ''}`} data-tauri-drag-region>
      <div className="splash-particles">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="splash-particle" style={{
            left: `${Math.random() * 100}%`, top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 3}s`, animationDuration: `${3 + Math.random() * 4}s`,
          }} />
        ))}
      </div>
      <div className="splash-content-v2">
        <div className="splash-logo-container">
          <img src="/aria-logo.png" alt="ARIA" className="splash-logo-img" />
          <div className="splash-logo-glow" />
        </div>
        <div className="splash-brand">ARIA</div>
        <div className="splash-version">Enterprise Manager v8.1</div>
        <div className="splash-boot-log">
          {BOOT_LINES.slice(0, visibleLines).map((line, i) => (
            <div key={i} className="splash-boot-line" style={{ animationDelay: `${i * 0.05}s` }}>
              {line}
            </div>
          ))}
          {visibleLines < BOOT_LINES.length && <span className="cursor-blink" />}
        </div>
      </div>
    </div>
  );
}
