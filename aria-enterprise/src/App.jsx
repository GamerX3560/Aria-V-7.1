import React, { useState } from 'react';
import './index.css';

import SplashScreen from './components/layout/SplashScreen';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import useAriaStore from './stores/useAriaStore';

// Pages
import CommandCenter from './pages/CommandCenter';
import AgentFoundry from './pages/AgentFoundry';
import SkillMatrix from './pages/SkillMatrix';
import ContextCore from './pages/ContextCore';
import LiveTelemetry from './pages/LiveTelemetry';
import CommLink from './pages/CommLink';
import TaskOrchestrator from './pages/TaskOrchestrator';
import DeviceMesh from './pages/DeviceMesh';
import BrowserAgent from './pages/BrowserAgent';
import GlobalSettings from './pages/GlobalSettings';
import PersonalInfo from './pages/PersonalInfo';
import APIVault from './pages/APIVault';
import VoicePersonality from './pages/VoicePersonality';
import SecurityCenter from './pages/SecurityCenter';

const PAGE_MAP = {
  command: CommandCenter,
  agents: AgentFoundry,
  skills: SkillMatrix,
  memory: ContextCore,
  telemetry: LiveTelemetry,
  chat: CommLink,
  tasks: TaskOrchestrator,
  devices: DeviceMesh,
  browser: BrowserAgent,
  config: GlobalSettings,
  personal: PersonalInfo,
  api: APIVault,
  voice: VoicePersonality,
  security: SecurityCenter,
};

/* ─── Toast Component ───────────────────────────────── */
function ToastContainer() {
  const toasts = useAriaStore((s) => s.toasts);
  const colors = { success: '#00cc66', error: '#ff4d4d', warning: '#ffa64d', info: '#00d2ff' };
  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };

  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className="toast-item" style={{ borderLeftColor: colors[t.type] || colors.info }}>
          <span className="toast-icon">{icons[t.type] || icons.info}</span>
          <span className="toast-message">{t.message}</span>
        </div>
      ))}
    </div>
  );
}

/* ─── Modal Component ───────────────────────────────── */
function ModalContainer() {
  const modal = useAriaStore((s) => s.modal);
  const closeModal = useAriaStore((s) => s.closeModal);

  if (!modal) return null;

  return (
    <div className="modal-overlay" onClick={closeModal}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{modal.title || 'Dialog'}</h3>
          <button className="modal-close-btn" onClick={closeModal}>✕</button>
        </div>
        <div className="modal-body">
          {modal.content}
        </div>
      </div>
    </div>
  );
}

function App() {
  const [loading, setLoading] = useState(true);
  const activeTab = useAriaStore((s) => s.activeTab);

  if (loading) {
    return (
      <>
        <div className="title-bar-drag" data-tauri-drag-region></div>
        <SplashScreen onFinish={() => setLoading(false)} />
      </>
    );
  }

  const PageComponent = PAGE_MAP[activeTab] || CommandCenter;

  return (
    <div className="app-container">
      <div className="title-bar-drag" data-tauri-drag-region></div>
      <Sidebar />
      <main className="main-wrapper">
        <TopBar />
        <div className="page-content">
          <PageComponent />
        </div>
      </main>
      <ToastContainer />
      <ModalContainer />
    </div>
  );
}

export default App;
