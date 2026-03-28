<div align="center">
  <img src="aria-enterprise/src-tauri/icons/128x128.png" alt="ARIA Logo" width="128" height="128" />
  <h1>ARIA v8.0<br/>Enterprise Context Engine & OS Intelligence</h1>
  <p><strong>The Ultimate Distributed, Privacy-First Autonomous AI Operating Environment</strong></p>
  
  [![Version](https://img.shields.io/badge/version-8.0.0-blue.svg?style=for-the-badge)](https://github.com/GamerX3560/Aria-V-7.1)
  [![Rust Bridge](https://img.shields.io/badge/Tauri_IPC-Rust-CE412B.svg?style=for-the-badge&logo=rust)](https://tauri.app)
  [![React UI](https://img.shields.io/badge/GUI-React_19-61DAFB.svg?style=for-the-badge&logo=react)](https://reactjs.org)
  [![Backend](https://img.shields.io/badge/AI_Engine-Python_3.12-3776AB.svg?style=for-the-badge&logo=python)](https://python.org)
  [![Platform](https://img.shields.io/badge/Target_OS-Arch_Linux_Wayland-1793D1.svg?style=for-the-badge&logo=arch-linux)](https://archlinux.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

<br/>

> **ARIA (Antigravity Research Intelligence Assistant)** is far more than a simple chatbot or script. It is a completely autonomous, multi-agent operating environment designed to deeply integrate with your physical OS (Arch Linux/Wayland), hardware architectures (AMD ROCm), and personal data structure. Version 8.0 couples a highly advanced autonomous execution ring with a Google Cloud-grade Tauri/React frontend dashboard. 

---

## ⚡ 1. The ARIA Vision & Core Tenets

ARIA is built with extreme paranoia and uncompromised local-first methodology. 

1. **Hardware Native (No NVIDIA Required):** ARIA explicitly avoids CUDA lock-in, optimizing AI workloads across AMD GPUs via ROCm and PyTorch OpenCL integrations. 
2. **Infinite Execution Stability:** AI models hallucinate. Rather than crashing, ARIA expects failure. The `agent_loop.py` incorporates stuck-detection, auto-correction algorithms, and duplicate-command evasion to keep ARIA working over hundreds of consecutive sub-tasks.
3. **Data Paranoia Vault:** No secrets exist in code. All GitHub keys, LLM tokens, and API webhooks are injected via the Git-ignored `vault/` directory with explicit memory scrubbing rules.
4. **Wayland & PipeWire Native:** Full integration with Hyprland screen captures, `ydotool` emulated keypresses, `wl-clipboard` interceptors, and Piper offline text-to-speech routing.

---

## 🧠 2. The Intelligence Core (Backend Python Architecture)

ARIA's brain consists of 18 meticulously separated Python modules operating inside `core/`. These form the "Exoskeleton" of the reasoning agent:

### Reasoning & Memory
*   **`core.context_engine`**: The exact context injector. It splices system configurations, API schemas, user preferences, and the exact directory contents before calling the LLM—guaranteeing 0-shot coding success by feeding the model undeniable reality.
*   **`core.rag_memory`**: A hybrid ChromaDB vector database and episodic JSON ledger system. It separates "active working memory" (short context window) from "long term semantic memory", recalling your preferences seamlessly weeks later.
*   **`core.model_router`**: ARIA is model agnostic. This router dynamically balances cost, speed, and intelligence. It can route menial bash tasks to local 7B models, complex UI mapping to Vision-Language Models, and intense mathematical reasoning to massive 32B cloud models (NVIDIA endpoints).
*   **`core.planner`**: A structural directed-acyclic-graph (DAG) creator. When given a massive objective ("Write a full game"), it fragments the workload into a checklist, operating as an autonomous software director.

### Sensory & Motor Control
*   **`core.browser_agent`**: A hybrid stealth web navigator. It dynamically switches between raw `httpx` logic, Javascript-executing headless `scrapling`, and remote Chrome DevTools Protocol (`Playwright CDP`) evasion techniques to bypass Bot Protection grids. 
*   **`core.vision_engine`**: Connects directly to Wayland `grim` or `slurp` to take instantaneous screenshots. It runs localized Tesseract OCR for text reading or zero-shot VLM parsing so ARIA can physically "see" your desktop interfaces.
*   **`core.voice_tts`**: Offline, instantaneous text-to-speech processing utilizing Piper ONNX binaries, allowing ARIA to verbalize critical proactive alerts or chat functionality directly to your speakers.

### System Safety & Healing
*   **`core.proactive_monitor`**: A relentless watcher. Checks `systemd` error logs, CPU thermals, and memory overloads. If an app crashes, ARIA can automatically diagnose the dump log before you even realize a crash occurred.
*   **`core.skill_evolver`**: Truly evolutionary code. If ARIA uses a Python tool and it crashes due to a library update, the Evolver reads the AST traceback, writes a patch to fix the script, overwrites the python file, and resumes operation seamlessly.

---

## 🕸️ 3. The ARIA Action Matrix (Skills & Sub-Agents)

ARIA's reach extends through the `skills/` directory—a registry of 30+ highly specialized python plugins parsed on script startup. By annotating a function with `@aria_skill`, it instantly becomes an actionable Tool-Call Schema for the LLM. 

<details>
<summary><b>🛠️ View the Full 30+ Skill Roster</b></summary>
<br>

| Domain | Skill Script | Capability |
| :--- | :--- | :--- |
| **Deep Research** | `deep_research_v4.py` | 6-stage web crawler combining Reddit, HN, GitHub APIs, and local personal-data hooks into triple-pass LLM syntheses. |
| **Mesh Network** | `mesh_agent.py` | Exposes local ARIA reasoning over a Cloudflare Tunnel reverse proxy for remote cross-device collaboration. |
| **System Security** | `network_security_scanner.py` | Autonomous Nmap parsing, vulnerability assessments, and local systemd log auditing. |
| **OS Control** | `desktop_agent.py` | `ydotool` window clicker, `hyprctl` window switcher, volume adjustments via Pipewire control. |
| **Local LLM** | `local_llm_inference.py` | Offline model loading when disconnected from the internet. |
| **Vision & UI** | `computer_vision_ocr.py` | Real-time desktop coordinate calculations via OCR matrix mappings. |
| **Data Syncer** | `data_backup_encrypted.py` | Hardware-encrypted tarball archives synced across connected ADB Android phones or separate drives. |
| **Media** | `movies4u_downloader.py`, `media_transcoding_amd.py` | CLI media scrapers utilizing OpenCL encoding via AMD RDNA hardware. |
| **File Manipulation**| `pdf_manipulation.py`, `image_editor.py` | Merge, split, read PDFs. Crop, watermark, or auto-enhance images blindly via Pillow. |
| **Automation** | `android_adb_automation.py` | Rooted Android UI manipulation, scrcpy integration, tapping, swiping, pushing APKs. |
| **Work ERP** | `adypu_erp_login.py` | Intricate web automation for university/employment ERP portals, extracting assignments seamlessly. |
| **Crypto/Password**| `password_manager_cli.py` | Interface wrapper for `pass` or Bitwarden, decrypting logic strictly in isolated memory segments. |
| **File Systems** | `terminal_file_manager.py` | Advanced regex-based grepping, zsh script executions, dynamic permission audits. |

</details>

---

## 🌐 4. Device Mesh Integration

ARIA is not bound to a single local machine. Using `core/aria_mesh.py`, the system establishes secure encrypted payloads over reversed Cloudflare tunnels. This allows multiple machines (Desktop, Laptop, Raspberry Pi nodes) to trade tokenized commands. 

- **Swarm Intelligence:** If your low-powered laptop needs to process an intense Deep Research report, it can offload the computation through the ARIA Mesh to your main Arch Desktop node.
- **REST Telemetry:** The Mesh exposes a 12-endpoint FastAPI server to interact programmatically with ARIA's internals.

---

## 🌌 5. Enterprise GUI Overview (React + Tauri)

Built to mimic the complexity of Google Cloud Console, the `aria-enterprise` dashboard is a masterclass in frontend integration.

### Structural Design & Styling
We utilize highly customized CSS modules providing deep **Glassmorphic** design elements (`backdrop-filter: blur(16px)`), complex animated gradients, absolute responsive grid frameworks, and extremely curated syntax highlighting. No Tailwind—just performant, absolute raw CSS architectures.

### Functional Domains
The dashboard dynamically parses the 18 backends via a zero-overhead Rust IPC Bridge (`/src-tauri/src/lib.rs`). 

1.  **Command Center:** Live Recharts CPU load mappers, instantly triggering background agent tasks, global pause switches.
2.  **Agent Foundry:** Spawn, name, and modify specialized agents. Create a "Coder Agent" restricted to `skills/` executing, while a "Research Agent" operates simultaneously.
3.  **Live Telemetry:** Forget `tail -f`. The Telemetry dash natively binds to `journalctl -u aria` parsing ERROR/INFO flags with colored regex spans.
4.  **Device Mesh:** A visual network mapping tool to oversee connected hardware nodes.
5.  **Skill Matrix:** An embedded Monaco code editor providing local syntax checks on your Python skills. Update a skill graphically—ARIA reloads its memory pipeline seamlessly.
6.  **Browser Agent:** Monitor active web-scraping footprints, block list metrics, and cache statuses.
7.  **Personal Info (Context Core):** Direct JSON manipulation of your identity schemas (`identity.yaml`) feeding directly into ARIA's prompt.
8.  **Automations / Cron Tasks:** A structural DAG viewer for scheduling recurring system commands. 
9.  **Comm-Link:** The chat bridge. Attach directories, images, or PDFs to chat prompts instantly using optimized multi-modal protocols.
10. **Security Center:** Edit Vault configurations. Activate the `Sudo Lock`—a permission layer rejecting potentially destructive actions without MFA.
11. **Models / LLMs:** Adjust inference endpoints from Ollama to vLLM to generic OpenAI protocols with real-time ping latency charts.
12. **Workspace:** Overview and hot-swaps of working directories preventing ARIA from scanning invalid trees.

---

## 🚀 6. Installation & Deployment Architecture

Due to the convergence of Python backend logic and Rust Frontend compilations, follow these strict steps. 

### Step 1: Core System Prerequisites (Arch Linux)
```bash
# ARIA requires rigorous structural tooling on Wayland/Arch environments:
sudo pacman -S base-devel rust cargo nodejs npm jq \
               webkit2gtk tesseract tesseract-data-eng \
               chromium poppler curl ydotool wl-clipboard
```

### Step 2: Bootstrapping the Python Engine
ARIA exclusively supports Python 3.12+ virtual environments to prevent library conflicts with Arch Linux's rigid pacman python structure.
```bash
git clone https://github.com/GamerX3560/Aria-V-7.1.git aria
cd aria

# Isolate the environment
python -m venv .venv
source .venv/bin/activate

# Install the monstrous requirement matrix
pip install -r requirements.txt
playwright install --with-deps chromium

# Initialize structural subdirectories and background keys
bash setup.sh
```

### Step 3: Compiling the Rust/Tauri Enterprise Dashboard
The UI exists inside `/aria-enterprise`.

```bash
cd aria-enterprise

# Sync massive Node modules (React 19, Zustand, Recharts, Lucide, Monaco)
npm install

# Start the interactive UI in Debug Watch Mode (ideal for developing UI)
npx tauri dev

# Compile the highly-optimized standalone Native Desktop Release Binary
npx tauri build
```
The compiled binary outputs to `/aria-enterprise/src-tauri/target/release/app`. Execute it directly or link it to `~/.local/share/applications/aria.desktop` for system search availability.

---

## 🔒 7. Advanced Configurations & Security Paranoia

By design, all API keys or context settings must not be pushed. They are mapped out in structural YAML / JSON files located at the project root:

*   **`identity.yaml`**: Your persona. Who are you? What hardware do you run? What shells do you prefer? ARIA reads this into its memory upon boot so you never have to repeat "use zsh, not bash".
*   **`config.yaml`**: Define your model endpoints (e.g. `base_url: http://localhost:11434/v1`), token limits, fallback models, and telemetry polling intervals.
*   **`vault/credentials.json`**: This file is completely ignored by Git. Here lies your massive `NVIDIA_API_KEY`, `GITHUB_TOKEN`, or Cloudflare tunnel secrets. ARIA's `encrypted_storage.py` parses this strictly in memory upon boot.
*   **`memory.json`**: The episodic ledger. If it grows too large, the DAG planner automatically runs a summary compression loop in the background, pruning dead data while retaining semantic weights.

---

## 🤝 8. Expanding the Ecosystem

Extending ARIA is as simple as dropping a new python logic file into `/skills`. 

```python
# Example: skills/my_new_skill.py
from core.skill_loader import aria_skill

@aria_skill
def format_user_drive(disk_name: str) -> str:
    """
    Destroys the user disk. ARIA reads this docstring automatically to understand what the skill does.
    """
    return "Complete! Awaits further instructions."
```

Upon restart, `skill_loader.py` uses AST parsing to serialize the docstring and function parameters directly into a JSON Tool Call Schema for the LLM. No rigid boilerplate required.

---

<div align="center">
<i>"Intelligence is the ability to adapt to change. ARIA doesn't adapt. ARIA forces the change."</i><br/>
<b>Written and Maintained exclusively by GamerX3560</b>
</div>
