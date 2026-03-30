import React, { useEffect, useState } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { Bot, Plus, Settings, Trash2 } from 'lucide-react';

function AgentCard({ agent, onConfigure, onKill }) {
  const statusColor = agent.status === 'ONLINE' ? '#00cc66' : agent.status === 'STANDBY' ? '#ffa64d' : '#666';
  return (
    <div className="glass-panel agent-card-v2">
      <div className="agent-card-header">
        <div className="agent-icon-lg">{agent.icon || '🤖'}</div>
        <div className="agent-status-badge" style={{ color: statusColor }}>
          <div className="status-dot-sm" style={{ background: statusColor }}></div>
          {agent.status}
        </div>
      </div>
      <h3 className="agent-card-name">{agent.name}</h3>
      <div className="agent-card-meta">
        <span>Model: <em>{agent.model}</em></span>
        <span>Role: {agent.role}</span>
      </div>
      <div className="agent-card-actions">
        <button className="btn-glass" onClick={() => onConfigure(agent)}><Settings size={14} /> Configure</button>
        <button className="btn-glass btn-danger" onClick={() => onKill(agent.id)}><Trash2 size={14} /> Kill</button>
      </div>
    </div>
  );
}

export default function AgentFoundry() {
  const agents = useAriaStore((s) => s.agents);
  const fetchAgents = useAriaStore((s) => s.fetchAgents);
  const createAgent = useAriaStore((s) => s.createAgent);
  const deleteAgent = useAriaStore((s) => s.deleteAgent);
  const updateAgent = useAriaStore((s) => s.updateAgent);
  const openModal = useAriaStore((s) => s.openModal);
  const closeModal = useAriaStore((s) => s.closeModal);
  const toast = useAriaStore((s) => s.toast);

  useEffect(() => { fetchAgents(); }, []);

  const handleCreate = () => {
    let data = { id: `agent_${Date.now()}`, name: '', model: '', role: '', icon: '🤖', status: 'STANDBY', systemPrompt: '' };
    openModal({
      title: 'Compile New Agent',
      content: (
        <div>
          <div className="settings-grid-2">
            <div className="input-group">
              <label>Agent Name</label>
              <input className="glass-input" placeholder="My Custom Agent" onChange={(e) => { data.name = e.target.value; }} />
            </div>
            <div className="input-group">
              <label>Icon (Emoji)</label>
              <input className="glass-input" placeholder="🤖" defaultValue="🤖" onChange={(e) => { data.icon = e.target.value; }} />
            </div>
            <div className="input-group">
              <label>Model / Engine</label>
              <input className="glass-input" placeholder="qwen2.5-coder-32b" onChange={(e) => { data.model = e.target.value; }} />
            </div>
            <div className="input-group">
              <label>Role</label>
              <input className="glass-input" placeholder="Research Specialist" onChange={(e) => { data.role = e.target.value; }} />
            </div>
          </div>
          <div className="input-group" style={{ marginTop: '12px' }}>
            <label>System Prompt</label>
            <textarea className="glass-input" rows={4} placeholder="You are a specialized agent that..." onChange={(e) => { data.systemPrompt = e.target.value; }} />
          </div>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-primary" onClick={() => {
              if (!data.name) { toast('Enter an agent name', 'warning'); return; }
              createAgent(data); closeModal();
            }}>Compile Agent</button>
          </div>
        </div>
      ),
    });
  };

  const handleConfigure = (agent) => {
    let updates = { ...agent };
    openModal({
      title: `Configure: ${agent.name}`,
      content: (
        <div>
          <div className="settings-grid-2">
            <div className="input-group">
              <label>Agent Name</label>
              <input className="glass-input" defaultValue={agent.name} onChange={(e) => { updates.name = e.target.value; }} />
            </div>
            <div className="input-group">
              <label>Model</label>
              <input className="glass-input" defaultValue={agent.model} onChange={(e) => { updates.model = e.target.value; }} />
            </div>
            <div className="input-group">
              <label>Role</label>
              <input className="glass-input" defaultValue={agent.role} onChange={(e) => { updates.role = e.target.value; }} />
            </div>
            <div className="input-group">
              <label>Status</label>
              <select className="glass-input" defaultValue={agent.status} onChange={(e) => { updates.status = e.target.value; }}>
                <option>ONLINE</option><option>STANDBY</option><option>OFFLINE</option>
              </select>
            </div>
          </div>
          <div className="input-group" style={{ marginTop: '12px' }}>
            <label>System Prompt</label>
            <textarea className="glass-input" rows={4} defaultValue={agent.systemPrompt || ''} onChange={(e) => { updates.systemPrompt = e.target.value; }} />
          </div>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-primary" onClick={() => { updateAgent(agent.id, updates); closeModal(); }}>Save Changes</button>
          </div>
        </div>
      ),
    });
  };

  const handleKill = (id) => {
    const agent = agents.find(a => a.id === id);
    openModal({
      title: 'Terminate Agent',
      content: (
        <div>
          <p>Are you sure you want to terminate <strong>{agent?.name}</strong>? This cannot be undone.</p>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-glass btn-danger" onClick={() => { deleteAgent(id); closeModal(); }}>Terminate</button>
          </div>
        </div>
      ),
    });
  };

  return (
    <div style={{ animation: 'fadeInApp 0.5s ease-out forwards', paddingBottom: '40px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
        <div>
          <h2 className="page-title" style={{ color: '#ffb3ff' }}>Agent Foundry</h2>
          <p className="page-subtitle">Create, configure, and terminate {agents.length} specialized sub-agents.</p>
        </div>
        <button className="btn-primary" onClick={handleCreate}><Plus size={16} /> Compile New Agent</button>
      </div>

      <div className="vitals-grid">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} onConfigure={handleConfigure} onKill={handleKill} />
        ))}
        {agents.length === 0 && <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'gray' }}>Loading agents...</div>}
      </div>
    </div>
  );
}
