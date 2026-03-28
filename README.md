<div align="center">
  <img src="aria-enterprise/src-tauri/icons/128x128.png" alt="ARIA Logo" width="128" height="128" />
  <h1>ARIA v8.0<br/>Enterprise Context Engine</h1>
  <p><strong>The Ultimate Distributed Autonomous Intelligence Desktop Environment</strong></p>
  
  [![Version](https://img.shields.io/badge/version-8.0.0-blue.svg?style=for-the-badge)](https://github.com/GamerX3560/Aria-V-7.1)
  [![Rust Bridge](https://img.shields.io/badge/Tauri_IPC-Rust-CE412B.svg?style=for-the-badge&logo=rust)](https://tauri.app)
  [![React UI](https://img.shields.io/badge/GUI-React_19-61DAFB.svg?style=for-the-badge&logo=react)](https://reactjs.org)
  [![Backend](https://img.shields.io/badge/Engine-Python_3.12-3776AB.svg?style=for-the-badge&logo=python)](https://python.org)
  [![Platform](https://img.shields.io/badge/OS-Arch_Linux-1793D1.svg?style=for-the-badge&logo=arch-linux)](https://archlinux.org/)
</div>

<br/>

> **ARIA (Antigravity Research Intelligence Assistant)** has evolved from a simple Python CLI tool into a fully distributed, multi-agent AI operating environment. Version 8.0 introduces the **Enterprise Desktop Manager**, a Google Cloud-grade Tauri/React frontend providing unparalleled control over 18 autonomous subsystems, real-time memory contexts, and the dynamic skill matrix.

---

## ⚡ Key Innovations in v8.0

- **🖥️ Enterprise GUI (Desktop Manager):** A brand new React 19 + Tauri 2.0 interface featuring glassmorphic design, 14 advanced panes, and sub-millisecond Rust IPC bridge latency.
- **🧠 Advanced RAG Memory:** ChromaDB-backed vector memory system that ensures hyper-contextual conversation continuity.
- **🕷️ Multi-Layer Browser Agent:** Integrated Scrapling, requests, and Playwright CDP automation for undetectable AI web interaction and scraping.
- **🌐 ARIA Mesh Network:** Distributed processing topology letting multiple devices orchestrate and trade intelligence tasks asynchronously via reverse Cloudflare tunnels.
- **🎛️ Agent Foundry:** Dynamic creation and modification of specialized sub-agents dynamically assembled by the Master Router.

---

## 🏗️ Architecture Overview

The ARIA architecture consists of a highly optimized 4-tier stack:

1. **Frontend View (React 19 + Vite + Zustand):**  
   Provides a massive dashboard including Live Telemetry, Skill Matrix, Agent Foundry, and a fully interactive Command Center. 
2. **IPC Integration Bridge (Tauri + Rust):**  
   Zero-overhead system calls. Processes real-time hardware telemetry (`sysinfo`), filesystem walking for skills, and `systemd` journalctl log streaming natively in Rust before feeding it to React.
3. **Core Orchestration Engine (Python):**  
   The `agent_loop.py` and `router.py` process loop. Manages model routing (Qwen, Llama, Gemma via Ollama/vLLM), async task execution, and sub-agent life cycles.
4. **Execution Layer & Mesh:**  
   Docker sandboxes, native tool execution nodes, and Playwright chromium processes handling the physical side-effects of ARIA's decisions.

---

## 🧩 The 18 Subsystems

ARIA v8 delegates reasoning to specialized sub-modules built inside `core/` and `skills/`:

| Module | Engine | Responsibility |
|:---|:---|:---|
| **Context Engine** | `core.context_engine` | Assembles the sliding context window for exact prompt injection. |
| **Model Router** | `core.model_router` | Dynamically selects the cheapest/fastest LLM for a given task complexity. |
| **Proactive Monitor**| `core.proactive_monitor` | Background worker that checks sys-vitals and throws proactive alerts. |
| **Browser Agent** | `core.browser_agent` | 3-tier scraping engine (HTTP → Scrapling → Remote CDP Playwright). |
| **Vision Engine** | `core.vision_engine` | Fast OCR and zero-shot VLM capability for reading GUI screens. |
| **Voice TTS** | `core.voice_tts` | Offline Piper ONNX speech synthesis with customizable pitch/rate. |
| **Skill Evolver** | `core.skill_evolver` | AI module that watches errors and rewrites its own Python tools to self-heal. |
| **Security Center** | `core.encrypted_storage`| Secures API keys using local hardware encryption. |

---

## 🌌 The Desktop Manager

Navigate to `aria-enterprise/` to access the Tauri-based GUI. The 12 primary domains include:

### Core Ops
*   **Command Center:** Live CPU/RAM/GPU monitoring, service health vitals, and one-click quick action flush commands.
*   **Agent Foundry:** Create, edit, and orchestrate multiple personalized AI agents operating simultaneously.
*   **Skill Matrix:** A file system explorer with an embedded Monaco code editor to view, write, and validate Python sub-routines live.
*   **Context Core:** Read and manipulate the exact ChromaDB vector knowledge chunks currently injected into ARIA's logic.

### Supervision
*   **Live Telemetry:** A stylized terminal pulling live `journalctl` error/info streams from the Python backend service.
*   **Comm-Link:** Standard interaction chat portal with multi-modal attachments.
*   **Task Orchestrator:** CRON-like graphical manager for recurring AI tasks.
*   **Device Mesh:** Visualized topology of all connected remote ARIA nodes.
*   **Browser Agent:** Monitor currently active autonomous webpage parsing or active browser interaction footprints.

---

## 🚀 Installation & Build Guide

### 1. Prerequisites
You must have the following dependencies installed on your system:
- **Rust & Cargo** (For Tauri backend)
- **Node.js (v20+) & npm** (For React frontend)
- **Python 3.12+** (For core intelligence)
- **ChromaDB & Playwright** (Python libraries)
- `systemd` for Linux background execution.

### 2. Backend Engine Initialization
```bash
git clone https://github.com/GamerX3560/Aria-V-7.1.git aria
cd aria

# Install core python intelligence
pip install -r requirements.txt
playwright install --with-deps chromium

# Execute the local daemon
bash setup.sh
```

### 3. Build & Run the Enterprise GUI
To compile the glassmorphic React Dashboard into a native desktop app:

```bash
cd aria-enterprise

# Install JS dependencies
npm install

# Run Desktop App in Development Mode
npx tauri dev

# Compile Release Native Application (.AppImage / .deb / .rpm)
npx tauri build
```

---

## 🔒 Security & Privacy

ARIA v8 is built with a **local-first** paranoia architecture:
*   **Local Inference:** Defaults to strictly local models (e.g., Qwen 2.5 Coder 32B).
*   **Token Vault:** All secret tokens (GitHub, Weather, APIs) are read from `.gitignore` enforced directories `vault/credentials.json`.
*   **Sandboxing:** Execution capabilities can be locked behind the "Sudo Lock" in the Security Center GUI.

---

## 🛠️ Extensibility & Custom Skills

ARIA is a blank canvas. To extend ARIA's capabilities, simply drop a new `.py` file into the `skills/` directory. 
The **Skill Loader** automatically detects new functions decorated with `@aria_skill`, parses their docstrings via AST, and registers them dynamically into the LLM Tool Call schema.

---

<div align="center">
<i>"Intelligence is the ability to adapt to change. ARIA forces the change."</i><br/>
<b>Maintained exclusively by GamerX3560</b>
</div>
