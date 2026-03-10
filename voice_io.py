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


def _find_webcam_mic() -> int | None:
    """Scan microphone list and return the index of the webcam's built-in mic.

    Matches names containing 'camera', 'webcam', 'usb', 'video', or 'cam'.
    Returns None if not found, which makes sr.Microphone() fall back to the
    system default.
    """
    keywords = ["camera", "webcam", "usb", "video", "cam"]
    try:
        names = sr.Microphone.list_microphone_names()
        print("[MIC] Available microphones:")
        for i, name in enumerate(names):
            print(f"       [{i}] {name}")
        for i, name in enumerate(names):
            if any(kw in name.lower() for kw in keywords):
                print(f"[MIC] Selected webcam mic: [{i}] {name}")
                return i
    except Exception as e:
        print(f"[MIC] Could not list microphones: {e}")
    print("[MIC] No webcam mic found — using system default")
    return None


def speak(text: str, rate: int = 145) -> None:
    """
    Speak text synchronously.
    Safe to call from any thread on both Windows and Linux/Pi.
    """
    print(f"[AI]  {text}")
    if IS_WINDOWS:
        import pyttsx3
        # Create a fresh engine instance — required for thread safety on Windows
        engine = pyttsx3.init()
        engine.setProperty("rate", rate)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    else:
        # en+f3 = English female voice; -s = speed (words/min)
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
    mic_index = None if IS_WINDOWS else _find_webcam_mic()
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("[LISTEN] Listening… speak now")
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_limit,
            )
    except sr.WaitTimeoutError:
        print("[LISTEN] Timeout — no speech detected.")
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
        print(f"[USER] {text}")
        return text

    except Exception as exc:
        print(f"[STT ERROR] {exc}")
        return ""

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
