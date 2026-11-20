# DictaDoc — capture_doc.py

Enregistre tes actions (clic → capture d'écran) et ta voix en parallèle, puis transcrit l'audio en local avec Whisper (aucun service en ligne).

## Fonctionnement

1. Lancement du script : démarrage simultané de l'enregistrement audio (micro) et de l'écoute des clics souris/clavier.
2. À chaque clic souris : capture uniquement l'écran actif (celui où le clic a eu lieu, en cas de multi-écrans), horodatée.
3. Pendant ce temps, tu commentes tes actions à voix haute.
4. Appui sur **Échap** : arrêt de l'enregistrement.
5. Post-traitement automatique :
   - sauvegarde de l'audio brut (`narration.wav`)
   - transcription locale avec `faster-whisper` (`transcript.txt`)
   - association de chaque capture au segment de voix le plus proche dans le temps (`steps.json`)

## Résultat

Un dossier `capture_AAAAMMJJ_HHMMSS/` contenant :

| Fichier | Contenu |
|---|---|
| `step_001.png`, `step_002.png`, ... | Une capture par clic |
| `narration.wav` | Audio brut de la narration |
| `transcript.txt` | Transcription horodatée complète |
| `steps.json` | Chaque étape + timestamp + screenshot + texte dit au même moment |

## Étape suivante

Dans Claude Code, ouvrir le projet DictaDoc et lancer le skill :

```
/dictadoc capture_AAAAMMJJ_HHMMSS
```

Claude lit `steps.json`, `transcript.txt` et les captures, puis écrit `documentation.md` dans le dossier de capture. Sans argument, le dossier le plus récent est utilisé. Les données sensibles visibles sur les captures (comptes, mots de passe, etc.) sont signalées avant diffusion.

## Installation

Prérequis : **Python 3.12** (le projet n'utilise pas d'environnement virtuel).

> Python 3.15 n'est pas supporté : `faster-whisper` dépend de `tokenizers`, qui n'a pas encore de version précompilée pour cette version. Si plusieurs versions de Python sont installées, il faut cibler la 3.12 explicitement (`py -3.12`).

```bash
py -3.12 -m pip install -r requirements.txt
```

Au premier lancement, `faster-whisper` télécharge le modèle Whisper (`small`) : une connexion Internet est nécessaire une seule fois, ensuite tout fonctionne hors ligne.

## Utilisation

Double-cliquer sur **`lancer_capture.bat`** (équivalent de `py -3.12 capture_doc.py`).

- Fais tes actions normalement en expliquant à voix haute ce que tu fais.
- Appuie sur **Échap** pour arrêter l'enregistrement.
- La transcription démarre automatiquement (1-2 minutes selon la durée).

## Variante : capture avec une touche au choix

`lancer_capture_touche.bat` (ou `py -3.12 capture_doc_touche.py`) fonctionne comme `capture_doc.py`, mais la capture se déclenche en appuyant sur une **touche du clavier** au lieu du clic de souris.

- Au lancement, le programme demande d'appuyer sur la touche à utiliser (², F9, &...). **Échap** est refusée car réservée à l'arrêt.
- L'écran capturé est celui où se trouve le curseur au moment de l'appui.
- La touche choisie est « avalée » : elle n'écrit rien dans l'application active (elle est donc inutilisable pour taper pendant l'enregistrement).
- **Échap** arrête l'enregistrement, la suite (transcription, `steps.json`, `/dictadoc`) est identique.
- Version `.exe` portable : `DictaDoc_Capture_Touche.exe` (voir ci-dessous).

## Version .exe portable (sans Python)

Le dossier `exe/` contient des copies des scripts, empaquetées avec PyInstaller en **un seul fichier** chacune. Les fichiers à la racine ne sont pas concernés.

| Exécutable | Équivalent |
|---|---|
| `exe/dist/DictaDoc_Capture.exe` | `capture_doc.py` (capture au clic de souris) |
| `exe/dist/DictaDoc_Capture_Touche.exe` | `capture_doc_touche.py` (capture avec une touche au choix) |

**Utilisation :** copier le `.exe` (~130 Mo) dans n'importe quel dossier, puis double-cliquer dessus. Les dossiers `capture_*` sont créés **dans le dossier où se trouve le `.exe`**. Aucune installation n'est nécessaire.

- Le démarrage prend 20 à 30 secondes : le `.exe` se décompresse à chaque lancement. Attendre l'affichage de « Enregistrement démarré ».
- Le modèle Whisper n'est pas inclus : il est téléchargé au premier lancement sur chaque poste (Internet requis une fois, ensuite stocké dans le profil de l'utilisateur).
- **Poste sans Internet :** placer un dossier `modele_whisper` (cache du modèle `small`) à côté du `.exe` : il sera utilisé à la place du téléchargement.
- `DictaDoc_Capture.exe --check` vérifie que les composants (Whisper, audio, écrans) sont embarqués et affiche le dossier de sortie.
- Reconstruction : `exe/build_exe.bat` et `exe/build_exe_touche.bat` (Python 3.12 + `py -3.12 -m pip install pyinstaller`). À refaire si un script change : les copies dans `exe/` doivent alors être resynchronisées.
- Un antivirus peut signaler l'exécutable (écoute clavier + micro) : prévoir une exception si besoin.

## Dépannage

| Erreur | Cause / solution |
|---|---|
| `ModuleNotFoundError: No module named 'numpy'` | Le script tourne avec la mauvaise version de Python. Utiliser `lancer_capture.bat` ou `py -3.12`. |
| `ERROR: ... tokenizers` à l'installation | Installation tentée sous Python 3.15 : utiliser `py -3.12 -m pip install ...`. |
| Pas de `transcript.txt` après un plantage | L'audio et les captures sont conservés : la transcription peut être relancée sur le dossier. |

## À noter

- Tout tourne en local (pas d'API cloud pour la transcription) — adapté à un contexte sensible.
- En multi-écrans, seul l'écran où le clic a eu lieu est capturé (détection via `screeninfo`), pas les autres moniteurs.
- Modèle Whisper utilisé par défaut : `small` (modifiable via `WHISPER_MODEL_SIZE` dans le script — `base` = plus rapide, `medium` = plus précis mais plus lent).
