# Leçons

Format : [date] | ce qui a mal tourné | règle pour l'éviter

- [2026-11-21] | Images et voix fabriquées par code jugées mauvaises | INTERDIT : dessiner des images ou créer des voix par code (PIL, moviepy pour générer des visuels, gTTS, pyttsx3). AUTORISÉ : appeler l'API Gemini (Nano Banana pour les images, modèle vidéo Gemini pour les clips avec dialogues français natifs) et assembler les clips avec ffmpeg
- [2026-11-21] | Veo 3.1 Fast/Lite demandés mais arrêtés dans l'API Gemini le 22/10/2026 | Vérifier modèles et prix dans la doc officielle avant tout code ; vidéo = gemini-omni-1.2-flash
- [2026-11-21] | « Partie N » incrusté au début de la vidéo et sous-titres affichés sur tout le plan : refusés | Pas de titre au début (il va dans la description/miniature TikTok) ; sous-titres par groupes de 2-3 mots calés sur la voix (transcrire.py) ; carte « Abonne-toi » APRÈS le dernier plan
- [2026-11-21] | Clip reçu en GIF (sans son) | Toujours demander le MP4 depuis Flow
- [2026-11-22] | Partie 1 trop lente (pauses, une seule réplique par plan) | Style maison : 2 répliques enchaînées par plan, « dialogue starts immediately », coupe des silences au montage
- [2026-11-22] | Ton jugé trop sage | Style maison : langage de jeunes (wesh, frérot, daron…), gros mots légers, gags débiles, jeu exagéré et gestes amples (« exaggerated over-the-top cartoon acting ») — sans insulte visant un groupe
- [2026-11-22] | Parties de 58-59 s : non rémunérables (TikTok paie au-delà d'1 min) | Viser 65-75 s : 9-10 plans par partie ; le montage avertit sous 61 s (options --fin, --sans-coupe)
- [2026-11-27] | Passage à Grok Imagine (clips de 6 s, basse résolution, 1 image) | Répliques ≤ ~12 mots par clip, 10 clips par partie, image C = les 4 persos pour les plans à deux ; mise à l'échelle lanczos au montage
- [2026-11-27] | Grok : rendu bizarre avec trop d'actions (clés + pointer la porte + mains sur la tête) | Avec Grok : caméra fixe, UNE action simple par personnage, « no morphing », prompt court
- [2026-11-27] | Trop de gros mots répétés (wallah, sa mère, putain dans chaque plan) | 1 gros mot / expression forte tous les 2-3 plans max, et varier : c'est chaud, t'abuses, j'hallucine, grave, ça me saoule, la honte, c'est mort, laisse tomber, t'es sérieux…
- [2026-11-27] | Clips qui finissent par une « pose de fin » (tête baissée, figés) : effet sketch, pas série | Prompt : « conversation still going on, no ending pose, ends mid-action » + montage : sortie 0,25 s après le dernier mot ; cadrage en pied, persos grands ; pas de personnage à genoux avec Grok
- [2026-11-27] | Trop d'excitation partout = histoire moins claire | Doser : l'émotion juste au bon plan (calme et tendre pour un pardon, explosif pour une révélation, drôle pour un gag) ; gros mots seulement aux moments de tension ; enchaîner les clips avec la dernière image du précédent
- [2026-11-27] | Enchaînements pas naturels | ENCHAÎNE quand les mêmes persos continuent la conversation (départ = dernière image du clip précédent) ; COUPE seulement pour un nouveau perso, un moment important ou un changement de scène
- [2026-11-27] | Image C (4 persos côte à côte, très large) → Grok rapetisse les personnages | Toujours une image de référence VERTICALE 9:16 avec seulement les 2 persos du plan (A, B, D, E, F…)
- [2026-11-28] | Grok invente des répliques en plus et surjoue sur un plan de tension | Ajouter « Only this line of dialogue, no other words » ; plan final calme et dramatique ; le dernier plan garde sa fin (réaction) au montage
