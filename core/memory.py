"""
ARIA v6 — Conversation Memory
Auto-compressing, session-persistent conversation memory system.
Inspired by agenticSeek's Memory architecture.
"""

import os
import json
import time
import datetime
import threading
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger("ARIA.memory")

ARIA_DIR = Path.home() / "aria"
MEMORY_DIR = ARIA_DIR / "memory"
FACTS_PATH = ARIA_DIR / "memory.json"
CONVERSATIONS_DIR = MEMORY_DIR / "conversations"

class ConversationMemory:
    """
    Manages the conversation history with auto-compression and persistence.
    
    Features:
    - Sliding window to keep context manageable
    - Auto-compression of long messages
    - Session save/load for persistence across restarts
    - Thread-safe operations
    - Semantic fact recall from long-term memory
    """

    def __init__(self, system_prompt: str, max_messages: int = 50, 
                 max_message_len: int = 3000, session_id: str = None):
        self._lock = threading.Lock()
        self._messages = [{"role": "system", "content": system_prompt}]
        self.max_messages = max_messages
        self.max_message_len = max_message_len
        self.session_id = session_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure directories exist
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

    @property
    def messages(self) -> list:
        """Get a copy of the current message history."""
        with self._lock:
            return list(self._messages)

    @property
    def context_length(self) -> int:
        """Approximate total character count in context."""
        with self._lock:
            return sum(len(m.get("content", "")) for m in self._messages)

    def update_system_prompt(self, prompt: str):
        """Update the system prompt (always message[0])."""
        with self._lock:
            if self._messages and self._messages[0]["role"] == "system":
                self._messages[0]["content"] = prompt
            else:
                self._messages.insert(0, {"role": "system", "content": prompt})

    def push(self, role: str, content: str):
        """
        Add a message to the conversation history.
        Auto-compresses if the message is too long.
        Auto-trims old messages if history exceeds max_messages.
        """
        with self._lock:
            # Compress long messages
            if len(content) > self.max_message_len:
                content = self._compress_message(content)

            self._messages.append({
                "role": role,
                "content": content,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            # Trim old messages, keeping system prompt
            if len(self._messages) > self.max_messages + 1:
                system = self._messages[0]
                # Keep last max_messages entries
                self._messages = [system] + self._messages[-(self.max_messages):]
                log.info(f"Trimmed conversation to {len(self._messages)} messages")

    def _compress_message(self, text: str) -> str:
        """
        Compress a long message by keeping the first and last portions.
        This is a fast heuristic — no ML model needed.
        """
        if len(text) <= self.max_message_len:
            return text
        
        keep = self.max_message_len // 2
        head = text[:keep]
        tail = text[-keep:]
        omitted = len(text) - (keep * 2)
        return f"{head}\n\n... [{omitted} chars omitted for context efficiency] ...\n\n{tail}"

    def clear(self):
        """Clear all messages except the system prompt."""
        with self._lock:
            self._messages = self._messages[:1]
            log.info("Conversation memory cleared")

    def save_session(self):
        """Save the current conversation to disk."""
        path = CONVERSATIONS_DIR / f"session_{self.session_id}.json"
        with self._lock:
            data = {
                "session_id": self.session_id,
                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "messages": self._messages
            }
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            log.info(f"Session saved to {path}")
        except Exception as e:
            log.error(f"Failed to save session: {e}")

    def load_last_session(self) -> bool:
        """Load the most recent conversation session."""
        try:
            sessions = sorted(CONVERSATIONS_DIR.glob("session_*.json"), 
                            key=lambda p: p.stat().st_mtime, reverse=True)
            if not sessions:
                log.info("No previous session found")
                return False
            
            with open(sessions[0], 'r') as f:
                data = json.load(f)
            
            with self._lock:
                system = self._messages[0] if self._messages else None
                self._messages = data.get("messages", [])
                # Ensure system prompt is current
                if system and (not self._messages or self._messages[0]["role"] != "system"):
                    self._messages.insert(0, system)
                elif system:
                    self._messages[0] = system
            
            log.info(f"Loaded session from {sessions[0].name} ({len(self._messages)} messages)")
            return True
        except Exception as e:
            log.error(f"Failed to load session: {e}")
            return False

    # ─── Long-Term Fact Storage ───────────────────────────────
    
    @staticmethod
    def _load_facts() -> dict:
        try:
            with open(FACTS_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"facts": {}, "preferences": {}, "skills": {}}

    @staticmethod
    def _save_facts(data: dict):
        tmp = str(FACTS_PATH) + ".tmp"
        with open(tmp, 'w') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, str(FACTS_PATH))

    def store_fact(self, key: str, value: str):
        """Store a fact in long-term memory."""
        data = self._load_facts()
        data["facts"][key] = {"value": value, "added": time.strftime("%Y-%m-%d")}
        self._save_facts(data)
        log.info(f"Stored fact: {key} = {value}")

    def recall_fact(self, query: str) -> Optional[str]:
        """Fuzzy-search for a fact in long-term memory."""
        data = self._load_facts()
        query_lower = query.lower()
        
        for key, info in data.get("facts", {}).items():
            if query_lower in key.lower() or query_lower in str(info.get("value", "")).lower():
                return info["value"]
        
        for name, info in data.get("skills", {}).items():
            if query_lower in name.lower() or query_lower in info.get("trigger", "").lower():
                return f"SKILL:{info['script']}"
        
        return None

    def get_facts_summary(self) -> str:
        """Get a formatted summary of all stored facts."""
        data = self._load_facts()
        lines = []
        for k, v in data.get("facts", {}).items():
            lines.append(f"  • {k}: {v['value']}")
        for k, v in data.get("skills", {}).items():
            lines.append(f"  ⚡ {k}: {v.get('trigger', 'no trigger')}")
        return "\n".join(lines) if lines else "  (no facts stored)"
