"""Modèles et tarifs de l'API Gemini.

Source : documentation officielle, relevée le 21/11/2026
  - https://aistudio.google.com/docs/pricing
  - https://aistudio.google.com/docs/omni
  - https://aistudio.google.com/docs/image-generation
Veo 3.1 (generate / fast / lite preview) a été ARRÊTÉ dans l'API Gemini le
22/10/2026 ; Google indique de migrer vers Gemini Omni Flash.
Revérifier ces chiffres avant toute grosse production : ils changent.
"""

# --- Images (Nano Banana 2.1) : $30 / 1M tokens image en sortie
IMAGE_MODEL = "gemini-nano-banana-2.1"
IMAGE_PRIX = {"1K": 0.0336, "2K": 0.0504, "4K": 0.113}   # $ par image
IMAGE_TAILLE = "2K"           # haute résolution recommandée pour l'image-to-video

# --- Vidéo (Gemini Omni Flash 1.2) : $12 / 1M tokens vidéo en sortie
VIDEO_MODEL = "gemini-omni-1.2-flash"
VIDEO_PRIX_SECONDE = {        # $ par seconde générée, selon la résolution
    "360p": 0.023,            # 1 931 tokens/s  -> mode --lite (brouillon)
    "720p": 0.07,             # 5 792 tokens/s  -> défaut
    "1080p": 0.104,           # 8 688 tokens/s  -> option --hd
}
VIDEO_DUREE_MIN, VIDEO_DUREE_MAX = 3, 8   # Omni accepte 3-15 s ; on plafonne à 8 s par plan

# Petites entrées (texte + images de référence, $1.50 / 1M tokens) : négligeables,
# on ajoute une marge forfaitaire par appel pour ne jamais sous-estimer.
MARGE_PAR_APPEL = 0.005


def cout_image(n=1, taille=IMAGE_TAILLE):
    return n * (IMAGE_PRIX[taille] + MARGE_PAR_APPEL)


def cout_video(secondes, resolution="720p"):
    return secondes * VIDEO_PRIX_SECONDE[resolution] + MARGE_PAR_APPEL
