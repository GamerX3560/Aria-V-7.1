#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║        🧠 ARIA — Autonomous Real-time Intelligent Agent      ║
# ║                    Installation Script v8.1                   ║
# ║                                                               ║
# ║        Built by GamerX • github.com/GamerX3560                ║
# ╚══════════════════════════════════════════════════════════════╝
set -euo pipefail

# ─── Colors & Styles ──────────────────────────────────────
RED='\033[0;31m' GREEN='\033[0;32m' CYAN='\033[0;36m'
PURPLE='\033[0;35m' YELLOW='\033[1;33m' BOLD='\033[1m'
DIM='\033[2m' NC='\033[0m'

# ─── Branding ────────────────────────────────────────────
print_banner() {
  echo ""
  echo -e "${PURPLE}${BOLD}"
  echo "    █████╗ ██████╗ ██╗ █████╗ "
  echo "   ██╔══██╗██╔══██╗██║██╔══██╗"
  echo "   ███████║██████╔╝██║███████║"
  echo "   ██╔══██║██╔══██╗██║██╔══██║"
  echo "   ██║  ██║██║  ██║██║██║  ██║"
  echo "   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝"
  echo -e "${NC}"
  echo -e "${CYAN}   Autonomous Real-time Intelligent Agent${NC}"
  echo -e "${DIM}   Enterprise Edition v8.1 • Installer${NC}"
  echo ""
  echo -e "   ${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""
}

log_step() { echo -e "  ${CYAN}▸${NC} ${BOLD}$1${NC}"; }
log_ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}⚠${NC} $1"; }
log_err()  { echo -e "  ${RED}✗${NC} $1"; }
log_info() { echo -e "  ${DIM}  $1${NC}"; }

separator() { echo -e "  ${DIM}─────────────────────────────────────────${NC}"; }

# ─── Detect Package Manager ──────────────────────────────
detect_pm() {
  if command -v pacman &>/dev/null; then
    PM="pacman"
    PM_INSTALL="sudo pacman -S --noconfirm --needed"
    PM_UPDATE="sudo pacman -Sy"
    DISTRO="Arch Linux"
  elif command -v apt &>/dev/null; then
    PM="apt"
    PM_INSTALL="sudo apt install -y"
    PM_UPDATE="sudo apt update"
    DISTRO="Ubuntu/Debian"
  elif command -v dnf &>/dev/null; then
    PM="dnf"
    PM_INSTALL="sudo dnf install -y"
    PM_UPDATE="sudo dnf check-update || true"
    DISTRO="Fedora/RHEL"
  else
    log_err "Unsupported package manager. Please install dependencies manually."
    exit 1
  fi
}

# ─── Check Prerequisites ─────────────────────────────────
check_prereqs() {
  log_step "Checking system prerequisites..."

  # Check disk space (need at least 5GB)
  local free_space
  free_space=$(df -BG "$HOME" | awk 'NR==2 {print $4}' | tr -d 'G')
  if (( free_space < 5 )); then
    log_err "Insufficient disk space: ${free_space}GB free, need at least 5GB"
    exit 1
  fi
  log_ok "Disk space: ${free_space}GB free"

  # Check RAM
  local total_ram
  total_ram=$(free -g | awk '/^Mem:/ {print $2}')
  if (( total_ram < 4 )); then
    log_warn "Low RAM: ${total_ram}GB detected (8GB+ recommended)"
  else
    log_ok "RAM: ${total_ram}GB"
  fi

  # Check internet
  if ping -c 1 -W 3 8.8.8.8 &>/dev/null; then
    log_ok "Internet connectivity: OK"
  else
    log_err "No internet connection detected"
    exit 1
  fi
}

# ─── Install System Dependencies ─────────────────────────
install_system_deps() {
  log_step "Installing system dependencies for ${DISTRO}..."
  separator

  $PM_UPDATE 2>/dev/null

  local deps="python python-pip git curl wget"

  case $PM in
    pacman)
      deps="$deps base-devel openssl webkit2gtk-4.1 libappindicator-gtk3 patchelf nodejs npm"
      ;;
    apt)
      deps="$deps build-essential libssl-dev libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf nodejs npm"
      ;;
    dnf)
      deps="$deps gcc openssl-devel webkit2gtk4.1-devel libappindicator-gtk3-devel nodejs npm"
      ;;
  esac

  $PM_INSTALL $deps 2>/dev/null
  log_ok "System packages installed"
}

