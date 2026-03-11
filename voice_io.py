"""
voice_io.py — Cross-platform Text-to-Speech and Speech-to-Text.

  TTS:
    Windows      → pyttsx3 (SAPI5).  A new engine instance is created per
                   call so it works safely from any background thread.
    Linux / Pi   → espeak-ng subprocess (no Python bindings needed).

  STT:
    Both platforms → Groq Whisper (whisper-large-v3-turbo).
    Audio is captured with SpeechRecognition, saved to a temp WAV file,
    uploaded to Groq, and the temp file is always cleaned up in a finally block.
    This avoids the flac.exe PermissionError that occurs on Windows when using
    SpeechRecognition's built-in Google engine.
"""

import os
import platform
import subprocess
import tempfile

import speech_recognition as sr

IS_WINDOWS = platform.system() == "Windows"
IS_PI      = platform.machine() in ("armv7l", "aarch64")   # Raspberry Pi

# ALSA output device for the Bluetooth speaker (Pi only).
# Mirrors config.py — defined here to avoid a circular import.
BT_SPEAKER_ALSA_DEVICE = os.environ.get("BT_SPEAKER_ALSA_DEVICE", "bluealsa")

# ── Mic index caches ──────────────────────────────────────────────────────────
# Each scan runs only once per process; results are cached in module globals.
_webcam_mic_index: int | None = None
_mic_scanned: bool = False
_pa_mic_index: int | None = None
_pa_mic_scanned: bool = False


def _find_usb_mic_pyaudio() -> int | None:
    """Enumerate input devices with PyAudio and return the first USB mic index.

    Searches for device names containing 'usb', 'camera', 'webcam', 'video',
    or 'cam'.  Result is cached — the scan runs only once per process.
    Returns None when no USB mic is detected or PyAudio is unavailable.
    """
    global _pa_mic_index, _pa_mic_scanned
    if _pa_mic_scanned:
        return _pa_mic_index

    try:
        import pyaudio
    except ImportError:
        print("[MIC/PA] PyAudio not installed — run: pip install pyaudio")
        _pa_mic_scanned = True
        return None

    keywords = ["usb", "camera", "webcam", "video", "cam", "microphone"]
    pa = pyaudio.PyAudio()
    try:
        count = pa.get_device_count()
        print("[MIC/PA] Enumerating input devices via PyAudio:")
        for i in range(count):
            info = pa.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0:
                name = info.get("name", "")
                print(f"        [{i}] {name}")
                if _pa_mic_index is None and any(k in name.lower() for k in keywords):
                    print(f"[MIC/PA] ✓ Selected USB mic → [{i}] {name}")
                    _pa_mic_index = i
    except Exception as exc:
        print(f"[MIC/PA] Enumeration error: {exc}")
    finally:
        pa.terminate()

    if _pa_mic_index is None:
        print("[MIC/PA] No USB mic found via PyAudio — will use system default")
    _pa_mic_scanned = True
    return _pa_mic_index


def _find_webcam_mic() -> int | None:
    """Scan microphone list via SpeechRecognition and return the USB mic index.

    Searches for names containing 'camera', 'webcam', 'usb', 'video', or 'cam'.
    Result is cached — the scan only runs on the very first call.
    Returns None if not found, causing sr.Microphone() to use the system default.
    """
    global _webcam_mic_index, _mic_scanned
    if _mic_scanned:                          # already scanned — return cached result
        return _webcam_mic_index

    keywords = ["camera", "webcam", "usb", "video", "cam"]
    try:
        names = sr.Microphone.list_microphone_names()
        print("[MIC] Scanning available microphones:")
        for i, name in enumerate(names):
            print(f"        [{i}] {name}")
        for i, name in enumerate(names):
            if any(kw in name.lower() for kw in keywords):
                print(f"[MIC] ✓ Auto-selected USB mic → [{i}] {name}")
                _webcam_mic_index = i
                break
        if _webcam_mic_index is None:
            print("[MIC] No USB mic found via SpeechRecognition — using system default")
    except Exception as exc:
        print(f"[MIC] Could not enumerate microphones: {exc}")

    _mic_scanned = True
    return _webcam_mic_index


def speak(text: str, rate: int = 145) -> None:
    """
    Speak text synchronously and print it to the terminal.
    Safe to call from any thread on both Windows and Linux/Pi.
    """
    print(f"\n[BOT REPLY] {text}")
    print("-" * 60)
    if IS_WINDOWS:
        import pyttsx3
        # Create a fresh engine instance — required for thread safety on Windows
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    elif IS_PI:
        # Raspberry Pi — pipe espeak-ng stdout → aplay → Bluetooth speaker.
        # espeak-ng --stdout writes raw PCM/WAV to stdout; aplay routes it to
        # the BlueZ ALSA device (bluealsa) so audio reaches the BT speaker.
        espeak_cmd = ["espeak-ng", "-s", str(rate), "-v", "en+f3", "--stdout", text]
        try:
            espeak_proc = subprocess.Popen(
                espeak_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            aplay_result = subprocess.run(
                ["aplay", "-D", BT_SPEAKER_ALSA_DEVICE, "-q"],
                stdin=espeak_proc.stdout,
                stderr=subprocess.PIPE,
            )
            espeak_proc.wait()
            if aplay_result.returncode != 0:
                err = aplay_result.stderr.decode(errors="replace").strip()
                print(f"[TTS] BT speaker '{BT_SPEAKER_ALSA_DEVICE}' error: {err}")
                print("[TTS] Falling back to default ALSA output")
                subprocess.run(
                    ["espeak-ng", "-s", str(rate), "-v", "en+f3", text],
                    check=False,
                )
        except FileNotFoundError as exc:
            print(f"[TTS] Command not found ({exc}) — install with:")
            print("  sudo apt install espeak-ng alsa-utils")
    else:
        # Generic Linux desktop — en+f3 = English female voice; -s = speed (wpm)
        subprocess.run(
            ["espeak-ng", "-s", str(rate), "-v", "en+f3", text],
            check=False,
        )


def listen(groq_client, whisper_model: str,
           timeout: int = 5, phrase_limit: int = 8) -> str:
    """
    Record one utterance from the default microphone and transcribe
    it via Groq Whisper.

    Returns the transcribed text, or an empty string on timeout / error.
    """
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True

    # ── Step 1: capture microphone audio ─────────────────────────────────────
    # On Pi: try PyAudio enumeration first (more reliable with USB mics),
    # then fall back to SpeechRecognition scan, then use system default.
    if IS_WINDOWS:
        mic_index = None
    elif IS_PI:
        mic_index = _find_usb_mic_pyaudio()
        if mic_index is None:
            mic_index = _find_webcam_mic()
    else:
        mic_index = _find_webcam_mic()
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("\n[LISTENING] Adjusting for ambient noise…")
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            print(f"[LISTENING] *** Speak now  (up to {phrase_limit}s) ***")
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit,
            )
        print("[LISTENING] Audio captured — transcribing…")
    except sr.WaitTimeoutError:
        print("[LISTENING] Timed out — no speech detected.")
        return ""

    # ── Step 2: transcribe via Groq Whisper ───────────────────────────────────
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio.get_wav_data())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            result = groq_client.audio.transcriptions.create(
                model=whisper_model,
                file=("audio.wav", f, "audio/wav"),
            )

        text = result.text.strip()
        print(f"[YOU SAID]  \"{text}\"")
        return text

    except Exception as exc:
        print(f"[STT ERROR] {exc}")
        return ""

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
