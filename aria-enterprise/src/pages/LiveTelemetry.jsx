import React, { useEffect, useState, useRef } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { ScrollText, Filter, Pause, Play, Download, X, Settings } from 'lucide-react';

const SEVERITY_COLORS = {
  INFO: '#00cc66', WARN: '#ffa64d', WARNING: '#ffa64d',
  ERROR: '#ff4d4d', TRACE: '#8a2be2', DEBUG: '#00d2ff',
};

function parseSeverity(line) {
  if (line.includes('[ERROR]')) return 'ERROR';
  if (line.includes('[WARN]') || line.includes('[WARNING]')) return 'WARN';
  if (line.includes('[DEBUG]')) return 'DEBUG';
  if (line.includes('[TRACE]') || line.includes('LLM')) return 'TRACE';
  return 'INFO';
}

const LOG_LEVELS = [
  { level: 1, label: 'Level 1', desc: 'Surface — errors + warnings only', filter: l => l.includes('[ERROR]') || l.includes('[WARN]') },
  { level: 2, label: 'Level 2', desc: 'Standard — INFO + warnings + errors', filter: l => true },
  { level: 3, label: 'Level 3', desc: 'Deep — includes DEBUG logs', filter: l => true },
  { level: 4, label: 'Level 4', desc: 'System — includes TRACE + LLM calls', filter: l => true },
  { level: 5, label: 'Level 5', desc: 'Unfiltered — every single log line', filter: l => true },
];

const SPAM_PATTERNS = [
  /HTTP Request: POST https:\/\/api\.telegram\.org/,
  /HTTP\/1\.1 200 OK/,
  /getUpdates/,
];

export default function LiveLogs() {
  const logs = useAriaStore((s) => s.logs);
  const fetchLogs = useAriaStore((s) => s.fetchLogs);
  const [paused, setPaused] = useState(false);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [logLevel, setLogLevel] = useState(2);
  const [hideTelegramSpam, setHideTelegramSpam] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const logRef = useRef(null);

  const logCounts = { INFO: 0, WARN: 0, ERROR: 0, TRACE: 0, DEBUG: 0 };

  useEffect(() => {
    fetchLogs(500);
    if (!paused) {
      const iv = setInterval(() => fetchLogs(500), 3000);
      return () => clearInterval(iv);
    }
  }, [paused]);

  useEffect(() => {
    if (logRef.current && !paused) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [logs, paused]);

  const filteredLogs = logs.filter((line) => {
    // Spam filter
    if (hideTelegramSpam && SPAM_PATTERNS.some(p => p.test(line))) return false;
    // Severity filter
    if (severityFilter !== 'ALL' && !line.includes(`[${severityFilter}]`)) return false;
    // Log level filter
    if (logLevel === 1 && !line.includes('[ERROR]') && !line.includes('[WARN]') && !line.includes('[WARNING]')) return false;
    if (logLevel <= 3 && line.includes('[DEBUG]') && logLevel < 3) return false;
    if (logLevel <= 3 && line.includes('[TRACE]') && logLevel < 4) return false;
    // Search
    if (searchTerm && !line.toLowerCase().includes(searchTerm.toLowerCase())) return false;
    // Count
    const sev = parseSeverity(line);
    logCounts[sev] = (logCounts[sev] || 0) + 1;
    return true;
  });

  return (
    <div style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '16px', animation: 'fadeInApp 0.4s ease-out' }}>
        <div>
          <h2 className="page-title" style={{ color: '#00d2ff' }}>Live Logs</h2>
          <p className="page-subtitle">Real-time log stream — {filteredLogs.length} of {logs.length} lines shown</p>
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap', alignItems: 'center', animation: 'slideInUp 0.4s 0.1s ease-out both' }}>
        {['ALL', 'INFO', 'WARN', 'ERROR', 'TRACE', 'DEBUG'].map((sev) => (
          <button key={sev}
            className={`btn-filter ${severityFilter === sev ? 'active' : ''}`}
            style={severityFilter === sev ? { borderColor: SEVERITY_COLORS[sev] || '#8a2be2' } : {}}
            onClick={() => setSeverityFilter(sev)}
          >{sev}</button>
        ))}
        <div style={{ flex: 1 }} />
        <select className="glass-input" value={logLevel} onChange={(e) => setLogLevel(Number(e.target.value))} style={{ width: '160px', fontSize: '0.82rem' }}>
          {LOG_LEVELS.map(l => <option key={l.level} value={l.level}>Level {l.level}</option>)}
        </select>
        <input className="glass-input" placeholder="Filter logs..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} style={{ width: '180px', fontSize: '0.82rem' }} />
        <button className="btn-glass" onClick={() => setShowSettings(!showSettings)} title="Log settings"><Settings size={14} /></button>
        <button className="btn-glass" onClick={() => setPaused(!paused)}>
          {paused ? <Play size={14} /> : <Pause size={14} />}
          {paused ? 'Resume' : 'Pause'}
        </button>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="glass-panel" style={{ padding: '16px', marginBottom: '12px', animation: 'scaleIn 0.2s ease-out' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div className={`toggle-switch ${hideTelegramSpam ? 'on' : ''}`} onClick={() => setHideTelegramSpam(!hideTelegramSpam)}>
                <div className="toggle-handle"></div>
              </div>
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 600 }}>Hide Telegram API Spam</div>
                <div className="text-muted" style={{ fontSize: '0.78rem' }}>Filters out repetitive getUpdates polling logs</div>
              </div>
            </div>
            <div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>Log Depth: <strong>{LOG_LEVELS[logLevel - 1].desc}</strong></div>
            </div>
          </div>
        </div>
      )}

      {/* Log Terminal */}
      <div className="glass-panel log-terminal" ref={logRef} style={{ animation: 'slideInUp 0.4s 0.2s ease-out both' }}>
        {filteredLogs.map((line, i) => {
          const sev = parseSeverity(line);
          return <div key={i} className="log-line" style={{ color: SEVERITY_COLORS[sev] || '#00cc66' }}>{line}</div>;
        })}
        {filteredLogs.length === 0 && (
          <div style={{ color: 'gray', padding: '40px', textAlign: 'center' }}>
            {logs.length === 0 ? 'Connecting to ARIA log stream...' : 'No logs match your filters'}
          </div>
        )}
        <div className="cursor-blink"></div>
      </div>
    </div>
  );
}
