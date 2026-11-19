# Fabrique de vidéos fruits

Génère des vidéos TikTok verticales (1080x1920, 24 i/s) entièrement par code :
personnages fruits dessinés et animés (pycairo), voix françaises (edge-tts),
musique et bruitages synthétisés (numpy), montage avec ffmpeg.

```bash
pip install pycairo edge-tts numpy
python3 build.py stories/banane.py      # toutes les parties
python3 build.py stories/banane.py 2    # seulement la partie 2
```

Les vidéos sortent dans `../videos/`.

- `engine.py` : personnages, décors, effets, textes
- `build.py` : voix, timing, musique, rendu et assemblage
- `stories/*.py` : une histoire = 4 parties, chaque partie = liste de plans
