"""
ARIA v7 — Multi-ARIA Mesh
Decentralized communication protocol for multiple ARIA instances.

Enables ARIA instances running on different machines (Desktop, Laptop,
Android phone, remote servers) to:
- Discover each other on the local network
- Delegate tasks to the best-suited instance
- Share RAG memory and context across devices
- Coordinate complex multi-device workflows
- Report status and health to each other

Architecture:
  Each ARIA instance runs a lightweight FastAPI server on a configurable port.
  Instances register themselves with a shared discovery file or mDNS broadcast.
  Task delegation uses a simple JSON-RPC protocol over HTTP.

Protocol:
  POST /aria/execute     — Execute a task on this instance
  POST /aria/delegate    — Delegate a task to the best available peer
  GET  /aria/status      — Get this instance's health + capabilities
  GET  /aria/peers       — List all known peers
  POST /aria/sync        — Sync RAG memory entries between instances
  POST /aria/register    — Register a new peer
"""

import os
import json
import time
import socket
import asyncio
import logging
import hashlib
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

log = logging.getLogger("ARIA.mesh")

ARIA_DIR = Path.home() / "aria"
PEERS_FILE = ARIA_DIR / "memory" / "mesh_peers.json"
DEFAULT_PORT = 8741  # ARIA mesh default port


