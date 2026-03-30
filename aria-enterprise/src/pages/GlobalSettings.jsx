import React, { useEffect, useState } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { Settings, Brain, Sliders, Save } from 'lucide-react';

export default function GlobalSettings() {
  const config = useAriaStore((s) => s.config);
  const fetchConfig = useAriaStore((s) => s.fetchConfig);
  const saveConfig = useAriaStore((s) => s.saveConfig);
  const toast = useAriaStore((s) => s.toast);

  const [model, setModel] = useState('');
  const [contextLimit, setContextLimit] = useState('128000');
  const [temperature, setTemperature] = useState(0.4);
  const [topP, setTopP] = useState(0.95);
  const [baseUrl, setBaseUrl] = useState('');
  const [selfImprove, setSelfImprove] = useState(false);
  const [overridePrompt, setOverridePrompt] = useState(true);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => { fetchConfig(); }, []);

  useEffect(() => {
    if (config && Object.keys(config).length > 0 && !loaded) {
      setModel(config.model || config.primary_model || 'qwen2.5-coder-32b-instruct');
      setContextLimit(config.context_limit || config.max_tokens || '128000');
      setTemperature(parseFloat(config.temperature) || 0.4);
      setTopP(parseFloat(config.top_p) || 0.95);
      setBaseUrl(config.base_url || '');
      setSelfImprove(config.self_improve === 'true');
      setOverridePrompt(config.override_prompt !== 'false');
      setSystemPrompt(config.system_prompt || '');
      setLoaded(true);
    }
  }, [config]);

  const handleSave = () => {
    saveConfig({
      model, context_limit: contextLimit, temperature: String(temperature),
      top_p: String(topP), base_url: baseUrl, self_improve: String(selfImprove),
      override_prompt: String(overridePrompt), system_prompt: systemPrompt,
    });
  };

  return (
    <div style={{ animation: 'fadeInApp 0.5s ease-out forwards', paddingBottom: '40px' }}>
      <h2 className="page-title">Global Settings</h2>
      <p className="page-subtitle">Configure ARIA's neural engine and behavioral protocols. Reads from config.yaml.</p>

      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <h3 className="section-title"><Brain size={16} /> Neural Engine Configuration</h3>
        <div className="settings-grid-2">
          <div className="input-group"><label>Primary Model</label>
            <input className="glass-input" value={model} onChange={(e) => setModel(e.target.value)} placeholder="qwen2.5-coder-32b-instruct" /></div>
          <div className="input-group"><label>Base URL</label>
            <input className="glass-input" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} placeholder="http://localhost:11434/v1" /></div>
          <div className="input-group"><label>Context Window Limit</label>
            <input type="number" className="glass-input" value={contextLimit} onChange={(e) => setContextLimit(e.target.value)} /></div>
          <div className="input-group"><label>Temperature: {temperature}</label>
            <input type="range" min="0" max="1" step="0.05" value={temperature} onChange={(e) => setTemperature(parseFloat(e.target.value))} />
            <div className="range-labels"><span>Strict</span><span>Creative</span></div></div>
          <div className="input-group"><label>Top P: {topP}</label>
            <input type="range" min="0" max="1" step="0.05" value={topP} onChange={(e) => setTopP(parseFloat(e.target.value))} /></div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <h3 className="section-title"><Sliders size={16} /> Agent Behavioral Protocols</h3>
        <div className="setting-row">
          <div><div className="setting-title">Self-Improving Loop</div>
            <div className="setting-desc">Allow ARIA to upgrade its own scripts without user approval.</div></div>
          <div className={`toggle-switch ${selfImprove ? 'on' : ''}`} onClick={() => setSelfImprove(!selfImprove)}><div className="toggle-handle"></div></div>
        </div>
        <div className="setting-row">
          <div><div className="setting-title">System Override Prompts</div>
            <div className="setting-desc">Inject priority rules into every LLM request.</div></div>
          <div className={`toggle-switch ${overridePrompt ? 'on' : ''}`} onClick={() => setOverridePrompt(!overridePrompt)}><div className="toggle-handle"></div></div>
        </div>
        <div className="input-group" style={{ marginTop: '16px' }}>
          <label>System Prompt</label>
          <textarea className="glass-input" rows="4" value={systemPrompt} onChange={(e) => setSystemPrompt(e.target.value)}
            style={{ resize: 'vertical', width: '100%' }} placeholder="Enter system-level instructions for ARIA..." />
        </div>
      </div>

      <button className="btn-primary" style={{ width: '100%' }} onClick={handleSave}><Save size={16} /> Save All Settings</button>
    </div>
  );
}
