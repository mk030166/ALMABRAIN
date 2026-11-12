# -*- coding: utf-8 -*-
"""
FASE 1 - PASSO 2: CLASSIFICAZIONE DEI VIDEO
===========================================
Classifica ogni video di dati/elenco_video.csv in:
    ALIMENTAZIONE  - il tema principale e' l'alimentazione
    MISTO          - alimentazione insieme ad altri temi
    ALTRO          - non riguarda l'alimentazione

Metodo:
 1. Toglie dalle descrizioni le righe ripetute in molti video (link, sponsor,
    saluti...), che altrimenti falserebbero il conteggio.
 2. Cerca le parole chiave di scripts/config.py nel titolo (peso maggiore)
    e nella descrizione.
 3. I casi incerti finiscono in dati/da_rivedere.csv.
 4. Le decisioni prese a mano in dati/revisione_manuale.csv
    (colonne: id;categoria;motivo) hanno SEMPRE la precedenza.

Risultati:
    dati/classificazione_completa.csv  - tutti i video
    dati/video_nutrizione.csv          - solo ALIMENTAZIONE e MISTO (con "motivo")
    dati/da_rivedere.csv               - casi dubbi non ancora rivisti
    dati/riepilogo_fase1.md            - riepilogo con conteggi ed esempi

Uso:  python scripts/02_classifica.py
"""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from comune import (CLASSIFICAZIONE, DA_RIVEDERE, DATI, ELENCO_VIDEO, REVISIONE_MANUALE,  # noqa: E402
                    VIDEO_NUTRIZIONE, leggi_csv, prepara_console, scrivi_csv)

CATEGORIE = ("ALIMENTAZIONE", "MISTO", "ALTRO")
CAMPI = ["id", "titolo", "data_pubblicazione", "durata", "categoria", "stato",
         "motivo", "parole_titolo", "parole_descrizione", "url"]
ESEMPI_PER_CATEGORIA = 15


def compila(radici):
    return [(r, re.compile(r"(?<![\w])" + r, re.IGNORECASE)) for r in radici]


FORTI = compila(config.ALIMENTAZIONE_FORTI)
DEBOLI = compila(config.ALIMENTAZIONE_DEBOLI)
ALTRI = compila(config.ALTRI_ARGOMENTI)


def etichetta(radice):
    return re.sub(r"\\b|\(|\)|\|.*?(?=\))", "", radice).replace("\\", "")


def trova(testo, elenco):
    return sorted({etichetta(r) for r, rx in elenco if rx.search(testo or "")})


def righe_ricorrenti(video):
    """Righe di descrizione presenti in molti video (link, sponsor, saluti...)."""
    conta = Counter()
    for v in video:
        righe = {re.sub(r"\s+", " ", r).strip().lower()
                 for r in (v.get("descrizione") or "").splitlines()}
        conta.update(r for r in righe if r)
    soglia = max(5, int(len(video) * 0.15))
    return {r for r, n in conta.items() if n >= soglia}


def pulisci_descrizione(testo, ricorrenti):
    tenute = []
    for r in (testo or "").splitlines():
        norm = re.sub(r"\s+", " ", r).strip().lower()
        if not norm or norm in ricorrenti:
            continue
        r = re.sub(r"https?://\S+", " ", r)   # via i link
        tenute.append(r)
    return "\n".join(tenute)


def classifica(v, ricorrenti):
    titolo = v.get("titolo") or ""
    descr = pulisci_descrizione(v.get("descrizione"), ricorrenti)

    f_tit, d_tit, a_tit = trova(titolo, FORTI), trova(titolo, DEBOLI), trova(titolo, ALTRI)
    f_des, d_des, a_des = trova(descr, FORTI), trova(descr, DEBOLI), trova(descr, ALTRI)

    nutr_desc = len(f_des) + 0.5 * len(d_des)
    altro_desc = len(a_des)

    def elenco(xs):
        return ", ".join(xs[:6])

    if f_tit and not a_tit:
        if altro_desc >= 3 and altro_desc > nutr_desc:
            return ("MISTO", "DA_RIVEDERE",
                    f"titolo di alimentazione ({elenco(f_tit)}) ma la descrizione parla molto "
                    f"anche di altro ({elenco(a_des)})")
        return ("ALIMENTAZIONE", "AUTOMATICA", f"titolo di alimentazione: {elenco(f_tit)}")
    if f_tit and a_tit:
        return ("MISTO", "AUTOMATICA",
                f"titolo con alimentazione ({elenco(f_tit)}) e altro ({elenco(a_tit)})")
    if d_tit:
        cat = "MISTO" if (nutr_desc >= 2 or a_tit) else "ALTRO"
        return (cat, "DA_RIVEDERE",
                f"parole ambigue nel titolo ({elenco(d_tit)}); descrizione: "
                f"{elenco(f_des) or 'nessuna parola forte'}")
    if len(f_des) >= 3 and not a_tit:
        return ("MISTO", "DA_RIVEDERE",
                f"titolo neutro ma descrizione ricca di alimentazione ({elenco(f_des)})")
    if f_des or nutr_desc >= 1:
        return ("ALTRO", "DA_RIVEDERE",
                f"alimentazione citata solo nella descrizione ({elenco(f_des + d_des)})")
    if a_tit or a_des:
        return ("ALTRO", "AUTOMATICA", f"altri temi: {elenco(a_tit or a_des)}")
    return ("ALTRO", "DA_RIVEDERE", "nessuna parola chiave trovata")


