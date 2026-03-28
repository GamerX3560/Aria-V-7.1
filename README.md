# ARIA v6 — Autonomous Agent System

<div align="center">

**The most powerful personal AI agent for Linux.**

Built on Nvidia NIM • Telegram Interface • Multi-Agent Architecture • Unlimited Execution

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)

</div>

---

## What is ARIA?

ARIA is a self-hosted, autonomous AI agent that runs on your Linux machine. Unlike chatbots, ARIA can:

- 🖥️ **Execute commands** on your system with no iteration limits
- 🌐 **Browse the web** stealthily, bypassing anti-bot protections
- 📁 **Manage files** — search, organize, read, and write
- 🔧 **Write & debug code** in any language
- 📋 **Plan complex tasks** by decomposing them into sub-agent steps
- 🧠 **Remember** facts, preferences, and tools across sessions

## Architecture

```
aria/
├── router.py            # Telegram bot entry point
├── core/                # The brain
│   ├── agent_loop.py    # Unlimited autonomous execution loop
│   ├── memory.py        # Auto-compressing conversation memory
│   ├── planner.py       # Task decomposition engine
│   ├── tool_executor.py # Safe command execution with security
│   └── skill_loader.py  # Dynamic skill discovery
├── agents/              # Specialized sub-agents
│   ├── base_agent.py    # Abstract agent interface
│   ├── coder_agent.py   # Code writing & debugging
│   ├── browser_agent.py # Web scraping (Scrapling stealth)
│   ├── file_agent.py    # File operations
│   └── casual_agent.py  # Conversation
├── skills/              # 30+ tools & automations
├── SOUL.md              # Personality & identity definition
├── identity.yaml        # User profile & decision rules
├── SKILLS_REGISTRY.md   # Tool descriptions for the LLM
├── requirements.txt     # Python dependencies
└── setup.sh             # Auto-installer for Arch Linux
```

## Quick Start

### 1. Clone

```bash
git clone https://github.com/yourusername/aria.git ~/aria
cd ~/aria
```

### 2. Install

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure

Set your Telegram bot token and user ID:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_USER_ID="your_user_id"
```

Optional: Set your Nvidia NIM API key:

```bash
export NVIDIA_API_KEY="your_nvidia_api_key"
```

### 4. Run

```bash
python3 ~/aria/router.py
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/status` | Show system status, model, memory |
| `/reset` | Clear conversation context |
| `/memory` | Show stored facts & skills |
| `/skills` | List all loaded skills |
| `/save` | Save current session to disk |
| `/reload` | Hot-reload skills from disk |

## Key Features

### Unlimited Execution
Unlike traditional chatbots limited to 5 turns, ARIA runs until the task is complete. The loop uses intelligent safety mechanisms (duplicate detection, stuck prevention) instead of hard iteration caps.

### Task Planning
For complex multi-step tasks, ARIA automatically decomposes them into sub-agent plans:

```json
{
  "plan": [
    {"id": "1", "agent": "browser", "task": "Search for X"},
    {"id": "2", "agent": "coder", "task": "Process the data", "need": ["1"]},
    {"id": "3", "agent": "file", "task": "Save results", "need": ["2"]}
  ]
}
```

### Stealth Web Scraping
Uses Scrapling to bypass Cloudflare and anti-bot protections with real stealth browser sessions.

### Memory Persistence
Conversations are auto-saved and can be recovered across restarts. Long messages are auto-compressed to keep context efficient.

## Skills

ARIA comes with 30+ pre-built skills including:

- 🔍 Deep Web Research (multi-level, auto-PDF)
- 📧 Email (Gmail API)
- 🐦 Social Media (Twitter/X)
- 🎥 Screen Recording
- 📱 Android Control (ADB/scrcpy)
- 🔐 Password Management
- 🧠 Memory Agent
- 🎬 Movie Download (Scrapling)
- And many more...

## License

MIT License — see LICENSE for details.
