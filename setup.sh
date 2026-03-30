#!/usr/bin/env bash
# ─────────────────────────────────────
# ARIA v6 — Setup Script
# One-command installation for Arch Linux
# ─────────────────────────────────────
set -euo pipefail

BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m"

ARIA_DIR="${HOME}/aria"

echo -e "${BOLD}${CYAN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║         ARIA v6 — Auto Installer         ║"
echo "  ║     Autonomous Agent System Setup        ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Check Prerequisites ──────────────────────────────
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 not found. Installing...${NC}"
    sudo pacman -S --noconfirm python python-pip
fi

if ! command -v pip &> /dev/null; then
    echo -e "${RED}pip not found. Installing...${NC}"
    sudo pacman -S --noconfirm python-pip
fi

echo -e "${GREEN}  ✓ Python $(python3 --version | cut -d' ' -f2)${NC}"

# ─── Create Directory Structure ─────────────────────────
echo -e "${YELLOW}[2/6] Setting up directory structure...${NC}"

mkdir -p "${ARIA_DIR}/core"
mkdir -p "${ARIA_DIR}/agents"
mkdir -p "${ARIA_DIR}/skills"
mkdir -p "${ARIA_DIR}/memory/conversations"
mkdir -p "${ARIA_DIR}/logs"

echo -e "${GREEN}  ✓ Directory structure created${NC}"

# ─── Install Python Dependencies ──────────────────────
echo -e "${YELLOW}[3/6] Installing Python dependencies...${NC}"
pip install --user -r "${ARIA_DIR}/requirements.txt" 2>&1 | tail -5

echo -e "${GREEN}  ✓ Dependencies installed${NC}"

# ─── Install System Tools ───────────────────────────────
echo -e "${YELLOW}[4/6] Installing system tools...${NC}"

SYSTEM_PKGS=(
    "ripgrep"       # Ultra-fast recursive search
    "ffmpeg"        # Media transcoding
    "nnn"           # Terminal file manager
    "glances"       # System monitoring
    "wf-recorder"   # Wayland screen recording
    "grim"          # Screenshot tool
    "slurp"         # Region selection
    "scrcpy"        # Android mirroring
)

for pkg in "${SYSTEM_PKGS[@]}"; do
    if ! command -v "$pkg" &> /dev/null 2>&1; then
        echo -e "  Installing ${pkg}..."
        yay -S --noconfirm "$pkg" 2>/dev/null || true
    fi
done

echo -e "${GREEN}  ✓ System tools checked${NC}"

# ─── Setup Playwright (for browser automation) ─────────
echo -e "${YELLOW}[5/6] Setting up browser automation...${NC}"
python3 -m playwright install chromium 2>/dev/null || echo "  ⚠ Playwright setup skipped (optional)"

echo -e "${GREEN}  ✓ Browser automation ready${NC}"

# ─── Environment Variables ────────────────────────────
echo -e "${YELLOW}[6/6] Checking environment...${NC}"

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
    echo -e "${YELLOW}  ⚠ TELEGRAM_BOT_TOKEN not set.${NC}"
    echo -e "  Export it: ${CYAN}export TELEGRAM_BOT_TOKEN=your_token${NC}"
fi

if [ -z "${TELEGRAM_USER_ID:-}" ]; then
    echo -e "${YELLOW}  ⚠ TELEGRAM_USER_ID not set.${NC}"
    echo -e "  Export it: ${CYAN}export TELEGRAM_USER_ID=your_id${NC}"
fi

echo ""
echo -e "${BOLD}${GREEN}  ╔══════════════════════════════════════════╗"
echo "  ║         ARIA v6 Setup Complete! ✓        ║"
echo "  ╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Start ARIA:  ${CYAN}python3 ~/aria/router.py${NC}"
echo -e "  Bot commands: /status, /reset, /memory, /skills, /save, /reload"
echo ""