# ─── Install Rust ─────────────────────────────────────────
install_rust() {
  if command -v rustc &>/dev/null; then
    local rust_ver
    rust_ver=$(rustc --version | awk '{print $2}')
    log_ok "Rust already installed: v${rust_ver}"
    return
  fi

  log_step "Installing Rust toolchain..."
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
  source "$HOME/.cargo/env"
  log_ok "Rust installed: $(rustc --version | awk '{print $2}')"
}

# ─── Install Ollama ───────────────────────────────────────
install_ollama() {
  if command -v ollama &>/dev/null; then
    log_ok "Ollama already installed"
    return
  fi

  log_step "Installing Ollama (local LLM runner)..."
  curl -fsSL https://ollama.ai/install.sh | sh
  log_ok "Ollama installed"
}

# ─── Pull Router Model ───────────────────────────────────
pull_router_model() {
  log_step "Pulling ARIA router model (Qwen 3.5 4B)..."
  log_info "This may take a few minutes on first run..."

  if ollama list 2>/dev/null | grep -q "aria-router"; then
    log_ok "Router model already available"
  else
    ollama pull qwen3:4b 2>/dev/null || log_warn "Could not pull model — you can pull it manually later"
    log_ok "Router model ready"
  fi
}

# ─── Install Python Dependencies ──────────────────────────
install_python_deps() {
  log_step "Installing Python dependencies..."

  pip install --user --quiet \
    python-telegram-bot \
    pyyaml \
    trafilatura \
    playwright \
    aiohttp \
    beautifulsoup4 \
    requests \
    reportlab \
    Pillow \
    2>/dev/null || true

  # Install Playwright browsers
  python3 -m playwright install chromium 2>/dev/null || \
    log_warn "Playwright browsers not installed — run 'playwright install chromium' manually"

  log_ok "Python dependencies installed"
}

# ─── Setup ARIA Directory Structure ──────────────────────
setup_aria() {
  log_step "Setting up ARIA directory structure..."

  ARIA_DIR="${HOME}/aria"

  # Create necessary directories
  mkdir -p "$ARIA_DIR"/{vault,memory,downloads,bin,docs,comms}

  # Set permissions on sensitive files
  if [[ -f "$ARIA_DIR/identity.yaml" ]]; then
    chmod 600 "$ARIA_DIR/identity.yaml"
  fi
  if [[ -d "$ARIA_DIR/vault" ]]; then
    chmod 700 "$ARIA_DIR/vault"
  fi

  # Create template identity.yaml if not exists
  if [[ ! -f "$ARIA_DIR/identity.yaml" ]]; then
    cat > "$ARIA_DIR/identity.yaml" << 'IDENTITY'
# ARIA Identity Configuration
# Fill this out so ARIA knows who you are

name: "Your Name"
alias: "YourAlias"
age: 0
location: "Your Location"
bio: "AI enthusiast"
os: "Linux"
shell: "bash"

emails:
  - address: "you@example.com"
    purpose: [primary]
IDENTITY
    chmod 600 "$ARIA_DIR/identity.yaml"
    log_info "Created template identity.yaml — edit it with your info"
  fi

  # Create config.yaml if not exists
  if [[ ! -f "$ARIA_DIR/config.yaml" ]]; then
    cat > "$ARIA_DIR/config.yaml" << 'CONFIG'
## Model
ollama_url: "http://localhost:11434"
router_model: "aria-router"

## Paths
soul_path: "~/aria/SOUL.md"
memory_path: "~/aria/memory.json"
skills_dir: "~/aria/skills"

## Behavior
max_retries: 3
context_messages: 20
response_timeout: 120
CONFIG
    log_info "Created template config.yaml"
  fi

  # Create empty memory if not exists
  if [[ ! -f "$ARIA_DIR/memory.json" ]]; then
    echo '{"facts": {}, "preferences": {}, "skills": {}}' > "$ARIA_DIR/memory.json"
  fi

  # Create security.json if not exists
  if [[ ! -f "$ARIA_DIR/security.json" ]]; then
    echo '{"allow_sudo":false,"allow_network":true,"bash_blocklist":["rm -rf /","dd if="],"sandbox_paths":["~/aria","~/Downloads"]}' > "$ARIA_DIR/security.json"
  fi

  log_ok "ARIA directory structure ready"
}

