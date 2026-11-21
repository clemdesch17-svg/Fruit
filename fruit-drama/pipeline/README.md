# Pipeline Fruit Drama (API Gemini)

Génère les fiches personnages, les keyframes et les clips vidéo avec l'API Gemini,
puis assemble la partie avec ffmpeg. **Aucune image ni voix n'est fabriquée par code** :
tout le visuel et toutes les voix viennent des modèles Gemini.

## Modèles et prix (doc officielle, relevés le 21/11/2026)
| Usage | Modèle | Prix |
|---|---|---|
| Fiches + keyframes | `gemini-nano-banana-2.1` (Nano Banana 2.1), 2K | 0,0504 $ / image |
| Clips (défaut) | `gemini-omni-1.2-flash`, 720p | ~0,07 $ / s → 0,56 $ le plan de 8 s |
| Clips `--lite` (brouillon) | `gemini-omni-1.2-flash`, 360p | ~0,023 $ / s → 0,18 $ le plan de 8 s |
| Clips `--hd` | `gemini-omni-1.2-flash`, 1080p | ~0,104 $ / s |

⚠️ **Veo 3.1 (Fast et Lite compris) a été arrêté dans l'API Gemini le 22/10/2026.**
Google indique de migrer vers Gemini Omni Flash : image-vers-vidéo, 9:16, 3 à 15 s,
audio natif avec dialogues. La doc précise que seul l'anglais est « entièrement
supporté » : le français marche, mais la qualité peut varier.
Une partie complète (10 plans × 6-8 s) coûte environ 5 $ en 720p ou 2 $ en `--lite`.

## Installation
```bash
cd fruit-drama/pipeline
pip install pyyaml            # ffmpeg doit être installé
cp .env.example .env          # puis colle ta clé : GEMINI_API_KEY=...
```
La clé se crée sur aistudio.google.com → Get API key. La génération vidéo demande
un compte avec **facturation activée** (pas de niveau gratuit pour Omni).

## Utilisation
```bash
python3 fruitpipe.py estimer demo-test 1          # coût, sans rien dépenser
python3 fruitpipe.py fiches  demo-test            # 1. fiches persos → à regarder
python3 fruitpipe.py valider demo-test            # 2. tu valides les fiches
python3 fruitpipe.py partie  demo-test 1          # 3. MODE TEST : plan 1 seulement
python3 fruitpipe.py partie  demo-test 1 --tout   # 4. toute la partie
python3 fruitpipe.py refaire demo-test 1 3        # refaire le clip du plan 3
python3 fruitpipe.py refaire demo-test 1 3 --image  # …et son keyframe
python3 fruitpipe.py montage demo-test 1          # 5. vidéo finale 1080x1920
```
- Chaque commande payante affiche le **coût estimé** et attend `o` (ou `--oui`).
- `--lite` = brouillon 360p bon marché, `--hd` = 1080p.
- Ce qui existe déjà n'est jamais regénéré (sauf `refaire`).
- Les dépenses réelles sont notées dans `series/<titre>/rendus/couts.jsonl`.
- Musique : dépose `series/<titre>/musique.mp3`, elle est mixée sous les voix.

## Fichiers d'entrée
`series/<titre>/bible.md` et `prod-partie-N.md` contiennent un bloc ```yaml
(texte libre autour autorisé). Voir `series/demo-test/` comme modèle.

**bible.md** — `# fruitpipe:bible` : `style`, `personnages.<id>` (`nom`, `couleur`
hex des sous-titres, `visuel` en anglais copié dans chaque prompt, `voix`),
`decors.<id>` (description en anglais).

**prod-partie-N.md** — `# fruitpipe:partie` : `partie`, `total`, `plans[]` avec
`n`, `duree` (3-8 s), `decor`, `persos`, `image` (pose/cadrage du keyframe),
`video` (caméra + action), `replique` (`perso`, `texte` en français, optionnel),
`texte_ecran` et `ambiance` (optionnels).

## Sorties
`series/<titre>/rendus/` : `fiches/`, `partie-N/planXX_keyframe.png`,
`partie-N/planXX.mp4`, `<titre>_partieN.mp4`, `couts.jsonl`.
