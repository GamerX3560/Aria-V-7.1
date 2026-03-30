"""
ARIA v7 — Voice TTS Engine
Text-to-speech with male and female voice switching.
Uses local TTS engines — no cloud APIs needed.

Setup Options (during install):
  Option 1 — VRAM Mode (best quality):
    Requires: LuxTTS + PyTorch with ROCm (for AMD GPU) or CUDA (for Nvidia GPU)
    Quality: Ultra-realistic (150x realtime, voice cloning, 48kHz)
    VRAM: ~1GB
    Status: Needs PyTorch ROCm rebuild on this AMD system. Ready when ROCm is configured.

  Option 2 — Optimized Mode (current, no GPU needed):
    Requires: piper-tts (installed at /opt/piper-tts/piper)
    Quality: Natural-sounding neural TTS (3 voice models: male/female/aria)
    VRAM: 0 (CPU only)
    Status: ✅ WORKING NOW

Backends (priority order):
1. LuxTTS (GPU, ultra-realistic) — future, when ROCm is ready
2. piper (CPU, neural, natural) — ✅ active now
3. espeak-ng (CPU, fast, robotic) — fallback
"""

import os
import subprocess
import logging
import tempfile
from pathlib import Path
from typing import Optional

log = logging.getLogger("ARIA.voice")

ARIA_DIR = Path.home() / "aria"
VOICE_DIR = ARIA_DIR / "voice"
VOICE_MODELS_DIR = VOICE_DIR / "models"

# ─── Voice Profiles ──────────────────────────────────────
VOICE_PROFILES = {
    "male": {
        "espeak": {"voice": "en+m3", "speed": "160", "pitch": "40"},
        "piper": {"model": "en_US-lessac-medium", "speaker": "0"},
        "description": "Deep, confident male voice",
    },
    "female": {
        "espeak": {"voice": "en+f3", "speed": "165", "pitch": "60"},
        "piper": {"model": "en_US-amy-medium", "speaker": "0"},
        "description": "Clear, warm female voice",
    },
    "aria": {
        "espeak": {"voice": "en+f2", "speed": "170", "pitch": "55"},
        "piper": {"model": "en_US-libritts_r-medium", "speaker": "0"},
        "description": "ARIA's signature voice",
    },
}


