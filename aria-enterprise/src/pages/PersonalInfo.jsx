import React, { useEffect, useState } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { User, Save, Mail, MapPin, Terminal, Key, Shield, ChevronDown, ChevronRight } from 'lucide-react';

function InfoCard({ icon: Icon, label, children, color = 'var(--neon-secondary)', delay = 0 }) {
  return (
    <div className="glass-panel" style={{ padding: '24px', animation: `slideInUp 0.4s ${delay}ms ease-out both` }}>
      <h3 className="section-title"><Icon size={16} style={{ color }} /> {label}</h3>
      {children}
    </div>
  );
}

export default function PersonalInfo() {
  const identity = useAriaStore((s) => s.identity);
  const fetchIdentity = useAriaStore((s) => s.fetchIdentity);
  const saveIdentity = useAriaStore((s) => s.saveIdentity);
  const toast = useAriaStore((s) => s.toast);

  const [name, setName] = useState('');
  const [alias, setAlias] = useState('');
  const [age, setAge] = useState('');
  const [location, setLocation] = useState('');
  const [bio, setBio] = useState('');
  const [os, setOs] = useState('');
  const [shell, setShell] = useState('');
  const [botToken, setBotToken] = useState('');
  const [emails, setEmails] = useState([]);
  const [expandedEmail, setExpandedEmail] = useState(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => { fetchIdentity(); }, []);

  useEffect(() => {
    if (identity && Object.keys(identity).length > 0 && !loaded) {
      setName(identity.name || identity.owner || '');
      setAlias(identity.alias || 'ARIA');
      setAge(identity.age || '');
      setLocation(identity.location || '');
      setBio(identity.bio || '');
      setOs(identity.os || identity.operating_system || '');
      setShell(identity.shell || identity.preferred_shell || '');
      setBotToken(identity.telegram_bot_token || '');
      // Parse emails from identity.yaml
      if (Array.isArray(identity.emails)) {
        setEmails(identity.emails);
      }
      setLoaded(true);
    }
  }, [identity]);

  const handleSave = () => {
    saveIdentity({
      ...identity,
      name, alias, age, location, bio, os, shell,
      telegram_bot_token: botToken,
      emails,
    });
  };

  const purposeColors = {
    primary: '#ff4d4d', youtube: '#ff0000', education: '#ffa64d',
    github: '#fff', gaming: '#00cc66', social: '#cc66ff',
    default: 'var(--text-secondary)',
  };

  return (
    <div style={{ paddingBottom: '40px' }}>
      <div style={{ animation: 'fadeInApp 0.4s ease-out', marginBottom: '24px' }}>
        <h2 className="page-title">Personal Info</h2>
        <p className="page-subtitle">ARIA's identity context — loaded from identity.yaml</p>
      </div>

      {/* Profile Overview */}
      <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px', animation: 'slideInUp 0.4s 0.05s ease-out both' }}>
        <div className="profile-area" style={{ marginBottom: '24px' }}>
          <div className="profile-avatar" style={{ background: 'url("https://api.dicebear.com/7.x/notionists/svg?seed=GamerX") center/cover' }}></div>
          <div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>{name || 'Loading...'}</div>
            <div style={{ color: 'var(--neon-secondary)', fontSize: '0.95rem' }}>aka {alias}</div>
            {bio && <div className="text-muted" style={{ marginTop: '4px' }}>{bio}</div>}
            <div style={{ display: 'flex', gap: '16px', marginTop: '8px', flexWrap: 'wrap' }}>
              {age && <span className="code-tag">Age: {age}</span>}
              {location && <span className="code-tag"><MapPin size={12} style={{ marginRight: '4px' }} />{location}</span>}
              {os && <span className="code-tag"><Terminal size={12} style={{ marginRight: '4px' }} />{os}</span>}
            </div>
          </div>
        </div>

        <div className="settings-grid-2">
          <div className="input-group"><label>Full Name</label>
            <input className="glass-input" value={name} onChange={(e) => setName(e.target.value)} /></div>
          <div className="input-group"><label>AI Alias</label>
            <input className="glass-input" value={alias} onChange={(e) => setAlias(e.target.value)} /></div>
          <div className="input-group"><label>Age</label>
            <input className="glass-input" value={age} onChange={(e) => setAge(e.target.value)} /></div>
          <div className="input-group"><label>Location</label>
            <input className="glass-input" value={location} onChange={(e) => setLocation(e.target.value)} /></div>
          <div className="input-group"><label>Bio</label>
            <input className="glass-input" value={bio} onChange={(e) => setBio(e.target.value)} /></div>
          <div className="input-group"><label>OS</label>
            <input className="glass-input" value={os} onChange={(e) => setOs(e.target.value)} /></div>
          <div className="input-group"><label>Shell</label>
            <input className="glass-input" value={shell} onChange={(e) => setShell(e.target.value)} /></div>
          <div className="input-group"><label>Telegram Bot Token</label>
            <input type="password" className="glass-input" value={botToken} onChange={(e) => setBotToken(e.target.value)} /></div>
        </div>
        <button className="btn-primary" style={{ marginTop: '20px' }} onClick={handleSave}><Save size={16} /> Save Profile</button>
      </div>

      {/* Emails Section */}
      <InfoCard icon={Mail} label={`Email Accounts (${emails.length})`} color="#ffa64d" delay={150}>
        {emails.length === 0 && <div className="text-muted">No emails found in identity.yaml</div>}
        {emails.map((email, i) => (
          <div key={i} className="setting-row" style={{ flexDirection: 'column', alignItems: 'stretch', cursor: 'pointer', marginBottom: '8px' }}
            onClick={() => setExpandedEmail(expandedEmail === i ? null : i)}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Mail size={14} style={{ color: '#ffa64d', flexShrink: 0 }} />
                <span style={{ fontWeight: 600 }}>{email.address || email}</span>
              </div>
              {expandedEmail === i ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
            </div>
            {expandedEmail === i && email.purpose && (
              <div style={{ marginTop: '12px' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
                  {(Array.isArray(email.purpose) ? email.purpose : []).map((p, j) => (
                    <span key={j} className="code-tag" style={{ fontSize: '0.72rem' }}>{p}</span>
                  ))}
                </div>
                {email.notes && <div className="text-muted" style={{ fontSize: '0.82rem' }}>{email.notes}</div>}
              </div>
            )}
          </div>
        ))}
      </InfoCard>

      {/* Raw Identity Data */}
      <div className="glass-panel" style={{ padding: '24px', marginTop: '24px', animation: 'slideInUp 0.4s 0.3s ease-out both' }}>
        <h3 className="section-title"><Key size={16} /> Raw Identity Data</h3>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', lineHeight: 1.6, color: 'var(--text-secondary)', maxHeight: '200px', overflowY: 'auto' }}>
          {Object.entries(identity || {}).filter(([k]) => k !== 'emails' && !k.includes('password') && !k.includes('token')).map(([k, v]) => (
            <div key={k}><span style={{ color: 'var(--neon-secondary)' }}>{k}:</span> {typeof v === 'object' ? JSON.stringify(v).substring(0, 100) : String(v)}</div>
          ))}
        </div>
      </div>
    </div>
  );
}
