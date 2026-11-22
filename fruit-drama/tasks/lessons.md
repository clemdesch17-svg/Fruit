# Leçons

Format : [date] | ce qui a mal tourné | règle pour l'éviter

- [2026-11-21] | Images et voix fabriquées par code jugées mauvaises | INTERDIT : dessiner des images ou créer des voix par code (PIL, moviepy pour générer des visuels, gTTS, pyttsx3). AUTORISÉ : appeler l'API Gemini (Nano Banana pour les images, modèle vidéo Gemini pour les clips avec dialogues français natifs) et assembler les clips avec ffmpeg
- [2026-11-21] | Veo 3.1 Fast/Lite demandés mais arrêtés dans l'API Gemini le 22/10/2026 | Vérifier modèles et prix dans la doc officielle avant tout code ; vidéo = gemini-omni-1.2-flash
- [2026-11-21] | « Partie N » incrusté au début de la vidéo et sous-titres affichés sur tout le plan : refusés | Pas de titre au début (il va dans la description/miniature TikTok) ; sous-titres par groupes de 2-3 mots calés sur la voix (transcrire.py) ; carte « Abonne-toi » APRÈS le dernier plan
- [2026-11-21] | Clip reçu en GIF (sans son) | Toujours demander le MP4 depuis Flow
- [2026-11-22] | Partie 1 trop lente (pauses, une seule réplique par plan) | Style maison : 2 répliques enchaînées par plan, « dialogue starts immediately », coupe des silences au montage
- [2026-11-22] | Ton jugé trop sage | Style maison : langage de jeunes (wesh, frérot, daron…), gros mots légers, gags débiles, jeu exagéré et gestes amples (« exaggerated over-the-top cartoon acting ») — sans insulte visant un groupe
