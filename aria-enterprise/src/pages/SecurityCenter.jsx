import React, { useEffect, useState } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { Shield, Lock, AlertTriangle, Plus, X, FolderLock, Globe, Terminal } from 'lucide-react';

export default function SecurityCenter() {
  const securityConfig = useAriaStore((s) => s.securityConfig);
  const fetchSecurityConfig = useAriaStore((s) => s.fetchSecurityConfig);
  const saveSecurityConfig = useAriaStore((s) => s.saveSecurityConfig);
  const toast = useAriaStore((s) => s.toast);

  const [sudoLock, setSudoLock] = useState(false);
  const [confirmMode, setConfirmMode] = useState(true);
  const [networkEgress, setNetworkEgress] = useState(true);
  const [blocklist, setBlocklist] = useState([]);
  const [sandbox, setSandbox] = useState([]);
  const [newRule, setNewRule] = useState('');
  const [newPath, setNewPath] = useState('');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => { fetchSecurityConfig(); }, []);

  useEffect(() => {
    if (securityConfig && !loaded) {
      setSudoLock(securityConfig.sudo_lock ?? false);
      setConfirmMode(securityConfig.confirm_mode ?? true);
      setNetworkEgress(securityConfig.network_egress ?? true);
      setBlocklist(securityConfig.blocklist || []);
      setSandbox(securityConfig.sandbox || []);
      setLoaded(true);
    }
  }, [securityConfig]);

  const saveAll = (overrides = {}) => {
    const data = { sudo_lock: sudoLock, confirm_mode: confirmMode, network_egress: networkEgress, blocklist, sandbox, ...overrides };
    saveSecurityConfig(data);
  };

  const toggleSudo = () => { const v = !sudoLock; setSudoLock(v); saveAll({ sudo_lock: v }); };
  const toggleConfirm = () => { const v = !confirmMode; setConfirmMode(v); saveAll({ confirm_mode: v }); };
  const toggleEgress = () => { const v = !networkEgress; setNetworkEgress(v); saveAll({ network_egress: v }); };

  const addRule = () => {
    if (!newRule) return;
    const updated = [...blocklist, newRule];
    setBlocklist(updated); setNewRule('');
    saveAll({ blocklist: updated });
  };
  const removeRule = (idx) => {
    const updated = blocklist.filter((_, i) => i !== idx);
    setBlocklist(updated); saveAll({ blocklist: updated });
  };
  const addPath = () => {
    if (!newPath) return;
    const updated = [...sandbox, newPath];
    setSandbox(updated); setNewPath('');
    saveAll({ sandbox: updated });
  };
  const removePath = (idx) => {
    const updated = sandbox.filter((_, i) => i !== idx);
    setSandbox(updated); saveAll({ sandbox: updated });
  };

  return (
    <div style={{ animation: 'fadeInApp 0.5s ease-out forwards', paddingBottom: '40px' }}>
      <h2 className="page-title" style={{ color: '#ff4d4d' }}>Security Center</h2>
      <p className="page-subtitle">Execution policies, filesystem sandboxing, and network control. Changes save to security.json.</p>

      <div className="glass-panel" style={{ padding: '24px', border: '1px solid rgba(255,77,77,0.3)', marginBottom: '24px' }}>
        <div className="setting-row">
          <div><div className="setting-title" style={{ color: '#ff4d4d' }}><Lock size={16} /> Global Sudo Execution Lock</div>
            <div className="setting-desc">When enabled, ARIA can run sudo commands. When disabled, all sudo is blocked.</div></div>
          <div className={`toggle-switch ${sudoLock ? 'on' : ''}`} onClick={toggleSudo}><div className="toggle-handle"></div></div>
        </div>
        <div className="setting-row" style={{ marginTop: '16px' }}>
          <div><div className="setting-title"><AlertTriangle size={16} /> Require Confirmation Before Execution</div>
            <div className="setting-desc">ARIA will ask for user approval before running any bash command.</div></div>
          <div className={`toggle-switch ${confirmMode ? 'on' : ''}`} onClick={toggleConfirm}><div className="toggle-handle"></div></div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <h3 className="section-title"><Terminal size={16} /> Bash Command Blocklist (RegEx)</h3>
        <div className="pill-container">
          {blocklist.map((rule, i) => (
            <div key={i} className="pill pill-danger">
              <code>{rule}</code>
              <X size={12} style={{ cursor: 'pointer' }} onClick={() => removeRule(i)} />
            </div>
          ))}
          <div style={{ display: 'flex', gap: '8px' }}>
            <input className="glass-input" placeholder="New regex pattern..." value={newRule}
              onChange={(e) => setNewRule(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addRule()}
              style={{ width: '200px', fontSize: '0.85rem' }} />
            <button className="btn-glass btn-sm" onClick={addRule}><Plus size={14} /> Add</button>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px' }}>
        <h3 className="section-title"><FolderLock size={16} /> Filesystem Sandbox (Allowed Paths)</h3>
        <div className="sandbox-list">
          {sandbox.map((path, i) => (
            <div key={i} className="sandbox-item">
              <code style={{ color: 'var(--neon-secondary)' }}>{path}</code>
              <X size={14} style={{ cursor: 'pointer', color: 'gray' }} onClick={() => removePath(i)} />
            </div>
          ))}
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <input className="glass-input" placeholder="/path/to/allow/*" value={newPath}
              onChange={(e) => setNewPath(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && addPath()}
              style={{ flex: 1, fontSize: '0.85rem' }} />
            <button className="btn-glass btn-sm" onClick={addPath}><Plus size={14} /> Add Path</button>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <h3 className="section-title"><Globe size={16} /> Network Egress Control</h3>
        <div className="setting-row">
          <div><div className="setting-title">Allow All Outbound Connections</div>
            <div className="setting-desc">When off, ARIA can only reach whitelisted domains.</div></div>
          <div className={`toggle-switch ${networkEgress ? 'on' : ''}`} onClick={toggleEgress}><div className="toggle-handle"></div></div>
        </div>
      </div>
    </div>
  );
}
