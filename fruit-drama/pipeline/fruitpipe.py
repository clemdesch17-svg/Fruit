#!/usr/bin/env python3
"""Fruit Drama — génération automatique via l'API Gemini.

Commandes (lancer depuis fruit-drama/pipeline/) :
  python3 fruitpipe.py estimer  <titre> <N>                 coût estimé, ne dépense rien
  python3 fruitpipe.py fiches   <titre>                     fiches personnages (à valider)
  python3 fruitpipe.py valider  <titre>                     valide les fiches générées
  python3 fruitpipe.py partie   <titre> <N> [--tout | --plans 1,4] [--lite | --hd] [--oui]
                                     par défaut : MODE TEST = plan 1 seulement
  python3 fruitpipe.py refaire  <titre> <N> <plan> [--image] [--lite | --hd] [--oui]
  python3 fruitpipe.py montage  <titre> <N>                 assemble les clips existants

Avant toute dépense, le coût estimé est affiché et une confirmation est demandée
(--oui pour confirmer d'avance). Chaque dépense réelle est notée dans
series/<titre>/rendus/couts.jsonl.
"""
import argparse
import datetime
import json
import os
import sys

import couts
import gemini
import montage
import serie

ICI = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------- utilitaires
def rendus(titre, *sous):
    d = os.path.join(serie.dossier(titre), "rendus", *sous)
    os.makedirs(d, exist_ok=True)
    return d


def resolution(args):
    return "360p" if args.lite else "1080p" if args.hd else "720p"


def confirmer(lignes, total, oui):
    print("\n=== COÛT ESTIMÉ (tarifs officiels Gemini API, relevés le 21/11/2026) ===")
    for l in lignes:
        print("  " + l)
    print(f"  TOTAL ESTIMÉ : {total:.2f} $\n")
    if oui:
        print("Confirmé d'avance (--oui).")
        return
    try:
        r = input("Lancer la génération ? (o/N) ").strip().lower()
    except EOFError:
        r = ""
    if r not in ("o", "oui", "y", "yes"):
        raise SystemExit("Annulé, rien n'a été dépensé.")


def noter(titre, quoi, cout, extra=None):
    with open(os.path.join(rendus(titre), "couts.jsonl"), "a") as f:
        f.write(json.dumps({"date": datetime.datetime.now().isoformat(timespec="seconds"),
                            "quoi": quoi, "cout_usd": round(cout, 4), **(extra or {})},
                           ensure_ascii=False) + "\n")


def fiche(titre, pid):
    return os.path.join(rendus(titre, "fiches"), f"{pid}.png")


def fiches_validees(titre):
    return os.path.exists(os.path.join(rendus(titre, "fiches"), "VALIDE"))


# ------------------------------------------------------------- commandes
def cmd_fiches(args):
    bib = serie.bible(args.titre)
    a_faire = [pid for pid in bib["personnages"] if args.refaire or not os.path.exists(fiche(args.titre, pid))]
    if not a_faire:
        print("Toutes les fiches existent déjà (--refaire pour les régénérer).")
        return
    c = couts.cout_image(len(a_faire))
    confirmer([f"{len(a_faire)} fiche(s) personnage · {couts.IMAGE_MODEL} {couts.IMAGE_TAILLE}"], c, args.oui)
    for pid in a_faire:
        print(f"→ fiche {pid}…", flush=True)
        gemini.generer_image(serie.prompt_fiche(bib, pid), fiche(args.titre, pid), couts.IMAGE_MODEL,
                             taille=couts.IMAGE_TAILLE)
        noter(args.titre, f"fiche {pid}", couts.cout_image(1))
        print("   ", os.path.relpath(fiche(args.titre, pid)))
    v = os.path.join(rendus(args.titre, "fiches"), "VALIDE")
    if os.path.exists(v):
        os.remove(v)
    print("\nRegarde les fiches, puis : python3 fruitpipe.py valider", args.titre)


def cmd_valider(args):
    bib = serie.bible(args.titre)
    manque = [pid for pid in bib["personnages"] if not os.path.exists(fiche(args.titre, pid))]
    if manque:
        raise SystemExit(f"Fiches manquantes : {', '.join(manque)}")
    open(os.path.join(rendus(args.titre, "fiches"), "VALIDE"), "w").write(datetime.date.today().isoformat())
    print("Fiches validées.")


