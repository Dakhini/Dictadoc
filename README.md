# DictaDoc

Documentez une procédure en la faisant : DictaDoc enregistre vos actions (une capture d'écran à chaque déclenchement) et votre voix en parallèle, puis transcrit l'audio **en local** avec Whisper (aucun service en ligne). Le dossier obtenu sert ensuite à générer une documentation pas à pas, avec Claude ou n'importe quelle autre IA.

## Démarrage rapide : version portable (.exe)

Aucune installation : ni Python, ni bibliothèques.

1. Téléchargez un `.exe` depuis la page [**Releases**](https://github.com/Dakhini/Dictadoc/releases/latest).
2. Copiez-le dans le dossier de votre choix, puis double-cliquez dessus.
3. Attendez l'affichage de « Enregistrement démarré » (20 à 30 secondes).
4. Faites vos actions en les commentant à voix haute.
5. Appuyez sur **Échap** pour arrêter : la transcription démarre automatiquement.

Un dossier `capture_AAAAMMJJ_HHMMSS` est créé **à côté du `.exe`**.

| Exécutable | La capture se déclenche... |
|---|---|
| `DictaDoc_Capture.exe` | à chaque **clic de souris** |
| `DictaDoc_Capture_Touche.exe` | en appuyant sur une **touche au choix** (², F9...), demandée au lancement |

À savoir :
- **Premier lancement :** le modèle Whisper (`small`, environ 500 Mo) est téléchargé une fois sur chaque poste (Internet requis). Les messages `HF_TOKEN` et `hf_xet` affichés à ce moment sont normaux.
- **Démarrage lent :** le `.exe` se décompresse à chaque lancement.
- **Poste sans Internet :** placez un dossier `modele_whisper` (cache du modèle `small`) à côté du `.exe` : il sera utilisé à la place du téléchargement.
- **Antivirus / SmartScreen :** le programme écoute le clavier et le micro, ce qui peut déclencher une alerte. Cliquez sur « Informations complémentaires » puis « Exécuter quand même », ou demandez une exception.
- **Touche de capture :** la touche choisie n'écrit rien dans l'application active pendant l'enregistrement. **Échap** est réservée à l'arrêt.

## Générer la documentation

Le `.exe` produit les captures et la transcription ; le document Markdown est rédigé ensuite par une IA, à partir du dossier `capture_*`.

### Option 1 : n'importe quelle IA (prompt à coller)

Utilisez le prompt de [**PROMPT_IA.md**](PROMPT_IA.md) avec une IA qui lit les images (Claude, ChatGPT, Gemini, Mistral, Copilot...) : collez-le, joignez les captures dans l'ordre ainsi que `steps.json` et `transcript.txt`, puis enregistrez le résultat sous `documentation.md` dans le dossier de capture.

> **Confidentialité :** les captures montrent tout votre écran. Floutez les zones sensibles avant de les envoyer à une IA en ligne, et utilisez uniquement un service autorisé par votre organisation.

### Option 2 : Claude Code (skill `/dictadoc`)

Dans Claude Code, ouvrez le projet DictaDoc et lancez :

```
/dictadoc capture_AAAAMMJJ_HHMMSS
```

Claude lit `steps.json`, `transcript.txt` et les captures, puis écrit `documentation.md` dans le dossier de capture. Sans argument, le dossier le plus récent est utilisé. Les données sensibles visibles sur les captures (comptes, mots de passe, etc.) sont signalées avant diffusion.

## Contenu d'un dossier de capture

| Fichier | Contenu |
|---|---|
| `step_001.png`, `step_002.png`, ... | Une capture par déclenchement |
| `narration.wav` | Audio brut de la narration |
| `transcript.txt` | Transcription horodatée complète |
| `steps.json` | Chaque étape + timestamp + screenshot + texte dit au même moment |

## Fonctionnement

1. Démarrage simultané de l'enregistrement audio (micro) et de l'écoute des clics (ou de la touche choisie).
2. À chaque déclenchement : capture de l'écran actif uniquement (celui où se trouve le clic ou le curseur, en multi-écrans), horodatée.
3. Pendant ce temps, vous commentez vos actions à voix haute.
4. **Échap** arrête l'enregistrement.
5. Post-traitement automatique :
   - sauvegarde de l'audio brut (`narration.wav`) ;
   - transcription locale avec `faster-whisper` (`transcript.txt`) ;
   - association de chaque capture au segment de voix le plus proche dans le temps (`steps.json`).

## Depuis les sources (avec Python)

Prérequis : **Python 3.12** (pas d'environnement virtuel).

> Python 3.15 n'est pas supporté : `faster-whisper` dépend de `tokenizers`, qui n'a pas encore de version précompilée pour cette version. Si plusieurs versions de Python sont installées, ciblez la 3.12 explicitement (`py -3.12`).

```bash
py -3.12 -m pip install -r requirements.txt
```

| Lanceur | Script | Déclencheur |
|---|---|---|
| `lancer_capture.bat` | `capture_doc.py` | clic de souris |
| `lancer_capture_touche.bat` | `capture_doc_touche.py` | touche au choix |

Double-cliquez sur le `.bat`, ou lancez `py -3.12 capture_doc.py`. Dans ce mode, les dossiers `capture_*` sont créés dans le dossier courant.

## Reconstruire les .exe

Les copies des scripts empaquetées avec PyInstaller (en un seul fichier) sont dans `exe/`. Elles se reconstruisent avec `exe/build_exe.bat` et `exe/build_exe_touche.bat` (Python 3.12 + `py -3.12 -m pip install pyinstaller`). Résultat dans `exe/dist/`.

À refaire si un script change : les copies dans `exe/` doivent alors être resynchronisées avec celles de la racine. `DictaDoc_Capture.exe --check` vérifie que les composants (Whisper, audio, écrans) sont embarqués et affiche le dossier de sortie.

## Dépannage

| Erreur | Cause / solution |
|---|---|
| Écran noir au lancement du `.exe` | Normal : le fichier se décompresse, patientez 20 à 30 secondes. |
| `ModuleNotFoundError: No module named 'numpy'` | Le script tourne avec la mauvaise version de Python. Utiliser `lancer_capture.bat` ou `py -3.12`. |
| `ERROR: ... tokenizers` à l'installation | Installation tentée sous Python 3.15 : utiliser `py -3.12 -m pip install ...`. |
| Pas de `transcript.txt` après un plantage | L'audio et les captures sont conservés : la transcription peut être relancée sur le dossier. |

## À noter

- Tout tourne en local (pas d'API cloud pour la transcription) : adapté à un contexte sensible. L'étape de rédaction par une IA, elle, envoie les captures au service choisi.
- Modèle Whisper utilisé par défaut : `small` (modifiable via `WHISPER_MODEL_SIZE` dans le script ; `base` = plus rapide, `medium` = plus précis mais plus lent).
