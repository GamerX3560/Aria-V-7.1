<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-success.svg?style=for-the-badge&logo=github">
  <img src="https://img.shields.io/badge/Version-7.1_Codename_Jarvis-blue.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/Python-3.12+-blue.svg?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge">
  <img src="https://img.shields.io/badge/Platform-Linux_|_Arch-orange.svg?style=for-the-badge&logo=archlinux">
  <br><br>
  <h1>🤖 ARIA V-7.1</h1>
  <h3>Autonomous Responsive Intelligence Agent</h3>
  <p><b>Your Personal, Local, Self-Hosting, Jarvis-Level Artificial Intelligence System</b></p>
  <br>
</div>

---

## 📖 Table of Contents
1. [Introduction & Philosophy](#-introduction--philosophy)
2. [What Makes ARIA Different?](#-what-makes-aria-different)
3. [The 12-Pillar Core Architecture](#-the-12-pillar-core-architecture)
4. [Deep Dive into Modules](#-deep-dive-into-modules)
5. [Hardware & Software Requirements](#-hardware--software-requirements)
6. [Detailed Installation Guide](#-detailed-installation-guide)
7. [Configuration & Storage](#-configuration--storage)
8. [Usage & Commands](#-usage--commands)
9. [Skills Ecosystem & Evolver](#-skills-ecosystem--evolver)
10. [Releases & Changelog](#-releases--changelog)
11. [Roadmap for V-8.0](#-roadmap-for-v-80)
12. [Security & Privacy](#-security--privacy)
13. [Contributing](#-contributing)
14. [License](#-license)

---

## 🌟 Introduction & Philosophy

Welcome to the **ARIA V-7.1** ecosystem. ARIA (Artificial Responsive Intelligence Agent) is not just another wrapper for an LLM API. It is a deeply integrated, autonomous operating system agent designed to act as your personal "Jarvis." 

Built entirely in Python, ARIA bridges the gap between conversational AI and system-level automation. Instead of you telling an AI what to do and copying its code, ARIA **executes** the code on your behalf, navigating your filesystem, monitoring your background processes, visually seeing your screen, natively processing external API responses, and speaking back to you with zero latency. 

The philosophy behind ARIA is **Maximum Autonomy with Maximum Privacy**. ARIA operates locally on your Linux machine, encrypts its own configuration, remembers everything you say via a local Vector Database, and controls an entire mesh network of your personal devices.

---

## 🚀 What Makes ARIA Different?

- **True Agentic Autonomy:** ARIA doesn't just reply with text; it runs a multi-agent loop. If you ask ARIA to "find the large files taking up disk space, delete `.tmp` files, and email me a report," ARIA will break this down into three sequential tasks, execute them safely via its Tool Executor, verify the results, and only then respond to you.
- **RAG Memory Integration:** Utilizing ChromaDB, every conversation, preference, and command is embedded into a high-dimensional vector space. ARIA remembers what you said 3 months ago with sub-second retrieval times.
- **Skill Evolution:** ARIA possesses the unique ability to **write its own tools**. If you ask it to perform a task it doesn't have a mapped skill for, it will use its `SkillEvolver` to dynamically generate a Python script, place it in the `skills/` directory, hot-reload itself, and execute the newly learned skill.
- **Proactive Notification:** ARIA doesn't wait for you to type. It runs a daemon thread (`proactive_monitor.py`) that monitors your PC's CPU temps, RAM usage, and RSS feeds. It will proactively message your Telegram directly if something requires your attention.

---

## 🏗️ The 12-Pillar Core Architecture

ARIA V-7.1 is structured around 12 robust, highly decoupled core modules located in the `core/` directory:

1. **🧠 Autonomous Agent Loop (`agent_loop.py`):** The beating heart of ARIA. Implements the continuous Thought-Action-Observation loop.
2. **🗃️ Vector RAG Memory (`rag_memory.py`):** The local `ChromaDB` integration utilizing `all-MiniLM-L6-v2` embeddings for long-term spatial memory.
3. **⚙️ Secure Tool Executor (`tool_executor.py`):** The sandbox where ARIA interacts with the Linux shell securely via a strict Regex blocklist.
4. **🧠 Intelligence Router (`model_router.py`):** Intelligently routes straightforward queries to fast edge models, while sending heavy coding/logic queries to frontier 32B/70B models to save costs and latency.
5. **👁️ Vision Engine (`vision_engine.py`):** Utilizes `grim`, `tesseract`, and Wayland tools to extract OCR text from your active windows and read your clipboard.
6. **🗣️ Voice & Audio TTS (`voice_tts.py`):** Neural Text-to-Speech using the lightning-fast `piper-tts` engine. Supports hot-swapping between male, female, and custom trained ARIA voices depending on context.
7. **🔌 Dynamic Skill Loader (`skill_loader.py`):** Auto-discovers and hot-reloads modular Python `.py` tools from the `skills/` directory at runtime.
8. **🧬 Skill Evolver (`skill_evolver.py`):** The self-improving metacognitive module allowing ARIA to write code to expand its own capabilities.
9. **🌐 Device Mesh (`device_mesh.py`):** Orchestrates commands across multiple machines (e.g., executing scripts on your rooted Android phone via SSH/ADB).
10. **⏱️ Proactive Monitor (`proactive_monitor.py`):** A persistent Asyncio background task evaluating system states autonomously.
11. **🎭 Personality Engine (`personality.py`):** Analyzes semantic sentiment and adjusts ARIA's textual tone (e.g., shifting from "professional" to "excited" or "sympathetic").
12. **🔒 Encrypted Storage (`encrypted_storage.py`):** AES-256 Fernet zero-configuration transparent encryption wrapper for all local files, logs, and API credentials.

---

## 🔍 Deep Dive into Modules

### The RAG Memory System
By default, standard LLM contexts overflow rapidly. ARIA V-7.1 destroys this limitation by combining a sliding window of short-term memory (the last N messages) alongside a ChromaDB instance natively mounted in `memory/rag/chromadb`. 
When you ask a question, the `rag_memory.py` module computes the cosine similarity of your query against the entire historical database, instantly injecting relevant context into the hidden system prompt.

### Encrypted AES-256 Keyring
When you first launch ARIA, the `encrypted_storage.py` module creates a secure cryptographic key (stored locally at `~/.aria_key` protected by strict `chmod 600` Linux user permissions). All configuration parameters, your `vault.json` API keys, and sensitive logs are immediately stripped from plain text and stored as `.enc` binaries. ARIA auto-decrypts them dynamically in volatile RAM only when an agent process explicitly requires the tokens.

### Neural TTS Synthesis
Gone are the days of robotic `espeak`. ARIA V-7.1 integrates `piper-tts` directly into the agent response handler. Audio generation happens locally on-device. Responses are piped through `aplay` (or PipeWire/PulseAudio) in milliseconds.

---

## 💻 Hardware & Software Requirements

ARIA is built by Linux Enthusiasts, for Linux Enthusiasts. 

**Recommended System Specs:**
- **OS:** Arch Linux / Manjaro / Debian 12+ (Wayland/Hyprland heavily preferred for Vision capabilities).
- **CPU:** 4+ Cores (Native x86_64).
- **RAM:** 8GB Minimum (16GB Recommended if running local smaller models).
- **Optional GPU:** For future LuxTTS or local LLM acceleration.
- **Python:** Highly optimized for Python 3.12, 3.13, and 3.14.

**Required Linux Packages:**
```bash
# Arch Linux Dependencies
sudo pacman -S git python-pip curl ffmpeg grim tesseract tesseract-data-eng espeak-ng xclip wayland
# Piper (AUR)
yay -S piper-tts
```

---

## ⚙️ Detailed Installation Guide

Follow these instructions to safely bootstrap ARIA onto your machine.

### 1. Clone the Repository
```bash
git clone https://github.com/GamerX3560/Aria-V-7.1.git
cd Aria-V-7.1
```

### 2. Scaffold the Virtual Environment
We strongly recommend running ARIA in an isolated environment.
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Initialize Placeholders
ARIA requires personal configurations mapped to the `vault.json` and `identity.yaml`. We have provided `.example` templates.
```bash
cp identity.example.yaml identity.yaml
cp vault.example.json vault.json
```

---

## 🔐 Configuration & Storage

Open `vault.json` in your favorite editor (`neovim`, `nano`, `vscode`) and insert your real tokens. 

```json
{
  "nvidia_api_key": "YOUR_LLM_PROVIDER_API_KEY",
  "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "telegram_user_id": "YOUR_UNIQUE_TELEGRAM_ID"
}
```

*Note: Immediately upon the first successful launch (`python3 router.py`), ARIA will parse your `vault.json`, encrypt it into `memory/encrypted_vault.enc`, and securely consume the API keys. You will never need to worry about accidentally uploading your tokens to GitHub.*

Modify `identity.yaml` to tailor ARIA to your specific personality preferences, constraints, and professional operating name.

---

## 📱 Usage & Commands

Running ARIA is fully headless. ARIA is accessed locally but controlled completely securely through **Telegram**. This means you can control your Desktop PC from anywhere in the world on your smartphone.

```bash
# Start the main Router Daemon
python3 router.py
```

### Essential Chat Commands (via Telegram UI)
- `/start` — Wakes ARIA up and initializes the memory session.
- `/status` — Fetches a comprehensive diagnostic report detailing CPU RAM usage, RAG entries counted, Device Mesh targets, Voice backend currently engaged, and active Skills.
- `/reset` — Clears volatile short term contextual memory without deleting the permanent ChromaDB vectors.
- `/memory` — Dumps analytical stats regarding how many conversational nodes exist.
- `/skills` — Lists all custom tools ARIA has access to.
- `/vision` — Forces ARIA to capture your current desktop window and interpret what is on the screen contextually.
- `/test` — Executes the majestic 15-module suite found in `test_aria.py` verifying system integrity.

---

## 🛠️ Skills Ecosystem & Evolver

The `skills/` directory is the extensible playground of ARIA. 
Skills are standard python files exposing an `execute()` function and mapped syntactically through docstrings. 
Example skills natively included in V-7.1:
- `system_info.py`: Fetch disk space, meminfo, and OS version.
- `movies4u_downloader.py`: Specialized scraper module.
- `web_search.py`: Navigates DuckDuckGo natively.

**The Skill Evolver:**
If you command ARIA to "Calculate the specific gravity of the current moon phase", ARIA will automatically realize it lacks the tool. The Agent Loop will transition to the `SkillEvolver`, formulate Python code leveraging `ephem` or API requests, save it as `moon_phase.py`, load it dynamically without a restart, and fulfill your initial command. It effectively writes its own API integrations.

---

## 📦 Releases & Changelog

### V-7.1 (Codename: Jarvis Complete) — *Current Release*
- **Massive Refactor:** Deprecated the monolithic `antigravity_bot.py`.
- **Introduced 12-Tier Modular Core:** Decoupled architecture deployed natively.
- **RAG ChromaDB Engine:** Full migration from flat-file JSON dict-matching to embedding-based semantic spatial searching.
- **Encrypted Filesystem:** Integrated the `cryptography` Fernet API block, locking all `.json` payload keys at rest.
- **Proactive Cron Subsystem:** Asynchronous `proactive_monitor.py` enabled daemon mode out of the box.

### V-6.0 (Codename: Sight & Sound)
- **Vision Integration:** Successfully deployed Wayland-based OCR screenshots.
- **Piper Neural TTS:** Swapped backend from standard robotic `espeak`. Model pipeline fully working.

### V-5.0 (Codename: Evolution)
- Introduced `SkillEvolver` functionality.
- Sandboxed the `ToolExecutor` shell bash wrapper heavily.

---

## 🗺️ Roadmap for V-8.0

The development does not stop here. We are actively working towards the next generational leap for ARIA.
1. **Advanced DOM Browser Agent:** Full, autonomous interaction with complex javascript DOM websites (logging into banks, filling out multi-page web forms) utilizing a hybrid of `Scrapling` + `browser-use`.
2. **Multi-ARIA Mesh Networks:** Decentralized Master-Master API protocols where ARIA instances running on Laptops, Desktops, and Android phones concurrently share JSON task delegations and synchronize RAG memory instances locally.
3. **LuxTTS VRAM Activation:** Supporting `<1GB` GPU dependent Ultra-realistic voice cloning generation natively tied to AMD ROCm/Nvidia CUDA environments at 150x speeds.

---

## 🛡️ Security & Privacy

ARIA treats your local environment as a fortress:
1. **No Telemetry:** ARIA dials out ONLY to the LLM API provider configured in your vault, and your securely encrypted personal Telegram loop. There is zero tracking.
2. **Regex Filter Execution:** By default, bash execution pathways via the `ToolExecutor` will explicitly intercept and neutralize destructive commands like `rm -rf`, `mkfs`, `dd`. 
3. **Restricted Auth:** The `router.py` polling thread actively drops any and all chat messages or prompts sent from Telegram IDs that **do not exclusively match** the unique integer you provide. Your instance cannot be hijacked by strangers.

---

## 🤝 Contributing

Contributions are welcomed, particularly inside the `skills/` directory. 
If you have written a novel, optimized, or interesting Python utility skill that ARIA can utilize:
1. Fork the Repository.
2. Drop your `your_skill.py` into the `skills/` folder.
3. Ensure it contains a robust, LLM-readable docstring.
4. Submit a Pull Request.

---

## 📝 License

This project is open-sourced software licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2026 GamerX3560

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">
  <b>Built with ❤️ by GamerX3560</b><br>
  <i>"For when answering a question isn't enough; the AI must do the work."</i>
</div>
