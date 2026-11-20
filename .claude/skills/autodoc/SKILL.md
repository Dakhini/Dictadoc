---
name: autodoc
description: Génère une documentation Markdown étape par étape à partir d'un dossier capture_AAAAMMJJ_HHMMSS produit par capture_doc.py (captures d'écran + steps.json + transcript.txt). À utiliser quand l'utilisateur demande de créer/rédiger la doc, la procédure ou le tutoriel à partir d'une capture, ou fournit un dossier capture_*.
---

# AutoDoc : génération de documentation à partir d'une capture

## Entrée

Un dossier `capture_AAAAMMJJ_HHMMSS/` (celui que l'utilisateur indique, sinon le plus récent à la racine du projet) contenant :

- `step_001.png`, `step_002.png`, ... : une capture d'écran par clic
- `steps.json` : chaque étape avec timestamp, screenshot et texte dit au même moment
- `transcript.txt` : transcription horodatée complète
- `narration.wav` : audio brut (ne pas l'ouvrir)

## Procédure

1. Lire `steps.json` et `transcript.txt`.
2. Ouvrir chaque capture avec Read, dans l'ordre, pour voir ce qui est réellement à l'écran (menus, boutons, champs, valeurs).
3. Pour chaque étape, croiser l'image avec la narration associée. Si les deux divergent, se fier à l'image pour les noms d'éléments de l'interface et à la narration pour l'intention.
4. Rédiger le document `.md` dans le dossier de capture (`documentation.md`), sauf indication contraire.

## Format de sortie

- Titre et courte introduction (objectif de la procédure), déduits de la narration.
- Prérequis éventuels, s'ils sont mentionnés.
- Étapes numérotées : une phrase d'action à l'impératif (« Cliquez sur **Paramètres** »), le nom exact des éléments d'interface en gras, puis la capture `![Étape N](step_00N.png)`.
- Les explications ou mises en garde dites à voix haute vont en remarque sous l'étape.
- Fusionner les clics qui forment une seule action logique (ex. ouvrir un menu puis choisir une option) ; ignorer les clics parasites sans effet visible.

## Règles

- Ne rien inventer : si un point n'est ni visible ni dit, le signaler dans une liste « À vérifier » en fin de document.
- Les transcriptions Whisper contiennent des erreurs (noms propres, termes techniques) : corriger d'après ce qui est affiché à l'écran.
- Contexte sensible : repérer les données personnelles ou secrets visibles sur les captures (mots de passe, noms, identifiants) et les signaler à l'utilisateur avant de finaliser.
- Rédiger en français, sauf demande contraire.
