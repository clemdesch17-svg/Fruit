"""Assemblage ffmpeg : clips -> vidéo TikTok 1080x1920.

- chaque clip remis à l'échelle en 1080x1920 (recadrage si besoin)
- sous-titres ASS colorés par personnage (couleurs de la bible)
- musique optionnelle : series/<titre>/musique.mp3 (ou .m4a/.wav), mixée sous les voix
- carte « Partie X/4 — la suite demain » sur les 2,5 dernières secondes
"""
import glob
import json
import os
import subprocess

POLICE = "DejaVu Sans"


def duree(chemin):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", chemin],
                         capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["format"]["duration"])


def a_audio(chemin):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", chemin], capture_output=True, text=True).stdout
    return bool(out.strip())


def _ass_couleur(hexa):
    h = hexa.lstrip("#")
    return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def _t(s):
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _echappe(texte):
    return texte.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def _morceaux(texte, mots, d):
    """Découpe la réplique en morceaux de 2-3 mots, chacun affiché pendant qu'il est prononcé.

    `mots` = mots repérés dans le clip [[mot, début, fin], ...]. On garde le texte du script
    (orthographe exacte) et on prend le timing de la voix.
    """
    jetons = texte.split()
    if mots:
        debut, fin = mots[0][1], mots[-1][2]
    else:                                   # pas de voix repérée : réplique sur tout le plan
        debut, fin = 0.3, d - 0.3
    if len(mots) == len(jetons):
        temps = [(m[1], m[2]) for m in mots]
    else:                                   # répartition proportionnelle à la longueur des mots
        poids = [len(j) + 1 for j in jetons]
        tot, acc, temps = sum(poids), 0, []
        for p in poids:
            a = debut + (fin - debut) * acc / tot
            acc += p
            temps.append((a, debut + (fin - debut) * acc / tot))
    groupes, cur = [], []
    for i, j in enumerate(jetons):
        cur.append(i)
        if len(cur) == 3 or j[-1] in ".?!,…" or (len(cur) == 2 and len(j) > 7):
            groupes.append(cur)
            cur = []
    if cur:
        groupes.append(cur)
    out = []
    for k, g in enumerate(groupes):
        a = temps[g[0]][0]
        b = temps[groupes[k + 1][0]][0] if k + 1 < len(groupes) else min(d - 0.05, temps[g[-1]][1] + 0.35)
        out.append((max(0.0, a - 0.05), max(b, a + 0.25), " ".join(jetons[i] for i in g)))
    return out


def ecrire_ass(chemin, bib, plans, durees, mots_par_plan=None):
    mots_par_plan = mots_par_plan or [None] * len(plans)
    styles = []
    for pid, p in bib["personnages"].items():
        # gros texte style TikTok, couleur du personnage, contour noir épais, au tiers bas
        styles.append(f"Style: {pid},{POLICE},86,{_ass_couleur(p['couleur'])},&H00FFFFFF,&H00000000,"
                      "&H80000000,-1,0,0,0,100,100,0,0,1,8,3,2,70,70,520,1")
    styles.append(f"Style: ecran,{POLICE},56,&H00FFFFFF,&H00FFFFFF,&H00000000,&HAA000000,-1,0,0,0,"
                  "100,100,0,0,3,14,0,8,80,80,380,1")
    ev, t = [], 0.0
    for plan, d, mots in zip(plans, durees, mots_par_plan):
        rep = plan.get("replique")
        if rep:
            for a, b, txt in _morceaux(rep["texte"], mots or [], d):
                # petit effet « pop » à l'apparition
                ev.append(f"Dialogue: 0,{_t(t + a)},{_t(t + b)},{rep['perso']},,0,0,0,,"
                          f"{{\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}}{_echappe(txt)}")
        if plan.get("texte_ecran"):
            ev.append(f"Dialogue: 0,{_t(t + 0.1)},{_t(t + d - 0.1)},ecran,,0,0,0,,{_echappe(plan['texte_ecran'])}")
        t += d
    with open(chemin, "w", encoding="utf-8") as f:
        f.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
                "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
                "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                + "\n".join(styles) +
                "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
                + "\n".join(ev) + "\n")


def assembler(dossier_serie, bib, partie, clips, sortie):
    tmp = os.path.join(os.path.dirname(sortie), "_montage")
    os.makedirs(tmp, exist_ok=True)
    # 1) normaliser chaque clip (1080x1920, 30 i/s, audio stéréo 48 kHz, silence si absent)
    norm, durees = [], []
    for i, c in enumerate(clips):
        o = os.path.join(tmp, f"n{i:02d}.mp4")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", c]
        if not a_audio(c):
            cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest"]
        cmd += ["-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-ar", "48000", "-ac", "2", o]
        subprocess.run(cmd, check=True)
        norm.append(o)
        durees.append(duree(o))
    total = sum(durees)
    # 2) concat
    lst = os.path.join(tmp, "liste.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.abspath(n)}'\n" for n in norm)
    brut = os.path.join(tmp, "brut.mp4")
    # la carte « Abonne-toi » vient APRÈS le dernier plan (image figée 3 s) pour ne pas
    # recouvrir le cliffhanger
    FIN = 3.0
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-vf", f"tpad=stop_mode=clone:stop_duration={FIN}", "-af", f"apad=pad_dur={FIN}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", brut], check=True)
    # 3) sous-titres + carte de fin + musique
    ass = os.path.join(tmp, "sous-titres.ass")
    # sous-titres calés sur le moment où chaque mot est prononcé
    import transcrire
    mots = transcrire.mots_des_clips(clips, os.path.join(os.path.dirname(clips[0]), "mots.json"))
    plans = partie["plans"][:len(clips)]
    mots_par_plan = [mots.get(os.path.basename(c)) if p.get("replique") else None
                     for p, c in zip(plans, clips)]
    ecrire_ass(ass, bib, plans, durees, mots_par_plan)
    debut_carte = total
    total += FIN
    n, tot = partie["partie"], partie["total"]
    if n < tot:
        fin1, fin2 = "ABONNE-TOI ET LIKE", f"POUR LA PARTIE {n + 1} !"
    else:
        fin1, fin2 = "ABONNE-TOI ET LIKE", "POUR LA SAISON 2 !"
    police = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    # pas de « Partie N » au début : il est dans la description et la miniature TikTok
    vf = (f"ass='{ass}',"
          # fin : appel à s'abonner pour la partie suivante
          f"drawbox=x=0:y=0:w=iw:h=ih:color=black@0.55:t=fill:enable='gte(t,{debut_carte})',"
          f"drawtext=fontfile={police}:text='{fin1}':fontcolor=white:fontsize=80:borderw=7:"
          f"x=(w-text_w)/2:y=(h-text_h)/2-70:enable='gte(t,{debut_carte})',"
          f"drawtext=fontfile={police}:text='{fin2}':fontcolor=0xFFD93D:fontsize=84:borderw=8:"
          f"x=(w-text_w)/2:y=(h-text_h)/2+60:enable='gte(t,{debut_carte})'")
    musique = next(iter(sorted(glob.glob(os.path.join(dossier_serie, "musique.*")))), None)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", brut]
    if musique:
        cmd += ["-stream_loop", "-1", "-i", musique, "-filter_complex",
                f"[1:a]volume=0.18,afade=t=out:st={max(0, total - 2)}:d=2[m];"
                "[0:a][m]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "0:v", "-map", "[a]"]
    cmd += ["-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", sortie]
    subprocess.run(cmd, check=True)
    return total, bool(musique)
