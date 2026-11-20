# Prompt à coller dans n'importe quelle IA

Ce prompt permet de générer la documentation à partir d'un dossier de capture DictaDoc avec **n'importe quelle IA** capable de lire des images (Claude, ChatGPT, Gemini, Mistral Le Chat, Copilot...).

## Comment l'utiliser

1. Ouvrez une nouvelle conversation avec une IA qui accepte les **images**.
2. Collez le prompt ci-dessous.
3. Joignez les fichiers du dossier `capture_AAAAMMJJ_HHMMSS` :
   - toutes les captures `step_001.png`, `step_002.png`... **dans l'ordre** (la plupart des IA acceptent 10 à 20 images par message ; au-delà, envoyez-les en plusieurs fois) ;
   - le contenu de `steps.json` et de `transcript.txt` (joints en fichiers, ou collés à la place des zones `[...]`).
   N'envoyez pas `narration.wav`.
4. Récupérez le Markdown généré et enregistrez-le sous `documentation.md` **dans le dossier de capture** : les images s'afficheront alors, car elles sont référencées par leur nom (`step_001.png`...).

> **Confidentialité.** Les captures montrent tout votre écran : comptes, adresses, noms de serveurs, mots de passe éventuels. Les envoyer à une IA en ligne les transmet à ce service. Floutez ou supprimez les zones sensibles avant l'envoi, et utilisez uniquement une IA autorisée par votre organisation. Le prompt demande à l'IA de signaler ces données, mais cela ne remplace pas votre relecture.

## Le prompt

````text
Tu es rédacteur technique. Je te fournis l'enregistrement d'une procédure réalisée à l'écran :
- des captures d'écran numérotées (step_001.png, step_002.png, ...), prises dans l'ordre, une par action ;
- steps.json : pour chaque capture, son numéro, son horodatage et le texte dit à voix haute à ce moment-là ;
- transcript.txt : la transcription complète et horodatée de la narration.

Ta mission : rédiger la documentation pas à pas de cette procédure, en Markdown, en français.

PROCÉDURE
1. Lis steps.json et transcript.txt pour comprendre l'objectif et le déroulé.
2. Regarde chaque capture, dans l'ordre, pour voir ce qui est réellement à l'écran (menus, boutons, champs, valeurs).
3. Pour chaque étape, croise l'image avec la narration. Si les deux divergent, fie-toi à l'image pour les noms des éléments de l'interface et à la narration pour l'intention.

FORMAT DE SORTIE
- Un titre et une courte introduction (objectif de la procédure), déduits de la narration.
- Une section « Prérequis » uniquement si des prérequis sont mentionnés.
- Des étapes numérotées. Chaque étape : une phrase d'action à l'impératif (« Cliquez sur **Paramètres** »), le nom exact des éléments d'interface en gras, puis l'image au format ![Étape N](step_00N.png).
- Les explications ou mises en garde dites à voix haute vont dans une remarque sous l'étape (ligne commençant par « > Remarque : »).
- Fusionne les clics qui forment une seule action logique (ex. ouvrir un menu puis choisir une option). Ignore les clics parasites sans effet visible.
- Si plusieurs captures sont fusionnées dans une étape, intègre chacune d'elles.
- Termine par une section « À vérifier ».

RÈGLES
- Ne rien inventer. Si un point n'est ni visible à l'écran ni dit à voix haute, ne le déduis pas : note-le dans « À vérifier ».
- La transcription automatique contient des erreurs (noms propres, termes techniques, mots mal compris) : corrige-les d'après ce qui est affiché à l'écran.
- Données sensibles : repère les données personnelles ou secrets visibles sur les captures (mots de passe, noms, adresses e-mail, identifiants, noms de serveurs ou d'URL internes, jetons). AVANT le document, donne-moi une liste « Données sensibles détectées » indiquant, pour chacune, la capture concernée et ce qui est visible. Ne recopie jamais un mot de passe ou un secret dans le document.
- Si une capture est illisible ou manquante, dis-le au lieu de supposer son contenu.

````