class ARIAPeer:
    """Represents a known ARIA instance."""
    def __init__(self, peer_id: str, host: str, port: int, name: str = "",
                 capabilities: List[str] = None, last_seen: float = 0, public_url: str = ""):
        self.peer_id = peer_id
        self.host = host
        self.port = port
        self.name = name or f"aria-{peer_id[:8]}"
        self.capabilities = capabilities or []
        self.last_seen = last_seen or time.time()
        self.public_url = public_url
        self.status = "unknown"

    def to_dict(self) -> dict:
        return {
            "peer_id": self.peer_id,
            "host": self.host,
            "port": self.port,
            "name": self.name,
            "capabilities": self.capabilities,
            "last_seen": self.last_seen,
            "public_url": self.public_url,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ARIAPeer":
        return cls(**{k: v for k, v in data.items() if k != "status"})


class ARIAMesh:
    """
    Multi-ARIA Mesh Network Manager.
    
    Manages peer discovery, task delegation, and inter-instance communication.
    
    Usage:
        mesh = ARIAMesh(instance_name="desktop-aria")
        
        # Start the mesh server
        await mesh.start_server(port=8741)
        
        # Register a peer
        mesh.register_peer("192.168.1.50", port=8741, name="laptop-aria")
        
        # Delegate a task to the best peer
        result = await mesh.delegate_task(
            "Download this file and process it",
            prefer_capabilities=["gpu", "browser"]
        )
        
        # Sync memory with all peers
        await mesh.sync_memory_with_peers()
    """

    def __init__(self, instance_name: str = None, port: int = DEFAULT_PORT):
        self.instance_id = self._generate_instance_id()
        self.instance_name = instance_name or f"aria-{socket.gethostname()}"
        self.port = port
        self.peers: Dict[str, ARIAPeer] = {}
        self.capabilities = self._detect_capabilities()
        self._server_task = None
        self._running = False
        self._task_handler = None  # Set by router.py to handle incoming tasks
        self._load_peers()

    def _generate_instance_id(self) -> str:
        """Generate a unique, stable ID for this ARIA instance."""
        hostname = socket.gethostname()
        mac = hex(hash(hostname))
        return hashlib.sha256(f"{hostname}-{mac}".encode()).hexdigest()[:16]

    def _detect_capabilities(self) -> List[str]:
        """Detect what this instance is capable of."""
        caps = ["execute", "scrape"]  # Every instance can do these

        # Check for GPU
        try:
            import subprocess
            result = subprocess.run(["lspci"], capture_output=True, text=True, timeout=5)
            if "VGA" in result.stdout:
                caps.append("gpu")
        except Exception:
            pass

        # Check for browser automation
        try:
            import playwright
            caps.append("browser")
        except ImportError:
            pass

        # Check for voice
        try:
            import subprocess
            result = subprocess.run(["which", "piper"], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                caps.append("voice")
        except Exception:
            pass

        # Check for ADB (android control)
        try:
            import subprocess
            result = subprocess.run(["which", "adb"], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                caps.append("android")
        except Exception:
            pass

        return caps

    # ─── Peer Management ──────────────────────────────────

    def _load_peers(self):
        """Load known peers from disk."""
        try:
            if PEERS_FILE.exists():
                data = json.loads(PEERS_FILE.read_text())
                for peer_data in data:
                    peer = ARIAPeer.from_dict(peer_data)
                    self.peers[peer.peer_id] = peer
                log.info(f"Loaded {len(self.peers)} known peers")
        except Exception as e:
            log.warning(f"Failed to load peers: {e}")

    def _save_peers(self):
        """Persist known peers to disk."""
        PEERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = [p.to_dict() for p in self.peers.values()]
        PEERS_FILE.write_text(json.dumps(data, indent=2))

    def register_peer(self, host: str, port: int = DEFAULT_PORT,
                      name: str = "", capabilities: List[str] = None,
                      peer_id: str = None) -> ARIAPeer:
        """
        Register a new ARIA peer instance.
        
        Args:
            host: IP address or hostname of the peer
            port: Port the peer's mesh server is running on
            name: Human-readable name ("laptop-aria", "phone-aria")
            capabilities: What this peer can do
            peer_id: Unique peer ID (auto-generated if not given)
        """
        pid = peer_id or hashlib.sha256(f"{host}:{port}".encode()).hexdigest()[:16]
        peer = ARIAPeer(pid, host, port, name, capabilities or [])
        peer.status = "registered"
        self.peers[pid] = peer
        self._save_peers()
        log.info(f"Registered peer: {peer.name} ({host}:{port})")
        return peer

    def remove_peer(self, peer_id: str) -> bool:
        """Remove a peer from the mesh."""
        if peer_id in self.peers:
            del self.peers[peer_id]
            self._save_peers()
            return True
        return False

    # ─── Communication ────────────────────────────────────

    async def ping_peer(self, peer: ARIAPeer) -> bool:
        """Check if a peer is alive."""
        try:
            import aiohttp
            url = f"http://{peer.host}:{peer.port}/aria/status"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        peer.status = "online"
                        peer.last_seen = time.time()
                        peer.capabilities = data.get("capabilities", peer.capabilities)
                        return True
        except Exception:
            peer.status = "offline"
        return False

    async def send_task(self, peer: ARIAPeer, task: str, 
                        context: dict = None) -> Dict[str, Any]:
        """
        Send a task to a specific peer for execution.
        
        Returns the peer's response.
        """
        try:
            import aiohttp
            url = f"http://{peer.host}:{peer.port}/aria/execute"
            payload = {
                "task": task,
                "from_peer": self.instance_id,
                "from_name": self.instance_name,
                "context": context or {},
                "timestamp": time.time(),
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload,
                                       timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    result = await resp.json()
                    return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def delegate_task(self, task: str, 
                            prefer_capabilities: List[str] = None,
                            context: dict = None) -> Dict[str, Any]:
        """
        Delegate a task to the best available peer.
        
        Selects the peer with the most matching capabilities.
        Falls back to local execution if no peers are available.
        """
        best_peer = None
        best_score = -1

        for peer in self.peers.values():
            # Check if peer is online
            if peer.status not in ("online", "registered"):
                continue

            score = 0
            if prefer_capabilities:
                for cap in prefer_capabilities:
                    if cap in peer.capabilities:
                        score += 1

            if score > best_score:
                best_score = score
                best_peer = peer

        if best_peer:
            # Verify peer is actually alive
            is_alive = await self.ping_peer(best_peer)
            if is_alive:
                log.info(f"Delegating task to {best_peer.name}: {task[:50]}...")
                return await self.send_task(best_peer, task, context)

        return {
            "status": "local_fallback",
            "message": "No suitable peers available, executing locally",
        }

    async def sync_memory(self, peer: ARIAPeer, entries: List[dict]) -> bool:
        """
        Sync RAG memory entries to a peer.
        
        Sends memory entries that the peer doesn't have yet.
        """
        try:
            import aiohttp
            url = f"http://{peer.host}:{peer.port}/aria/sync"
            payload = {
                "from_peer": self.instance_id,
                "entries": entries,
                "timestamp": time.time(),
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload,
                                       timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    return resp.status == 200
        except Exception as e:
            log.error(f"Memory sync failed with {peer.name}: {e}")
            return False

    # ─── FastAPI Server ───────────────────────────────────

    async def start_server(self, port: int = None):
        """
        Start the mesh API server.
        
        This makes this ARIA instance discoverable and 
        able to receive tasks from other instances.
        """
        self.port = port or self.port

        try:
            from fastapi import FastAPI
            from fastapi.responses import JSONResponse
            import uvicorn

            app = FastAPI(title=f"ARIA Mesh — {self.instance_name}")

            @app.get("/aria/status")
            async def get_status():
                return {
                    "instance_id": self.instance_id,
                    "instance_name": self.instance_name,
                    "capabilities": self.capabilities,
                    "peers": len(self.peers),
                    "uptime": time.time(),
                    "status": "online",
                }

            @app.get("/aria/peers")
            async def get_peers():
                return [p.to_dict() for p in self.peers.values()]

            @app.post("/aria/execute")
            async def execute_task(payload: dict):
                task = payload.get("task", "")
                from_peer = payload.get("from_name", "unknown")
                log.info(f"Received task from {from_peer}: {task[:80]}")

                if self._task_handler:
                    result = await self._task_handler(task, payload.get("context", {}))
                    return {"status": "success", "result": result}
                return {"status": "error", "error": "No task handler configured"}

            @app.post("/aria/register")
            async def register(payload: dict):
                peer = self.register_peer(
                    host=payload.get("host"),
                    port=payload.get("port", DEFAULT_PORT),
                    name=payload.get("name", ""),
                    capabilities=payload.get("capabilities", []),
                    peer_id=payload.get("peer_id"),
                )
                return {"status": "registered", "peer": peer.to_dict()}

            @app.post("/aria/sync")
            async def sync_memory(payload: dict):
                entries = payload.get("entries", [])
                log.info(f"Received {len(entries)} memory entries from {payload.get('from_peer')}")
                # TODO: integrate with RAG memory module
                return {"status": "ok", "received": len(entries)}

            # Run server in background
            config = uvicorn.Config(app, host="0.0.0.0", port=self.port, 
                                    log_level="warning")
            server = uvicorn.Server(config)
            self._running = True
            self._server_task = asyncio.create_task(server.serve())
            log.info(f"Mesh server started on LAN port {self.port}")

            # Also start internet tunnel
            asyncio.create_task(self._start_internet_tunnel())

        except ImportError:
            log.warning("FastAPI/uvicorn not installed. Mesh server disabled.")
            log.warning("Install: pip install fastapi uvicorn")
        except Exception as e:
            log.error(f"Mesh server failed: {e}")

    async def _start_internet_tunnel(self):
        """Spins up a free Cloudflare tunnel so mesh is accessible anywhere."""
        cf_bin = ARIA_DIR / "bin" / "cloudflared"
        if not cf_bin.exists():
            log.info("cloudflared not found, mesh will be LAN-only. Install cloudflared to enable internet mesh.")
            return

        import asyncio
        import subprocess
        import re
        try:
            log.info("Starting public internet tunnel for ARIA Mesh...")
            proc = await asyncio.create_subprocess_exec(
                str(cf_bin), "tunnel", "--url", f"http://localhost:{self.port}",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Read stderr line by line looking for the trycloudflare URL
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
                line_text = line.decode('utf-8').strip()
                
                # e.g. "INF Requesting new quick Tunnel on https://xyz.trycloudflare.com"
                # or "INF |  https://xyz.trycloudflare.com  |"
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line_text)
                if match:
                    self.public_url = match.group(0)
                    log.warning(f"🌐 ARIA Mesh is now live on the public internet: {self.public_url}")
                    # Only need to read until we get the URL
                    break
                    
        except Exception as e:
            log.error(f"Tunnel failed to start: {e}")

    def set_task_handler(self, handler):
        """Set the callback function that handles incoming tasks from peers."""
        self._task_handler = handler

    # ─── Discovery ────────────────────────────────────────

    async def discover_lan_peers(self, subnet: str = None) -> List[ARIAPeer]:
        """
        Scan the local network for other ARIA instances.
        
        Tries to connect to the default mesh port on each IP in the subnet.
        """
        discovered = []
        if not subnet:
            # Auto-detect subnet from local IP
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                subnet = ".".join(local_ip.split(".")[:3])
            except Exception:
                subnet = "192.168.1"

        log.info(f"Scanning {subnet}.0/24 for ARIA peers...")

        async def try_peer(ip: str):
            try:
                import aiohttp
                url = f"http://{ip}:{DEFAULT_PORT}/aria/status"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get("instance_id") != self.instance_id:
                                peer = self.register_peer(
                                    host=ip,
                                    port=DEFAULT_PORT,
                                    name=data.get("instance_name", ""),
                                    capabilities=data.get("capabilities", []),
                                    peer_id=data.get("instance_id"),
                                )
                                peer.public_url = data.get("public_url", "")
                                peer.status = "online"
                                discovered.append(peer)
            except Exception:
                pass

        # Scan in parallel (fast)
        tasks = [try_peer(f"{subnet}.{i}") for i in range(1, 255)]
        await asyncio.gather(*tasks)

        if discovered:
            log.info(f"Discovered {len(discovered)} ARIA peers on LAN")
            self._save_peers()

        return discovered

    # ─── Status ───────────────────────────────────────────

    def get_mesh_status(self) -> str:
        """Get formatted mesh status."""
        online = sum(1 for p in self.peers.values() if p.status == "online")
        total = len(self.peers)

        lines = [
            f"🔗 ARIA Mesh Network",
            f"  Instance: {self.instance_name} ({self.instance_id[:8]}...)",
            f"  Port: {self.port} (LAN)",
        ]
        
        if hasattr(self, 'public_url') and self.public_url:
            lines.append(f"  Public URI: {self.public_url} (Global)")
            
        lines.extend([
            f"  Capabilities: {', '.join(self.capabilities)}",
            f"  Server: {'🟢 Running' if self._running else '⚪ Stopped'}",
            f"  Peers: {online} online / {total} total",
        ])

        for pid, peer in self.peers.items():
            icon = "🟢" if peer.status == "online" else "🔴" if peer.status == "offline" else "🟡"
            peer_loc = peer.public_url if peer.public_url else f"{peer.host}:{peer.port}"
            lines.append(f"    {icon} {peer.name} ({peer_loc})")

        return "\n".join(lines)

    @property
    def peer_count(self) -> int:
        return len(self.peers)
