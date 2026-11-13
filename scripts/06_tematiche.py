# -*- coding: utf-8 -*-
"""
CLASSIFICAZIONE PER TEMATICHE (tutti i video del canale)
========================================================
Assegna a ogni video:
  - area_principale   una sola area (es. "DOLORE E FISIOTERAPIA")
  - aree_secondarie   altre aree trattate in modo rilevante
  - argomenti         argomenti specifici (es. "Schiena e lombare")
  - pubblico          destinatari (Over 50 e anziani, Donne, Uomini, Sportivi...)
  - formato           Lezione da seguire, Testimonianza o caso clinico, Short...

Lo schema e le parole chiave sono in scripts/tematiche_config.py.
Le correzioni manuali vanno in dati/revisione_tematiche.csv
(colonne: id;area_principale;argomenti) e hanno sempre la precedenza.

Richiede: dati/elenco_video.csv e dati/classificazione_completa.csv (Fase 1).
Risultati: dati/tematiche.csv e dati/riepilogo_tematiche.md

Uso:  python scripts/06_tematiche.py
"""
import importlib
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import tematiche_config as TC  # noqa: E402
from comune import (CLASSIFICAZIONE, DATI, ELENCO_VIDEO, leggi_csv, prepara_console,  # noqa: E402
                    scrivi_csv)

classifica = importlib.import_module("02_classifica")

TEMATICHE = DATI / "tematiche.csv"
RIEPILOGO = DATI / "riepilogo_tematiche.md"
REVISIONE = DATI / "revisione_tematiche.csv"

# argomenti con parole molto generiche: valgono la meta'
GENERICI = {
    "Ginnastica e allenamenti guidati", "Esami, analisi e diagnosi", "Critica del sistema sanitario",
    "Abitudini e routine quotidiane", "Infiammazione", "Dolore cronico e fibromialgia",
    "Crescita personale e filosofia", "Peso e metabolismo",
}
# in caso di parita' vince l'area che compare prima in questo elenco
PRIORITA = [
    "ALIMENTAZIONE", "DOLORE E FISIOTERAPIA", "UOMO, DONNA E SESSUALITÀ", "ORGANI E MALATTIE",
    "CUORE E CIRCOLAZIONE", "CERVELLO, SONNO E MENTE", "PELLE, DENTI E SENSI",
    "LONGEVITÀ E INVECCHIAMENTO", "ESERCIZIO E MOVIMENTO", "FARMACI, ESAMI E SANITÀ",
    "AMBIENTE E ABITUDINI QUOTIDIANE", "CANALE E VARIE",
]
PESO_TITOLO, PESO_DESCR = 3.0, 1.0
SOGLIA_ARGOMENTO = 2.0      # punteggio minimo perche' un argomento venga assegnato
SOGLIA_SECONDARIA = 3.0     # punteggio minimo perche' un'area sia "secondaria"
CAMPI = ["id", "titolo", "data_pubblicazione", "durata", "categoria_alimentazione", "area_principale",
         "aree_secondarie", "argomenti", "pubblico", "formato", "stato", "url"]


def compila(parole):
    return [re.compile(r"(?<![\w])" + p, re.IGNORECASE) for p in parole]


SCHEMA = {area: {arg: compila(p) for arg, p in args.items()} for area, args in TC.AREE.items()}
PUBBLICO = {k: compila(v) for k, v in TC.PUBBLICO.items()}
FORMATO = {k: compila(v) for k, v in TC.FORMATO.items()}


def conta(testo, regex):
    return sum(1 for rx in regex if rx.search(testo))


def analizza(titolo, descrizione, cat_alim):
    punti_arg = {}
    for area, args in SCHEMA.items():
        if area == "ALIMENTAZIONE" and cat_alim not in ("ALIMENTAZIONE", "MISTO"):
            continue
        for arg, rx in args.items():
            p = PESO_TITOLO * min(conta(titolo, rx), 2) + PESO_DESCR * min(conta(descrizione, rx), 3)
            if arg in GENERICI:
                p /= 2
            if p:
                punti_arg[(area, arg)] = p

    punti_area = defaultdict(float)
    for (area, _), p in punti_arg.items():
        punti_area[area] += p
    # garanzie dalla Fase 1
    if cat_alim == "ALIMENTAZIONE":
        punti_area["ALIMENTAZIONE"] += 100
    elif cat_alim == "MISTO":
        punti_area["ALIMENTAZIONE"] = max(punti_area["ALIMENTAZIONE"], SOGLIA_SECONDARIA)

    candidate = [a for a in punti_area if a not in TC.AREE_SECONDARIE_SOLO] or list(punti_area)
    if candidate:
        principale = max(candidate, key=lambda a: (punti_area[a], -PRIORITA.index(a)))
    else:
        principale = "DA CLASSIFICARE"
    secondarie = [a for a in sorted(punti_area, key=lambda a: -punti_area[a])
                  if a != principale and punti_area[a] >= SOGLIA_SECONDARIA]
    argomenti = [arg for (area, arg), p in sorted(punti_arg.items(), key=lambda x: -x[1])
                 if p >= SOGLIA_ARGOMENTO and (area == principale or area in secondarie)]
    pubblico = [k for k, rx in PUBBLICO.items() if conta(titolo, rx) or conta(descrizione[:200], rx)]
    formato = [k for k, rx in FORMATO.items() if conta(titolo, rx)] or ["Spiegazione"]
    return principale, secondarie, argomenti, pubblico, formato


