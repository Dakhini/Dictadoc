"""
capture_doc.py
---------------
Enregistre tes actions (clic -> capture d'écran) et ta voix en parallèle,
puis transcrit l'audio en local avec Whisper (aucun service en ligne).

Résultat : un dossier capture_AAAAMMJJ_HHMMSS/ contenant :
  - step_001.png, step_002.png, ...   (une capture par clic)
  - narration.wav                      (audio brut)
  - transcript.txt                     (transcription horodatée complète)
  - steps.json                         (chaque étape + le texte dit au même moment)

Étape suivante : envoie le contenu de ce dossier (images + steps.json) à Claude
et demande-lui de générer la documentation .md.

Installation (une seule fois) :
    pip install pynput pillow sounddevice soundfile numpy faster-whisper screeninfo

Utilisation :
    python capture_doc.py
    -> fais tes actions normalement en expliquant à voix haute ce que tu fais
    -> appuie sur Échap pour arrêter l'enregistrement
"""

import json
import os
import sys
import time
from datetime import datetime

import numpy as np
import sounddevice as sd
import soundfile as sf
from PIL import ImageGrab
from pynput import keyboard, mouse
from screeninfo import get_monitors

SAMPLE_RATE = 16000
# Version .exe : les captures sont créées à côté de l'exécutable (et non dans le dossier courant)
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
WHISPER_MODEL_SIZE = "small"  # "base" = plus rapide / "medium" = plus précis mais plus lent

CHECK_MODE = "--check" in sys.argv  # auto-test : vérifie les imports sans rien enregistrer

if not CHECK_MODE:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

start_time = None
step_count = 0
steps = []
audio_frames = []
recording = True


def monitor_bbox_at(x, y):
    for m in get_monitors():
        if m.x <= x < m.x + m.width and m.y <= y < m.y + m.height:
            return (m.x, m.y, m.x + m.width, m.y + m.height)
    return None  # coordonnées hors de tout écran connu -> capture globale en secours


def on_click(x, y, button, pressed):
    global step_count
    if pressed and recording:
        step_count += 1
        elapsed = time.time() - start_time
        filename = f"step_{step_count:03d}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        bbox = monitor_bbox_at(x, y)
        ImageGrab.grab(bbox=bbox).save(filepath)
        steps.append({"index": step_count, "timestamp": round(elapsed, 2), "screenshot": filename})
        print(f"[{elapsed:5.1f}s] capture -> {filename}")


def on_press(key):
    global recording
    if key == keyboard.Key.esc:
        recording = False
        return False  # arrête le listener clavier


def audio_callback(indata, frames, time_info, status):
    audio_frames.append(indata.copy())


def main():
    global start_time

    print("Enregistrement démarré.")
    print("Fais tes actions en parlant à voix haute. Appuie sur Échap pour arrêter.\n")
    start_time = time.time()

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback)
    stream.start()

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    keyboard_listener.join()  # bloque jusqu'à Échap

    mouse_listener.stop()
    stream.stop()
    stream.close()

    audio_path = os.path.join(OUTPUT_DIR, "narration.wav")
    if audio_frames:
        audio_data = np.concatenate(audio_frames, axis=0)
        sf.write(audio_path, audio_data, SAMPLE_RATE)
        print(f"\nAudio enregistré : {audio_path}")

    with open(os.path.join(OUTPUT_DIR, "steps.json"), "w", encoding="utf-8") as f:
        json.dump(steps, f, ensure_ascii=False, indent=2)

    if not audio_frames:
        print(f"\nTerminé (sans audio). Dossier : {OUTPUT_DIR}")
        return

    print("Transcription locale en cours (peut prendre 1-2 minutes selon la durée)...")
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        # On passe directement le signal (numpy) pour ne pas dépendre du décodeur PyAV
        audio_np = audio_data.astype("float32").flatten()
        segments, _ = model.transcribe(audio_np, language="fr")
        segments = list(segments)

        with open(os.path.join(OUTPUT_DIR, "transcript.txt"), "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(f"[{seg.start:.1f}s -> {seg.end:.1f}s] {seg.text.strip()}\n")

        for step in steps:
            best_text, best_diff = "", float("inf")
            for seg in segments:
                mid = (seg.start + seg.end) / 2
                diff = abs(mid - step["timestamp"])
                if diff < best_diff:
                    best_diff, best_text = diff, seg.text.strip()
            step["narration"] = best_text

        with open(os.path.join(OUTPUT_DIR, "steps.json"), "w", encoding="utf-8") as f:
            json.dump(steps, f, ensure_ascii=False, indent=2)

        print("Transcription terminée.")
    except ImportError:
        print("faster-whisper n'est pas installé -> transcription ignorée.")
        print("Installe-le avec : pip install faster-whisper")

    print(f"\nTout est dans le dossier : {OUTPUT_DIR}")
    print("Envoie les .png + steps.json à Claude pour générer la doc en .md")


def check():
    import faster_whisper
    from faster_whisper.vad import get_assets_path

    vad = os.path.join(get_assets_path(), "silero_vad_v6.onnx")
    print("faster_whisper OK, assets VAD présents :", os.path.isdir(get_assets_path()))
    print("sounddevice OK, périphériques audio :", len(sd.query_devices()))
    print("screeninfo OK, écrans :", len(get_monitors()))


if __name__ == "__main__":
    if CHECK_MODE:
        check()
    else:
        main()
