import React, { useEffect, useState, useMemo } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip, PieChart, Pie, Cell, BarChart, Bar } from 'recharts';
import { Cpu, MemoryStick, HardDrive, Zap, Radio, RotateCcw, FlaskConical, Trash2, Power, Activity, Wifi, Clock, Bot, Brain, Shield, Sparkles } from 'lucide-react';

const ARIA_GREETINGS = [
  "I am ARIA — your Autonomous Real-time Intelligent Agent.",
  "All systems operational. Awaiting your command, Commander.",
  "Neural core active. Ready for anything.",
  "Your autonomous intelligence network is standing by.",
  "Skill matrix loaded. Agent swarm online. Let's build.",
  "I don't sleep. I don't forget. I just execute.",
  "Think of me as JARVIS, but open-source and local-first.",
  "Running on pure intelligence. No cloud required.",
  "Your digital second brain is ready.",
  "From code to conversation — I handle it all.",
];

function VitalCard({ icon: Icon, label, value, unit, sub, color = '#00d2ff', delay = 0 }) {
  return (
    <div className="vital-card glass-panel" style={{ animation: `slideInUp 0.4s ${delay}ms ease-out both`, transition: 'transform 0.2s, box-shadow 0.2s', cursor: 'default' }}
      onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = `0 8px 32px ${color}22`; }}
      onMouseLeave={(e) => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div className="vital-label">{label}</div>
        <Icon size={18} style={{ color, opacity: 0.7 }} />
      </div>
      <div className="vital-value" style={{ color }}>
        {value}<span className="vital-unit">{unit}</span>
      </div>
      {sub && <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>{sub}</div>}
    </div>
  );
}

