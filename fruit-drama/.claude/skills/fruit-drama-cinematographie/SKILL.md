---
name: fruit-drama-cinematographie
description: Mise en scène caméra pour les clips fruit drama (Grok, Flow, Veo) — cadrages, mouvements, zooms, inserts, enchaînements et rythme de montage, pour que chaque partie se regarde comme une vraie mini-série.
---

# Cinématographie fruit drama

But : que le spectateur ait l'impression de regarder une série, pas une suite de sketchs. Chaque prompt vidéo contient une ligne `CAMERA:` précise.

## Règles d'or
1. **Les personnages sont grands au début du plan** (plan en pied ou mi-corps, centrés) pour que le générateur garde leur apparence ; ensuite seulement la caméra bouge.
2. **Jamais deux plans de suite avec le même cadrage ni le même mouvement.**
3. **Un mouvement de caméra par plan**, au service de l'émotion du moment.
4. **ENCHAÎNE / COUPE** : mêmes personnages qui continuent la conversation → le plan part de la dernière image du précédent (`CAMERA: continues smoothly from the last frame, …`). Nouveau personnage, moment fort ou changement de scène → COUPE avec un nouveau cadrage.
5. **Pas de pose de fin** : le plan se termine en pleine action ou sur une réaction.

## Boîte à outils (formules à coller)
| Moment | Formule CAMERA |
|---|---|
| Début de scène | `starts on a wide establishing shot of <décor> with <persos> large in the foreground, then a slow push-in` |
| Réplique forte / aveu | `slow push-in to a close-up of <perso>'s face as she says the last line` |
| Réaction choc | `quick dramatic zoom onto <perso>'s shocked face` (« dun dun dunnn » au montage) |
| Indice / objet clé | `quick push-in to an insert close-up of <objet : pendentif qui brille, tache brune, écran de téléphone, photo>` |
| Dialogue à deux | `over-the-shoulder shot from behind <perso A>, focus on <perso B>` puis plan inverse au plan suivant |
| Méchant / menace | `low-angle shot looking up at <méchant>, slow push-in, cold light` |
| Personnage vulnérable | `high-angle shot looking down at <perso>, slow pull-back` |
| Poursuite / panique | `handheld shaky camera following <perso> running` |
| Gag | `static wide shot` puis `quick snap zoom on the funny reaction` |
| Romance | `slow circular tracking shot around the two characters, warm light` |
| Cliffhanger | `slow push-in on <perso>'s face, freeze on the reaction` (le montage garde la fin du dernier plan) |

## Rythme d'une partie (10 clips ≈ 1:01)
- Plan 1 : hook visuel en 0-2 s (insert ou zoom choc).
- Alterner : large → serré → insert → épaule → large…
- Plans 8-10 : resserrer de plus en plus vers le cliffhanger.

## Montage (pipeline `fruitpipe.py montage`)
- Coupe juste avant la première parole et 0,25 s après la dernière (ça enchaîne).
- Le dernier plan garde sa fin (réaction), puis carte « Abonne-toi et like pour la Partie N+1 ».
- Sous-titres 2-3 mots synchronisés, couleur par personnage.