def esempi(righe, n):
    """n esempi distribuiti nel tempo (non solo i piu' recenti)."""
    if len(righe) <= n:
        return righe
    passo = len(righe) / n
    return [righe[int(i * passo)] for i in range(n)]


def main():
    prepara_console()
    video = leggi_csv(ELENCO_VIDEO)
    if not video:
        sys.exit("Non trovo dati/elenco_video.csv: lancia prima scripts/01_inventario.py")

    ricorrenti = righe_ricorrenti(video)
    revisione = {r["id"]: r for r in leggi_csv(REVISIONE_MANUALE) if r.get("id")}

    risultati = []
    for v in video:
        cat, stato, motivo = classifica(v, ricorrenti)
        titolo = v.get("titolo") or ""
        descr = pulisci_descrizione(v.get("descrizione"), ricorrenti)
        r = {
            "id": v["id"], "titolo": titolo, "data_pubblicazione": v.get("data_pubblicazione"),
            "durata": v.get("durata"), "categoria": cat, "stato": stato, "motivo": motivo,
            "parole_titolo": ", ".join(trova(titolo, FORTI) + [p + "?" for p in trova(titolo, DEBOLI)]
                                       + ["#" + p for p in trova(titolo, ALTRI)]),
            "parole_descrizione": ", ".join(trova(descr, FORTI) + [p + "?" for p in trova(descr, DEBOLI)]
                                            + ["#" + p for p in trova(descr, ALTRI)]),
            "url": v.get("url"),
        }
        man = revisione.get(v["id"])
        if man and (man.get("categoria") or "").upper() in CATEGORIE:
            r["categoria"] = man["categoria"].upper()
            r["stato"] = "REVISIONATA"
            r["motivo"] = "revisione: " + (man.get("motivo") or "decisione manuale")
        risultati.append(r)

    nutr = [r for r in risultati if r["categoria"] in ("ALIMENTAZIONE", "MISTO")]
    dubbi = [r for r in risultati if r["stato"] == "DA_RIVEDERE"]

    scrivi_csv(CLASSIFICAZIONE, CAMPI, risultati)
    scrivi_csv(VIDEO_NUTRIZIONE, CAMPI, nutr)
    scrivi_csv(DA_RIVEDERE, CAMPI, dubbi)
    if not REVISIONE_MANUALE.exists():
        scrivi_csv(REVISIONE_MANUALE, ["id", "categoria", "motivo"], [])

    conta = Counter(r["categoria"] for r in risultati)
    md = ["# Riepilogo Fase 1 - Inventario e classificazione", "",
          f"- **Video totali** (tab Video, Shorts esclusi): {len(risultati)}",
          f"- **ALIMENTAZIONE**: {conta['ALIMENTAZIONE']}",
          f"- **MISTO**: {conta['MISTO']}",
          f"- **ALTRO**: {conta['ALTRO']}",
          f"- Casi ancora da rivedere: {len(dubbi)}  -  gia' rivisti a mano: "
          f"{sum(r['stato'] == 'REVISIONATA' for r in risultati)}",
          f"- Righe ricorrenti tolte dalle descrizioni: {len(ricorrenti)}", ""]
    for cat in CATEGORIE:
        gruppo = [r for r in risultati if r["categoria"] == cat]
        md += [f"## {cat} - {ESEMPI_PER_CATEGORIA} esempi", "",
               "| Data | Titolo | Motivo |", "|---|---|---|"]
        for r in esempi(gruppo, ESEMPI_PER_CATEGORIA):
            t = r["titolo"].replace("|", "/")
            md.append(f"| {r['data_pubblicazione']} | [{t}]({r['url']}) | {r['motivo'].replace('|', '/')} |")
        md.append("")
    (DATI / "riepilogo_fase1.md").write_text("\n".join(md), encoding="utf-8")

    print("\n=== RIEPILOGO FASE 1 ===")
    print(f"Video totali:   {len(risultati)}")
    print(f"ALIMENTAZIONE:  {conta['ALIMENTAZIONE']}")
    print(f"MISTO:          {conta['MISTO']}")
    print(f"ALTRO:          {conta['ALTRO']}")
    print(f"Da rivedere:    {len(dubbi)}  (vedi dati/da_rivedere.csv)")
    print("\nFile creati: dati/classificazione_completa.csv, dati/video_nutrizione.csv,")
    print("             dati/da_rivedere.csv, dati/riepilogo_fase1.md (con 15 esempi per categoria)")


if __name__ == "__main__":
    main()
