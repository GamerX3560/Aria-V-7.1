<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-success.svg">
  <img src="https://img.shields.io/badge/Version-7.1-blue.svg">
  <img src="https://img.shields.io/badge/Python-3.14+-blue.svg">
  <img src="https://img.shields.io/badge/License-MIT-green.svg">
</p>

<h1 align="center">🤖 ARIA V-7.1 — Autonomous Jarvis-Level AI System</h1>

<p align="center">
  <b>A deeply integrated, autonomous AI agent capable of managing your system, executing complex tasks, learning new skills, and proactively monitoring your digital life.</b>
</p>

---

## 🌟 What is ARIA?

ARIA (Artificial Responsive Intelligence Agent) is not just another chatbot. It is a fully modular, locally-aware AI ecosystem built around a highly advanced **Agent Loop Architecture**. 

Taking inspiration from systems like Jarvis, ARIA is designed to run silently in the background, capable of:
- **Executing Terminal Commands:** Safely interacting with your Linux environment.
- **Synthesizing Speech:** Speaking back with neural TTS (`piper`).
- **Seeing your Screen:** Utilizing grim/tesseract for localized Vision.
- **Remembering Everything:** Leveraging `ChromaDB` for persistent Vector RAG memory.
- **Learning New Skills:** Automatically writing, testing, and incorporating its own python tools into its `skills/` directory.

---

## 🏗️ The 12-Module Architecture

ARIA 7.1 is built on a massive 12-pillar framework:

1. **🧠 Autonomous Agent Loop:** The core engine that plans, executes, and verifies tasks in a loop without needing continuous human prompting.
2. **🗃️ Vector RAG Memory:** (Powered by `ChromaDB`) ARIA remembers past conversations, system states, and preferences across reboots.
3. **⚙️ Tool Executor:** A strict, secure bash/python executor with Regex blocklists to prevent catastrophic commands (e.g., `rm -rf /`).
4. **🧠 Model Router:** Automatically routes cheap tasks to fast local models, and complex coding tasks to heavy 32B models.
5. **👁️ Vision Engine:** Grabs screen context, active windows, and clipboard data on demand.
6. **🗣️ Voice TTS:** Neural Text-to-Speech using `piper-tts`, supporting seamless male/female voice switching. *(LuxTTS GPU Voice coming soon)*.
7. **🔌 Skill Loader:** Hot-reloads custom Python plugins from the `skills/` directory.
8. **🧬 Skill Evolver:** ARIA can literally write its own skills when it discovers a missing capability, tests them, and saves them.
9. **🌐 Device Mesh:** A master-slave SSH orchestrator allowing ARIA to execute commands on your Android phone or remote servers.
10. **⏱️ Proactive Monitor:** A background Async daemon that watches system health, RSS feeds, and logs, alerting you via Telegram *before* you ask.
11. **🎭 Personality Engine:** Dynamically shifts tone, style, and responses based on the length and mood of your messages.
12. **🔒 Encrypted Storage:** AES-256 Fernet encrypted key value store. No plaintext API keys on disk!

---

## 🚀 Getting Started

### 1. Requirements

- Arch Linux (or a Debian-based distro with minor path tweaks)
- Python 3.12+ 
- `yay` (or your preferred AUR helper)

### 2. Installation

Clone the repository and install the required system tools:

```bash
git clone https://github.com/GamerX3560/Aria-V-7.1.git
cd Aria-V-7.1

# 1. Install System Dependencies
./install.sh

# 2. Setup Python Environment
pip install -r requirements.txt --break-system-packages

# 3. Setup configurations
cp identity.example.yaml identity.yaml
cp vault.example.json vault.json
```

**Edit your `vault.json`** to include your API keys:
```json
{
  "nvidia_api_key": "nvapi-...",
  "telegram_bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
  "telegram_user_id": "123456789"
}
```

### 3. Setup Piper TTS (Optional but Recommended)
For natural voice synthesis, ARIA relies on `piper-tts`.

On Arch Linux:
```bash
yay -S piper-tts
```
Download models (e.g. `en_US-lessac-medium.onnx`) into `~/.local/share/piper-voices/`. ARIA looks for `piper` in `/opt/piper-tts/piper`.

---

## 💻 Usage

Start ARIA in the terminal. It will connect to the Telegram Bot API and begin polling.

```bash
python3 router.py
```

### Essential Telegram Commands:
- `/status` — View ARIA's core diagnostic health (RAG entries, Mesh status, Memory usage).
- `/reset` — Wipe the current short-term conversation context (RAG is unaffected).
- `/skills` — List all currently loaded Python skills.
- `/test` — Run the 15-module internal diagnostic suite to verify all systems.

---

## 🔒 Security

**ARIA has ROOT-level potential.** Use at your own risk.
- The `tool_executor.py` contains a strict blocklist.
- `router.py` ONLY allows messages from the `telegram_user_id` specified in the vault. **Everyone else is ignored.**
- API keys are automatically ingested and migrated to a `AES-256 Fernet` encrypted `.enc` vault on first launch.

---

## 🤝 Contributing

This is a personal JARVIS implementation by **GamerX3560**, but community patches are welcome! Check out the `skills/` directory to see how easy it is to write a new tool for ARIA.

---
*Built with ❤️ and excessive caffeine*
