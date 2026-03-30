import React, { useEffect, useState, useMemo } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { Search, Database, Trash2, Plus, Edit3, ChevronDown, ChevronRight, Tag } from 'lucide-react';

function MemoryCard({ category, entries, onDelete, onEdit }) {
  const [expanded, setExpanded] = useState(true);
  const typeColors = { facts: '#ffb3ff', preferences: '#00d2ff', skills: '#00cc66', sessions: '#ffa64d' };
  const color = typeColors[category] || '#8a2be2';

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '16px', animation: 'slideInUp 0.4s ease-out both' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer', marginBottom: expanded ? '16px' : 0 }}
        onClick={() => setExpanded(!expanded)}>
        {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <Tag size={14} style={{ color }} />
        <span style={{ fontWeight: 700, color, fontSize: '1rem', textTransform: 'capitalize' }}>{category}</span>
        <span className="memory-type-badge">{entries.length} {entries.length === 1 ? 'entry' : 'entries'}</span>
      </div>
      {expanded && (
        <div className="memory-entries-list">
          {entries.map((entry, i) => (
            <div key={i} className="memory-entry-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div className="memory-entry-key">{entry.key}</div>
                <div className="memory-entry-value" style={{ wordBreak: 'break-word' }}>{entry.displayValue}</div>
                {entry.added && <div className="memory-entry-meta"><span className="text-muted" style={{ fontSize: '0.75rem' }}>Added: {entry.added}</span></div>}
              </div>
              <div style={{ display: 'flex', gap: '6px', flexShrink: 0, marginLeft: '12px' }}>
                <button className="btn-glass btn-sm" onClick={() => onEdit(entry)}><Edit3 size={12} /></button>
                <button className="btn-glass btn-sm btn-danger" onClick={() => onDelete(entry.fullKey)}><Trash2 size={12} /></button>
              </div>
            </div>
          ))}
          {entries.length === 0 && <div className="text-muted" style={{ padding: '12px', textAlign: 'center' }}>No entries in this category</div>}
        </div>
      )}
    </div>
  );
}

