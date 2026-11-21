# Leçons

Format : [date] | ce qui a mal tourné | règle pour l'éviter

- [2026-11-19] | Le lien TikTok (vm.tiktok.com) n'a rien renvoyé à part la page vide « TikTok - Make Your Day » | Demander la légende, une capture d'écran ou une description du TikTok plutôt que de compter sur le lien
- [2026-11-19] | edge-tts échouait (certificat) derrière le proxy | Forcer certifi.where() vers /root/.ccr/ca-bundle.crt avant d'importer edge_tts
- [2026-11-19] | Couleurs hex à 8 caractères (#RRGGBBAA) rendues opaques → gros disque orange | hexc() doit lire le canal alpha ; vérifier chaque rendu sur une planche d'images avant de livrer
- [2026-11-19] | Sous-titres posés sur les visages | Garder les visages au-dessus de y≈1450 et les sous-titres à y≈1490–1650
- [2026-11-19] | Vidéos en dessin animé fait par code refusées : l'utilisateur veut le style hyper-réaliste « fruits IA » (ex. compte @rudyfruityia) avec de vraies voix | Ne pas livrer de rendu fait main pour ce projet ; passer par un générateur vidéo IA (Veo/Kling) + voix pro (ElevenLabs), et valider le style sur 1 plan test avant de tout produire
- [2026-11-21] | Images/voix/vidéos générées par code (dessin cairo, TTS, SDXL local) jugées mauvaises | Ne JAMAIS générer de média par code : livrer scénarios + prompts pour Veo 3/Kling/Nano Banana/ElevenLabs/CapCut (voir fruit-drama/)
