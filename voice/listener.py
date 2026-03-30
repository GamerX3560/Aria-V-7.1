#!/usr/bin/env python3
"""
ARIA Voice Listener — Always-on wake word detection + Whisper STT.
Runs as systemd service (aria-voice.service).
"""
import os
import sys
import time
import signal
import logging
import numpy as np
import pyaudio

# Configure logging before imports that print
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [VOICE] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("VOICE")

# Lazy imports to speed up startup
sys.path.insert(0, os.path.expanduser("~/aria"))
sys.path.insert(0, os.path.expanduser("~/aria/voice"))

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280
WAKEWORD = "hey_jarvis"
WAKEWORD_THRESHOLD = 0.6
LISTEN_TIMEOUT = 5
PHRASE_LIMIT = 15
COOLDOWN_SECS = 1.0

# Graceful shutdown
_running = True
def _sig_handler(sig, frame):
    global _running
    _running = False
    log.info("Shutting down...")

signal.signal(signal.SIGTERM, _sig_handler)
signal.signal(signal.SIGINT, _sig_handler)

def lazy_load_models():
    """Load heavy models only when needed, not at import time."""
    import speech_recognition as sr
    from faster_whisper import WhisperModel
    from openwakeword.model import Model

    log.info("Loading Whisper model (tiny.en, CPU, int8)...")
    whisper = WhisperModel("tiny.en", device="cpu", compute_type="int8")

    log.info("Loading OpenWakeWord model...")
    oww = Model(wakeword_models=[WAKEWORD], inference_framework="onnx")

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_threshold = True

    return whisper, oww, recognizer

def process_voice_command(text):
    """Send transcribed text to the router and speak the response."""
    import router
    import speaker

    log.info(f"[USER] {text}")
    try:
        response = router.process_message(text)
        log.info(f"[ARIA] {response[:120]}...")
        speaker.speak(response)
    except Exception as e:
        log.error(f"Router error: {e}")

def listen_loop():
    import speech_recognition as sr

    whisper_model, oww_model, recognizer = lazy_load_models()

    audio = pyaudio.PyAudio()
    mic_stream = None

    log.info("Voice interface active. Listening for wake word...")

    while _running:
        try:
            if mic_stream is None or not mic_stream.is_active():
                mic_stream = audio.open(
                    format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK
                )

            # Read chunk
            pcm = np.frombuffer(
                mic_stream.read(CHUNK, exception_on_overflow=False),
                dtype=np.int16
            )

            # Predict wake word
            predictions = oww_model.predict(pcm)
            score = list(predictions.values())[0] if predictions else 0.0

            if score > WAKEWORD_THRESHOLD:
                log.info("[WAKEWORD] Detected! Listening for command...")

                # Release mic for SpeechRecognition
                mic_stream.stop_stream()
                mic_stream.close()
                mic_stream = None

                # Record and transcribe
                with sr.Microphone() as source:
                    try:
                        audio_data = recognizer.listen(
                            source, timeout=LISTEN_TIMEOUT,
                            phrase_time_limit=PHRASE_LIMIT
                        )
                        log.info("Transcribing...")

                        temp_wav = f"/tmp/aria_cmd_{int(time.time())}.wav"
                        with open(temp_wav, "wb") as f:
                            f.write(audio_data.get_wav_data())

                        segments, _ = whisper_model.transcribe(temp_wav, beam_size=5)
                        transcription = "".join(
                            [seg.text for seg in segments]
                        ).strip()

                        # Cleanup temp file
                        try:
                            os.unlink(temp_wav)
                        except OSError:
                            pass

                        if transcription:
                            process_voice_command(transcription)
                        else:
                            log.info("No speech detected.")

                    except sr.WaitTimeoutError:
                        log.info("Timed out listening for command.")
                    except Exception as e:
                        log.error(f"STT error: {e}")

                # Reset wake word model state
                oww_model.reset()

                log.info("Returning to wake word detection...")
                time.sleep(COOLDOWN_SECS)

        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"Loop error: {e}")
            time.sleep(2)

    # Cleanup
    if mic_stream:
        mic_stream.stop_stream()
        mic_stream.close()
    audio.terminate()
    log.info("Voice interface stopped.")

if __name__ == "__main__":
    log.info("═══════════════════════════════════════")
    log.info("  ARIA v4 — Voice Interface Active")
    log.info(f"  Wake word: '{WAKEWORD}'")
    log.info("═══════════════════════════════════════")
    listen_loop()
