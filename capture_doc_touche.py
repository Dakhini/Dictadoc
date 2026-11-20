"""
capture_doc_touche.py
---------------------
Variante de capture_doc.py : la capture d'écran se déclenche en appuyant sur une
touche (et non plus à chaque clic de souris). Au lancement, le programme demande
d'appuyer sur la touche de son choix (², F9, ...). La touche est « avalée » :
elle n'écrit rien dans l'application active.

Enregistre ta voix en parallèle, puis transcrit l'audio en local avec Whisper
(aucun service en ligne). L'écran capturé est celui où se trouve le curseur.

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
    python capture_doc_touche.py
    -> fais tes actions normalement en expliquant à voix haute ce que tu fais
    -> appuie sur la touche de ton choix quand le programme te le demande
    -> appuie sur cette touche à chaque moment où tu veux une capture
    -> appuie sur Échap pour arrêter l'enregistrement
"""

import json
import os
import threading
import time
from datetime import datetime

import numpy as np
import sounddevice as sd
import soundfile as sf
from PIL import ImageGrab
from pynput import keyboard, mouse
from screeninfo import get_monitors

SAMPLE_RATE = 16000
OUTPUT_DIR = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
WHISPER_MODEL_SIZE = "small"  # "base" = plus rapide / "medium" = plus précis mais plus lent

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


VK_TOUCHE = 0xDE  # touche de capture (code Windows) ; 0xDE = « ² » en AZERTY, redéfini au lancement
NOM_TOUCHE = "²"
WM_KEYDOWN, WM_KEYUP, WM_SYSKEYDOWN, WM_SYSKEYUP = 0x100, 0x101, 0x104, 0x105

mouse_ctrl = mouse.Controller()
capture_lock = threading.Lock()


def take_capture(x, y, elapsed):
    global step_count
    with capture_lock:  # garde l'ordre et la numérotation si on appuie très vite
        step_count += 1
        filename = f"step_{step_count:03d}.png"
        filepath = os.path.join(OUTPUT_DIR, filename)
        ImageGrab.grab(bbox=monitor_bbox_at(x, y)).save(filepath)
        steps.append({"index": step_count, "timestamp": round(elapsed, 2), "screenshot": filename})
        print(f"[{elapsed:5.1f}s] capture -> {filename}")


def key_filter(msg, data):
    """Intercepte la touche de capture au niveau Windows : déclenche la capture et empêche la frappe."""
    if data.vkCode != VK_TOUCHE:
        return True  # autres touches : traitement normal
    if msg in (WM_KEYDOWN, WM_SYSKEYDOWN) and recording:
        x, y = mouse_ctrl.position
        elapsed = time.time() - start_time
        # thread séparé : le hook clavier Windows doit répondre très vite
        threading.Thread(target=take_capture, args=(x, y, elapsed), daemon=True).start()
    keyboard_listener.suppress_event()  # n'écrit pas la touche dans l'application active


def on_press(key):
    global recording
    if key == keyboard.Key.esc:
        recording = False
        return False  # arrête le listener clavier


def audio_callback(indata, frames, time_info, status):
    audio_frames.append(indata.copy())


keyboard_listener = None


def choisir_touche():
    """Demande à l'utilisateur d'appuyer sur la touche qui déclenchera les captures."""
    global VK_TOUCHE, NOM_TOUCHE
    choix = {}
    done = threading.Event()

    def on_press_choix(key):
        if key == keyboard.Key.esc:
            print("Échap est réservée à l'arrêt de l'enregistrement. Choisis une autre touche.")
            return
        vk = key.vk if isinstance(key, keyboard.KeyCode) else key.value.vk
        if vk is None:
            print("Touche non reconnue, essaie-en une autre.")
            return
        choix["vk"] = vk
        char = getattr(key, "char", None)
        choix["nom"] = char if char else str(key).replace("Key.", "").upper()
        done.set()
        return False

    print("Appuie sur la touche que tu veux utiliser pour déclencher les captures (ex. ², F9, &...) :")
    with keyboard.Listener(on_press=on_press_choix) as listener:
        done.wait()
        listener.join()
    VK_TOUCHE, NOM_TOUCHE = choix["vk"], choix["nom"]
    print(f"-> Touche de capture : {NOM_TOUCHE} (code {VK_TOUCHE})\n")
    time.sleep(0.3)  # laisse passer le relâchement de la touche


def main():
    global start_time, keyboard_listener
    choisir_touche()

    print("Enregistrement démarré.")
    print("Fais tes actions en parlant à voix haute.")
    print(f"Appuie sur {NOM_TOUCHE} pour prendre une capture, sur Échap pour arrêter.\n")
    start_time = time.time()

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback)
    stream.start()

    keyboard_listener = keyboard.Listener(on_press=on_press, win32_event_filter=key_filter)
    keyboard_listener.start()
    keyboard_listener.join()  # bloque jusqu'à Échap

    time.sleep(0.5)  # laisse finir une capture éventuellement en cours
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


if __name__ == "__main__":
    main()
