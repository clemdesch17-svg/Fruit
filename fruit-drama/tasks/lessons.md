# Leçons

Format : [date] | ce qui a mal tourné | règle pour l'éviter

- [2026-11-21] | Images et voix fabriquées par code jugées mauvaises | INTERDIT : dessiner des images ou créer des voix par code (PIL, moviepy pour générer des visuels, gTTS, pyttsx3). AUTORISÉ : appeler l'API Gemini (Nano Banana pour les images, modèle vidéo Gemini pour les clips avec dialogues français natifs) et assembler les clips avec ffmpeg
- [2026-11-21] | Veo 3.1 Fast/Lite demandés mais arrêtés dans l'API Gemini le 22/10/2026 | Vérifier modèles et prix dans la doc officielle avant tout code ; vidéo = gemini-omni-1.2-flash
- [2026-11-21] | « Partie N » incrusté au début de la vidéo et sous-titres affichés sur tout le plan : refusés | Pas de titre au début (il va dans la description/miniature TikTok) ; sous-titres par groupes de 2-3 mots calés sur la voix (transcrire.py) ; carte « Abonne-toi » APRÈS le dernier plan
- [2026-11-21] | Clip reçu en GIF (sans son) | Toujours demander le MP4 depuis Flow
