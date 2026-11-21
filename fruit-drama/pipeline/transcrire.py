"""Repère le moment où chaque mot est prononcé dans les clips (faster-whisper, local).

Sert uniquement à caler les sous-titres sur les voix générées par Flow/Veo :
aucune voix n'est créée ici. Le résultat est mis en cache dans mots.json.
"""
import json
import os
import subprocess

import numpy as np

_MODELE = None


def _modele():
    global _MODELE
    if _MODELE is None:
        from faster_whisper import WhisperModel
        _MODELE = WhisperModel("small", device="cpu", compute_type="int8")
    return _MODELE


def mots_du_clip(chemin):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", chemin, "-f", "s16le", "-ac", "1",
                          "-ar", "16000", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    segs, _ = _modele().transcribe(audio, language="fr", word_timestamps=True)
    return [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for s in segs for w in s.words]


def mots_des_clips(clips, cache):
    """{nom_du_clip: [[mot, début, fin], ...]} — recalcule seulement les clips nouveaux/modifiés."""
    data = json.load(open(cache)) if os.path.exists(cache) else {}
    change = False
    for c in clips:
        cle = os.path.basename(c)
        sig = f"{os.path.getsize(c)}-{int(os.path.getmtime(c))}"
        if data.get(cle, {}).get("sig") != sig:
            data[cle] = {"sig": sig, "mots": mots_du_clip(c)}
            change = True
    if change:
        json.dump(data, open(cache, "w"), ensure_ascii=False)
    return {k: v["mots"] for k, v in data.items()}
