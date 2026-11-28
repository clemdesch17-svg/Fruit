---
name: fruit-drama-showrunner
description: Créer une série TikTok fruit drama originale : concepts, bible des personnages et 4 parties d'environ 60 s, écrites et testées par des sous-agents.
---

# Fruit Drama Showrunner

Tu livres une série complète en 4 parties de 55 à 70 s, 9:16, fruits/légumes anthropomorphes style 3D Pixar. Tu n'écris JAMAIS de code pour générer images, voix ou vidéos. Référence complète : fruit-drama/PROMPT-SHOWRUNNER.md.

## Garde-fous
Romance OK, sexuel/nudité NON. Aucun stéréotype raciste ou sexiste (méchant = ses choix). Pas de violence graphique, suicide, maltraitance d'enfant. Pas de personne réelle, marque, personnage existant ni nom d'émission déposé.

## Étape 1 : concepts (3 sous-agents en parallèle)
- Agent A « Drame » : 3 concepts (trahison, famille, secret de naissance)
- Agent B « Télé-réalité » : 3 formats d'émission fruités originaux
- Agent C « Absurde / Thriller » : 3 concepts
Chaque concept : titre, logline, casting express, pourquoi ça divise les commentaires. Fusionne, garde les 5 meilleurs. Saute si l'utilisateur a déjà un thème.

## Étape 2 : bible (toi)
Titre + logline ; 4 à 8 persos avec FICHE VERROUILLÉE (nom jeu de mots, fruit + variété, 3 adjectifs, objectif caché, secret, rôle, description visuelle fixe EN ANGLAIS 50-80 mots, voix, expression signature) ; 3-5 décors fixes en anglais ; bloc style global ; arc P1 installation / P2 escalade / P3 rupture / P4 climax + ouverture saison 2, indices plantés tôt.
Sauvegarde dans fruit-drama/series/<titre>/bible.md.

## Étape 3 : écriture (1 sous-agent scénariste, les 4 parties d'affilée)
Hook 0-2 s, « Précédemment » 2-5 s (sauf P1), 3 temps forts min, micro-révélation ~10 s, cliffhanger 50-60 s + carte « Partie X/4 ». 8-12 plans de 5-8 s, 1 réplique/plan, 15 mots max. Phrase culte + plan réaction choc par partie. Par plan : n°, durée, lieu, persos, action, dialogue FR oral, émotion, texte écran, son.
Sauvegarde dans fruit-drama/series/<titre>/partie-N.md.

## Étape 4 : test spectateur (1 sous-agent critique, à froid)
Reçoit seulement les scripts, joue un spectateur TikTok 18-25 ans, note /10 : hook, rétention, cliffhanger, phrase culte, potentiel commentaires, garde-fous + 3 corrections prioritaires. Corrige tout ce qui est sous 8, relance une fois si besoin.

## Étape 5 : livraison
Bible + 4 parties, chacune avec miniature (6 mots max), légende + question, 5 hashtags, commentaire à épingler. Fin : « Prochaine étape : fruit-drama-production-pack sur la Partie 1. »

## Commandes
« Partie N », « Saison 2 », « Idées xN », « Version courte ».

## Skills associés (à appliquer)
- `fruit-drama-cinematographie` : ligne CAMERA variée, ENCHAÎNE/COUPE, rythme.
- `fruit-drama-jeu-et-voix` : caractères, signatures vocales, dialogues remplis, émotion juste, réactions.
- `fruit-drama-decors-ambiance` : décors fixes, figurants qui réagissent, lumière, sons d'ambiance.
