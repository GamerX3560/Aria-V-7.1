import React, { useState } from 'react';
import { Clock, Plus, Play, Pause, Trash2, ChevronRight, RefreshCw } from 'lucide-react';

const DEFAULT_TASKS = [
  { name: 'Check GitHub Notifications', cron: '*/15 * * * *', desc: 'Parses PRs and summarizes via notification daemon.', next: '4m 12s', rate: '100%', active: true },
  { name: 'Deep Research Digest', cron: '0 8 * * *', desc: 'Scrapes HN/Reddit for AI news, generates morning briefing.', next: '17h 08m', rate: '98.4%', active: true },
  { name: 'Memory Consolidation', cron: '0 3 * * *', desc: 'Merges session cache into long-term memory at 3 AM.', next: '9h 22m', rate: '100%', active: true },
  { name: 'System Health Snapshot', cron: '0 */6 * * *', desc: 'Takes CPU/RAM/disk snapshot for trend analysis.', next: '2h 15m', rate: '99.7%', active: false },
];

export default function TaskOrchestrator() {
  const [tasks, setTasks] = useState(DEFAULT_TASKS);

  return (
    <div style={{ animation: 'fadeInApp 0.5s ease-out forwards', paddingBottom: '40px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
        <div>
          <h2 className="page-title">Task Orchestrator</h2>
          <p className="page-subtitle">Manage autonomous scheduled tasks and background loops.</p>
        </div>
        <button className="btn-primary"><Plus size={16} /> New Scheduled Task</button>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <div className="task-list">
          {tasks.map((task, i) => (
            <div key={i} className="task-row">
              <div className="task-info">
                <div className="task-name">{task.name}</div>
                <div className="task-desc">{task.desc}</div>
                <code className="code-tag">{task.cron}</code>
              </div>
              <div className="task-stats">
                <div className="task-next">Next: <strong>{task.next}</strong></div>
                <div className="task-rate">Success: {task.rate}</div>
              </div>
              <div className="task-actions">
                <div className={`toggle-switch ${task.active ? 'on' : ''}`} onClick={() => {
                  const updated = [...tasks];
                  updated[i] = { ...updated[i], active: !updated[i].active };
                  setTasks(updated);
                }}><div className="toggle-handle"></div></div>
                <button className="btn-glass btn-sm"><RefreshCw size={12} /> Run Now</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