class VoiceTTSEngine:
    """
    Text-to-speech engine with voice profile switching.
    
    Usage:
        tts = VoiceTTSEngine()
        tts.speak("Hello Mangesh!")
        tts.set_voice("female")
        tts.speak("How can I help you today?")
    """

    def __init__(self, default_voice: str = "aria"):
        self.current_voice = default_voice
        self._backend = self._detect_backend()
        VOICE_MODELS_DIR.mkdir(parents=True, exist_ok=True)
        log.info(f"TTS initialized. Backend: {self._backend}, Voice: {self.current_voice}")

    # Known piper binary locations
    PIPER_PATHS = [
        "/opt/piper-tts/piper",  # Arch AUR (piper-tts-bin)
        "/usr/bin/piper",
        "/usr/local/bin/piper",
    ]

    @staticmethod
    def _find_piper() -> str:
        """Find the piper binary path."""
        for path in VoiceTTSEngine.PIPER_PATHS:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        return ""

    @staticmethod
    def _detect_backend() -> str:
        """Detect the best available TTS backend."""
        # Check for piper (neural, best quality)
        piper_path = VoiceTTSEngine._find_piper()
        if piper_path:
            return "piper"
        
        # Check for espeak-ng (always available on Linux)
        try:
            result = subprocess.run(["espeak-ng", "--version"], capture_output=True, timeout=3)
            if result.returncode == 0:
                return "espeak"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Fallback to basic espeak
        try:
            result = subprocess.run(["espeak", "--version"], capture_output=True, timeout=3)
            if result.returncode == 0:
                return "espeak"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return "none"

    def set_voice(self, voice_name: str) -> bool:
        """Switch to a different voice profile."""
        if voice_name.lower() in VOICE_PROFILES:
            self.current_voice = voice_name.lower()
            log.info(f"Voice switched to: {voice_name}")
            return True
        log.warning(f"Unknown voice profile: {voice_name}")
        return False

    def get_available_voices(self) -> list:
        """List all available voice profiles."""
        return [
            {"name": name, "description": profile["description"]}
            for name, profile in VOICE_PROFILES.items()
        ]

    def speak(self, text: str, save_to: Optional[str] = None) -> bool:
        """
        Speak text using the current voice profile.
        
        Args:
            text: Text to speak.
            save_to: Optional file path to save audio instead of playing.
            
        Returns:
            True if successful.
        """
        if not text.strip():
            return False

        if self._backend == "piper":
            return self._speak_piper(text, save_to)
        elif self._backend == "espeak":
            return self._speak_espeak(text, save_to)
        else:
            log.error("No TTS backend available. Install espeak-ng: yay -S espeak-ng")
            return False

    def _speak_espeak(self, text: str, save_to: Optional[str] = None) -> bool:
        """Speak using espeak-ng."""
        profile = VOICE_PROFILES[self.current_voice]["espeak"]
        cmd = [
            "espeak-ng" if self._backend == "espeak" else "espeak",
            "-v", profile["voice"],
            "-s", profile["speed"],
            "-p", profile["pitch"],
        ]
        
        if save_to:
            cmd.extend(["-w", save_to])
        
        cmd.append(text[:5000])  # Limit text length
        
        try:
            env = {**os.environ}
            # Get Wayland audio access
            uid = os.getuid()
            env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
            
            result = subprocess.run(cmd, capture_output=True, timeout=30, env=env)
            if result.returncode == 0:
                log.info(f"Spoke {len(text)} chars with {self.current_voice} voice")
                return True
            else:
                log.error(f"espeak error: {result.stderr.decode()[:200]}")
                return False
        except Exception as e:
            log.error(f"TTS error: {e}")
            return False

    def _speak_piper(self, text: str, save_to: Optional[str] = None) -> bool:
        """Speak using piper TTS (neural, high quality)."""
        profile = VOICE_PROFILES[self.current_voice]["piper"]
        piper_bin = self._find_piper()
        if not piper_bin:
            log.warning("Piper binary not found, falling back to espeak")
            return self._speak_espeak(text, save_to)
        
        if save_to:
            output_path = save_to
        else:
            output_path = tempfile.mktemp(suffix=".wav")
        
        # Model path: models are stored as <name>.onnx
        model_path = VOICE_MODELS_DIR / f"{profile['model']}.onnx"
        if not model_path.exists():
            log.warning(f"Piper model not found: {model_path}, falling back to espeak")
            return self._speak_espeak(text, save_to)
        
        try:
            # Piper reads from stdin and outputs WAV
            cmd = [
                piper_bin,
                "--model", str(model_path),
                "--output_file", output_path,
            ]
            
            env = {**os.environ}
            uid = os.getuid()
            env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
            
            result = subprocess.run(
                cmd, input=text.encode(), capture_output=True, timeout=60, env=env
            )
            
            if result.returncode == 0:
                if not save_to:
                    # Play the audio via PipeWire
                    subprocess.Popen(
                        ["pw-play", output_path],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        env=env
                    )
                log.info(f"Spoke {len(text)} chars with piper {self.current_voice}")
                return True
            else:
                log.warning(f"Piper failed: {result.stderr.decode()[:200]}, falling back to espeak")
                return self._speak_espeak(text, save_to)
        except Exception as e:
            log.warning(f"Piper error ({e}), falling back to espeak")
            return self._speak_espeak(text, save_to)

    def speak_async(self, text: str) -> bool:
        """Speak in the background (non-blocking)."""
        import threading
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()
        return True
