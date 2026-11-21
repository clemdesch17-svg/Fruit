---
name: fruit-drama-production-pack
description: Transformer un script de fruit drama en prompts prêts à coller : images (Nano Banana/Midjourney), vidéo (Veo 3/Kling), voix (ElevenLabs) et plan de montage CapCut.
---

# Fruit Drama Production Pack

Entrée : bible + script d'une partie (fruit-drama/series/<titre>/). Sortie : tous les prompts techniques. INTERDIT : générer images/voix/vidéos par code (Python, PIL, TTS, moviepy, ffmpeg).

## Règle d'or
Descriptions visuelles des persos et décors copiées MOT POUR MOT dans chaque prompt. Une action principale par plan.

## Étape 0 : fiches de référence
Si pas encore faites : un prompt « character sheet » par perso (face, fond neutre, éclairage studio, pose neutre + trois-quarts). Rappeler de les générer en premier : toutes les scènes partent d'elles.

## Étape 1 : 4 sous-agents en parallèle (chacun reçoit bible + script)
- IMAGE : 1 keyframe/plan en anglais = [style global] + [fiche copiée] + [décor] + [pose] + [expression] + [cadrage] + [éclairage] + "vertical 9:16 composition, no text, no watermark". Variante Midjourney (--ar 9:16 --style raw --v 7 + référence perso). Note Nano Banana (upload référence, « keep the exact same character design »). Jamais 2 cadrages identiques de suite.
- VIDÉO : Veo 3 (≤ 8 s) = caméra + mouvement + The character says in French: "<réplique>" + voix + ambiance + "no subtitles, no music". Kling/Vidu (5 ou 10 s) sans dialogue + note lip-sync. Décrire l'état final. Négatif : "no deformed hands, no extra limbs, no morphing, no text, consistent character design".
- VOIX : par réplique → perso, voix ElevenLabs fixe, texte annoté (… / MAJUSCULES), émotion, stabilité 30-40 % émotion / 60-70 % narration. Voix off narrateur si besoin.
- MONTAGE : plan CapCut seconde par seconde (transitions, ralentis, zooms, sous-titres colorés par perso, musique + silences avant révélations, SFX, carte « Partie X/4 »), total 55-70 s.

## Étape 2 : contrôle de cohérence (1 sous-agent à froid)
Reçoit bible + sorties. Vérifie : fiches identiques partout, répliques identiques script/vidéo/voix, durées (Veo ≤ 8 s, Kling ≤ 10 s), cadrages non répétés, total 55-70 s, aucun texte/logo/marque dans l'image, garde-fous. Liste les écarts → corrige tout.

## Étape 3 : livraison
Fichier fruit-drama/series/<titre>/prod-partie-N.md, un bloc par plan :
PLAN N (durée) — Image / Vidéo Veo 3 / Vidéo Kling / Voix
Puis plan de montage + checklist : fiches → keyframes → vidéos → voix → montage → étiquette « contenu IA ».

## « Plan N refait »
Réécrit seulement ce plan : action simplifiée, cadrage plus serré, une émotion, caméra plus lente. 2 variantes.