def plan_fichiers(titre, n, plan_n):
    d = rendus(titre, f"partie-{n}")
    return os.path.join(d, f"plan{plan_n:02d}_keyframe.png"), os.path.join(d, f"plan{plan_n:02d}.mp4")


def _plans_choisis(args, part):
    if args.tout:
        return part["plans"]
    if args.plans:
        voulus = {int(x) for x in args.plans.split(",")}
        return [p for p in part["plans"] if p["n"] in voulus]
    return part["plans"][:1]          # mode test par défaut


def estimation(titre, part, plans, res, refaire_image=False, refaire_video=False):
    lignes, total = [], 0.0
    for p in plans:
        kf, clip = plan_fichiers(titre, part["partie"], p["n"])
        if refaire_image or not os.path.exists(kf):
            c = couts.cout_image(1)
            lignes.append(f"plan {p['n']:>2} keyframe  · {couts.IMAGE_MODEL} {couts.IMAGE_TAILLE}  {c:.3f} $")
            total += c
        if refaire_video or refaire_image or not os.path.exists(clip):
            c = couts.cout_video(p["duree"], res)
            lignes.append(f"plan {p['n']:>2} clip {p['duree']} s · {couts.VIDEO_MODEL} {res}  {c:.3f} $")
            total += c
    if not lignes:
        lignes.append("rien à générer (tout existe déjà)")
    return lignes, total


def generer_plan(titre, bib, part, plan, res, refaire_image, refaire_video):
    kf, clip = plan_fichiers(titre, part["partie"], plan["n"])
    if refaire_image or not os.path.exists(kf):
        print(f"→ plan {plan['n']} : keyframe…", flush=True)
        refs = [fiche(titre, pid) for pid in plan["persos"]]
        gemini.generer_image(serie.prompt_keyframe(bib, plan), kf, couts.IMAGE_MODEL, references=refs,
                             taille=couts.IMAGE_TAILLE)
        noter(titre, f"P{part['partie']} plan {plan['n']} keyframe", couts.cout_image(1))
        refaire_video = True
    if refaire_video or not os.path.exists(clip):
        print(f"→ plan {plan['n']} : clip {plan['duree']} s {res} (quelques minutes)…", flush=True)
        meta = gemini.generer_video(serie.prompt_video(bib, plan), clip, couts.VIDEO_MODEL, kf,
                                    duree=plan["duree"], resolution=res)
        reel = montage.duree(clip)
        cout = couts.cout_video(reel, res)
        noter(titre, f"P{part['partie']} plan {plan['n']} clip", cout,
              {"secondes": round(reel, 2), "resolution": res, "interaction": meta.get("id")})
    print("   ", os.path.relpath(kf), "\n   ", os.path.relpath(clip))


def _exiger_fiches(titre):
    if not fiches_validees(titre):
        raise SystemExit("Fiches non validées. Lance d'abord : fiches puis valider.")


def cmd_estimer(args):
    bib = serie.bible(args.titre)
    part = serie.partie(args.titre, args.n, bib)
    res = resolution(args)
    nf = sum(not os.path.exists(fiche(args.titre, pid)) for pid in bib["personnages"])
    for mode, plans in (("plan 1 (mode test)", part["plans"][:1]), ("partie complète", part["plans"])):
        lignes, total = estimation(args.titre, part, plans, res)
        total += couts.cout_image(nf)
        sec = sum(p["duree"] for p in plans)
        print(f"{mode:20} {len(plans):2} plan(s), {sec:3} s de vidéo {res} : {total:6.2f} $"
              + (f"  (dont {nf} fiche(s))" if nf else ""))


def cmd_partie(args):
    bib = serie.bible(args.titre)
    part = serie.partie(args.titre, args.n, bib)
    _exiger_fiches(args.titre)
    plans = _plans_choisis(args, part)
    res = resolution(args)
    if not args.tout and not args.plans:
        print("MODE TEST : plan 1 seulement (--tout pour toute la partie).")
    lignes, total = estimation(args.titre, part, plans, res)
    confirmer(lignes, total, args.oui)
    for p in plans:
        generer_plan(args.titre, bib, part, p, res, False, False)
    bilan(args.titre)