function MiniChart({ data, dataKey, color, title }) {
  return (
    <div className="glass-panel" style={{ padding: '20px', height: '220px' }}>
      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: 600 }}>{title}</div>
      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={data}>
          <defs><linearGradient id={`grad_${dataKey}`} x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={color} stopOpacity={0.4}/><stop offset="95%" stopColor={color} stopOpacity={0}/></linearGradient></defs>
          <XAxis dataKey="ts" hide /><YAxis domain={[0, 100]} hide />
          <Tooltip contentStyle={{ background: '#0e0e1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.82rem' }} labelFormatter={() => ''} formatter={(v) => [`${typeof v === 'number' ? v.toFixed(1) : v}%`, title]} />
          <Area type="monotone" dataKey={dataKey} stroke={color} fill={`url(#grad_${dataKey})`} strokeWidth={2} dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function CommandCenter() {
  const vitals = useAriaStore((s) => s.vitals);
  const vitalsHistory = useAriaStore((s) => s.vitalsHistory);
  const fetchVitals = useAriaStore((s) => s.fetchVitals);
  const serviceStatus = useAriaStore((s) => s.serviceStatus);
  const fetchServiceStatus = useAriaStore((s) => s.fetchServiceStatus);
  const restartService = useAriaStore((s) => s.restartService);
  const stopService = useAriaStore((s) => s.stopService);
  const memorySize = useAriaStore((s) => s.memorySize);
  const fetchMemorySize = useAriaStore((s) => s.fetchMemorySize);
  const skills = useAriaStore((s) => s.skills);
  const fetchSkills = useAriaStore((s) => s.fetchSkills);
  const agents = useAriaStore((s) => s.agents);
  const fetchAgents = useAriaStore((s) => s.fetchAgents);
  const meshStatus = useAriaStore((s) => s.meshStatus);
  const fetchMeshStatus = useAriaStore((s) => s.fetchMeshStatus);
  const runSelfTest = useAriaStore((s) => s.runSelfTest);
  const flushCache = useAriaStore((s) => s.flushCache);
  const openModal = useAriaStore((s) => s.openModal);
  const closeModal = useAriaStore((s) => s.closeModal);
  const toast = useAriaStore((s) => s.toast);

  const [ariaLine, setAriaLine] = useState('');

  useEffect(() => {
    fetchVitals(); fetchServiceStatus(); fetchMemorySize(); fetchSkills(); fetchAgents(); fetchMeshStatus();
    const iv = setInterval(fetchVitals, 2000);
    // Rotate ARIA greeting
    setAriaLine(ARIA_GREETINGS[Math.floor(Math.random() * ARIA_GREETINGS.length)]);
    return () => clearInterval(iv);
  }, []);

  const ramGB = (vitals.ram_usage / 1024 / 1024 / 1024).toFixed(1);
  const ramTotalGB = (vitals.ram_total / 1024 / 1024 / 1024).toFixed(1);
  const ramPct = vitals.ram_total > 0 ? ((vitals.ram_usage / vitals.ram_total) * 100).toFixed(0) : 0;
  const memKB = (memorySize / 1024).toFixed(1);

  const cpuData = vitalsHistory.map(h => ({ ...h, cpu: h.cpu_load }));
  const ramData = vitalsHistory.map(h => ({ ...h, ram: h.ram_total > 0 ? (h.ram_usage / h.ram_total) * 100 : 0 }));

  const enabledSkills = skills.filter(s => s.enabled).length;
  const skillCategories = useMemo(() => {
    const cats = {};
    skills.forEach(s => { cats[s.category] = (cats[s.category] || 0) + 1; });
    return Object.entries(cats).map(([name, value]) => ({ name, value }));
  }, [skills]);

  const PIE_COLORS = ['#8a2be2', '#00d2ff', '#00cc66', '#ffa64d', '#ff4d4d', '#cc66ff', '#ffb3ff'];

  const handleSelfTest = async () => {
    const result = await runSelfTest();
    openModal({ title: 'Self-Test Results', content: (
      <div><pre style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{result}</pre>
        <div className="modal-actions"><button className="btn-primary" onClick={closeModal}>Close</button></div></div>
    )});
  };

  const handleEmergencyStop = () => {
    openModal({ title: '⚠️ Emergency Stop', content: (
      <div><p style={{ color: 'var(--accent-red)' }}>This will immediately stop the ARIA service. Are you sure?</p>
        <div className="modal-actions"><button className="btn-glass" onClick={closeModal}>Cancel</button>
          <button className="btn-glass btn-danger" onClick={() => { stopService(); closeModal(); }}>STOP ARIA</button></div></div>
    )});
  };

  const now = new Date();
  const greeting = now.getHours() < 12 ? 'Good Morning' : now.getHours() < 18 ? 'Good Afternoon' : 'Good Evening';

  return (
    <div style={{ paddingBottom: '40px' }}>
      {/* Hero Welcome Banner */}
      <div className="glass-panel" style={{
        padding: '48px 40px', marginBottom: '32px', textAlign: 'center',
        background: 'linear-gradient(135deg, rgba(138,43,226,0.12) 0%, rgba(0,210,255,0.06) 100%)',
        border: '1px solid rgba(138,43,226,0.2)',
        animation: 'scaleIn 0.5s ease-out',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', marginBottom: '8px' }}>
          <img src="/aria-logo.png" alt="" style={{ width: 48, height: 48, borderRadius: '50%' }} />
        </div>
        <div style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: '6px', animation: 'fadeInApp 0.6s ease-out' }}>{greeting},</div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 900, margin: '0 0 8px',
          background: 'linear-gradient(135deg, #fff 20%, var(--neon-secondary) 50%, var(--neon-primary) 80%)',
          WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>GamerX</h1>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', animation: 'fadeInApp 0.8s 0.2s ease-out both' }}>
          <Sparkles size={14} style={{ color: 'var(--neon-secondary)' }} />
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', fontStyle: 'italic' }}>"{ariaLine}"</span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', marginTop: '20px', animation: 'fadeInApp 0.8s 0.3s ease-out both' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: serviceStatus === 'active' ? '#00cc66' : '#ff4d4d' }}>●</div>
            <div className="text-muted" style={{ fontSize: '0.78rem' }}>Service {serviceStatus}</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#8a2be2' }}>{agents.length}</div>
            <div className="text-muted" style={{ fontSize: '0.78rem' }}>Agents</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffa64d' }}>{skills.length}</div>
            <div className="text-muted" style={{ fontSize: '0.78rem' }}>Skills</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#00d2ff' }}>{memKB}</div>
            <div className="text-muted" style={{ fontSize: '0.78rem' }}>KB Memory</div>
          </div>
        </div>
      </div>

      {/* Vitals Grid */}
      <div className="vitals-grid-5">
        <VitalCard icon={Cpu} label="CPU Load" value={vitals.cpu_load.toFixed(1)} unit="%" sub="System processing" color="#8a2be2" delay={0} />
        <VitalCard icon={MemoryStick} label="RAM" value={ramGB} unit={`/${ramTotalGB}GB`} sub={`${ramPct}% used`} color="#00d2ff" delay={60} />
        <VitalCard icon={Brain} label="Memory Bank" value={memKB} unit="KB" sub="Long-term knowledge" color="#ffa64d" delay={120} />
        <VitalCard icon={Zap} label="Skills" value={`${enabledSkills}/${skills.length}`} unit="" sub="Active tools" color="#00cc66" delay={180} />
        <VitalCard icon={Bot} label="Agents" value={agents.length} unit="deployed" sub={`${agents.filter(a => a.status === 'ONLINE').length} online`} color="#cc66ff" delay={240} />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '24px', animation: 'slideInUp 0.5s 0.3s ease-out both' }}>
        <MiniChart data={cpuData} dataKey="cpu" color="#8a2be2" title="CPU Load (60s)" />
        <MiniChart data={ramData} dataKey="ram" color="#00d2ff" title="RAM Usage (60s)" />
        <div className="glass-panel" style={{ padding: '20px', height: '220px' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '8px', fontWeight: 600 }}>Skills by Category</div>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie data={skillCategories.length > 0 ? skillCategories : [{ name: 'Loading', value: 1 }]} cx="50%" cy="50%" innerRadius={35} outerRadius={60} dataKey="value" paddingAngle={3}>
                {skillCategories.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#0e0e1a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.82rem' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="section-header" style={{ animation: 'slideInUp 0.5s 0.4s ease-out both' }}><h3>⚡ Quick Actions</h3></div>
      <div className="quick-actions-grid" style={{ animation: 'slideInUp 0.5s 0.45s ease-out both' }}>
        <button className="quick-action-btn" onClick={restartService}><RotateCcw size={18} style={{ color: '#ffa64d' }} /><span>Restart ARIA</span></button>
        <button className="quick-action-btn" onClick={handleSelfTest}><FlaskConical size={18} style={{ color: '#00cc66' }} /><span>Run Self-Test</span></button>
        <button className="quick-action-btn" onClick={flushCache}><Trash2 size={18} style={{ color: '#ff4d4d' }} /><span>Flush Cache</span></button>
        <button className="quick-action-btn" onClick={handleEmergencyStop}><Power size={18} style={{ color: '#ff4d4d' }} /><span>Emergency Stop</span></button>
        <button className="quick-action-btn" onClick={() => toast('Fast path toggled', 'info')}><Activity size={18} style={{ color: '#00d2ff' }} /><span>Toggle Fast Path</span></button>
        <button className="quick-action-btn" onClick={() => toast('Mesh restart signal sent', 'info')}><Wifi size={18} style={{ color: '#cc66ff' }} /><span>Restart Mesh</span></button>
      </div>
    </div>
  );
}
