import React, { useEffect, useState } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { Layers, Globe, Search, Camera, Download } from 'lucide-react';

export default function BrowserAgent() {
  const browserStatus = useAriaStore((s) => s.browserStatus);
  const fetchBrowserStatus = useAriaStore((s) => s.fetchBrowserStatus);
  const scrapeUrl = useAriaStore((s) => s.scrapeUrl);
  const toast = useAriaStore((s) => s.toast);
  const executeShell = useAriaStore((s) => s.executeShell);

  const [url, setUrl] = useState('');
  const [selector, setSelector] = useState('');
  const [scrapeResult, setScrapeResult] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchBrowserStatus(); }, []);

  const layers = [
    { name: 'Layer 1: Scrapling', lib: 'scrapling + curl_cffi',
      status: browserStatus?.layer1_scrapling || 'Available', desc: 'Stealth read-only scraping with anti-bot bypass' },
    { name: 'Layer 2: browser-use', lib: 'browser-use + Chromium',
      status: browserStatus?.layer2_browseruse || 'Idle', desc: 'LLM-driven autonomous browsing (clicks, forms, login)' },
    { name: 'Layer 3: Playwright', lib: 'playwright + Chromium',
      status: browserStatus?.layer3_playwright || 'Idle', desc: 'Raw screenshots, JavaScript execution, downloads' },
  ];

  const statusColor = (s) => s === 'Active' ? '#00cc66' : s === 'Available' ? '#ffa64d' : '#666';

  const handleScrape = async () => {
    if (!url) { toast('Enter a URL to scrape', 'warning'); return; }
    setLoading(true);
    setScrapeResult('Scraping...');
    const result = await scrapeUrl(url);
    setScrapeResult(result || 'No content extracted.');
    setLoading(false);
  };

  const handleScreenshot = async () => {
    if (!url) { toast('Enter a URL first', 'warning'); return; }
    toast('Taking screenshot...', 'info');
    const r = await executeShell(`python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); pg=b.new_page(); pg.goto('${url.replace(/'/g, "\\'")}'); pg.screenshot(path='/tmp/aria_screenshot.png'); b.close(); p.stop(); print('Screenshot saved to /tmp/aria_screenshot.png')"`);
    toast(r || 'Screenshot captured', 'success');
  };

  const handleReinstall = async (lib) => {
    toast(`Reinstalling ${lib}...`, 'info');
    const r = await executeShell(`pip install --upgrade ${lib.split('+')[0].trim().split(' ')[0]}`);
    toast(r ? 'Reinstall complete' : `Reinstalled ${lib}`, 'success');
  };

  return (
    <div style={{ animation: 'fadeInApp 0.5s ease-out forwards', paddingBottom: '40px' }}>
      <h2 className="page-title" style={{ color: '#00d2ff' }}>Browser Agent</h2>
      <p className="page-subtitle">Monitor and control ARIA's 3-layer browser automation stack. Status: <span style={{ color: statusColor(browserStatus?.status) }}>{browserStatus?.status || 'Unknown'}</span></p>

      <div className="section-header"><h3><Layers size={18} /> Layer Status</h3></div>
      <div className="vitals-grid">
        {layers.map((layer, i) => (
          <div key={i} className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ margin: 0 }}>{layer.name}</h4>
              <span className="status-badge" style={{ color: statusColor(layer.status) }}>● {layer.status}</span>
            </div>
            <div className="text-muted" style={{ marginBottom: '8px' }}>{layer.desc}</div>
            <code className="code-tag">{layer.lib}</code>
            <div style={{ marginTop: '12px' }}>
              <button className="btn-glass btn-sm" onClick={() => handleReinstall(layer.lib)}>Reinstall</button>
            </div>
          </div>
        ))}
      </div>

      <div className="section-header" style={{ marginTop: '32px' }}><h3><Search size={18} /> Scrape Tester</h3></div>
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <input className="glass-input" placeholder="Enter URL to scrape..." style={{ flex: 1 }}
            value={url} onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleScrape()} />
          <button className="btn-primary" onClick={handleScrape} disabled={loading}>
            <Globe size={16} /> {loading ? 'Scraping...' : 'Scrape'}
          </button>
        </div>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <input className="glass-input" placeholder="CSS Selector (optional)" style={{ flex: 1 }}
            value={selector} onChange={(e) => setSelector(e.target.value)} />
          <button className="btn-glass btn-sm" onClick={handleScreenshot}><Camera size={14} /> Screenshot</button>
        </div>
        <div className="scrape-results">
          {scrapeResult || 'Enter a URL and click Scrape to test'}
        </div>
      </div>
    </div>
  );
}
