import React, { useState, useRef, useEffect } from 'react';
import useAriaStore from '../stores/useAriaStore';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';

function ChatBubble({ msg }) {
  const isAria = msg.from === 'aria';
  return (
    <div className={`chat-bubble ${msg.from}`} style={{ animation: 'slideInUp 0.3s ease-out' }}>
      <div className="chat-sender" style={{ color: isAria ? 'var(--neon-secondary)' : 'var(--neon-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
        {isAria ? <Bot size={12} /> : <User size={12} />}
        {isAria ? 'ARIA CORE' : 'You'}
        {msg.timestamp && <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginLeft: '8px' }}>{msg.timestamp}</span>}
      </div>
      <div className="chat-text" style={{ lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>{msg.text}</div>
    </div>
  );
}

export default function AriaChats() {
  const executeShell = useAriaStore((s) => s.executeShell);
  const toast = useAriaStore((s) => s.toast);

  const [messages, setMessages] = useState([
    { from: 'aria', text: '⚡ Welcome, Commander. I am ARIA Core — your autonomous intelligence agent.\n\nI can help you execute tasks, write & manage skills, research topics, control devices, and manage your system. Ask me anything.', timestamp: new Date().toLocaleTimeString() },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [messages]);

  const quickPrompts = [
    'What can you do?',
    'Check my system health',
    'List my installed skills',
    'Write me a web scraper skill',
  ];

  const sendMessage = async (overrideText) => {
    const text = overrideText || input;
    if (!text.trim() || loading) return;
    const userMsg = { from: 'user', text, timestamp: new Date().toLocaleTimeString() };
    setMessages(prev => [...prev, userMsg]);
    if (!overrideText) setInput('');
    setLoading(true);

    try {
      // Use urllib3/requests-free approach via raw python urllib
      const escaped = text.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
      const result = await executeShell(
`python3 -c "
import urllib.request, json, ssl
ctx = ssl.create_default_context()
data = json.dumps({
    'model': 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
    'messages': [
        {'role': 'system', 'content': 'You are ARIA, a powerful autonomous AI agent built by GamerX. Be helpful, concise, technical, and direct. You run on Arch Linux. You have access to skills (Python scripts), memory, device mesh, browser automation, and more. Respond with useful information.'},
        {'role': 'user', 'content': '${escaped}'}
    ],
    'max_tokens': 1024,
    'temperature': 0.4,
    'stream': False
}).encode()
req = urllib.request.Request('https://integrate.api.nvidia.com/v1/chat/completions', data=data, headers={'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_NVIDIA_NIM_API_KEY'})
resp = urllib.request.urlopen(req, timeout=60, context=ctx)
j = json.loads(resp.read())
print(j['choices'][0]['message']['content'])
" 2>&1`
      );

      setMessages(prev => [...prev, {
        from: 'aria',
        text: result?.trim() || 'I processed your request but received no output.',
        timestamp: new Date().toLocaleTimeString(),
      }]);
    } catch (e) {
      setMessages(prev => [...prev, {
        from: 'aria',
        text: `⚠️ Connection error: ${e}\n\nTip: Make sure you have internet access for the NVIDIA NIM API.`,
        timestamp: new Date().toLocaleTimeString(),
      }]);
      toast('Failed to reach NVIDIA NIM API', 'error');
    }
    setLoading(false);
  };

  return (
    <div style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ animation: 'fadeInApp 0.4s ease-out', marginBottom: '16px' }}>
        <h2 className="page-title">ARIA Chats</h2>
        <p className="page-subtitle">Direct conversation with ARIA Core via NVIDIA NIM API</p>
      </div>

      <div className="glass-panel chat-container" style={{ animation: 'slideInUp 0.4s 0.1s ease-out both', flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div className="chat-messages" ref={chatRef} style={{ flex: 1 }}>
          {messages.map((msg, i) => <ChatBubble key={i} msg={msg} />)}
          {loading && (
            <div className="chat-bubble aria" style={{ animation: 'slideInUp 0.3s ease-out' }}>
              <div className="chat-sender" style={{ color: 'var(--neon-secondary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Bot size={12} /> ARIA CORE
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)' }}>
                <Loader2 size={14} className="spinning" /> Thinking...
              </div>
            </div>
          )}
        </div>

        {/* Quick prompts */}
        {messages.length <= 1 && (
          <div style={{ display: 'flex', gap: '8px', padding: '8px 16px', flexWrap: 'wrap' }}>
            {quickPrompts.map((qp, i) => (
              <button key={i} className="category-pill" onClick={() => sendMessage(qp)} style={{ fontSize: '0.78rem' }}>
                <Sparkles size={12} /> {qp}
              </button>
            ))}
          </div>
        )}

        <div className="chat-input-bar">
          <input className="glass-input" placeholder="Ask ARIA anything..." value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            style={{ flex: 1 }} disabled={loading} />
          <button className="btn-send" onClick={() => sendMessage()} disabled={loading}>
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
