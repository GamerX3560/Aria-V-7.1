"""
ARIA v7 — Encrypted Storage
Transparent AES-256 Fernet encryption for all sensitive data.

Design priorities (per user):
- Performance: instant read/write, no startup delays
- Availability: secrets always accessible to agents, browser, logins
- No prompts: auto-unlock, no passphrase on every startup
- Transparent: agents call store/retrieve without knowing about encryption

How it works:
1. On first run, generates a random master key and saves it to ~/.aria_key
   (chmod 600, only readable by the user)
2. All data is encrypted/decrypted transparently via store()/retrieve()
3. Agents access secrets via get_secret()/set_secret() — instant, no prompts
"""

import os
import json
import base64
import logging
from pathlib import Path
from typing import Any, Optional, Dict

log = logging.getLogger("ARIA.crypto")

ARIA_DIR = Path.home() / "aria"
KEY_FILE = Path.home() / ".aria_key"
VAULT_PATH = ARIA_DIR / "vault.json"
ENCRYPTED_VAULT_PATH = ARIA_DIR / "memory" / "encrypted_vault.enc"


class EncryptedStorage:
    """
    Transparent encryption layer for ARIA's sensitive data.
    
    Usage:
        store = EncryptedStorage()
        store.set_secret("nvidia_api_key", "nvapi-xxx")
        key = store.get_secret("nvidia_api_key")  # instant
        
        # Encrypt/decrypt arbitrary data
        store.encrypt_file("~/aria/memory/sessions.json")
        data = store.decrypt_file("~/aria/memory/sessions.json.enc")
    """

    def __init__(self):
        self._fernet = None
        self._secrets_cache: Dict[str, str] = {}
        self._init_encryption()
        self._load_secrets()

    def _init_encryption(self):
        """Initialize encryption with auto-generated key."""
        try:
            from cryptography.fernet import Fernet
            
            if KEY_FILE.exists():
                key = KEY_FILE.read_bytes().strip()
            else:
                # Generate new key on first run
                key = Fernet.generate_key()
                KEY_FILE.write_bytes(key)
                os.chmod(str(KEY_FILE), 0o600)  # Only owner can read
                log.info("Generated new encryption key")
            
            self._fernet = Fernet(key)
            log.info("Encryption initialized (AES-256 Fernet)")
        except ImportError:
            log.warning("cryptography not installed. Secrets stored in plaintext.")
            log.warning("Install: python3 -m pip install cryptography --break-system-packages")
        except Exception as e:
            log.error(f"Encryption init error: {e}")

    def _load_secrets(self):
        """Load secrets into memory cache for instant access."""
        # Try encrypted vault first
        if ENCRYPTED_VAULT_PATH.exists() and self._fernet:
            try:
                encrypted = ENCRYPTED_VAULT_PATH.read_bytes()
                decrypted = self._fernet.decrypt(encrypted)
                self._secrets_cache = json.loads(decrypted.decode())
                log.info(f"Loaded {len(self._secrets_cache)} secrets from encrypted vault")
                return
            except Exception as e:
                log.error(f"Failed to decrypt vault: {e}")
        
        # Fall back to plain vault.json
        if VAULT_PATH.exists():
            try:
                self._secrets_cache = json.loads(VAULT_PATH.read_text())
                log.info(f"Loaded {len(self._secrets_cache)} secrets from plain vault")
                # Auto-migrate to encrypted
                self._save_secrets()
            except Exception:
                self._secrets_cache = {}

    def _save_secrets(self):
        """Save secrets to encrypted vault."""
        ENCRYPTED_VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(self._secrets_cache, indent=2).encode()
        
        if self._fernet:
            encrypted = self._fernet.encrypt(data)
            ENCRYPTED_VAULT_PATH.write_bytes(encrypted)
        else:
            # Fallback: save as plain JSON
            VAULT_PATH.write_text(json.dumps(self._secrets_cache, indent=2))

    # ─── Secret Access (instant, cached) ──────────────────

    def get_secret(self, key: str, default: str = "") -> str:
        """
        Get a secret instantly from cache.
        Used by agents, browser, logins — always available.
        """
        return self._secrets_cache.get(key, default)

    def set_secret(self, key: str, value: str):
        """Store a secret. Encrypted at rest, instant in memory."""
        self._secrets_cache[key] = value
        self._save_secrets()
        log.info(f"Secret stored: {key}")

    def delete_secret(self, key: str) -> bool:
        """Delete a secret."""
        if key in self._secrets_cache:
            del self._secrets_cache[key]
            self._save_secrets()
            return True
        return False

    def list_secrets(self) -> list:
        """List all secret keys (not values)."""
        return list(self._secrets_cache.keys())

    def get_all_secrets(self) -> dict:
        """
        Get all secrets. Used by the system prompt builder
        and automation scripts that need credentials.
        """
        return dict(self._secrets_cache)

    # ─── File Encryption ──────────────────────────────────

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt arbitrary bytes."""
        if self._fernet:
            return self._fernet.encrypt(data)
        return data  # Fallback: no encryption

    def decrypt_data(self, data: bytes) -> bytes:
        """Decrypt arbitrary bytes."""
        if self._fernet:
            return self._fernet.decrypt(data)
        return data

    def encrypt_file(self, filepath: str) -> str:
        """
        Encrypt a file in-place (saves as .enc).
        Returns path to encrypted file.
        """
        path = Path(filepath).expanduser()
        if not path.exists():
            return ""
        
        data = path.read_bytes()
        encrypted = self.encrypt_data(data)
        
        enc_path = path.with_suffix(path.suffix + ".enc")
        enc_path.write_bytes(encrypted)
        return str(enc_path)

    def decrypt_file(self, filepath: str) -> Optional[bytes]:
        """Decrypt a .enc file and return the raw bytes."""
        path = Path(filepath).expanduser()
        if not path.exists():
            return None
        
        encrypted = path.read_bytes()
        return self.decrypt_data(encrypted)

    def encrypt_json(self, data: Any) -> bytes:
        """Encrypt a JSON-serializable object."""
        json_bytes = json.dumps(data).encode()
        return self.encrypt_data(json_bytes)

    def decrypt_json(self, encrypted: bytes) -> Any:
        """Decrypt bytes back to a JSON object."""
        decrypted = self.decrypt_data(encrypted)
        return json.loads(decrypted.decode())

    # ─── Status ───────────────────────────────────────────

    def get_status(self) -> str:
        """Get encryption status."""
        enc_status = "🔒 Active (AES-256)" if self._fernet else "⚠️ Plaintext (install cryptography)"
        return (
            f"Encryption: {enc_status}\n"
            f"Secrets: {len(self._secrets_cache)} stored\n"
            f"Key file: {'✓' if KEY_FILE.exists() else '✗'} {KEY_FILE}"
        )

    def is_encrypted(self) -> bool:
        """Check if encryption is active."""
        return self._fernet is not None