def main():
    prepara_console()
    video = leggi_csv(ELENCO_VIDEO)
    cat = {r["id"]: r.get("categoria", "") for r in leggi_csv(CLASSIFICAZIONE)}
    if not video or not cat:
        sys.exit("Servono dati/elenco_video.csv e dati/classificazione_completa.csv (Fase 1).")
    ricorrenti = classifica.righe_ricorrenti(video)
    revisione = {r["id"]: r for r in leggi_csv(REVISIONE) if r.get("id")}

    righe = []
    for v in video:
        descr = classifica.pulisci_descrizione(v.get("descrizione"), ricorrenti)
        descr = re.sub(r"#\w+", " ", descr)   # via gli hashtag (#fisioterapiamilano...)
        princ, sec, args, pub, form = analizza(v.get("titolo") or "", descr, cat.get(v["id"], ""))
        r = {
            "id": v["id"], "titolo": v.get("titolo"), "data_pubblicazione": v.get("data_pubblicazione"),
            "durata": v.get("durata"), "categoria_alimentazione": cat.get(v["id"], ""),
            "area_principale": princ, "aree_secondarie": " | ".join(sec),
            "argomenti": " | ".join(args[:5]), "pubblico": " | ".join(pub),
            "formato": " | ".join(form), "stato": "AUTOMATICA", "url": v.get("url"),
        }
        man = revisione.get(v["id"])
        if man:
            for campo in ("area_principale", "argomenti"):
                if man.get(campo):
                    r[campo] = man[campo]
            r["stato"] = "REVISIONATA"
        righe.append(r)

    scrivi_csv(TEMATICHE, CAMPI, righe)
    if not REVISIONE.exists():
        scrivi_csv(REVISIONE, ["id", "area_principale", "argomenti"], [])

    per_area = Counter(r["area_principale"] for r in righe)
    tocca = Counter()
    for r in righe:
        for a in [r["area_principale"]] + [x for x in r["aree_secondarie"].split(" | ") if x]:
            tocca[a] += 1
    per_arg = defaultdict(Counter)
    for r in righe:
        for a in [x for x in r["argomenti"].split(" | ") if x]:
            per_arg[r["area_principale"]][a] += 1
    pub = Counter(p for r in righe for p in r["pubblico"].split(" | ") if p)
    form = Counter(f for r in righe for f in r["formato"].split(" | ") if f)

    md = ["# Riepilogo tematiche del canale", "",
          f"Video totali: {len(righe)}", "",
          "## Aree", "", "| Area | Area principale | Video che la trattano (anche secondaria) |",
          "|---|---|---|"]
    for a, n in per_area.most_common():
        md.append(f"| {a} | {n} | {tocca[a]} |")
    md += ["", "## Argomenti per area (sui video con quell'area principale)", ""]
    for a, _ in per_area.most_common():
        md.append(f"**{a}**: " + ", ".join(f"{k} ({n})" for k, n in per_arg[a].most_common()))
        md.append("")
    md += ["## Pubblico", "", ", ".join(f"{k} ({n})" for k, n in pub.most_common()), "",
           "## Formato", "", ", ".join(f"{k} ({n})" for k, n in form.most_common()), ""]
    for a, _ in per_area.most_common():
        gruppo = [r for r in righe if r["area_principale"] == a]
        passo = max(1, len(gruppo) // 8)
        md += [f"## Esempi: {a}", ""]
        md += [f"- {r['titolo']}  _({r['argomenti'] or '-'})_" for r in gruppo[::passo][:8]]
        md.append("")
    RIEPILOGO.write_text("\n".join(md), encoding="utf-8")

    print("=== AREE PRINCIPALI ===")
    for a, n in per_area.most_common():
        print(f"{n:5}  {a}   (trattata in {tocca[a]} video)")
    print("\nFile creati: dati/tematiche.csv, dati/riepilogo_tematiche.md")


if __name__ == "__main__":
    main()
