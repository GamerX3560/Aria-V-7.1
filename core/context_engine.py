"""
ARIA v7 — Context Engine
Always-aware contextual intelligence. Provides live data about
time, weather, system state, and key info for every prompt.
"""

import os
import json
import time
import psutil
import logging
import subprocess
from datetime import datetime
from pathlib import Path

log = logging.getLogger("ARIA.context")

ARIA_DIR = Path.home() / "aria"


class ContextEngine:
    """
    Gathers real-time contextual information and injects it
    into ARIA's system prompt so the LLM always knows:
    - Current date/time/day
    - System health (CPU, RAM, disk, GPU temp)
    - Weather (via wttr.in, no API key needed)
    - Recent system events
    - User session info
    """

    def __init__(self):
        self._weather_cache = {"data": "", "fetched_at": 0}
        self._CACHE_TTL = 900  # 15 minutes

    def get_datetime_context(self) -> str:
        """Current date, time, and day of week."""
        now = datetime.now()
        return (
            f"📅 Date: {now.strftime('%A, %B %d, %Y')}\n"
            f"🕐 Time: {now.strftime('%I:%M %p')} IST\n"
            f"📊 Uptime: {self._get_uptime()}"
        )

    def get_system_context(self) -> str:
        """Live system health metrics."""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # GPU temperature (AMD RX 6600)
            gpu_temp = self._get_gpu_temp()
            
            # Network status
            net = "Connected" if self._check_network() else "Offline"
            
            return (
                f"💻 CPU: {cpu}% | RAM: {ram.percent}% ({ram.used // (1024**3)}/{ram.total // (1024**3)}GB)\n"
                f"💾 Disk: {disk.percent}% ({disk.free // (1024**3)}GB free)\n"
                f"🌡️ GPU: {gpu_temp}\n"
                f"🌐 Network: {net}"
            )
        except Exception as e:
            return f"System: Error reading metrics ({e})"

    def get_weather_context(self) -> str:
        """Weather via wttr.in (free, no API key)."""
        now = time.time()
        if now - self._weather_cache["fetched_at"] < self._CACHE_TTL and self._weather_cache["data"]:
            return self._weather_cache["data"]
        
        try:
            result = subprocess.run(
                ["curl", "-s", "wttr.in/?format=%C+%t+%w+%h", "--max-time", "3"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                weather = f"🌤️ Weather: {result.stdout.strip()}"
                self._weather_cache = {"data": weather, "fetched_at": now}
                return weather
        except Exception:
            pass
        return "🌤️ Weather: (unavailable)"

    def get_running_apps_context(self) -> str:
        """Currently running notable apps."""
        notable = {
            "brave": "🌐 Brave Browser",
            "firefox": "🦊 Firefox",
            "code": "📝 VS Code",
            "kitty": "🐱 Kitty Terminal",
            "discord": "💬 Discord",
            "spotify": "🎵 Spotify",
            "obs": "📹 OBS Studio",
            "scrcpy": "📱 Android Mirror",
            "telegram": "📨 Telegram",
        }
        running = []
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info['name'].lower() if proc.info['name'] else ""
                for key, label in notable.items():
                    if key in name and label not in running:
                        running.append(label)
        except Exception:
            pass
        
        if running:
            return "🖥️ Running: " + ", ".join(running[:8])
        return "🖥️ Running: (no notable apps detected)"

    def get_full_context(self) -> str:
        """
        Build the complete context block for the system prompt.
        Called before every LLM request.
        """
        sections = [
            "--- 🌍 LIVE CONTEXT (auto-updated) ---",
            self.get_datetime_context(),
            self.get_system_context(),
            self.get_weather_context(),
            self.get_running_apps_context(),
            "--- END LIVE CONTEXT ---",
        ]
        return "\n".join(sections)

    # ─── Helper Methods ───────────────────────────────────
    
    @staticmethod
    def _get_uptime() -> str:
        try:
            boot = datetime.fromtimestamp(psutil.boot_time())
            delta = datetime.now() - boot
            hours = delta.seconds // 3600
            mins = (delta.seconds % 3600) // 60
            return f"{delta.days}d {hours}h {mins}m"
        except Exception:
            return "unknown"

    @staticmethod
    def _get_gpu_temp() -> str:
        try:
            result = subprocess.run(
                ["cat", "/sys/class/drm/card1/device/hwmon/hwmon1/temp1_input"],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                temp_c = int(result.stdout.strip()) / 1000
                return f"{temp_c:.0f}°C"
        except Exception:
            pass
        # Fallback
        try:
            result = subprocess.run(
                ["sensors"], capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'edge' in line.lower() or 'junction' in line.lower():
                        return line.strip().split(':')[1].strip().split('(')[0].strip()
        except Exception:
            pass
        return "N/A"

    @staticmethod
    def _check_network() -> bool:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", "8.8.8.8"],
                capture_output=True, timeout=3
            )
            return result.returncode == 0
        except Exception:
            return False
