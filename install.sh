#!/bin/bash
# ╔══════════════════════════════════════════════════════════╗
# ║  ARIA v4 Interactive Installer                           ║
# ║  Automates dependencies, services, and environment       ║
# ╚══════════════════════════════════════════════════════════╝

set -e

echo -e "\n\033[1;36m[ARIA]\033[0m Starting ARIA v4 Installation..."

# 1. Install System Dependencies
echo -e "\n\033[1;35m==> Installing Arch dependencies...\033[0m"
sudo pacman -S --needed --noconfirm python python-pip git grim slurp tesseract tesseract-data-eng piper-tts-bin pw-play mpv python-pyaudio

# 2. Install Python Dependencies
echo -e "\n\033[1;35m==> Installing Python dependencies...\033[0m"
pip install --break-system-packages -r requirements.txt || pip install --user -r requirements.txt || echo "Please install python dependencies manually via uv/pip."
pip install --break-system-packages python-telegram-bot requests asyncio subprocess pathlib re json time threading numpy pyaudio SpeechRecognition faster-whisper openwakeword ctranslate2 onnxruntime scipy scikit-learn sympy flatbuffers pytesseract Pillow pyyaml

# 3. Setup Directories
echo -e "\n\033[1;35m==> Configuring directories...\033[0m"
mkdir -p ~/aria/voice/models
mkdir -p ~/aria/skills
mkdir -p ~/.config/systemd/user

# 4. Download Piper Model (if not exists)
MODEL_PATH="$HOME/aria/voice/models/en_US-lessac-medium.onnx"
if [ ! -f "$MODEL_PATH" ]; then
    echo -e "\n\033[1;35m==> Downloading TTS Voice Model...\033[0m"
    wget -O "$MODEL_PATH" "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    wget -O "${MODEL_PATH}.json" "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
fi

# 5. Secure Sensitive Files
echo -e "\n\033[1;35m==> Securing identity and vault files...\033[0m"
touch ~/aria/vault.json ~/aria/memory.json ~/aria/identity.yaml
chmod 600 ~/aria/vault.json ~/aria/memory.json ~/aria/identity.yaml

# 6. Install Systemd Services
echo -e "\n\033[1;35m==> Installing systemd services...\033[0m"
cat > ~/.config/systemd/user/jarvis.service << 'EOF'
[Unit]
Description=ARIA v4 Hybrid Router Daemon
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/aria
ExecStart=/usr/bin/python3 %h/aria/router.py
Restart=always
RestartSec=3
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=%h/aria/.env
Environment="WAYLAND_DISPLAY=wayland-1"
Environment="XDG_RUNTIME_DIR=/run/user/1000"

[Install]
WantedBy=default.target
EOF

cat > ~/.config/systemd/user/aria-voice.service << 'EOF'
[Unit]
Description=ARIA Voice Interface (Wake Word + STT)
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/aria
ExecStart=/usr/bin/python3 %h/aria/voice/listener.py
Restart=always
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now jarvis.service aria-voice.service

echo -e "\n\033[1;32m[SUCCESS]\033[0m ARIA v4 has been successfully installed and started!"
echo -e "Check status with: \033[1mjournalctl --user -u jarvis.service -f\033[0m"
