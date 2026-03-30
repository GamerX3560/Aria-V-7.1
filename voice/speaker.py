import os
import re
import subprocess

PIPER_BIN = "/opt/piper-tts/piper"
MODEL_PATH = os.path.expanduser("~/aria/voice/models/en_US-lessac-medium.onnx")
MAX_SPEECH_LEN = 500  # Don't speak excessively long text

def clean_text_for_speech(text):
    """Remove markdown formatting, code blocks, and URLs before speaking."""
    # Remove code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Remove markdown bold/italic/links
    text = text.replace("*", "").replace("_", "")
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [text](url) → text
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove emoji (common unicode ranges)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:MAX_SPEECH_LEN]

def speak(text):
    text = clean_text_for_speech(text)
    if not text or len(text) < 2:
        return

    if not os.path.exists(PIPER_BIN):
        print(f"[SPEAKER] Piper not found at {PIPER_BIN}")
        return
    if not os.path.exists(MODEL_PATH):
        print(f"[SPEAKER] Voice model not found at {MODEL_PATH}")
        return

    print(f"[SPEAKER] Speaking: {text[:80]}...")
    try:
        # Use pw-play (PipeWire native) instead of aplay for Wayland
        process = subprocess.Popen(
            [PIPER_BIN, "--model", MODEL_PATH, "--output_file", "-", "-q"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        play_proc = subprocess.Popen(
            ["pw-play", "--rate=22050", "--channels=1", "--format=s16", "-"],
            stdin=process.stdout,
            stderr=subprocess.DEVNULL
        )
        process.communicate(input=text.encode('utf-8'), timeout=30)
        play_proc.wait(timeout=30)
    except subprocess.TimeoutExpired:
        print("[SPEAKER] Speech timed out")
        process.kill()
        play_proc.kill()
    except FileNotFoundError as e:
        print(f"[SPEAKER] Missing binary: {e}")
    except Exception as e:
        print(f"[SPEAKER] Error: {e}")

if __name__ == "__main__":
    import sys
    speak(sys.argv[1] if len(sys.argv) > 1 else "Hello, I am Aria.")
