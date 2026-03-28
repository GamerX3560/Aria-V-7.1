import React, { useState } from 'react';
import './index.css';

const agentsList = [
  { id: 'desktop', name: 'Desktop GUI Agent', desc: 'Native Wayland automation (ydotool)', icon: '🖥️', active: true, usage: 45 },
  { id: 'research', name: 'Deep Research v4', desc: 'Web crawling, Scrapling bypass', icon: '🔍', active: true, usage: 80 },
  { id: 'voice', name: 'Voice Calling Agent', desc: 'WhatsApp/Telegram Web RTC', icon: '📞', active: false, usage: 0 },
  { id: 'genesis', name: 'Genesis Engine', desc: 'Self-improving code generation', icon: '⚡', active: false, usage: 0 },
  { id: 'memory', name: 'Vector Memory', desc: 'Context retrieval & storage', icon: '🧠', active: true, usage: 20 },
];

function App() {
  const [activeTab, setActiveTab] = useState('agents');
  const [agents, setAgents] = useState(agentsList);

  const toggleAgent = (id) => {
    setAgents(agents.map(a => a.id === id ? { ...a, active: !a.active } : a));
  };

  return (
    <div className="app-container">
      {/* SIDEBAR */}
      <aside className="sidebar glass-panel">
        <div className="logo-area">
          <div className="logo-icon"></div>
          <div className="logo-text">ARIA v5</div>
        </div>
        
        <nav className="nav-menu">
          <div className={`nav-item ${activeTab === 'home' ? 'active' : ''}`} onClick={() => setActiveTab('home')}>🏠 Overview</div>
          <div className={`nav-item ${activeTab === 'agents' ? 'active' : ''}`} onClick={() => setActiveTab('agents')}>🤖 Agents</div>
          <div className={`nav-item ${activeTab === 'config' ? 'active' : ''}`} onClick={() => setActiveTab('config')}>⚙️ Configurator</div>
          <div className={`nav-item ${activeTab === 'memory' ? 'active' : ''}`} onClick={() => setActiveTab('memory')}>🧠 Memory Base</div>
        </nav>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">
        <header className="header">
          <h1>Active Intelligence Nodes</h1>
          <p>Monitor and manage ARIA's autonomous sub-agents and resource distribution.</p>
        </header>

        {activeTab === 'agents' && (
          <div className="agent-grid">
            {agents.map(agent => (
              <div key={agent.id} className="agent-card glass-panel">
                <div className="agent-header">
                  <div className="agent-icon-bg">{agent.icon}</div>
                  <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
                    <div className={`status-dot ${agent.active ? 'active' : ''}`}></div>
                    <div className={`toggle-switch ${agent.active ? 'on' : ''}`} onClick={() => toggleAgent(agent.id)}>
                      <div className="toggle-handle"></div>
                    </div>
                  </div>
                </div>
                <h3 className="agent-title">{agent.name}</h3>
                <p className="agent-desc">{agent.desc}</p>
                <div style={{fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '8px', display: 'flex', justifyContent: 'space-between'}}>
                  <span>Resource Usage</span>
                  <span>{agent.active ? agent.usage + '%' : 'Idle'}</span>
                </div>
                <div className="metrics-bar">
                  <div className="metrics-fill" style={{width: agent.active ? `${agent.usage}%` : '0%'}}></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'config' && (
          <div className="config-layout">
            <div className="config-panel glass-panel">
              <h2>System Identity (YAML)</h2>
              
              <div className="input-group">
                <label>AI Alias</label>
                <input type="text" className="glass-input" defaultValue="ARIA" />
              </div>

              <div className="input-group">
                <label>Assigned Model</label>
                <input type="text" className="glass-input" defaultValue="qwen2.5-coder-32b-instruct" />
              </div>

              <div className="input-group" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                <label style={{marginBottom: 0}}>Strict Mode (Safety Check)</label>
                <div className="toggle-switch on"><div className="toggle-handle"></div></div>
              </div>

              <div className="input-group" style={{marginTop: '24px'}}>
                <label>Core Interests (Tags)</label>
                <div className="pill-container">
                  <div className="pill">⚛️ Quantum UI</div>
                  <div className="pill">🐧 Arch Linux</div>
                  <div className="pill">🛡️ Root Access</div>
                  <div className="pill" style={{borderStyle: 'dashed', opacity: 0.7}}>+ Add New</div>
                </div>
              </div>

              <button style={{
                width: '100%', padding: '12px', marginTop: '20px', borderRadius: '8px',
                background: 'linear-gradient(90deg, var(--neon-primary), var(--neon-secondary))',
                border: 'none', color: 'white', fontWeight: 'bold', cursor: 'pointer'
              }}>
                Save Configuration
              </button>
            </div>

            <div className="config-panel glass-panel">
              <h2>Active Memory & Database</h2>
              <input type="text" className="glass-input" placeholder="🔍 Search memory facts..." style={{marginBottom: '20px'}} />
              
              <div className="memory-list">
                <div className="memory-item">
                  <div>
                    <div className="memory-key">USER_NAME</div>
                    <div className="memory-val">GamerX</div>
                  </div>
                  <button className="btn-delete">×</button>
                </div>
                <div className="memory-item">
                  <div>
                    <div className="memory-key">OS_PREF</div>
                    <div className="memory-val">Arch Linux with Hyprland</div>
                  </div>
                  <button className="btn-delete">×</button>
                </div>
                <div className="memory-item">
                  <div>
                    <div className="memory-key">API_KEY</div>
                    <div className="memory-val">NVIDIA_NIM_...</div>
                  </div>
                  <button className="btn-delete">×</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
