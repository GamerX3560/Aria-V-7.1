import React from 'react';
import useAriaStore from '../../stores/useAriaStore';
import {
  Globe, Bot, Zap, Brain, KeyRound, BarChart3, MessageSquare,
  Clock, Smartphone, Settings, User, Shield, AppWindow, Mic,
  ScrollText,
} from 'lucide-react';

const NAV_SECTIONS = [
  {
    label: 'Core Ops',
    items: [
      { id: 'command',  icon: Globe,          label: 'Command Center' },
      { id: 'agents',   icon: Bot,            label: 'Agent Foundry' },
      { id: 'skills',   icon: Zap,            label: 'Skill Matrix' },
      { id: 'memory',   icon: Brain,          label: 'Context Core' },
    ],
  },
  {
    label: 'Supervision',
    items: [
      { id: 'telemetry', icon: ScrollText,   label: 'Live Logs' },
      { id: 'chat',      icon: MessageSquare, label: 'ARIA Chats' },
      { id: 'tasks',     icon: Clock,         label: 'Task Orchestrator' },
      { id: 'devices',   icon: Smartphone,    label: 'Device Mesh' },
      { id: 'browser',   icon: AppWindow,     label: 'Browser Agent' },
    ],
  },
  {
    label: 'System',
    items: [
      { id: 'config',    icon: Settings,      label: 'Global Settings' },
      { id: 'personal',  icon: User,          label: 'Personal Info' },
      { id: 'api',       icon: KeyRound,      label: 'API Vault' },
      { id: 'voice',     icon: Mic,           label: 'Voice & Personality' },
      { id: 'security',  icon: Shield,        label: 'Security Center' },
    ],
  },
];

export default function Sidebar() {
  const activeTab = useAriaStore((s) => s.activeTab);
  const setActiveTab = useAriaStore((s) => s.setActiveTab);

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-header" data-tauri-drag-region>
        <img src="/aria-logo.png" alt="ARIA" className="sidebar-logo-img" />
        <div className="sidebar-title">ARIA v8.1</div>
      </div>

      <div className="sidebar-scroll">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <div className="nav-category">{section.label}</div>
            {section.items.map((item) => {
              const Icon = item.icon;
              return (
                <div
                  key={item.id}
                  className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(item.id)}
                >
                  <Icon size={16} className="nav-icon-svg" />
                  <span>{item.label}</span>
                </div>
              );
            })}
          </div>
        ))}
      </div>

      <div className="sidebar-user-profile">
        <div
          className="user-avatar"
          style={{
            background: 'url("https://api.dicebear.com/7.x/notionists/svg?seed=GamerX") center/cover',
          }}
        ></div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#fff' }}>GamerX</div>
          <div style={{ color: 'var(--neon-secondary)', fontSize: '0.75rem' }}>ARIA Owner</div>
        </div>
      </div>
    </aside>
  );
}
