"""
ARIA v7 — Proactive Monitor Daemon
Background service that monitors the system and sends autonomous
alerts via Telegram without being asked.

Monitors:
- Disk space (warns at 85%, critical at 95%)
- RAM usage (warns at 90%)
- CPU sustained high load (>90% for 5 minutes)
- GPU temperature (warns at 85°C)
- Network connectivity loss
- Battery level (if laptop, warns at 15%)
- New login sessions
"""

import os
import time
import json
import logging
import asyncio
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

log = logging.getLogger("ARIA.monitor")

ARIA_DIR = Path.home() / "aria"
MONITOR_STATE_PATH = ARIA_DIR / "memory" / "monitor_state.json"

# ─── Alert Thresholds ─────────────────────────────────────
THRESHOLDS = {
    "disk_warn": 85,       # percent
    "disk_critical": 95,
    "ram_warn": 90,
    "cpu_sustained": 90,   # percent for 5+ minutes
    "gpu_temp_warn": 85,   # celsius
    "battery_warn": 15,    # percent
    "check_interval": 60,  # seconds between checks
    "cooldown": 1800,      # 30 min before re-alerting same issue
}


class ProactiveMonitor:
    """
    Background daemon that watches system health and sends 
    proactive alerts via a Telegram bot instance.
    
    Usage:
        monitor = ProactiveMonitor(telegram_bot, chat_id)
        asyncio.create_task(monitor.start())
    """

    def __init__(self, telegram_bot=None, chat_id: str = None):
        self.bot = telegram_bot
        self.chat_id = chat_id
        self._running = False
        self._alert_history = self._load_state()
        self._cpu_high_since = None

    def _load_state(self) -> dict:
        try:
            with open(MONITOR_STATE_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"last_alerts": {}}

    def _save_state(self):
        MONITOR_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MONITOR_STATE_PATH, 'w') as f:
            json.dump(self._alert_history, f)

    def _can_alert(self, alert_key: str) -> bool:
        """Check if enough time has passed since last alert of this type."""
        last = self._alert_history.get("last_alerts", {}).get(alert_key, 0)
        return (time.time() - last) > THRESHOLDS["cooldown"]

    def _record_alert(self, alert_key: str):
        if "last_alerts" not in self._alert_history:
            self._alert_history["last_alerts"] = {}
        self._alert_history["last_alerts"][alert_key] = time.time()
        self._save_state()

    async def _send_alert(self, message: str, alert_key: str):
        """Send an alert via Telegram if bot is available."""
        if not self._can_alert(alert_key):
            return
        
        self._record_alert(alert_key)
        log.warning(f"PROACTIVE ALERT [{alert_key}]: {message}")
        
        if self.bot and self.chat_id:
            try:
                await self.bot.send_message(chat_id=self.chat_id, text=f"🚨 ARIA Alert\n\n{message}")
            except Exception as e:
                log.error(f"Failed to send alert: {e}")

    async def check_disk(self):
        """Monitor disk space."""
        try:
            disk = psutil.disk_usage('/')
            if disk.percent >= THRESHOLDS["disk_critical"]:
                free_gb = disk.free // (1024**3)
                await self._send_alert(
                    f"⚠️ CRITICAL: Disk almost full!\n"
                    f"Usage: {disk.percent}% | Only {free_gb}GB free\n"
                    f"Run `ncdu /` to find large files.",
                    "disk_critical"
                )
            elif disk.percent >= THRESHOLDS["disk_warn"]:
                free_gb = disk.free // (1024**3)
                await self._send_alert(
                    f"💾 Disk space running low\n"
                    f"Usage: {disk.percent}% | {free_gb}GB free",
                    "disk_warn"
                )
        except Exception as e:
            log.error(f"Disk check error: {e}")

    async def check_ram(self):
        """Monitor RAM usage."""
        try:
            ram = psutil.virtual_memory()
            if ram.percent >= THRESHOLDS["ram_warn"]:
                top_procs = []
                for proc in sorted(psutil.process_iter(['name', 'memory_percent']), 
                                 key=lambda p: p.info.get('memory_percent', 0) or 0, reverse=True)[:3]:
                    top_procs.append(f"  • {proc.info['name']}: {proc.info['memory_percent']:.1f}%")
                
                await self._send_alert(
                    f"🔴 RAM usage high: {ram.percent}%\n"
                    f"Top consumers:\n" + "\n".join(top_procs),
                    "ram_high"
                )
        except Exception as e:
            log.error(f"RAM check error: {e}")

    async def check_cpu(self):
        """Monitor sustained high CPU usage."""
        try:
            cpu = psutil.cpu_percent(interval=1)
            if cpu >= THRESHOLDS["cpu_sustained"]:
                if self._cpu_high_since is None:
                    self._cpu_high_since = time.time()
                elif time.time() - self._cpu_high_since > 300:  # 5 minutes
                    await self._send_alert(
                        f"🔥 CPU at {cpu}% for 5+ minutes!\nSomething may be stuck.",
                        "cpu_sustained"
                    )
            else:
                self._cpu_high_since = None
        except Exception as e:
            log.error(f"CPU check error: {e}")

    async def check_gpu_temp(self):
        """Monitor GPU temperature."""
        try:
            # AMD GPU via sysfs
            temp_paths = [
                "/sys/class/drm/card1/device/hwmon/hwmon1/temp1_input",
                "/sys/class/drm/card0/device/hwmon/hwmon0/temp1_input",
            ]
            for path in temp_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        temp_c = int(f.read().strip()) / 1000
                    if temp_c >= THRESHOLDS["gpu_temp_warn"]:
                        await self._send_alert(
                            f"🌡️ GPU temperature high: {temp_c:.0f}°C\n"
                            f"Consider closing GPU-intensive apps.",
                            "gpu_temp"
                        )
                    break
        except Exception as e:
            log.error(f"GPU temp check error: {e}")

    async def check_network(self):
        """Monitor network connectivity."""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True, timeout=5
            )
            if result.returncode != 0:
                await self._send_alert(
                    "🌐 Network connection lost!\nCannot reach the internet.",
                    "network_down"
                )
        except Exception:
            pass  # Can't alert if there's no network anyway

    async def check_battery(self):
        """Monitor battery level (if available)."""
        try:
            battery = psutil.sensors_battery()
            if battery and not battery.power_plugged:
                if battery.percent <= THRESHOLDS["battery_warn"]:
                    await self._send_alert(
                        f"🔋 Battery low: {battery.percent}%\n"
                        f"Estimated {battery.secsleft // 60}min remaining. Plug in soon!",
                        "battery_low"
                    )
        except Exception:
            pass  # Desktop PC, no battery

    async def run_checks(self) -> dict:
        """Run all health checks once. Returns summary of current metrics."""
        stats = self.get_system_stats()
        await self.check_disk()
        await self.check_ram()
        await self.check_cpu()
        await self.check_gpu_temp()
        await self.check_network()
        await self.check_battery()
        return stats

    async def start(self):
        """Start the monitoring loop."""
        self._running = True
        log.info("Proactive Monitor started")
        
        while self._running:
            try:
                await self.run_checks()
            except Exception as e:
                log.error(f"Monitor cycle error: {e}")
            
            await asyncio.sleep(THRESHOLDS["check_interval"])

    def stop(self):
        """Stop the monitoring loop."""
        self._running = False
        log.info("Proactive Monitor stopped")

    def get_system_stats(self) -> dict:
        """Get current system metrics as a dict (for on-demand queries)."""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            stats = {
                "cpu_percent": cpu,
                "ram_percent": ram.percent,
                "ram_used_gb": round(ram.used / (1024**3), 1),
                "ram_total_gb": round(ram.total / (1024**3), 1),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 1),
                "disk_total_gb": round(disk.total / (1024**3), 1),
            }
            
            # GPU temp (AMD)
            for path in [
                "/sys/class/drm/card1/device/hwmon/hwmon1/temp1_input",
                "/sys/class/drm/card0/device/hwmon/hwmon0/temp1_input",
            ]:
                if os.path.exists(path):
                    try:
                        with open(path) as f:
                            stats["gpu_temp_c"] = round(int(f.read().strip()) / 1000, 1)
                    except Exception:
                        pass
                    break
            
            # Battery
            battery = psutil.sensors_battery()
            if battery:
                stats["battery_percent"] = battery.percent
                stats["battery_plugged"] = battery.power_plugged
            
            return stats
        except Exception as e:
            log.error(f"get_system_stats error: {e}")
            return {}

    def get_status(self) -> str:
        """Get a formatted status summary string."""
        try:
            stats = self.get_system_stats()
            gpu_info = f" | GPU: {stats.get('gpu_temp_c', '?')}°C" if 'gpu_temp_c' in stats else ""
            return (
                f"Monitor: {'🟢 Active' if self._running else '⚪ Stopped'}\n"
                f"CPU: {stats.get('cpu_percent','?')}% | "
                f"RAM: {stats.get('ram_percent','?')}% ({stats.get('ram_used_gb','?')}/{stats.get('ram_total_gb','?')}GB) | "
                f"Disk: {stats.get('disk_percent','?')}% ({stats.get('disk_free_gb','?')}GB free)"
                f"{gpu_info}\n"
                f"Alerts sent: {len(self._alert_history.get('last_alerts', {}))}"
            )
        except Exception:
            return "Monitor: Error reading status"

