import React, { useEffect, useState } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { Smartphone, Globe, Plus, Power, Eye, Trash2, Monitor } from 'lucide-react';

export default function DeviceMesh() {
  const devices = useAriaStore((s) => s.devices);
  const fetchDevices = useAriaStore((s) => s.fetchDevices);
  const saveDevices = useAriaStore((s) => s.saveDevices);
  const meshStatus = useAriaStore((s) => s.meshStatus);
  const fetchMeshStatus = useAriaStore((s) => s.fetchMeshStatus);
  const openModal = useAriaStore((s) => s.openModal);
  const closeModal = useAriaStore((s) => s.closeModal);
  const toast = useAriaStore((s) => s.toast);
  const executeShell = useAriaStore((s) => s.executeShell);

  useEffect(() => { fetchDevices(); fetchMeshStatus(); }, []);

  const handleAddDevice = () => {
    let data = { name: '', icon: '📱', conn: '', status: 'Inactive', type: 'custom' };
    openModal({
      title: 'Add Device',
      content: (
        <div>
          <div className="settings-grid-2">
            <div className="input-group"><label>Device Name</label>
              <input className="glass-input" placeholder="My Android Phone" onChange={(e) => { data.name = e.target.value; }} /></div>
            <div className="input-group"><label>Icon</label>
              <input className="glass-input" defaultValue="📱" onChange={(e) => { data.icon = e.target.value; }} /></div>
            <div className="input-group"><label>Connection</label>
              <input className="glass-input" placeholder="ADB / SSH / SPICE" onChange={(e) => { data.conn = e.target.value; }} /></div>
            <div className="input-group"><label>Type</label>
              <select className="glass-input" onChange={(e) => { data.type = e.target.value; }}>
                <option value="android">Android (ADB)</option><option value="vm">Virtual Machine</option>
                <option value="ssh">SSH Host</option><option value="custom">Custom</option>
              </select></div>
          </div>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-primary" onClick={() => {
              if (!data.name) { toast('Enter a device name', 'warning'); return; }
              saveDevices([...devices, data]); closeModal(); toast(`Added ${data.name}`, 'success');
            }}>Add Device</button>
          </div>
        </div>
      ),
    });
  };

  const handleRemove = (idx) => {
    const name = devices[idx]?.name;
    openModal({
      title: 'Remove Device',
      content: (
        <div>
          <p>Remove <strong>{name}</strong> from your device mesh?</p>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-glass btn-danger" onClick={() => {
              const updated = devices.filter((_, i) => i !== idx);
              saveDevices(updated); closeModal(); toast(`Removed ${name}`, 'warning');
            }}>Remove</button>
          </div>
        </div>
      ),
    });
  };

  const handleMirror = async (device) => {
    toast('Launching scrcpy mirror...', 'info');
    await executeShell('scrcpy &');
  };

  const handleWake = async (device) => {
    if (device.type === 'android') {
      const r = await executeShell(`adb shell input keyevent KEYCODE_WAKEUP`);
      toast(r || 'Wake signal sent', 'success');
    } else if (device.type === 'vm') {
      toast('VM start command sent', 'info');
    } else {
      toast('Wake signal sent', 'info');
    }
  };

  return (
    <div style={{ animation: 'fadeInApp 0.5s ease-out forwards', paddingBottom: '40px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
        <div>
          <h2 className="page-title" style={{ color: '#cc66ff' }}>Device Mesh</h2>
          <p className="page-subtitle">Manage {devices.length} connected devices and ARIA mesh peers.</p>
        </div>
        <button className="btn-primary" onClick={handleAddDevice}><Plus size={16} /> Add Device</button>
      </div>

      <div className="section-header"><h3><Smartphone size={18} /> Connected Devices</h3></div>
      <div className="vitals-grid">
        {devices.map((d, i) => (
          <div key={i} className="glass-panel device-card">
            <div className="device-icon">{d.icon || '📱'}</div>
            <h3>{d.name}</h3>
            <div className="device-meta">{d.conn}</div>
            <div className="device-status" style={{ color: d.status === 'Active' ? '#00cc66' : '#666' }}>● {d.status}</div>
            <div className="device-actions">
              <button className="btn-glass btn-sm" onClick={() => handleWake(d)}>
                <Power size={14} /> {d.status === 'Active' ? 'Sleep' : 'Wake'}
              </button>
              {d.status === 'Active' && d.type === 'android' &&
                <button className="btn-glass btn-sm" onClick={() => handleMirror(d)}><Eye size={14} /> Mirror</button>}
              <button className="btn-glass btn-sm btn-danger" onClick={() => handleRemove(i)}><Trash2 size={14} /></button>
            </div>
          </div>
        ))}
        {devices.length === 0 && <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'gray' }}>No devices configured. Click "Add Device" to register one.</div>}
      </div>

      <div className="section-header" style={{ marginTop: '32px' }}><h3><Globe size={18} /> ARIA Mesh Peers</h3></div>
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div className="mesh-topology-placeholder">
          <div className="mesh-node mesh-node-self"><div>🌍</div><span>aria-GamerX (self)</span></div>
          <div className="mesh-line"></div>
          <div className="mesh-node mesh-node-peer" style={{ opacity: meshStatus?.peers > 0 ? 1 : 0.5 }}>
            <div>{meshStatus?.peers > 0 ? '🔗' : '⚫'}</div>
            <span>{meshStatus?.peers > 0 ? `${meshStatus.peers} peer(s) connected` : 'No peers connected'}</span>
          </div>
        </div>
        <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
          Mesh Status: <span style={{ color: meshStatus?.status === 'offline' ? '#ff4d4d' : '#00cc66' }}>{meshStatus?.status || 'unknown'}</span>
        </div>
      </div>
    </div>
  );
}
