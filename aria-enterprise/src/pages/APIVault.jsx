import React, { useEffect, useState } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { KeyRound, Plus, Eye, EyeOff, Trash2, Edit3, Clock, Shield, RefreshCw, Search, AlertCircle } from 'lucide-react';

export default function APIVault() {
  const credentials = useAriaStore((s) => s.credentials);
  const fetchCredentials = useAriaStore((s) => s.fetchCredentials);
  const saveCredentials = useAriaStore((s) => s.saveCredentials);
  const openModal = useAriaStore((s) => s.openModal);
  const closeModal = useAriaStore((s) => s.closeModal);
  const toast = useAriaStore((s) => s.toast);
  const executeShell = useAriaStore((s) => s.executeShell);
  const [showKey, setShowKey] = useState({});
  const [search, setSearch] = useState('');
  const [allCreds, setAllCreds] = useState([]);

  useEffect(() => { fetchCredentials(); scanForApiKeys(); }, []);

  // Scan for API keys across ARIA's codebase
  const scanForApiKeys = async () => {
    try {
      const result = await executeShell(`grep -roPhI '(nvapi-[A-Za-z0-9_-]+|AIza[A-Za-z0-9_-]+|GOCSPX-[A-Za-z0-9_-]+|sk-[A-Za-z0-9_-]{20,})' ~/aria/skills/ ~/aria/config.yaml ~/aria/.env 2>/dev/null | sort -u | head -20`);
      if (result) {
        const keys = result.split('\n').filter(Boolean);
        const found = keys.map(line => {
          const parts = line.split(':');
          const file = parts[0] || 'unknown';
          const key = parts.slice(1).join(':').trim();
          let service = 'Unknown';
          if (key.startsWith('nvapi-')) service = 'NVIDIA NIM';
          else if (key.startsWith('AIza')) service = 'Google';
          else if (key.startsWith('GOCSPX-')) service = 'Google OAuth';
          else if (key.startsWith('sk-')) service = 'OpenAI';
          return { name: `${service}_key`, value: key, service, source: file.split('/').pop(), used: 'Detected in code' };
        });
        setAllCreds(prev => [...prev, ...found]);
      }
    } catch (e) { /* silently fail */ }
  };

  useEffect(() => {
    // Parse vault/credentials.json
    const fromVault = [];
    if (credentials && typeof credentials === 'object') {
      // Handle the nested "installed" format from Google OAuth
      Object.entries(credentials).forEach(([k, v]) => {
        if (typeof v === 'object' && v !== null) {
          if (v.client_id) {
            fromVault.push({ name: 'Google OAuth Client ID', value: v.client_id, service: 'Google Cloud', used: 'OAuth flow', source: 'credentials.json' });
            fromVault.push({ name: 'Google OAuth Client Secret', value: v.client_secret, service: 'Google Cloud', used: 'OAuth flow', source: 'credentials.json' });
            fromVault.push({ name: 'Google Project ID', value: v.project_id, service: 'Google Cloud', used: 'Project config', source: 'credentials.json' });
          } else if (v.value) {
            fromVault.push({ name: k, value: v.value, service: v.service || k, used: v.used || 'Unknown', source: 'credentials.json' });
          } else {
            fromVault.push({ name: k, value: JSON.stringify(v).substring(0, 80) + '...', service: k, used: 'Unknown', source: 'credentials.json' });
          }
        } else {
          fromVault.push({ name: k, value: String(v), service: k, used: 'Unknown', source: 'credentials.json' });
        }
      });
    }
    setAllCreds(prev => {
      // Merge: vault first, then scanned (deduplicated)
      const existing = new Set(fromVault.map(c => c.value));
      const scanned = prev.filter(c => !existing.has(c.value));
      return [...fromVault, ...scanned];
    });
  }, [credentials]);

  const maskValue = (v) => {
    if (!v || v.length < 8) return '••••••••';
    return v.substring(0, 6) + '•'.repeat(Math.min(8, v.length - 10)) + v.substring(v.length - 4);
  };

  const filtered = allCreds.filter(c =>
    !search || c.name.toLowerCase().includes(search.toLowerCase()) || c.service.toLowerCase().includes(search.toLowerCase())
  );

  const handleAdd = () => {
    let newCred = { name: '', value: '', service: '' };
    openModal({
      title: 'Add Credential',
      content: (
        <div>
          <div className="input-group"><label>Key Name</label>
            <input className="glass-input" placeholder="MY_API_KEY" onChange={(e) => { newCred.name = e.target.value; }} /></div>
          <div className="input-group"><label>Service</label>
            <input className="glass-input" placeholder="NVIDIA / Google / Custom" onChange={(e) => { newCred.service = e.target.value; }} /></div>
          <div className="input-group"><label>Secret Value</label>
            <input type="password" className="glass-input" placeholder="Enter API key..." onChange={(e) => { newCred.value = e.target.value; }} /></div>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-primary" onClick={() => {
              if (!newCred.name || !newCred.value) { toast('Name and value required', 'warning'); return; }
              const updated = { ...credentials };
              updated[newCred.name] = { value: newCred.value, service: newCred.service, used: 'Just added' };
              saveCredentials(updated); closeModal();
            }}>Save Credential</button>
          </div>
        </div>
      ),
    });
  };

  const handleDelete = (name) => {
    openModal({
      title: 'Delete Credential',
      content: (
        <div>
          <p>Remove <strong>{name}</strong> from the vault?</p>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-glass btn-danger" onClick={() => {
              const updated = { ...credentials };
              delete updated[name];
              saveCredentials(updated); closeModal();
            }}>Delete</button>
          </div>
        </div>
      ),
    });
  };

  return (
    <div style={{ paddingBottom: '40px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px', animation: 'fadeInApp 0.4s ease-out' }}>
        <div>
          <h2 className="page-title">API Vault</h2>
          <p className="page-subtitle">Discovered {filtered.length} credentials from vault, config, and skills scripts.</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn-glass" onClick={() => { scanForApiKeys(); toast('Rescanning codebase...', 'info'); }}><RefreshCw size={14} /> Rescan</button>
          <button className="btn-primary" onClick={handleAdd}><Plus size={16} /> Add Credential</button>
        </div>
      </div>

      <div style={{ marginBottom: '16px', animation: 'slideInUp 0.4s 0.1s ease-out both' }}>
        <div className="search-input-wrapper" style={{ maxWidth: '400px' }}>
          <Search size={16} />
          <input className="glass-input" placeholder="Search credentials..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ flex: 1 }} />
        </div>
      </div>

      <div className="glass-panel" style={{ padding: 0, animation: 'slideInUp 0.4s 0.15s ease-out both' }}>
        <table className="data-table">
          <thead><tr><th>Key Name</th><th>Service</th><th>Source</th><th style={{ maxWidth: '280px' }}>Value</th><th style={{ textAlign: 'right' }}>Actions</th></tr></thead>
          <tbody>
            {filtered.map((cred, idx) => (
              <tr key={idx} style={{ animation: `slideInUp 0.3s ${idx * 30}ms ease-out both` }}>
                <td style={{ fontWeight: 600, color: 'var(--neon-secondary)' }}>{cred.name}</td>
                <td><span className="code-tag">{cred.service}</span></td>
                <td className="text-muted" style={{ fontSize: '0.82rem' }}>{cred.source || '-'}</td>
                <td style={{ maxWidth: '280px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <code style={{
                      color: '#00ffcc', fontSize: '0.78rem',
                      overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                      maxWidth: '240px', display: 'inline-block'
                    }}>
                      {showKey[idx] ? cred.value : maskValue(cred.value)}
                    </code>
                    <button className="btn-icon" onClick={() => setShowKey({ ...showKey, [idx]: !showKey[idx] })} title={showKey[idx] ? 'Hide' : 'Show'}>
                      {showKey[idx] ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                  </div>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                    <button className="btn-glass btn-sm" onClick={() => {
                      navigator.clipboard.writeText(cred.value);
                      toast('Copied to clipboard', 'success');
                    }}>Copy</button>
                    <button className="btn-glass btn-sm btn-danger" onClick={() => handleDelete(cred.name)}><Trash2 size={12} /></button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && <tr><td colSpan={5} style={{ textAlign: 'center', padding: '40px', color: 'gray' }}>No credentials found.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
