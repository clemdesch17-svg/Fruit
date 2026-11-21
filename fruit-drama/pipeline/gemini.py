"""Client minimal de l'API Interactions de Gemini (REST, bibliothèque standard).

Endpoints et formats tirés de la doc officielle (aistudio.google.com/docs/omni
et /docs/image-generation).
"""
import base64
import json
import os
import time
import urllib.error
import urllib.request

BASE = "https://generativelanguage.googleapis.com/v1beta"
API_REVISION = "2026-05-20"


def charger_env(chemin):
    """Lit un fichier .env (CLE=valeur) sans dépendance externe."""
    if not os.path.exists(chemin):
        return
    for ligne in open(chemin, encoding="utf-8"):
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and "=" in ligne:
            k, v = ligne.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _cle():
    cle = os.environ.get("GEMINI_API_KEY")
    if not cle:
        raise SystemExit("GEMINI_API_KEY manquante : copie .env.example en .env et mets ta clé dedans.")
    return cle


def _post(chemin, corps, timeout=900):
    req = urllib.request.Request(
        BASE + chemin, data=json.dumps(corps).encode(), method="POST",
        headers={"Content-Type": "application/json", "x-goog-api-key": _cle(),
                 "Api-Revision": API_REVISION})
    for essai in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:800]
            if e.code in (429, 500, 502, 503, 504) and essai < 3:
                time.sleep(10 * (essai + 1))
                continue
            raise RuntimeError(f"API Gemini {e.code} : {detail}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if essai < 3:
                time.sleep(10 * (essai + 1))
                continue
            raise RuntimeError(f"Réseau : {e}") from None


def _get_binaire(url):
    req = urllib.request.Request(url, headers={"x-goog-api-key": _cle()})
    with urllib.request.urlopen(req, timeout=600) as r:
        return r.read()


def _sorties(rep, type_):
    """Contenus de type `type_` dans les étapes model_output (format REST)."""
    out = []
    for step in rep.get("steps", []):
        if step.get("type") == "model_output":
            out += [c for c in step.get("content", []) if c.get("type") == type_]
    return out


def _img_part(chemin):
    mime = "image/png" if chemin.lower().endswith(".png") else "image/jpeg"
    return {"type": "image", "mime_type": mime,
            "data": base64.b64encode(open(chemin, "rb").read()).decode()}


def generer_image(prompt, sortie, modele, references=(), ratio="9:16", taille="2K"):
    """Nano Banana : texte (+ images de référence) -> image. Retourne la réponse brute."""
    entree = [_img_part(r) for r in references] + [{"type": "text", "text": prompt}]
    rep = _post("/interactions", {
        "model": modele, "input": entree,
        "response_format": {"type": "image", "mime_type": "image/png",
                            "aspect_ratio": ratio, "image_size": taille}})
    imgs = _sorties(rep, "image")
    if not imgs:
        raise RuntimeError("Aucune image renvoyée : " + json.dumps(rep)[:600])
    with open(sortie, "wb") as f:
        f.write(base64.b64decode(imgs[-1]["data"]))
    return rep


def generer_video(prompt, sortie, modele, image_depart, duree=8, resolution="720p", ratio="9:16"):
    """Omni Flash : image de départ + prompt -> clip mp4 avec audio natif."""
    rep = _post("/interactions", {
        "model": modele,
        "input": [_img_part(image_depart), {"type": "text", "text": prompt}],
        "response_format": {"type": "video", "aspect_ratio": ratio, "resolution": resolution,
                            "duration": f"{int(duree)}s", "delivery": "uri"},
        "generation_config": {"video_config": {"task": "image_to_video"}},
        "store": False,
    })
    vids = _sorties(rep, "video")
    if not vids:
        raise RuntimeError("Aucune vidéo renvoyée : " + json.dumps(rep)[:600])
    v = vids[-1]
    if v.get("data"):
        donnees = base64.b64decode(v["data"])
    else:
        uri = v["uri"]
        fichier = uri.split("/files/")[-1].split(":")[0]
        for _ in range(120):  # attend que le fichier soit ACTIF (doc : polling toutes les 5 s)
            req = urllib.request.Request(f"{BASE}/files/{fichier}", headers={"x-goog-api-key": _cle()})
            with urllib.request.urlopen(req, timeout=60) as r:
                etat = json.load(r).get("state")
            if etat == "ACTIVE":
                break
            if etat == "FAILED":
                raise RuntimeError("Génération vidéo échouée côté Google.")
            time.sleep(5)
        donnees = _get_binaire(uri)
    with open(sortie, "wb") as f:
        f.write(donnees)
    return {k: v for k, v in rep.items() if k != "steps"}
