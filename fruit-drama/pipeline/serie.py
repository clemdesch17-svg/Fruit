"""Lecture de series/<titre>/bible.md et prod-partie-N.md.

Chaque fichier contient, en plus du texte lisible, UN bloc ```yaml dont la
première ligne est un commentaire repère :
  bible.md        ->  # fruitpipe:bible
  prod-partie-N   ->  # fruitpipe:partie
Le format exact est documenté dans pipeline/README.md.
"""
import os
import re

import yaml

ICI = os.path.dirname(os.path.abspath(__file__))
SERIES = os.path.join(ICI, "..", "series")


def _bloc(chemin, repere):
    texte = open(chemin, encoding="utf-8").read()
    for m in re.finditer(r"```ya?ml\n(.*?)```", texte, re.S):
        if m.group(1).lstrip().startswith(f"# fruitpipe:{repere}"):
            return yaml.safe_load(m.group(1))
    raise SystemExit(f"{chemin} : bloc ```yaml commençant par « # fruitpipe:{repere} » introuvable.")


def dossier(titre):
    d = os.path.join(SERIES, titre)
    if not os.path.isdir(d):
        raise SystemExit(f"Série introuvable : {d}")
    return d


def bible(titre):
    b = _bloc(os.path.join(dossier(titre), "bible.md"), "bible")
    for k in ("style", "personnages", "decors"):
        if k not in b:
            raise SystemExit(f"bible.md : champ « {k} » manquant")
    for pid, p in b["personnages"].items():
        for k in ("nom", "visuel", "voix", "couleur"):
            if k not in p:
                raise SystemExit(f"bible.md : personnage {pid}, champ « {k} » manquant")
    return b


def partie(titre, n, bib):
    p = _bloc(os.path.join(dossier(titre), f"prod-partie-{n}.md"), "partie")
    for plan in p["plans"]:
        for k in ("n", "duree", "decor", "persos", "image", "video"):
            if k not in plan:
                raise SystemExit(f"prod-partie-{n}.md : plan {plan.get('n')}, champ « {k} » manquant")
        if not 3 <= plan["duree"] <= 8:
            raise SystemExit(f"Plan {plan['n']} : durée {plan['duree']} s hors limites (3-8 s)")
        if plan["decor"] not in bib["decors"]:
            raise SystemExit(f"Plan {plan['n']} : décor « {plan['decor']} » absent de la bible")
        for pid in plan["persos"]:
            if pid not in bib["personnages"]:
                raise SystemExit(f"Plan {plan['n']} : perso « {pid} » absent de la bible")
        rep = plan.get("replique")
        if rep and rep["perso"] not in bib["personnages"]:
            raise SystemExit(f"Plan {plan['n']} : réplique d'un perso inconnu « {rep['perso']} »")
    p.setdefault("total", 4)
    return p


# ------------------------------------------------------------- prompts
def prompt_fiche(bib, pid):
    p = bib["personnages"][pid]
    return (f"Character reference sheet. {bib['style']}. {p['visuel']} "
            "Full body, standing in a neutral pose, facing the camera, plain light grey studio "
            "background, soft even studio lighting, the whole character visible head to toe, "
            "vertical 9:16 composition, no text, no watermark.")


def prompt_keyframe(bib, plan):
    persos = " ".join(bib["personnages"][pid]["visuel"] for pid in plan["persos"])
    return (f"{bib['style']}. {persos} Setting: {bib['decors'][plan['decor']]} "
            f"{plan['image']} Keep the exact same character design as the reference image(s). "
            "Vertical 9:16 composition, no text, no watermark.")


def prompt_video(bib, plan):
    morceaux = [plan["video"]]
    rep = plan.get("replique")
    if rep:
        p = bib["personnages"][rep["perso"]]
        morceaux.append(f'{p["nom"]} says in French: "{rep["texte"]}" '
                        f"Voice: {p['voix']}.")
    else:
        morceaux.append("No dialogue.")
    if plan.get("ambiance"):
        morceaux.append(f"Sound: {plan['ambiance']}.")
    morceaux.append("Keep the exact character design from the image. No subtitles, no on-screen "
                    "text, no music. Do not deform hands, no extra limbs, no morphing.")
    return " ".join(morceaux)