def cmd_refaire(args):
    bib = serie.bible(args.titre)
    part = serie.partie(args.titre, args.n, bib)
    _exiger_fiches(args.titre)
    plan = next((p for p in part["plans"] if p["n"] == args.plan), None)
    if not plan:
        raise SystemExit(f"Plan {args.plan} introuvable dans la partie {args.n}")
    res = resolution(args)
    lignes, total = estimation(args.titre, part, [plan], res, args.image, True)
    confirmer(lignes, total, args.oui)
    generer_plan(args.titre, bib, part, plan, res, args.image, True)
    bilan(args.titre)


def cmd_montage(args):
    bib = serie.bible(args.titre)
    part = serie.partie(args.titre, args.n, bib)
    clips, plans_ok = [], []
    for p in part["plans"]:
        _, clip = plan_fichiers(args.titre, args.n, p["n"])
        if os.path.exists(clip):
            clips.append(clip)
            plans_ok.append(p)
        else:
            print(f"(plan {p['n']} absent, ignoré)")
    if not clips:
        raise SystemExit("Aucun clip à assembler.")
    part = dict(part, plans=plans_ok)
    sortie = os.path.join(rendus(args.titre), f"{args.titre}_partie{args.n}.mp4")
    total, musique = montage.assembler(serie.dossier(args.titre), bib, part, clips, sortie,
                                       couper=not args.sans_coupe, fin=args.fin)
    print(f"→ {os.path.relpath(sortie)}  ({total:.1f} s, musique : {'oui' if musique else 'non — ajoute series/<titre>/musique.mp3'})")
    if total < 61:
        print(f"ATTENTION : {total:.1f} s — TikTok ne rémunère que les vidéos de PLUS d'une minute "
              "(ajoute un plan, --fin 6 ou --sans-coupe).")
    elif total > 90:
        print(f"ATTENTION : {total:.1f} s — un peu long, vise 65-75 s.")


def bilan(titre):
    chemin = os.path.join(rendus(titre), "couts.jsonl")
    if os.path.exists(chemin):
        total = sum(json.loads(l)["cout_usd"] for l in open(chemin))
        print(f"\nCoût réel cumulé pour « {titre} » : {total:.2f} $  (détail : {os.path.relpath(chemin)})")


def main():
    gemini.charger_env(os.path.join(ICI, ".env"))
    ap = argparse.ArgumentParser(description="Fruit Drama — pipeline Gemini")
    sp = ap.add_subparsers(dest="cmd", required=True)

    def qualite(p):
        g = p.add_mutually_exclusive_group()
        g.add_argument("--lite", action="store_true", help="brouillon 360p (~0,023 $/s)")
        g.add_argument("--hd", action="store_true", help="1080p (~0,104 $/s)")
        p.add_argument("--oui", action="store_true", help="confirmer le coût d'avance")

    p = sp.add_parser("estimer"); p.add_argument("titre"); p.add_argument("n", type=int); qualite(p)
    p = sp.add_parser("fiches"); p.add_argument("titre"); p.add_argument("--refaire", action="store_true")
    p.add_argument("--oui", action="store_true")
    p = sp.add_parser("valider"); p.add_argument("titre")
    p = sp.add_parser("partie"); p.add_argument("titre"); p.add_argument("n", type=int)
    g = p.add_mutually_exclusive_group(); g.add_argument("--tout", action="store_true"); g.add_argument("--plans")
    qualite(p)
    p = sp.add_parser("refaire"); p.add_argument("titre"); p.add_argument("n", type=int)
    p.add_argument("plan", type=int); p.add_argument("--image", action="store_true", help="refaire aussi le keyframe")
    qualite(p)
    p = sp.add_parser("montage"); p.add_argument("titre"); p.add_argument("n", type=int)
    p.add_argument("--sans-coupe", action="store_true", help="ne pas couper les silences des clips")
    p.add_argument("--fin", type=float, default=4.0, help="durée de la carte « Abonne-toi » (s)")

    args = ap.parse_args()
    {"estimer": cmd_estimer, "fiches": cmd_fiches, "valider": cmd_valider, "partie": cmd_partie,
     "refaire": cmd_refaire, "montage": cmd_montage}[args.cmd](args)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        sys.exit(f"ERREUR : {e}")