export default function ContextCore() {
  const memoryEntries = useAriaStore((s) => s.memoryEntries);
  const fetchMemory = useAriaStore((s) => s.fetchMemory);
  const memorySize = useAriaStore((s) => s.memorySize);
  const fetchMemorySize = useAriaStore((s) => s.fetchMemorySize);
  const saveMemoryEntry = useAriaStore((s) => s.saveMemoryEntry);
  const deleteMemoryEntry = useAriaStore((s) => s.deleteMemoryEntry);
  const openModal = useAriaStore((s) => s.openModal);
  const closeModal = useAriaStore((s) => s.closeModal);
  const toast = useAriaStore((s) => s.toast);
  const [search, setSearch] = useState('');

  useEffect(() => { fetchMemory(); fetchMemorySize(); }, []);

  // Parse entries into categorized, human-readable format
  const categorizedEntries = useMemo(() => {
    const categories = {};
    memoryEntries.forEach(entry => {
      const cat = entry.type || 'uncategorized';
      if (!categories[cat]) categories[cat] = [];

      // If the value is JSON-like string with nested objects, flatten it
      let displayValue = entry.value;
      let subEntries = null;

      try {
        const parsed = JSON.parse(entry.value);
        if (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) {
          // It's a nested object like {"TEST_DIAGNOSTIC": {"value": "...", "added": "..."}}
          subEntries = Object.entries(parsed).map(([k, v]) => ({
            key: k,
            displayValue: typeof v === 'object' ? (v.value || JSON.stringify(v)) : String(v),
            added: typeof v === 'object' ? v.added : null,
            fullKey: `${entry.key}.${k}`,
            category: cat,
          }));
        } else if (typeof parsed === 'string') {
          displayValue = parsed;
        }
      } catch {
        // Not JSON, use raw value
      }

      if (subEntries && subEntries.length > 0) {
        categories[cat].push(...subEntries);
      } else {
        categories[cat].push({
          key: entry.key,
          displayValue: displayValue,
          added: entry.timestamp ? new Date(entry.timestamp).toLocaleDateString() : null,
          fullKey: entry.key,
          category: cat,
        });
      }
    });
    return categories;
  }, [memoryEntries]);

  const totalEntries = Object.values(categorizedEntries).reduce((sum, arr) => sum + arr.length, 0);

  // Filter entries by search
  const filteredCategories = useMemo(() => {
    if (!search) return categorizedEntries;
    const out = {};
    Object.entries(categorizedEntries).forEach(([cat, entries]) => {
      const filtered = entries.filter(e =>
        e.key.toLowerCase().includes(search.toLowerCase()) ||
        e.displayValue.toLowerCase().includes(search.toLowerCase())
      );
      if (filtered.length > 0) out[cat] = filtered;
    });
    return out;
  }, [categorizedEntries, search]);

  const handleAdd = () => {
    let data = { key: '', value: '', type: 'facts' };
    openModal({
      title: 'Add Memory Entry',
      content: (
        <div>
          <div className="input-group"><label>Key</label>
            <input className="glass-input" placeholder="e.g. favorite_color" onChange={(e) => { data.key = e.target.value; }} /></div>
          <div className="input-group"><label>Value</label>
            <textarea className="glass-input" rows={3} placeholder="e.g. Purple" onChange={(e) => { data.value = e.target.value; }} /></div>
          <div className="input-group"><label>Category</label>
            <select className="glass-input" onChange={(e) => { data.type = e.target.value; }}>
              <option value="facts">Facts</option><option value="preferences">Preferences</option>
              <option value="skills">Skills</option><option value="sessions">Sessions</option>
            </select></div>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-primary" onClick={() => {
              if (!data.key) { toast('Key is required', 'warning'); return; }
              saveMemoryEntry(data.key, data.value, data.type); closeModal();
            }}>Save Entry</button>
          </div>
        </div>
      ),
    });
  };

  const handleEdit = (entry) => {
    let updates = { ...entry };
    openModal({
      title: `Edit: ${entry.key}`,
      content: (
        <div>
          <div className="input-group"><label>Value</label>
            <textarea className="glass-input" rows={3} defaultValue={entry.displayValue}
              onChange={(e) => { updates.displayValue = e.target.value; }} /></div>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-primary" onClick={() => {
              saveMemoryEntry(updates.fullKey, updates.displayValue, entry.category);
              closeModal();
            }}>Update</button>
          </div>
        </div>
      ),
    });
  };

  const handleDelete = (key) => {
    openModal({
      title: 'Delete Memory Entry',
      content: (
        <div>
          <p>Delete <strong>{key}</strong> from ARIA's memory?</p>
          <div className="modal-actions">
            <button className="btn-glass" onClick={closeModal}>Cancel</button>
            <button className="btn-glass btn-danger" onClick={() => { deleteMemoryEntry(key); closeModal(); }}>Delete</button>
          </div>
        </div>
      ),
    });
  };

  return (
    <div style={{ paddingBottom: '40px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '16px', animation: 'fadeInApp 0.4s ease-out' }}>
        <div>
          <h2 className="page-title" style={{ color: '#ffb3ff' }}>Context Core</h2>
          <p className="page-subtitle">ARIA's long-term memory — categorized knowledge from memory.json</p>
        </div>
        <button className="btn-primary" onClick={handleAdd}><Plus size={16} /> Add Entry</button>
      </div>

      <div className="stat-bar" style={{ animation: 'slideInUp 0.4s 0.1s ease-out both' }}>
        <div className="stat-item"><Database size={16} style={{ color: '#ffb3ff' }} /><span>{totalEntries} entries across {Object.keys(categorizedEntries).length} categories</span></div>
        <div className="stat-item"><span>{(memorySize / 1024).toFixed(1)} KB total</span></div>
      </div>

      <div style={{ marginBottom: '24px', animation: 'slideInUp 0.4s 0.15s ease-out both' }}>
        <div className="search-input-wrapper" style={{ maxWidth: '500px' }}>
          <Search size={16} />
          <input className="glass-input" placeholder="Search memory entries..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ flex: 1 }} />
        </div>
      </div>

      {Object.entries(filteredCategories).map(([category, entries], i) => (
        <MemoryCard key={category} category={category} entries={entries} onDelete={handleDelete} onEdit={handleEdit} />
      ))}

      {Object.keys(filteredCategories).length === 0 && (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', color: 'gray' }}>
          {memoryEntries.length === 0 ? 'No memory entries found in memory.json' : 'No entries match your search'}
        </div>
      )}
    </div>
  );
}
