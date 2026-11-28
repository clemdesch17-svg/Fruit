---
name: fruit-drama-production-pack
description: Transformer un script de fruit drama en prompts prêts à coller : images (Nano Banana/Midjourney), vidéo (Veo 3/Kling), voix (ElevenLabs) et plan de montage CapCut.
---

# Fruit Drama Production Pack

Entrée : bible + script d'une partie (fruit-drama/series/<titre>/). Sortie : tous les prompts techniques. INTERDIT : dessiner des images ou créer des voix par code (PIL, moviepy pour générer des visuels, gTTS, pyttsx3). AUTORISÉ : l'API Gemini via fruit-drama/pipeline/ (Nano Banana 2.1 + Gemini Omni Flash — Veo 3.1 est arrêté dans l'API Gemini) et l'assemblage ffmpeg.

## Règle d'or
ENCHAÎNE / COUPE : mêmes personnages qui continuent la même conversation → le clip suivant part de la dernière image du précédent (continuité, pas de pose de fin). Nouveau personnage, moment important ou changement de scène → COUPE : nouvelle image de référence et nouveau cadrage.
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
Ajoute aussi le bloc ```yaml « # fruitpipe:partie » lu par le pipeline (format : fruit-drama/pipeline/README.md), et le bloc « # fruitpipe:bible » dans bible.md s'il manque. Ensuite : `python3 fruitpipe.py estimer <titre> N`.

## « Plan N refait »
Réécrit seulement ce plan : action simplifiée, cadrage plus serré, une émotion, caméra plus lente. 2 variantes.

## Skills associés (à appliquer)
- `fruit-drama-cinematographie` : ligne CAMERA variée, ENCHAÎNE/COUPE, rythme.
- `fruit-drama-jeu-et-voix` : caractères, signatures vocales, dialogues remplis, émotion juste, réactions.
- `fruit-drama-decors-ambiance` : décors fixes, figurants qui réagissent, lumière, sons d'ambiance.
