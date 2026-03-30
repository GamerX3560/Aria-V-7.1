"""
ARIA v7 — Vision Engine
Screen awareness through efficient text extraction.
Captures screenshots and reads visible text to understand
what's happening on the user's screen.

Strategy (as per user's suggestion):
- Default: Extract text from screen directly (fast, efficient)
- On-demand: Full screenshot capture + OCR for visual understanding
- NOT continuous image capture — text-first approach
"""

import os
import re
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple

log = logging.getLogger("ARIA.vision")

ARIA_DIR = Path.home() / "aria"
SCREENSHOTS_DIR = ARIA_DIR / "memory" / "screenshots"


class VisionEngine:
    """
    Screen awareness engine.
    
    Primary mode: Read active window title + clipboard + system notifications
    Secondary mode: Screenshot → OCR text extraction
    
    This is much more efficient than continuously capturing images.
    """

    def __init__(self):
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        self._ocr_reader = None

    # ─── Primary: Text-Based Awareness (Fast, Efficient) ───
    
    def get_active_window(self) -> str:
        """Get the currently focused window title and app name."""
        try:
            # Hyprland: use hyprctl
            result = subprocess.run(
                ["hyprctl", "activewindow", "-j"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                title = data.get("title", "Unknown")
                app = data.get("class", "Unknown")
                return f"🪟 Active Window: [{app}] {title}"
        except Exception:
            pass
        
        return "🪟 Active Window: (unable to detect)"

    def get_clipboard_text(self) -> str:
        """Read current clipboard content (text only)."""
        try:
            result = subprocess.run(
                ["wl-paste", "--no-newline"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                text = result.stdout.strip()[:500]
                return f"📋 Clipboard: {text}"
        except Exception:
            pass
        return "📋 Clipboard: (empty or non-text)"

    def get_screen_text_context(self) -> str:
        """
        Get a quick text-based summary of what's visible on screen.
        Uses window title + clipboard — no screenshots required.
        """
        parts = [self.get_active_window(), self.get_clipboard_text()]
        
        # Also check for any notification text
        notif = self._get_latest_notification()
        if notif:
            parts.append(f"🔔 Notification: {notif}")
        
        return "\n".join(parts)

    # ─── Secondary: Screenshot + OCR (On-Demand) ──────────
    
    def capture_screenshot(self, region: str = None) -> Optional[str]:
        """
        Capture a screenshot of the full screen or a selected region.
        
        Args:
            region: Optional, "x,y WxH" format for partial capture.
            
        Returns:
            Path to the saved screenshot, or None on failure.
        """
        timestamp = subprocess.run(["date", "+%Y%m%d_%H%M%S"], 
                                   capture_output=True, text=True).stdout.strip()
        output_path = str(SCREENSHOTS_DIR / f"screen_{timestamp}.png")
        
        try:
            uid = os.getuid()
            env = {
                **os.environ,
                "WAYLAND_DISPLAY": "wayland-1",
                "XDG_RUNTIME_DIR": f"/run/user/{uid}",
            }
            # Inject Hyprland instance
            hypr_dir = f"/run/user/{uid}/hypr"
            if os.path.exists(hypr_dir):
                instances = os.listdir(hypr_dir)
                if instances:
                    env["HYPRLAND_INSTANCE_SIGNATURE"] = instances[0]
            
            cmd = ["grim"]
            if region:
                cmd.extend(["-g", region])
            cmd.append(output_path)
            
            result = subprocess.run(cmd, capture_output=True, timeout=5, env=env)
            if result.returncode == 0:
                log.info(f"Screenshot saved: {output_path}")
                return output_path
            else:
                log.error(f"grim error: {result.stderr.decode()[:200]}")
        except Exception as e:
            log.error(f"Screenshot error: {e}")
        return None

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image using OCR."""
        try:
            # Try easyocr first (better accuracy)
            if self._ocr_reader is None:
                try:
                    import easyocr
                    self._ocr_reader = easyocr.Reader(['en'], gpu=True)
                except ImportError:
                    log.warning("easyocr not available, using tesseract fallback")
                    self._ocr_reader = "tesseract"
            
            if self._ocr_reader == "tesseract":
                result = subprocess.run(
                    ["tesseract", image_path, "-", "--oem", "1"],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            else:
                results = self._ocr_reader.readtext(image_path)
                texts = [r[1] for r in results if r[2] > 0.3]  # confidence > 30%
                return "\n".join(texts)
        except Exception as e:
            log.error(f"OCR error: {e}")
        return ""

    def see_screen(self) -> str:
        """
        Full screen understanding: capture + OCR.
        Returns extracted text from the current screen.
        """
        screenshot = self.capture_screenshot()
        if not screenshot:
            return "Unable to capture screen."
        
        text = self.extract_text_from_image(screenshot)
        if text:
            # Limit output and add context
            lines = text.strip().split('\n')[:30]
            return (
                f"👁️ Screen Content ({len(lines)} text blocks detected):\n"
                + "\n".join(lines)
            )
        return "👁️ Screen appears to have no readable text."

    # ─── Helper Methods ───────────────────────────────────
    
    @staticmethod
    def _get_latest_notification() -> Optional[str]:
        """Get the latest desktop notification (if available)."""
        try:
            # Try dunstctl for dunst notification daemon
            result = subprocess.run(
                ["dunstctl", "history"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                import json
                data = json.loads(result.stdout)
                if data.get("data") and data["data"][0]:
                    latest = data["data"][0][0]
                    summary = latest.get("summary", {}).get("data", "")
                    body = latest.get("body", {}).get("data", "")
                    if summary:
                        return f"{summary}: {body}"[:200]
        except Exception:
            pass
        
        # Fallback: try swaync
        try:
            result = subprocess.run(
                ["swaync-client", "--get-latest"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()[:200]
        except Exception:
            pass
        
        return None
