"""
ARIA v6 — Tool Executor
Safe, multi-language code execution engine with security sandbox,
escalating timeouts, and background process tracking.
"""

import os
import re
import subprocess
import logging

log = logging.getLogger("ARIA.executor")

# ─── Security Blocklist ─────────────────────────────────────
BLOCKED_PATTERNS = [
    r"\brm\s+-rf\s+/",
    r"\brm\s+-rf\s+~",
    r"\brm\s+-rf\s+\$HOME",
    r"\bmkfs\b",
    r"\bdd\s+if=.*of=/dev/",
    r":\(\)\{.*\};:",
    r"\bchmod\s+-R\s+777\s+/",
    r"\bcurl\b.*\|\s*bash",
    r"\bwget\b.*\|\s*bash",
    r"\bsudo\s+rm\s+-rf\s+/",
]

# GUI apps that must run in background
BG_APPS = frozenset([
    "firefox", "brave", "code", "spotify", "missioncenter",
    "vlc", "mpv", "discord", "telegram-desktop", "obs",
    "gimp", "blender", "libreoffice", "thunar", "nautilus",
    "kitty", "alacritty", "wezterm", "scrcpy",
])

# Timeout tiers (seconds) based on command characteristics
TIMEOUT_FAST = 30
TIMEOUT_MEDIUM = 60
TIMEOUT_LONG = 120

def is_command_safe(code: str) -> bool:
    """Reject obviously destructive commands."""
    for pat in BLOCKED_PATTERNS:
        if re.search(pat, code, re.IGNORECASE):
            log.warning(f"[SECURITY] Blocked dangerous command: {code[:80]}")
            return False
    return True

def classify_timeout(code: str) -> int:
    """Determine appropriate timeout based on command type."""
    code_lower = code.lower()
    # Long-running commands
    if any(kw in code_lower for kw in ["pip install", "npm install", "cargo build", "make", "cmake", "git clone", "wget", "curl -o", "apt", "pacman", "yay"]):
        return TIMEOUT_LONG
    # Medium commands
    if any(kw in code_lower for kw in ["python3", "node", "find /", "grep -r", "rg ", "du -"]):
        return TIMEOUT_MEDIUM
    return TIMEOUT_FAST

def get_wayland_env() -> dict:
    """Build environment dict with display server variables."""
    uid = os.getuid()
    env = {
        **os.environ,
        "DISPLAY": ":0",
        "WAYLAND_DISPLAY": "wayland-1",
        "XDG_RUNTIME_DIR": f"/run/user/{uid}",
        "DBUS_SESSION_BUS_ADDRESS": f"unix:path=/run/user/{uid}/bus",
    }
    # Inject Hyprland instance signature
    try:
        hypr_dir = f"/run/user/{uid}/hypr"
        if os.path.exists(hypr_dir):
            instances = os.listdir(hypr_dir)
            if instances:
                env["HYPRLAND_INSTANCE_SIGNATURE"] = instances[0]
    except Exception:
        pass
    return env

def extract_code_blocks(text: str) -> list:
    """Extract all fenced code blocks (```bash, ```python, ```sh, etc.)."""
    pattern = r'```(?:bash|shell|sh|python|python3|js|javascript|node)?\s*\n(.*?)```'
    return re.findall(pattern, text, re.DOTALL)

def detect_language(text: str) -> str:
    """Detect the language tag from a code block header."""
    match = re.search(r'```(bash|shell|sh|python|python3|js|javascript|node)\s*\n', text)
    if match:
        lang = match.group(1).lower()
        if lang in ("python", "python3"):
            return "python"
        if lang in ("js", "javascript", "node"):
            return "node"
    return "bash"

def execute(code: str, timeout: int = None, truncate: int = 2000) -> str:
    """
    Execute a code block safely.
    
    Args:
        code: The code string to execute.
        timeout: Override timeout in seconds. If None, auto-classifies.
        truncate: Max output characters to return.
    
    Returns:
        Execution output string (truncated if necessary).
    """
    code = code.strip()
    if not code:
        return ""

    if not is_command_safe(code):
        return "ERROR: Command blocked by ARIA security policy."

    if timeout is None:
        timeout = classify_timeout(code)

    # Auto-background GUI apps
    first_word = code.split()[0].lower() if code.split() else ""
    if first_word in BG_APPS and not code.rstrip().endswith("&"):
        code = f"{code} &"

    env = get_wayland_env()

    try:
        result = subprocess.run(
            code, shell=True, executable="/bin/bash",
            capture_output=True, text=True, timeout=timeout, env=env
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            output = stdout + f"\nERROR (exit {result.returncode}): {stderr}" if stderr else stdout
        elif stderr and ("command not found" in stderr.lower() or "no such" in stderr.lower()):
            output = stdout + f"\nWARNING: {stderr}"
        else:
            output = stdout

        if not output:
            output = "(executed successfully, no output)"

        # Truncate to prevent context overflow
        if len(output) > truncate:
            output = output[:truncate] + f"\n... (truncated, {len(output)} total chars)"

        return output

    except subprocess.TimeoutExpired:
        return f"ERROR: Command timed out after {timeout}s. If this is a long-running process, try running it in the background with '&'."
    except Exception as e:
        return f"ERROR: Execution failed: {e}"
