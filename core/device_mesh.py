"""
ARIA v7 — Device Mesh
Coordinates actions across multiple devices:
- Local PC (direct bash)
- Android phone (ADB root shell over USB or network)
- Remote Linux machines (SSH)

Future: Magisk module integration, multi-ARIA mesh communication.
"""

import os
import subprocess
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict

log = logging.getLogger("ARIA.mesh")

ARIA_DIR = Path.home() / "aria"
MESH_CONFIG_PATH = ARIA_DIR / "memory" / "mesh_devices.json"


class DeviceMesh:
    """
    Multi-device orchestration hub.
    
    Manages connections to:
    1. Local PC — direct subprocess execution
    2. Android — ADB shell (root, USB or WiFi/network)
    3. Remote — SSH execution on other machines
    
    Future: Multiple ARIA instances communicating across devices.
    """

    def __init__(self):
        self._devices = self._load_config()

    def _load_config(self) -> Dict[str, dict]:
        """Load device configurations."""
        default = {
            "local": {
                "name": "Local PC",
                "type": "local",
                "status": "active",
                "os": "Arch Linux",
            }
        }
        try:
            with open(MESH_CONFIG_PATH, 'r') as f:
                data = json.load(f)
                return {**default, **data}
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def _save_config(self):
        MESH_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(MESH_CONFIG_PATH, 'w') as f:
            json.dump(self._devices, f, indent=2)

    # ─── Device Management ────────────────────────────────

    def add_android_device(self, name: str = "Android", serial: str = None, 
                          ip: str = None, port: int = 5555) -> bool:
        """
        Register an Android device (rooted, ADB).
        
        Args:
            name: Display name for the device.
            serial: USB serial number (for USB connection).
            ip: IP address (for network ADB).
            port: ADB port (default 5555).
        """
        device_id = name.lower().replace(" ", "_")
        
        # Try to connect
        if ip:
            try:
                subprocess.run(
                    ["adb", "connect", f"{ip}:{port}"],
                    capture_output=True, timeout=10
                )
            except Exception:
                pass
        
        self._devices[device_id] = {
            "name": name,
            "type": "android",
            "serial": serial,
            "ip": ip,
            "port": port,
            "status": "registered",
            "root": True,
        }
        self._save_config()
        log.info(f"Registered Android device: {name}")
        return True

    def add_ssh_device(self, name: str, host: str, user: str = "gamerx", 
                      port: int = 22, key_path: str = None) -> bool:
        """Register a remote Linux machine accessible via SSH."""
        device_id = name.lower().replace(" ", "_")
        self._devices[device_id] = {
            "name": name,
            "type": "ssh",
            "host": host,
            "user": user,
            "port": port,
            "key_path": key_path or str(Path.home() / ".ssh" / "id_ed25519"),
            "status": "registered",
        }
        self._save_config()
        log.info(f"Registered SSH device: {name} ({user}@{host})")
        return True

    # ─── Execution on Devices ─────────────────────────────

    def execute_on(self, device_id: str, command: str, timeout: int = 30) -> str:
        """
        Execute a command on a specific device.
        
        Args:
            device_id: The device identifier.
            command: The command to execute.
            timeout: Timeout in seconds.
            
        Returns:
            Command output string.
        """
        device = self._devices.get(device_id)
        if not device:
            return f"Error: Unknown device '{device_id}'"
        
        dtype = device["type"]
        
        if dtype == "local":
            return self._exec_local(command, timeout)
        elif dtype == "android":
            return self._exec_android(device, command, timeout)
        elif dtype == "ssh":
            return self._exec_ssh(device, command, timeout)
        else:
            return f"Error: Unknown device type '{dtype}'"

    def _exec_local(self, command: str, timeout: int) -> str:
        """Execute on local machine."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout, executable="/bin/bash"
            )
            output = result.stdout.strip()
            if result.returncode != 0 and result.stderr:
                output += f"\nError: {result.stderr.strip()}"
            return output or "(done)"
        except subprocess.TimeoutExpired:
            return f"Error: Timed out after {timeout}s"
        except Exception as e:
            return f"Error: {e}"

    def _exec_android(self, device: dict, command: str, timeout: int) -> str:
        """Execute on Android via ADB shell (root)."""
        adb_cmd = ["adb"]
        
        # Target specific device
        if device.get("serial"):
            adb_cmd.extend(["-s", device["serial"]])
        elif device.get("ip"):
            adb_cmd.extend(["-s", f"{device['ip']}:{device.get('port', 5555)}"])
        
        # Use root shell
        if device.get("root"):
            adb_cmd.extend(["shell", "su", "-c", command])
        else:
            adb_cmd.extend(["shell", command])
        
        try:
            result = subprocess.run(
                adb_cmd, capture_output=True, text=True, timeout=timeout
            )
            output = result.stdout.strip()
            if result.returncode != 0 and result.stderr:
                output += f"\nError: {result.stderr.strip()}"
            return output or "(done)"
        except subprocess.TimeoutExpired:
            return f"Error: ADB command timed out after {timeout}s"
        except FileNotFoundError:
            return "Error: adb not found. Install with: yay -S android-tools"
        except Exception as e:
            return f"Error: {e}"

    def _exec_ssh(self, device: dict, command: str, timeout: int) -> str:
        """Execute on remote machine via SSH."""
        ssh_cmd = [
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            "-p", str(device.get("port", 22)),
        ]
        
        if device.get("key_path"):
            ssh_cmd.extend(["-i", device["key_path"]])
        
        ssh_cmd.append(f"{device['user']}@{device['host']}")
        ssh_cmd.append(command)
        
        try:
            result = subprocess.run(
                ssh_cmd, capture_output=True, text=True, timeout=timeout
            )
            output = result.stdout.strip()
            if result.returncode != 0 and result.stderr:
                output += f"\nError: {result.stderr.strip()}"
            return output or "(done)"
        except subprocess.TimeoutExpired:
            return f"Error: SSH command timed out after {timeout}s"
        except Exception as e:
            return f"Error: {e}"

    # ─── Status & Discovery ───────────────────────────────

    def check_device_status(self, device_id: str) -> str:
        """Check if a device is reachable."""
        device = self._devices.get(device_id)
        if not device:
            return "unknown"
        
        if device["type"] == "local":
            return "active"
        elif device["type"] == "android":
            try:
                result = subprocess.run(
                    ["adb", "devices"], capture_output=True, text=True, timeout=5
                )
                if device.get("serial") and device["serial"] in result.stdout:
                    return "connected"
                if device.get("ip") and device["ip"] in result.stdout:
                    return "connected"
                return "disconnected"
            except Exception:
                return "error"
        elif device["type"] == "ssh":
            try:
                result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=3", "-o", "BatchMode=yes",
                     f"{device['user']}@{device['host']}", "echo ok"],
                    capture_output=True, text=True, timeout=5
                )
                return "active" if result.returncode == 0 else "unreachable"
            except Exception:
                return "error"
        return "unknown"

    def list_devices(self) -> str:
        """Get a formatted list of all devices."""
        lines = [f"📡 Device Mesh ({len(self._devices)} devices):"]
        for did, dev in self._devices.items():
            status = self.check_device_status(did)
            icon = {"active": "🟢", "connected": "🟢", "registered": "🟡",
                    "disconnected": "🔴", "unreachable": "🔴"}.get(status, "⚪")
            lines.append(f"  {icon} {dev['name']} [{dev['type']}] — {status}")
        return "\n".join(lines)

    def discover_android_devices(self) -> List[str]:
        """Auto-discover connected Android devices via ADB."""
        try:
            result = subprocess.run(
                ["adb", "devices", "-l"],
                capture_output=True, text=True, timeout=5
            )
            devices = []
            for line in result.stdout.strip().split('\n')[1:]:
                if 'device' in line and 'List' not in line:
                    serial = line.split()[0]
                    devices.append(serial)
            return devices
        except Exception:
            return []
