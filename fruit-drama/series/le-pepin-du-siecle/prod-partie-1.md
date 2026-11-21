# Le Pépin du Siècle — Production Partie 1/4 « L'échographie »

**Outil :** vidIQ (connecteur) · images = générateur vidIQ avec les fiches en référence · vidéos = **Veo 3.1 Lite, 720p, 9:16**, image-vers-vidéo, voix française native.
**Durée :** 56 s · **Coût en crédits vidIQ :** 8 images × 22 = 176 + vidéo 56 s × 10 = 560 → **736 crédits**.
**Fiches de référence** (`rendus/fiches/`) : `fraisine_mangeo.jpg`, `raisino_citronella.jpg` (URLs dans `rendus/fiches/urls.md`).

Style global (dans chaque prompt image) : *Pixar-style 3D animation, ultra detailed, cinematic lighting, shallow depth of field, soft volumetric light, rich saturated colors, glossy realistic fruit skin with tiny water droplets, expressive big eyes, vertical 9:16, 4K.*

---

### PLAN 1 (6 s) — Hook
- **Image :** [style] + Fraisine (fiche) lying on the white examination bed, hand on her small pregnant belly, staring wide-eyed at the glowing ultrasound monitor in the foreground which shows a grainy blue scan with about ten small shiny violet seeds clustered like a grape bunch (no baby silhouette). Setting: ultrasound room (bible). Over-the-shoulder shot from behind the monitor.
- **Vidéo Veo :** Fast pan from the glowing monitor with violet seeds to Fraisine's face, ending on a close-up, her eyes wide in panic. Fraisine says in French, shocked and panicked: « Pourquoi mon bébé a des pépins… violets ?! » The monitor beep stops abruptly.
- **Texte écran :** DES PÉPINS… VIOLETS ?!

### PLAN 2 (8 s)
- **Image :** Medium two-shot: Mangeo standing beside the bed holding Fraisine's hand, forced big smile; Fraisine lying down, staring at him silently. Ultrasound room.
- **Vidéo Veo :** Slow dolly in. Mangeo laughs too loudly, lets go of her hand and scratches his stem nervously. Mangeo says in French with a deep warm voice, uneasy: « C'est sûrement un bug de la machine, mon cœur. » Ends on his tense smile, Fraisine staring.

### PLAN 3 (8 s)
- **Image :** Wide shot from the back of the room: the door opens, Raisino enters holding a big bunch of pink and mint balloons, huge smile, an old yellowed photo corner sticking out of his mustard hoodie pocket; Mangeo in the foreground, back to camera, turning. Ultrasound room.
- **Vidéo Veo :** Raisino walks in cheerfully and says in French, joyful and fast: « Frérot, j'ai les ballons ! Alors, fille ou garçon ? » Mangeo turns slowly to face him; Raisino freezes, the balloons slip from his hand and float to the ceiling. Squeaky balloons, then sudden silence.

### PLAN 4 (6 s) — Indice, plan muet
- **Image :** Extreme close-up of Mangeo's and Raisino's heads side by side in profile, both raising a hand to scratch their stems at the same time, mirrored. Ultrasound room, shallow depth of field.
- **Vidéo Veo :** Slight slow motion. Mangeo and Raisino scratch their stems at exactly the same moment, in perfect mirror, then freeze. No dialogue. Sound: a single heartbeat.
- **Texte écran :** Vous avez vu ?

### PLAN 5 (8 s) — Indice médaillon
- **Image :** Medium close-up of Mamie Citronella standing near the potted succulent, her lemon skin turning pale, her hand clutching the gold locket on her chest. Ultrasound room.
- **Vidéo Veo :** Slow vertical pan from her pale face down to her hand tightening around the gold locket. Mamie Citronella says in French with a high-pitched, prim elderly voice, cold and contemptuous: « Ma chérie… des pépins violets ? Explique-toi, et vite. » Ends on her white-knuckled fingers around the locket.

### PLAN 6 (6 s) — Réaction choc
- **Image :** Close-up of Fraisine sitting on the bed, one single tear running down her cheek, chin up, looking straight ahead with dignity.
- **Vidéo Veo :** Fast zoom in on her eyes. Fraisine says in French, softly, voice breaking but firm: « Regarde-moi, Mangeo. Je ne t'ai jamais trompé. » The tear rolls down. Sound: dramatic "dun dun dunnn" sting, then silence.

### PLAN 7 (8 s) — ★ Phrase culte
- **Image :** Point-of-view shot at Raisino's height: Mangeo and Mamie Citronella side by side, turning toward the camera with accusing glares, frowning. Ultrasound room.
- **Vidéo Veo :** Mangeo and Mamie Citronella slowly turn toward the camera and stare, three seconds of total silence. Then an off-screen young man's voice, warm and slightly husky, panicked and funny, says in French: « Frérot, j'ai juste apporté des ballons, pas des pépins ! » The camera steps back slightly. Ends on their two frozen frowning faces.
- **Texte écran :** —

### PLAN 8 (6 s) — Cliffhanger
- **Image :** Low-angle extreme close-up of Mangeo, jaw clenched, pointing his finger at the camera, backlit so the small violet grape-shaped birthmark near his stem is visible.
- **Vidéo Veo :** Half a second of silence, then a brutal push-in. Mangeo says in French, furious and betrayed, deep voice: « C'est lui le père ?! » Ends on his face, then cut to black. Heavy thud.
- **Texte écran :** Partie 1/4

---

## Montage
Ordre 1→8, cuts secs, flash blanc sur le plan 4, fondu au noir sur le plan 8. Sous-titres colorés par personnage (Fraisine rose, Mangeo orange, Raisino violet, Citronella jaune). Carte « PARTIE 1/4 — La suite demain ». Musique : piano doux → nappe grave à partir du plan 5.

## Checklist
fiches ✅ → 8 images de départ → 8 clips Veo → montage → publication avec l'étiquette « contenu généré par IA ».

```yaml
# fruitpipe:partie
partie: 1
total: 4
plans:
  - {n: 1, duree: 6, decor: echographie, persos: [fraisine], image: "", video: "", replique: {perso: fraisine, texte: "Pourquoi mon bébé a des pépins… violets ?!"}, texte_ecran: "DES PÉPINS… VIOLETS ?!"}
  - {n: 2, duree: 8, decor: echographie, persos: [fraisine, mangeo], image: "", video: "", replique: {perso: mangeo, texte: "C'est sûrement un bug de la machine, mon cœur."}}
  - {n: 3, duree: 8, decor: echographie, persos: [raisino, mangeo], image: "", video: "", replique: {perso: raisino, texte: "Frérot, j'ai les ballons ! Alors, fille ou garçon ?"}}
  - {n: 4, duree: 6, decor: echographie, persos: [mangeo, raisino], image: "", video: "", texte_ecran: "Vous avez vu ?"}
  - {n: 5, duree: 8, decor: echographie, persos: [citronella], image: "", video: "", replique: {perso: citronella, texte: "Ma chérie… des pépins violets ? Explique-toi, et vite."}}
  - {n: 6, duree: 6, decor: echographie, persos: [fraisine], image: "", video: "", replique: {perso: fraisine, texte: "Regarde-moi, Mangeo. Je ne t'ai jamais trompé."}}
  - {n: 7, duree: 8, decor: echographie, persos: [mangeo, citronella], image: "", video: "", replique: {perso: raisino, texte: "Frérot, j'ai juste apporté des ballons, pas des pépins !"}}
  - {n: 8, duree: 6, decor: echographie, persos: [mangeo], image: "", video: "", replique: {perso: mangeo, texte: "C'est lui le père ?!"}}
```
