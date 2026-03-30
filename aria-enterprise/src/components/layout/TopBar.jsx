import React, { useEffect } from 'react';
import useAriaStore from '../../stores/useAriaStore';
import { Search, Command } from 'lucide-react';

export default function TopBar() {
  const toggleCommandPalette = useAriaStore((s) => s.toggleCommandPalette);

  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        toggleCommandPalette();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [toggleCommandPalette]);

  return (
    <div className="top-bar">
      <div className="search-wrapper" onClick={toggleCommandPalette}>
        <Search size={16} style={{ color: 'var(--text-secondary)' }} />
        <span className="search-placeholder">Search agents, skills, settings...</span>
        <div className="search-shortcut">
          <Command size={12} /> K
        </div>
      </div>
    </div>
  );
}
