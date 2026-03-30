# 🧠 ARIA — Autonomous Real-time Intelligent Agent

<div align="center">

![ARIA Logo](aria-enterprise/public/aria-logo.png)

**The most advanced open-source autonomous AI agent for Linux power users.**

*Think JARVIS, but local-first, privacy-respecting, and built for Arch Linux.*

[![Version](https://img.shields.io/badge/version-8.1-blueviolet?style=for-the-badge)](https://github.com/GamerX3560/Aria-V-7.1)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Arch Linux](https://img.shields.io/badge/Arch_Linux-Optimized-1793D1?style=for-the-badge&logo=archlinux)](https://archlinux.org)
[![Tauri](https://img.shields.io/badge/Tauri-2.0-FFC131?style=for-the-badge&logo=tauri)](https://tauri.app)

---

**ARIA is not just another chatbot.** It's a fully autonomous AI agent that lives on your machine, manages your system, writes code, automates browsers, conducts deep research, controls devices, and evolves through self-improvement — all while respecting your privacy with a strict local-first architecture.

[📥 Quick Install](#-quick-install) • [🏗️ Architecture](#️-architecture) • [⚡ Features](#-features) • [🖥️ Manager GUI](#️-aria-enterprise-manager) • [📖 Skills](#-skill-matrix) • [🤖 Agents](#-agent-swarm) • [🔬 Deep Research](#-deep-research-engine) • [🛡️ Security](#️-security--privacy)

</div>

---

## 📋 Table of Contents

- [What is ARIA?](#-what-is-aria)
- [Quick Install](#-quick-install)
- [System Requirements](#-system-requirements)
- [Architecture](#️-architecture)
- [Core Engine](#-core-engine)
- [Features](#-features)
- [Skill Matrix](#-skill-matrix)
- [Agent Swarm](#-agent-swarm)
- [Deep Research Engine](#-deep-research-engine)
- [Browser Automation](#-browser-automation)
- [Device Mesh](#-device-mesh)
- [Context Core (Memory)](#-context-core--memory)
- [Voice & Personality](#-voice--personality)
- [ARIA Enterprise Manager (GUI)](#️-aria-enterprise-manager)
- [Security & Privacy](#️-security--privacy)
- [Configuration](#-configuration)
- [Telegram Integration](#-telegram-integration)
- [API & Services](#-api--services)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 What is ARIA?

ARIA (**A**utonomous **R**eal-time **I**ntelligent **A**gent) is a next-generation AI assistant that operates as a persistent, autonomous agent on your Linux system. Unlike cloud-based assistants, ARIA:

- **Lives locally** — Your data never leaves your machine unless you explicitly allow it
- **Manages itself** — Self-improving agent loops, automated skill generation, and error recovery
- **Controls everything** — From your desktop to your Android devices, from browsers to system services
- **Thinks deeply** — Multi-depth research engine that scrapes, synthesizes, and generates dossiers
- **Never sleeps** — Runs 24/7 as a background service, always listening, always ready

### Key Differentiators

| Feature | ARIA | ChatGPT | Siri | Alexa |
|---------|------|---------|------|-------|
| **Runs locally** | ✅ | ❌ | ❌ | ❌ |
| **Autonomous execution** | ✅ | ❌ | ❌ | ❌ |
| **Full system access** | ✅ | ❌ | ❌ | ❌ |
| **Browser automation** | ✅ | ❌ | ❌ | ❌ |
| **Self-improving** | ✅ | ❌ | ❌ | ❌ |
| **Custom skill creation** | ✅ | Plugins | ❌ | Skills |
| **Device mesh control** | ✅ | ❌ | Limited | Limited |
| **Privacy-first** | ✅ | ❌ | ❌ | ❌ |
| **Open source** | ✅ | ❌ | ❌ | ❌ |
| **Offline-capable** | ✅ | ❌ | Partial | ❌ |
| **Deep research** | ✅ (4 levels) | ❌ | ❌ | ❌ |

---

## 📥 Quick Install

### One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/GamerX3560/Aria-V-7.1/master/install.sh | bash
```

### Manual Install

```bash
git clone https://github.com/GamerX3560/Aria-V-7.1.git ~/aria
cd ~/aria
chmod +x install.sh
./install.sh
```

The installer will:
1. 🔍 Detect your system (Arch, Ubuntu, Fedora)
2. 📦 Install all dependencies (Python, Node.js, Rust, Ollama, etc.)
3. 🧠 Pull the router model (`aria-router` via Ollama)
4. 🖥️ Install the ARIA Enterprise Manager (GUI)
5. ⚙️ Configure identity, security, and vault
6. 🚀 Start the ARIA background service

---

## 💻 System Requirements

### Minimum
| Component | Requirement |
|-----------|-------------|
| **OS** | Linux (Arch Linux recommended, Ubuntu/Fedora supported) |
| **CPU** | 4+ cores, x86_64 |
| **RAM** | 8 GB |
| **Storage** | 20 GB free |
| **Python** | 3.10+ |
| **Network** | Required for NVIDIA NIM API |

### Recommended (Full Experience)
| Component | Requirement |
|-----------|-------------|
| **OS** | Arch Linux with Hyprland (Wayland) |
| **CPU** | AMD Ryzen 5+ / Intel i5+ (8 threads) |
| **GPU** | AMD RX 6000+ (ROCm) or NVIDIA GTX 1060+ (CUDA) |
| **RAM** | 16 GB |
| **Storage** | 50 GB NVMe SSD |
| **Ollama** | For local model inference |

---

## 🏗️ Architecture

ARIA uses a modular, event-driven architecture with clear separation of concerns:

```
┌──────────────────────────────────────────────────────────────┐
│                    ARIA Enterprise Manager                    │
│                  (Tauri + React + Glassmorphic UI)            │
├──────────────────────────────────────────────────────────────┤
│                          IPC Bridge                           │
│              (35+ Rust commands, real file I/O)               │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Router   │  │  Agent   │  │  Skill   │  │  Memory  │     │
│  │  Engine   │  │  Swarm   │  │  Matrix  │  │  Engine  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │              │              │              │           │
│  ┌────▼──────────────▼──────────────▼──────────────▼─────┐    │
│  │              Core Event Loop (router.py)               │    │
│  │     Intent Parsing → Agent Selection → Execution       │    │
│  └────────────────────┬──────────────────────────────────┘    │
│                       │                                       │
│  ┌────────────────────▼──────────────────────────────────┐    │
│  │                 Integration Layer                      │    │
│  │  Telegram │ Browser │ Voice │ Device Mesh │ Security   │    │
│  └──────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### Core Components

| Component | File | Purpose |
|-----------|------|---------|
| **Router** | `router.py` | Intent classification, agent dispatch, conversation loop |
| **Core** | `core/` | Base agent framework, LLM interface, event handlers |
| **Agents** | `agents/` | Specialized agent implementations (browser, coder, file, casual) |
| **Skills** | `skills/` | 30+ Python tools (deep research, browser automation, etc.) |
| **Memory** | `memory.json` | Long-term knowledge persistence (facts, preferences, skills) |
| **Identity** | `identity.yaml` | User profile, emails, system context |
| **Config** | `config.yaml` | Model selection, paths, behavior tuning |
| **Soul** | `SOUL.md` | System hardware/software profile for context-aware decisions |
| **Vault** | `vault/` | Encrypted credential storage (Google OAuth, API keys) |
| **Manager** | `aria-enterprise/` | Tauri desktop GUI with 14 management pages |

---

## ⚙️ Core Engine

### Router & Intent System

ARIA's router (`router.py`) is the brain that processes every incoming message:

1. **Intent Classification** — Uses a local Qwen 3.5 4B model (`aria-router`) to classify user intent
2. **Agent Selection** — Routes to the appropriate specialized agent based on classification
3. **Context Injection** — Loads relevant memory, user identity, and system state into the LLM context
4. **Execution** — The selected agent processes the request, potentially invoking skills or system commands
5. **Memory Persistence** — Important facts and outcomes are stored for future reference

### LLM Stack

| Layer | Model | Purpose |
|-------|-------|---------|
| **Router** | Qwen 3.5 4B (Ollama) | Local intent parsing, fast classification |
| **Primary** | NVIDIA NIM (Nemotron Ultra 253B) | Complex reasoning, code generation, analysis |
| **Fallback** | Google Gemini Pro | Alternative cloud inference |
| **Local TTS** | Piper / eSpeak | Voice synthesis |

### Conversation Flow

```
User Message (Telegram/GUI)
     │
     ▼
┌─────────────┐     ┌────────────────┐
│   Router    │────▶│ Intent Classify │
│  (Qwen 4B) │     └───────┬────────┘
└─────────────┘             │
                    ┌───────▼────────┐
                    │ Agent Dispatch  │
                    └───────┬────────┘
         ┌──────────┬──────┴──────┬──────────┐
         ▼          ▼             ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Coder   │ │ Browser │ │ Casual  │ │  File   │
    │ Agent   │ │  Agent  │ │  Agent  │ │  Agent  │
    └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
         │           │            │           │
         └─────┬─────┘     ┌─────┘           │
               ▼            ▼                 ▼
          ┌─────────┐  ┌─────────┐     ┌─────────┐
          │ Skills  │  │  LLM    │     │  System │
          │ Execute │  │Response │     │  Access │
          └─────────┘  └─────────┘     └─────────┘
```

---

## ⚡ Features

### Overview

| Category | Features |
|----------|----------|
| **Intelligence** | Multi-model routing, context-aware responses, long-term memory, personality tuning |
| **Automation** | Browser control (Playwright), shell execution, file management, device mesh |
| **Research** | 4-depth multi-engine search, Trafilatura scraping, PDF dossier generation |
| **Development** | AI code generation, skill creation, self-improvement loops, project analysis |
| **Communication** | Telegram bot, voice synthesis, natural language interface |
| **Management** | Enterprise GUI (14 pages), real-time monitoring, security controls |
| **Privacy** | Local-first, no telemetry, sandboxed execution, encrypted vault |

---

## 📖 Skill Matrix

ARIA's power comes from its extensible skill system — **30+ Python tools** that can be mixed, matched, and AI-generated.

### Built-in Skills

| Skill | Description |
|-------|-------------|
| `deep_research_v4.py` | 4-level multi-engine research with PDF dossier output |
| `browser_agent.py` | Full Playwright browser automation (click, type, screenshot, scrape) |
| `desktop_agent.py` | Desktop control via Wayland/Hyprland (window management, screenshots) |
| `email_agent.py` | Gmail integration with OAuth2 (send, read, search) |
| `computer_vision_ocr_screenshot_agent.py` | Screen capture + OCR text extraction |
| `android_adb_automation_scrcpy_agent.py` | Android device control via ADB + scrcpy mirror |
| `clipboard_manager_wayland_agent.py` | System clipboard management (Wayland-native wl-copy/wl-paste) |
| `data_backup_sync_encrypted_agent.py` | Encrypted system backup with sync capabilities |
| `network_security_scanner_linux_agent.py` | Network scanning and security audit (nmap, port scanning) |
| `password_manager_cli_agent.py` | CLI-based encrypted password management |
| `pdf_manipulation_python_agent.py` | PDF generation, splitting, merging, text extraction |
| `screen_recording_wayland_agent.py` | Wayland-native screen recording (wf-recorder) |
| `media_transcoding_amd_gpu_agent.py` | Hardware-accelerated video transcoding (AMD VAAPI/ROCm) |
| `image_editor_cli_python_agent.py` | CLI image editing (resize, crop, filter, watermark) |
| `memory_agent.py` | Memory management — store, recall, forget, search facts |
| `self_improve_agent.py` | Autonomous self-improvement loop (analyze → generate → test → deploy) |
| `genesis_agent.py` | Skill generation engine — create new skills from descriptions |
| `google_auth.py` | Google OAuth2 multi-account authentication |
| `local_llm_inference_engine_agent.py` | Local LLM management (Ollama model pull/run/list) |
| `business_agent.py` | Business intelligence and analysis tools |
| `movies4u_downloader.py` | Media discovery and download automation |
| `adypu_erp_login.py` | University ERP system automation |

### AI Skill Builder

The ARIA Manager includes an **AI-powered skill generator**:

1. Describe what you want in natural language
2. NVIDIA NIM (Nemotron Ultra 253B) generates complete Python code
3. One-click deploy to the skills directory
4. Skill is immediately available for ARIA to use

```
You: "Create a weather checker that fetches current weather from wttr.in"

ARIA generates:
├── weather_checker.py
│   ├── run() entry point
│   ├── urllib-based HTTP client
│   ├── JSON parsing
│   ├── Error handling
│   └── Beautiful formatted output
```

---

## 🤖 Agent Swarm

ARIA operates through a **swarm of specialized agents**, each optimized for different task types:

| Agent | Role | Capabilities |
|-------|------|-------------|
| **Casual Agent** | General conversation | Natural language, jokes, explanations, advice |
| **Coder Agent** | Software development | Code generation, debugging, project setup, review |
| **Browser Agent** | Web automation | Navigate, click, type, screenshot, scrape, download |
| **File Agent** | File system operations | Create, read, edit, delete, organize, search |
| **Base Agent** | Foundation framework | Common utilities, LLM interface, error handling |

### Agent Lifecycle

```
1. CREATION → Agent is instantiated with its system prompt and capabilities
2. CONTEXT  → Receives user identity, memory, and system state
3. ROUTING  → Router assigns task based on intent classification
4. EXECUTE  → Agent processes, potentially calling skills or system commands
5. RESPOND  → Formats response and sends back to user
6. LEARN    → Stores relevant facts in long-term memory
```

---

## 🔬 Deep Research Engine

ARIA's flagship feature is its **4-level deep research engine** — the most advanced autonomous research system available in any open-source AI agent.

### Research Depths

| Level | Name | Method | Time | Output |
|-------|------|--------|------|--------|
| **1** | Surface | Single search + top results | ~30s | Quick summary |
| **2** | Standard | Multi-engine search + scraping | ~2 min | Detailed analysis |
| **3** | Deep | Multi-engine + cross-referencing + validation | ~5 min | Comprehensive report |
| **4** | Exhaustive | Full web crawl + academic sources + synthesis | ~15 min | PDF dossier |

### Research Pipeline

```
Query → Topic Router → Search (SearXNG + DuckDuckGo + Google)
                          │
                          ▼
                    URL Collection
                          │
                          ▼
              Trafilatura Extraction (parallel)
                          │
                          ▼
                Content Quality Filter
                (min-year, relevance scoring)
                          │
                          ▼
              LLM Synthesis (Nemotron Ultra)
                          │
                          ▼
              ┌──────────┴──────────┐
              │   Output Format     │
              ├─────────────────────┤
              │ • Markdown Report   │
              │ • PDF Dossier       │
              │ • Telegram Summary  │
              └─────────────────────┘
```

### Research Features

- **Multi-engine search** — Queries SearXNG, DuckDuckGo, and Google simultaneously
- **Year-based filtering** — Prioritizes sources from 2023+ for freshness
- **Trafilatura scraping** — High-speed content extraction from web pages
- **Checkpointing** — Saves progress for long research sessions
- **Topic routing** — Automatically selects relevant search strategies
- **PDF generation** — Professional styled dossiers with ReportLab

---

## 🌐 Browser Automation

ARIA can **fully control web browsers** via Playwright CDP (Chrome DevTools Protocol):

- Navigate to URLs, click elements, fill forms
- Take full-page screenshots
- Extract text content via DOM or OCR
- Download files and manage cookies
- Automate multi-step workflows (login → navigate → extract → download)
- Handle JavaScript-rendered pages

### Supported Browsers
- Chromium (default)
- Brave Browser
- Firefox (experimental)

---

## 📱 Device Mesh

Control and monitor multiple devices from a single ARIA instance:

- **Android devices** via ADB (install apps, run commands, mirror screens with scrcpy)
- **SSH-connected Linux machines** (remote command execution)
- **Wake-on-LAN** (power on networked devices)
- **Device health monitoring** (CPU, RAM, disk, battery)

---

## 🧩 Context Core — Memory

ARIA maintains a **persistent long-term memory** organized by category:

| Category | Example Entries |
|----------|----------------|
| **Facts** | User preferences, important dates, code secrets, personal info |
| **Preferences** | Download quality, music player, language settings |
| **Skills** | Learned capabilities, improvement notes |
| **Sessions** | Conversation highlights, task outcomes |

Memory is stored in `memory.json` and persists across sessions, restarts, and updates.

---

## 🎤 Voice & Personality

ARIA supports multiple **TTS (Text-to-Speech) backends**:

| Backend | Quality | Speed | Latency |
|---------|---------|-------|---------|
| **Piper** | High (neural) | Fast | ~200ms |
| **eSpeak** | Medium | Fastest | ~50ms |
| **Coqui TTS** | Highest | Slow | ~2s |

### Personality Tuning
Three adjustable personality axes (0–100 scale):
- **Formal ↔ Casual** — How ARIA addresses you
- **Concise ↔ Verbose** — How much detail in responses
- **Serious ↔ Playful** — Tone and humor level

---

## 🖥️ ARIA Enterprise Manager

The **ARIA Enterprise Manager** is a premium desktop GUI built with Tauri 2.0 + React, providing full control over every aspect of ARIA:

### Technology Stack
| Layer | Technology |
|-------|-----------|
| **Framework** | Tauri 2.0 (Rust backend + webview frontend) |
| **Frontend** | React 19 + Zustand state management |
| **Charts** | Recharts (real-time CPU, RAM, skill analytics) |
| **Design** | Glassmorphic dark theme with neon accents |
| **IPC** | 35+ Rust commands with real file I/O |

### Pages (14 Total)

| Page | Features |
|------|----------|
| **Command Center** | Welcome dashboard, CPU/RAM charts, skill pie chart, quick actions, service status |
| **Agent Foundry** | Create, configure, and kill agents with modal editors |
| **Skill Matrix** | Browse, search, filter, enable/disable, edit source, AI Skill Builder |
| **Context Core** | Categorized memory viewer with add/edit/delete and search |
| **Live Logs** | 5 log levels, telegram spam filter, search, pause/resume |
| **ARIA Chats** | Real AI chat via NVIDIA NIM (Nemotron Ultra 253B) |
| **Task Orchestrator** | Manage cron-scheduled autonomous tasks |
| **Device Mesh** | Add/remove/wake/mirror devices |
| **Browser Agent** | Scrape tester, screenshot, layer status |
| **Global Settings** | Model selection, temperature, system prompt, base URL |
| **Personal Info** | Profile, all emails with purpose tags, raw identity data |
| **API Vault** | Auto-discovers API keys across codebase + vault |
| **Voice & Personality** | TTS configuration, personality tuning sliders |
| **Security Center** | Sudo toggle, network egress, bash blocklist, sandbox paths |

### Design Language
- **Glassmorphic panels** with backdrop blur
- **Animated gradient background** (dual-layer radial, looping)
- **Staggered animations** on page load
- **Toast notifications** for all operations
- **Modal dialogs** for create/edit/delete
- **Dark theme** with neon purple/cyan accents

---

## 🛡️ Security & Privacy

ARIA follows **strict security principles**:

### Local-First Architecture
- All data stays on your machine
- No telemetry, no tracking, no cloud sync
- Credentials stored in `vault/` with restricted permissions

### Security Controls
| Control | Description |
|---------|-------------|
| **Sudo Execution** | Toggle whether ARIA can run privileged commands |
| **Network Egress** | Control ARIA's ability to make outbound connections |
| **Bash Blocklist** | Block specific commands (rm -rf, dd, etc.) |
| **Sandbox Paths** | Restrict filesystem access to whitelisted directories |
| **Credential Masking** | API keys hidden by default, reveal on demand |

### File Permissions
- `identity.yaml` — `chmod 600` (owner-only read/write)
- `vault/` — `chmod 700` (owner-only access)
- `security.json` — Runtime security policy

---

## ⚙️ Configuration

### `config.yaml`
```yaml
# Model routing
ollama_url: "http://localhost:11434"
router_model: "aria-router"          # Qwen 3.5 4B — intent parser

# Paths
soul_path: "~/aria/SOUL.md"
memory_path: "~/aria/memory.json"
skills_dir: "~/aria/skills"

# Behavior
max_retries: 3
context_messages: 20                 # Conversation window size
response_timeout: 120                # Max seconds per LLM call
```

### `identity.yaml`
```yaml
name: "Your Name"
alias: "YourAlias"
location: "Your Location"
os: "Arch Linux"
shell: "zsh"

emails:
  - address: "you@gmail.com"
    purpose: [primary, personal]
```

### `SOUL.md`
System hardware and software profile — ARIA reads this to make context-aware decisions about resource usage, compatibility, and optimization.

---

## 📱 Telegram Integration

ARIA operates primarily through **Telegram** as its interface:

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID` as environment variables
3. Start ARIA — it immediately begins listening for your messages

### Telegram Features
- Natural language commands
- File upload/download
- Voice messages (with TTS response)
- Inline keyboard for quick actions
- Research report delivery
- Real-time log streaming

---

## 🔌 API & Services

| Service | Usage | Auth |
|---------|-------|------|
| **NVIDIA NIM** | Primary LLM (Nemotron Ultra 253B) | API key |
| **Google Gemini** | Fallback LLM | API key |
| **Ollama** | Local router model (Qwen 4B) | None (local) |
| **Telegram Bot API** | Primary user interface | Bot token |
| **Google OAuth2** | Gmail, YouTube, Drive integration | OAuth2 flow |
| **SearXNG** | Privacy-respecting search | Self-hosted or public |

---

## 🗺️ Roadmap

### v8.1 (Current)
- [x] Enterprise Manager GUI (14 pages)
- [x] AI Skill Builder (NVIDIA NIM)
- [x] Real-time monitoring dashboard
- [x] 35+ IPC commands
- [x] Deep research engine v4

### v9.0 (Planned)
- [ ] Multi-modal vision (image/video analysis)
- [ ] Agent collaboration (multi-agent task solving)
- [ ] Mobile companion app (Android)
- [ ] Plugin marketplace
- [ ] Distributed agent mesh (multi-machine)
- [ ] RAG-enhanced memory (vector embeddings)
- [ ] Real-time screen understanding

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone
git clone https://github.com/GamerX3560/Aria-V-7.1.git ~/aria
cd ~/aria

# Install dependencies
pip install -r requirements.txt

# Build the GUI
cd aria-enterprise
npm install
npx tauri dev  # Development mode with hot-reload
```

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [GamerX](https://github.com/GamerX3560)**

*ARIA — Because your AI assistant should work for you, not the other way around.*

</div>
