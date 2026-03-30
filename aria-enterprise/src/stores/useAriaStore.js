import { create } from 'zustand';
import { invoke } from '@tauri-apps/api/core';

let toastId = 0;

const useAriaStore = create((set, get) => ({
  // ─── Navigation ─────────────────────────────────────
  activeTab: 'command',
  setActiveTab: (tab) => set({ activeTab: tab }),
  commandPaletteOpen: false,
  toggleCommandPalette: () => set((s) => ({ commandPaletteOpen: !s.commandPaletteOpen })),

  // ─── Toast Notifications ────────────────────────────
  toasts: [],
  toast: (message, type = 'info') => {
    const id = ++toastId;
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }));
    setTimeout(() => set((s) => ({ toasts: s.toasts.filter(t => t.id !== id) })), 3500);
  },

  // ─── Modal ──────────────────────────────────────────
  modal: null,
  openModal: (modal) => set({ modal }),
  closeModal: () => set({ modal: null }),

  // ─── System Vitals ──────────────────────────────────
  vitals: { cpu_load: 0, ram_usage: 0, ram_total: 1 },
  vitalsHistory: [],
  fetchVitals: async () => {
    try {
      const v = await invoke('get_sys_vitals');
      set((s) => ({
        vitals: v,
        vitalsHistory: [...s.vitalsHistory.slice(-59), { ...v, ts: Date.now() }],
      }));
    } catch (e) { console.warn('vitals IPC error:', e); }
  },

  // ─── Skills ─────────────────────────────────────────
  skills: [],
  fetchSkills: async () => {
    try {
      const s = await invoke('get_installed_skills');
      set({ skills: s });
    } catch (e) { console.warn('skills IPC error:', e); }
  },
  readSkillSource: async (name) => {
    try { return await invoke('read_skill_source', { name }); }
    catch (e) { get().toast(`Failed to read ${name}: ${e}`, 'error'); return null; }
  },
  writeSkillSource: async (name, content) => {
    try {
      const r = await invoke('write_skill_source', { name, content });
      get().toast(r, 'success');
      get().fetchSkills();
    } catch (e) { get().toast(`Save failed: ${e}`, 'error'); }
  },
  deleteSkill: async (name) => {
    try {
      const r = await invoke('delete_skill', { name });
      get().toast(r, 'success');
      get().fetchSkills();
    } catch (e) { get().toast(`Delete failed: ${e}`, 'error'); }
  },
  toggleSkill: async (name) => {
    try {
      const r = await invoke('toggle_skill', { name });
      get().toast(r, 'success');
      get().fetchSkills();
    } catch (e) { get().toast(`Toggle failed: ${e}`, 'error'); }
  },
  importSkill: async (name, content) => {
    try {
      const r = await invoke('import_skill', { name, content });
      get().toast(r, 'success');
      get().fetchSkills();
    } catch (e) { get().toast(`Import failed: ${e}`, 'error'); }
  },

  // ─── Memory ─────────────────────────────────────────
  memoryEntries: [],
  memorySize: 0,
  fetchMemory: async () => {
    try {
      const raw = await invoke('get_memory_entries');
      // Convert object {key: {value, type, timestamp}} to array
      let entries = [];
      if (Array.isArray(raw)) { entries = raw; }
      else if (raw && typeof raw === 'object') {
        entries = Object.entries(raw).map(([k, v]) => ({
          key: k,
          value: typeof v === 'object' ? (v.value || JSON.stringify(v)) : String(v),
          type: typeof v === 'object' ? (v.type || 'unknown') : 'fact',
          timestamp: typeof v === 'object' ? v.timestamp : null,
        }));
      }
      set({ memoryEntries: entries });
    } catch (e) { console.warn('memory IPC error:', e); }
  },
  fetchMemorySize: async () => {
    try { const sz = await invoke('get_memory_size'); set({ memorySize: sz }); }
    catch (e) { console.warn('memory size error:', e); }
  },
  saveMemoryEntry: async (key, value, entryType) => {
    try {
      const r = await invoke('save_memory_entry', { key, value, entryType });
      get().toast(r, 'success');
      get().fetchMemory();
    } catch (e) { get().toast(`Save failed: ${e}`, 'error'); }
  },
  deleteMemoryEntry: async (key) => {
    try {
      const r = await invoke('delete_memory_entry', { key });
      get().toast(r, 'success');
      get().fetchMemory();
    } catch (e) { get().toast(`Delete failed: ${e}`, 'error'); }
  },

  // ─── Config ─────────────────────────────────────────
  config: {},
  fetchConfig: async () => {
    try { const cfg = await invoke('get_aria_config'); set({ config: cfg }); }
    catch (e) { console.warn('config IPC error:', e); }
  },
  saveConfig: async (data) => {
    try {
      const r = await invoke('save_aria_config', { data });
      get().toast(r, 'success');
      get().fetchConfig();
    } catch (e) { get().toast(`Config save failed: ${e}`, 'error'); }
  },

  // ─── Identity ───────────────────────────────────────
  identity: {},
  fetchIdentity: async () => {
    try { const id = await invoke('get_identity'); set({ identity: id }); }
    catch (e) { console.warn('identity error:', e); }
  },
  saveIdentity: async (data) => {
    try {
      const r = await invoke('save_identity', { data });
      get().toast(r, 'success');
      get().fetchIdentity();
    } catch (e) { get().toast(`Identity save failed: ${e}`, 'error'); }
  },

  // ─── Logs ───────────────────────────────────────────
  logs: [],
  fetchLogs: async (count = 200) => {
    try { const lines = await invoke('get_logs', { count }); set({ logs: lines }); }
    catch (e) { console.warn('logs IPC error:', e); }
  },

  // ─── Mesh ───────────────────────────────────────────
  meshStatus: null,
  fetchMeshStatus: async () => {
    try { const ms = await invoke('get_mesh_status'); set({ meshStatus: ms }); }
    catch (e) { console.warn('mesh IPC error:', e); }
  },

  // ─── Browser Agent ──────────────────────────────────
  browserStatus: null,
  fetchBrowserStatus: async () => {
    try { const bs = await invoke('get_browser_status'); set({ browserStatus: bs }); }
    catch (e) { console.warn('browser IPC error:', e); }
  },
  scrapeUrl: async (url) => {
    try {
      get().toast('Scraping URL...', 'info');
      const result = await invoke('scrape_url', { url });
      get().toast('Scrape complete', 'success');
      return result;
    } catch (e) { get().toast(`Scrape failed: ${e}`, 'error'); return null; }
  },

  // ─── Service Control ───────────────────────────────
  serviceStatus: 'unknown',
  fetchServiceStatus: async () => {
    try { const st = await invoke('get_service_status'); set({ serviceStatus: st }); }
    catch (e) { console.warn('service error:', e); }
  },
  restartService: async () => {
    try {
      const r = await invoke('restart_aria_service');
      get().toast(r, 'success');
      setTimeout(() => get().fetchServiceStatus(), 2000);
    } catch (e) { get().toast(`Restart failed: ${e}`, 'error'); }
  },
  stopService: async () => {
    try {
      const r = await invoke('stop_aria_service');
      get().toast(r, 'warning');
      setTimeout(() => get().fetchServiceStatus(), 1000);
    } catch (e) { get().toast(`Stop failed: ${e}`, 'error'); }
  },
  runSelfTest: async () => {
    try {
      const result = await invoke('run_self_test');
      get().toast('Self-test complete', 'success');
      return result;
    } catch (e) { get().toast(`Test failed: ${e}`, 'error'); return 'Test failed: ' + e; }
  },
  flushCache: async () => {
    try {
      const r = await invoke('flush_cache');
      get().toast(r, 'success');
    } catch (e) { get().toast(`Flush failed: ${e}`, 'error'); }
  },

  // ─── Agents ─────────────────────────────────────────
  agents: [],
  fetchAgents: async () => {
    try {
      const raw = await invoke('get_agents');
      set({ agents: Array.isArray(raw) ? raw : [] });
    } catch (e) { console.warn('agents IPC error:', e); }
  },
  saveAgents: async (agents) => {
    try {
      await invoke('save_agents', { data: agents });
      set({ agents });
    } catch (e) { get().toast(`Save failed: ${e}`, 'error'); }
  },
  createAgent: (agent) => {
    const agents = [...get().agents, agent];
    get().saveAgents(agents);
    get().toast(`Agent "${agent.name}" compiled`, 'success');
  },
  deleteAgent: (id) => {
    const agents = get().agents.filter(a => a.id !== id);
    get().saveAgents(agents);
    get().toast('Agent terminated', 'warning');
  },
  updateAgent: (id, updates) => {
    const agents = get().agents.map(a => a.id === id ? { ...a, ...updates } : a);
    get().saveAgents(agents);
    get().toast('Agent updated', 'success');
  },

  // ─── Voice ──────────────────────────────────────────
  voiceConfig: {},
  fetchVoiceConfig: async () => {
    try { const vc = await invoke('get_voice_config'); set({ voiceConfig: vc }); }
    catch (e) { console.warn('voice IPC error:', e); }
  },
  saveVoiceConfig: async (backend, speed, pitch) => {
    try {
      const r = await invoke('save_voice_config', { backend, speed, pitch });
      get().toast(r, 'success');
    } catch (e) { get().toast(`Voice save failed: ${e}`, 'error'); }
  },
  testVoice: async (text) => {
    try {
      const r = await invoke('test_voice', { text });
      get().toast(r, 'info');
    } catch (e) { get().toast(`Voice test failed: ${e}`, 'error'); }
  },

  // ─── Credentials ────────────────────────────────────
  credentials: {},
  fetchCredentials: async () => {
    try { const c = await invoke('get_credentials'); set({ credentials: c }); }
    catch (e) { console.warn('creds IPC error:', e); }
  },
  saveCredentials: async (data) => {
    try {
      const r = await invoke('save_credentials', { data });
      get().toast(r, 'success');
      set({ credentials: data });
    } catch (e) { get().toast(`Save failed: ${e}`, 'error'); }
  },

  // ─── Devices ────────────────────────────────────────
  devices: [],
  fetchDevices: async () => {
    try {
      const raw = await invoke('get_devices');
      set({ devices: Array.isArray(raw) ? raw : [] });
    } catch (e) { console.warn('devices IPC error:', e); }
  },
  saveDevices: async (devices) => {
    try {
      await invoke('save_devices', { data: devices });
      set({ devices });
    } catch (e) { get().toast(`Save failed: ${e}`, 'error'); }
  },

  // ─── Personality ────────────────────────────────────
  personality: {},
  fetchPersonality: async () => {
    try { const p = await invoke('get_personality'); set({ personality: p }); }
    catch (e) { console.warn('personality IPC error:', e); }
  },
  savePersonality: async (formality, verbosity, playfulness) => {
    try {
      const r = await invoke('save_personality', { formality, verbosity, playfulness });
      get().toast(r, 'success');
    } catch (e) { get().toast(`Save failed: ${e}`, 'error'); }
  },

  // ─── Security ───────────────────────────────────────
  securityConfig: null,
  fetchSecurityConfig: async () => {
    try { const sc = await invoke('get_security_config'); set({ securityConfig: sc }); }
    catch (e) { console.warn('security error:', e); }
  },
  saveSecurityConfig: async (data) => {
    try {
      const r = await invoke('save_security_config', { data });
      get().toast(r, 'success');
      set({ securityConfig: data });
    } catch (e) { get().toast(`Security save failed: ${e}`, 'error'); }
  },

  // ─── Shell Execution ───────────────────────────────
  executeShell: async (cmd) => {
    try {
      const r = await invoke('execute_shell', { cmd });
      return r;
    } catch (e) { get().toast(`Command failed: ${e}`, 'error'); return null; }
  },
}));

export default useAriaStore;