# ─── Build Enterprise Manager ─────────────────────────────
build_manager() {
  log_step "Building ARIA Enterprise Manager..."
  separator

  MANAGER_DIR="${HOME}/aria/aria-enterprise"

  if [[ ! -d "$MANAGER_DIR" ]]; then
    log_warn "Manager source not found at $MANAGER_DIR — skipping GUI build"
    return
  fi

  cd "$MANAGER_DIR"

  # Install Node dependencies
  log_info "Installing Node.js dependencies..."
  npm install --silent 2>/dev/null

  # Build with Tauri
  log_info "Compiling Rust backend + React frontend..."
  npx tauri build 2>/dev/null || log_warn "Build had warnings but binary was produced"

  # Copy binary
  if [[ -f "src-tauri/target/release/app" ]]; then
    cp -f "src-tauri/target/release/app" "$HOME/aria/bin/aria-manager"
    chmod +x "$HOME/aria/bin/aria-manager"
    log_ok "ARIA Enterprise Manager built → ~/aria/bin/aria-manager"
  fi

  # Install .deb if available
  local deb_file
  deb_file=$(find src-tauri/target/release/bundle/deb/ -name "*.deb" 2>/dev/null | head -1)
  if [[ -n "$deb_file" ]] && command -v dpkg &>/dev/null; then
    sudo dpkg -i "$deb_file" 2>/dev/null || true
    log_ok "Installed .deb package"
  fi

  cd "$HOME/aria"
}

# ─── Create Desktop Entry ────────────────────────────────
create_desktop_entry() {
  log_step "Creating desktop entry..."

  mkdir -p "$HOME/.local/share/applications"
  cat > "$HOME/.local/share/applications/aria-manager.desktop" << DESKTOP
[Desktop Entry]
Name=ARIA Enterprise Manager
Comment=Autonomous Real-time Intelligent Agent
Exec=${HOME}/aria/bin/aria-manager
Icon=${HOME}/aria/aria-enterprise/public/aria-logo.png
Terminal=false
Type=Application
Categories=Utility;Development;
StartupWMClass=aria-enterprise
DESKTOP

  log_ok "Desktop entry created (find ARIA in your app launcher)"
}

# ─── Final Summary ────────────────────────────────────────
print_summary() {
  echo ""
  separator
  echo ""
  echo -e "  ${GREEN}${BOLD}🎉 ARIA Installation Complete!${NC}"
  echo ""
  echo -e "  ${BOLD}Quick Start:${NC}"
  echo -e "    ${CYAN}1.${NC} Configure your identity:  ${DIM}nano ~/aria/identity.yaml${NC}"
  echo -e "    ${CYAN}2.${NC} Set Telegram credentials: ${DIM}export TELEGRAM_BOT_TOKEN=your_token${NC}"
  echo -e "    ${CYAN}3.${NC} Start ARIA:               ${DIM}cd ~/aria && python3 router.py${NC}"
  echo -e "    ${CYAN}4.${NC} Launch the Manager GUI:   ${DIM}~/aria/bin/aria-manager${NC}"
  echo ""
  echo -e "  ${BOLD}Useful Commands:${NC}"
  echo -e "    ${DIM}ollama list${NC}            — Check available LLM models"
  echo -e "    ${DIM}ollama pull qwen3:4b${NC}   — Pull the router model"
  echo -e "    ${DIM}aria-manager${NC}           — Launch Enterprise Manager"
  echo ""
  echo -e "  ${BOLD}Documentation:${NC} ${CYAN}https://github.com/GamerX3560/Aria-V-7.1${NC}"
  echo ""
  separator
  echo ""
  echo -e "  ${PURPLE}Thank you for installing ARIA. Welcome to the future. 🧠${NC}"
  echo ""
}

# ─── Main ─────────────────────────────────────────────────
main() {
  print_banner

  log_step "Starting ARIA installation..."
  echo ""

  detect_pm
  log_ok "Detected: ${DISTRO} (${PM})"
  echo ""

  check_prereqs
  echo ""

  install_system_deps
  echo ""

  install_rust
  install_ollama
  echo ""

  install_python_deps
  echo ""

  setup_aria
  echo ""

  pull_router_model
  echo ""

  build_manager
  echo ""

  create_desktop_entry
  echo ""

  print_summary
}

main "$@"
