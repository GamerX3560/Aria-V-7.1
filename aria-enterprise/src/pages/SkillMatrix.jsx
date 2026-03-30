import React, { useEffect, useState, useMemo } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { FileCode, Search, Trash2, Plus, Power, PowerOff, Send, Bot, Code, Wand2 } from 'lucide-react';

function AISkillBuilder({ onSkillCreated }) {
  const executeShell = useAriaStore((s) => s.executeShell);
  const importSkill = useAriaStore((s) => s.importSkill);
  const toast = useAriaStore((s) => s.toast);
  const [prompt, setPrompt] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const quickPrompts = [
    '📡 Create a skill that checks system disk usage and alerts if >80%',
    '🌐 Create a web scraper skill that extracts article titles from a URL',
    '📧 Create a skill that sends system status reports via email',
    '🔍 Create a search skill that queries DuckDuckGo and returns results',
    '📊 Create a skill that monitors CPU/RAM and logs to CSV',
  ];

  const handleGenerate = async (customPrompt) => {
    const p = customPrompt || prompt;
    if (!p.trim()) { toast('Enter a description of the skill you want', 'warning'); return; }
    setLoading(true);
    setOutput('Generating skill with NVIDIA NIM...');
    setHistory(prev => [...prev, { role: 'user', text: p }]);

    try {
      const escaped = p.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
      const result = await executeShell(
        `python3 -c "
import urllib.request, json, ssl
ctx = ssl.create_default_context()
system_prompt = 'You are a Python skill generator for ARIA AI assistant. Generate COMPLETE, working Python skills. Rules: Every skill MUST have a run() function as the entry point. Use standard library where possible. Include docstrings and comments. File should be self-contained. Include error handling. Return results as strings. Output ONLY the Python code, no markdown fences, no explanations.'
data = json.dumps({'model': 'nvidia/llama-3.1-nemotron-ultra-253b-v1', 'messages': [{'role':'system','content': system_prompt}, {'role':'user','content':'${escaped}'}], 'max_tokens': 2048, 'temperature': 0.3, 'stream': False}).encode()
req = urllib.request.Request('https://integrate.api.nvidia.com/v1/chat/completions', data=data, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_NVIDIA_NIM_API_KEY'})
resp = urllib.request.urlopen(req, timeout=120, context=ctx)
j = json.loads(resp.read())
print(j['choices'][0]['message']['content'])
" 2>&1`
      );

      const code = result?.replace(/^```python\n?/m, '').replace(/^```\n?/m, '').replace(/```$/m, '').trim();
      setOutput(code || 'No response received');
      setHistory(prev => [...prev, { role: 'aria', text: code }]);
    } catch (e) {
      setOutput(`Error: ${e}`);
    }
    setLoading(false);
    setPrompt('');
  };

  const handleSaveSkill = () => {
    if (!output || output.startsWith('Error') || output.startsWith('Generating')) {
      toast('No valid skill to save', 'warning'); return;
    }
    const name = prompt ? prompt.replace(/[^a-zA-Z0-9_]/g, '_').toLowerCase().substring(0, 30) + '.py' : 'ai_generated_skill.py';
    importSkill(name, output);
    onSkillCreated?.();
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px', animation: 'slideInUp 0.4s 0.2s ease-out both', border: '1px solid rgba(138,43,226,0.3)' }}>
      <h3 className="section-title"><Wand2 size={16} style={{ color: '#cc66ff' }} /> AI Skill Builder <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>powered by NVIDIA NIM</span></h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
        {quickPrompts.map((qp, i) => (
          <button key={i} className="category-pill" onClick={() => { setPrompt(qp.substring(2)); handleGenerate(qp.substring(2)); }}
            style={{ fontSize: '0.75rem' }}>{qp}</button>
        ))}
      </div>
      <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
        <input className="glass-input" placeholder="Describe the skill you want... e.g. 'Create a weather checker that uses wttr.in API'"
          value={prompt} onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
          style={{ flex: 1 }} />
        <button className="btn-primary" onClick={() => handleGenerate()} disabled={loading}>
          <Bot size={16} /> {loading ? 'Generating...' : 'Generate Skill'}
        </button>
      </div>
      {output && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>Generated Code:</span>
            <button className="btn-glass btn-sm" onClick={handleSaveSkill}><Plus size={12} /> Save as Skill</button>
          </div>
          <pre className="scrape-results" style={{ color: '#00cc66', maxHeight: '300px' }}>{output}</pre>
        </div>
      )}
    </div>
  );
}

export default function SkillMatrix() {
  const skills = useAriaStore((s) => s.skills);
  const fetchSkills = useAriaStore((s) => s.fetchSkills);
  const deleteSkill = useAriaStore((s) => s.deleteSkill);
  const toggleSkill = useAriaStore((s) => s.toggleSkill);
  const readSkillSource = useAriaStore((s) => s.readSkillSource);
  const writeSkillSource = useAriaStore((s) => s.writeSkillSource);
  const importSkill = useAriaStore((s) => s.importSkill);
  const openModal = useAriaStore((s) => s.openModal);
  const closeModal = useAriaStore((s) => s.closeModal);
  const toast = useAriaStore((s) => s.toast);

  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  useEffect(() => { fetchSkills(); }, []);

  const categories = useMemo(() => {
    const cats = new Set(skills.map(s => s.category));
    return ['All', ...Array.from(cats).sort()];
  }, [skills]);

  const filtered = skills.filter((s) => {
    const matchSearch = s.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchCat = categoryFilter === 'All' || s.category === categoryFilter;
    return matchSearch && matchCat;
  });

  const handleEditSource = async (name) => {
    const src = await readSkillSource(name);
    if (src === null) return;
    let editedSrc = src;
    openModal({
      title: `Edit: ${name}`,
      content: (
        <div>
          <textarea className="glass-input" rows={20} defaultValue={src}
            onChange={(e) => { editedSrc = e.target.value; }}
            style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', width: '100%' }} />
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-primary" onClick={() => { writeSkillSource(name, editedSrc); closeModal(); }}>Save</button>
          </div>
        </div>
      ),
    });
  };

  const handleDelete = (name) => {
    openModal({
      title: 'Confirm Deletion',
      content: (
        <div>
          <p>Delete <strong>{name}</strong>? This cannot be undone.</p>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-glass btn-danger" onClick={() => { deleteSkill(name); closeModal(); }}>Delete</button>
          </div>
        </div>
      ),
    });
  };

  const handleCreate = () => {
    let newName = '';
    let newContent = '#!/usr/bin/env python3\n"""\nNew ARIA Skill\n"""\n\ndef run():\n    pass\n';
    openModal({
      title: 'Create New Skill',
      content: (
        <div>
          <div className="input-group"><label>File Name</label>
            <input className="glass-input" placeholder="my_skill.py" onChange={(e) => { newName = e.target.value; }} /></div>
          <div className="input-group"><label>Initial Script</label>
            <textarea className="glass-input" rows={10} defaultValue={newContent}
              onChange={(e) => { newContent = e.target.value; }}
              style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }} /></div>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-primary" onClick={() => {
              if (newName) { importSkill(newName, newContent); closeModal(); }
              else { toast('Enter a file name', 'warning'); }
            }}>Create Skill</button>
          </div>
        </div>
      ),
    });
  };

  return (
    <div style={{ paddingBottom: '40px' }}>
      <div style={{ animation: 'fadeInApp 0.4s ease-out', marginBottom: '16px' }}>
        <h2 className="page-title" style={{ color: '#ffa64d' }}>Skill Matrix</h2>
        <p className="page-subtitle">Manage {skills.length} Python tools — or use AI to generate new ones.</p>
      </div>

      {/* AI Skill Builder */}
      <AISkillBuilder onSkillCreated={fetchSkills} />

      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', animation: 'slideInUp 0.4s 0.1s ease-out both' }}>
        <div className="search-input-wrapper" style={{ flex: 1 }}>
          <Search size={16} />
          <input type="text" className="glass-input" placeholder="Search skills..." value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)} style={{ flex: 1 }} />
        </div>
        <button className="btn-primary" onClick={handleCreate}><Plus size={16} /> Create Skill</button>
      </div>

      <div className="category-filters" style={{ marginBottom: '20px', animation: 'slideInUp 0.4s 0.15s ease-out both' }}>
        {categories.map(cat => (
          <button key={cat} className={`category-pill ${categoryFilter === cat ? 'active' : ''}`}
            onClick={() => setCategoryFilter(cat)}>
            {cat} {cat !== 'All' && `(${skills.filter(s => s.category === cat).length})`}
          </button>
        ))}
      </div>

      <div className="glass-panel" style={{ padding: 0, animation: 'slideInUp 0.4s 0.2s ease-out both' }}>
        <table className="data-table">
          <thead><tr><th>File Name</th><th>Category</th><th>Size</th><th>Status</th><th style={{ textAlign: 'right' }}>Actions</th></tr></thead>
          <tbody>
            {filtered.map((skill, idx) => (
              <tr key={idx} style={{ animation: `slideInUp 0.3s ${idx * 20}ms ease-out both` }}>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileCode size={16} style={{ color: '#ffa64d' }} />
                    <span style={{ fontWeight: 600, opacity: skill.enabled ? 1 : 0.5 }}>{skill.name}</span>
                  </div>
                </td>
                <td><span className="code-tag">{skill.category}</span></td>
                <td className="text-muted">{(skill.size / 1024).toFixed(1)} KB</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
                    onClick={() => toggleSkill(skill.name)}>
                    {skill.enabled
                      ? <><Power size={16} style={{ color: '#00cc66' }} /> <span style={{ color: '#00cc66', fontSize: '0.82rem' }}>Enabled</span></>
                      : <><PowerOff size={16} style={{ color: '#666' }} /> <span style={{ color: '#666', fontSize: '0.82rem' }}>Disabled</span></>}
                  </div>
                </td>
                <td style={{ textAlign: 'right' }}>
                  <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                    <button className="btn-glass btn-sm" onClick={() => handleEditSource(skill.name)}>Edit</button>
                    <button className="btn-glass btn-sm btn-danger" onClick={() => handleDelete(skill.name)}><Trash2 size={12} /></button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: 'center', padding: '40px', color: 'gray' }}>
                {skills.length === 0 ? 'Loading skills...' : 'No skills match your filters'}
              </td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
