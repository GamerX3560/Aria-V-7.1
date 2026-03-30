import React, { useEffect, useState } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { Mic, Play, Smile } from 'lucide-react';

export default function VoicePersonality() {
  const voiceConfig = useAriaStore((s) => s.voiceConfig);
  const fetchVoiceConfig = useAriaStore((s) => s.fetchVoiceConfig);
  const saveVoiceConfig = useAriaStore((s) => s.saveVoiceConfig);
  const testVoice = useAriaStore((s) => s.testVoice);
  const personality = useAriaStore((s) => s.personality);
  const fetchPersonality = useAriaStore((s) => s.fetchPersonality);
  const savePersonality = useAriaStore((s) => s.savePersonality);
  const toast = useAriaStore((s) => s.toast);

  const [voiceBackend, setVoiceBackend] = useState('piper');
  const [speed, setSpeed] = useState(1.0);
  const [pitch, setPitch] = useState(1.0);
  const [formality, setFormality] = useState(50);
  const [verbosity, setVerbosity] = useState(50);
  const [playfulness, setPlayfulness] = useState(50);
  const [testText, setTestText] = useState('Hello, I am ARIA, your autonomous intelligence assistant.');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => { fetchVoiceConfig(); fetchPersonality(); }, []);

  useEffect(() => {
    if (voiceConfig && !loaded) {
      setVoiceBackend(voiceConfig.backend || 'piper');
      setSpeed(parseFloat(voiceConfig.speed) || 1.0);
      setPitch(parseFloat(voiceConfig.pitch) || 1.0);
    }
    if (personality && !loaded) {
      setFormality(personality.formality ?? 50);
      setVerbosity(personality.verbosity ?? 50);
      setPlayfulness(personality.playfulness ?? 50);
      if (voiceConfig || personality) setLoaded(true);
    }
  }, [voiceConfig, personality]);

  const handleSaveVoice = () => { saveVoiceConfig(voiceBackend, String(speed), String(pitch)); };
  const handleSavePersonality = () => { savePersonality(parseInt(formality), parseInt(verbosity), parseInt(playfulness)); };
  const handleTestVoice = () => { testVoice(testText); };

  return (
    <div style={{ animation: 'fadeInApp 0.5s ease-out forwards', paddingBottom: '40px' }}>
      <h2 className="page-title" style={{ color: '#cc66ff' }}>Voice &amp; Personality</h2>
      <p className="page-subtitle">Configure ARIA's voice output and personality traits. Changes persist to identity.yaml.</p>

      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <h3 className="section-title"><Mic size={16} /> Voice Configuration</h3>
        <div className="settings-grid-2">
          <div className="input-group"><label>TTS Backend</label>
            <select className="glass-input" value={voiceBackend} onChange={(e) => setVoiceBackend(e.target.value)}>
              <option value="piper">Piper (Fast, Local)</option><option value="espeak">eSpeak (System Default)</option>
              <option value="coqui">Coqui TTS (Neural)</option><option value="disabled">Disabled</option>
            </select></div>
          <div className="input-group"><label>Voice Profile</label>
            <select className="glass-input"><option>ARIA Default (Female)</option><option>ARIA Male</option><option>Custom ONNX Model</option></select></div>
          <div className="input-group"><label>Speed: {speed.toFixed(1)}x</label>
            <input type="range" min="0.5" max="2.0" step="0.1" value={speed} onChange={(e) => setSpeed(parseFloat(e.target.value))} /></div>
          <div className="input-group"><label>Pitch: {pitch.toFixed(1)}</label>
            <input type="range" min="0.5" max="2.0" step="0.1" value={pitch} onChange={(e) => setPitch(parseFloat(e.target.value))} /></div>
        </div>
        <div style={{ display: 'flex', gap: '12px', marginTop: '16px', alignItems: 'center' }}>
          <input className="glass-input" value={testText} onChange={(e) => setTestText(e.target.value)} style={{ flex: 1 }} placeholder="Enter text to speak..." />
          <button className="btn-glass" onClick={handleTestVoice}><Play size={14} /> Test Voice</button>
          <button className="btn-primary" onClick={handleSaveVoice}>Save Voice Config</button>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 className="section-title"><Smile size={16} /> Personality Tuner</h3>
        <div className="personality-sliders">
          <div className="slider-row"><span>Formal</span>
            <input type="range" min="0" max="100" value={formality} onChange={(e) => setFormality(e.target.value)} />
            <span>Casual</span><span style={{ minWidth: '40px', textAlign: 'right', color: 'var(--neon-secondary)' }}>{formality}</span></div>
          <div className="slider-row"><span>Concise</span>
            <input type="range" min="0" max="100" value={verbosity} onChange={(e) => setVerbosity(e.target.value)} />
            <span>Verbose</span><span style={{ minWidth: '40px', textAlign: 'right', color: 'var(--neon-secondary)' }}>{verbosity}</span></div>
          <div className="slider-row"><span>Serious</span>
            <input type="range" min="0" max="100" value={playfulness} onChange={(e) => setPlayfulness(e.target.value)} />
            <span>Playful</span><span style={{ minWidth: '40px', textAlign: 'right', color: 'var(--neon-secondary)' }}>{playfulness}</span></div>
        </div>
        <button className="btn-primary" style={{ marginTop: '20px' }} onClick={handleSavePersonality}>Save Personality</button>
      </div>
    </div>
  );
}
