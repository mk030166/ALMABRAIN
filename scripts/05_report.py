# -*- coding: utf-8 -*-
"""
FASE 2 - PASSO 3: REPORT FINALE
===============================
Crea report.md con: video elaborati, video senza sottotitoli, errori,
parole totali trascritte e stima dei token per la Fase 3 (analisi con Claude),
anche suddivisi per area tematica e per categoria di alimentazione.

Uso:  python scripts/05_report.py
"""
import os
import re
import sys
from collections import Counter
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from comune import (ERRORI, REPORT, SENZA_SOTTOTITOLI, TRASCRIZIONI, leggi_csv,  # noqa: E402
                    prepara_console, video_da_trascrivere)

RX_MARCATORE = re.compile(r"^\[\d+(?::\d{2}){1,2}\]\s*", re.MULTILINE)
ORDINE_CAT = ["ALIMENTAZIONE", "MISTO", "ALTRO"]


def leggi_trascrizione(p):
    testo = p.read_text(encoding="utf-8")
    meta = {}
    m = re.match(r"---\n(.*?)\n---\n", testo, re.DOTALL)
    if m:
        for riga in m.group(1).splitlines():
            if ":" in riga:
                k, v = riga.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
    corpo = testo.split("## Trascrizione", 1)[-1]
    corpo = RX_MARCATORE.sub("", corpo)
    parole = len(re.findall(r"\w+(?:['’]\w+)?", corpo))
    return meta, parole


def numero(n):
    return f"{n:,.0f}".replace(",", ".")


def token(parole):
    return parole * config.TOKEN_PER_PAROLA


def tabella(titolo_col, conteggi, parole, ordine=None):
    chiavi = ordine or [k for k, _ in conteggi.most_common()]
    righe = [f"| {titolo_col} | Video | Parole | Token stimati |", "|---|---|---|---|"]
    for k in chiavi:
        if conteggi.get(k):
            righe.append(f"| {k} | {conteggi[k]} | {numero(parole[k])} | ~{numero(token(parole[k]))} |")
    return righe


def main():
    prepara_console()
    da_trascrivere = video_da_trascrivere()
    senza = leggi_csv(SENZA_SOTTOTITOLI)
    errori = leggi_csv(ERRORI)
    trascrizioni = sorted(TRASCRIZIONI.glob("*.md"))

    dati = []
    for p in trascrizioni:
        meta, parole = leggi_trascrizione(p)
        dati.append({"file": p.name, "parole": parole, **meta})

    tot_parole = sum(d["parole"] for d in dati)
    per_cat, parole_cat = Counter(), Counter()
    per_area, parole_area = Counter(), Counter()
    for d in dati:
        c = d.get("categoria") or "?"
        a = d.get("area_principale") or "(senza area)"
        per_cat[c] += 1
        parole_cat[c] += d["parole"]
        per_area[a] += 1
        parole_area[a] += d["parole"]
    per_tipo = Counter(d.get("sottotitoli", "?") for d in dati)

    tok = token(tot_parole)
    tok_min, tok_max = tot_parole * 1.3, tot_parole * 1.7
    tok_fase3 = tok * 1.3      # istruzioni e risposte dell'analisi: +30% circa
    media = tot_parole / len(dati) if dati else 0

    fatti = {d.get("id") for d in dati}
    senza_id = {s.get("id") for s in senza}
    errori_id = {e.get("id") for e in errori}
    mancanti = [v for v in da_trascrivere
                if v["id"] not in fatti and v["id"] not in senza_id and v["id"] not in errori_id]

    r = ["# Report base di conoscenza AlmaPhysio",
         "",
         f"_Generato il {datetime.now():%Y-%m-%d %H:%M}_",
         "",
         "## Riepilogo",
         "",
         "| Voce | Valore |",
         "|---|---|",
         f"| Video da trascrivere | {len(da_trascrivere)} |",
         f"| Video elaborati (trascrizione creata) | {len(dati)} |",
         f"| - con sottotitoli manuali | {per_tipo.get('manuali', 0)} |",
         f"| - con sottotitoli automatici | {per_tipo.get('automatici', 0)} |",
         f"| Video senza sottotitoli italiani | {len(senza)} |",
         f"| Errori registrati | {len(errori)} |",
         f"| Video non ancora elaborati | {len(mancanti)} |",
         f"| **Parole totali trascritte** | **{numero(tot_parole)}** |",
         f"| Parole medie per video | {numero(media)} |",
         "",
         "## Stima dei token per la Fase 3 (analisi con Claude)",
         "",
         f"- Testo di tutte le trascrizioni: circa **{numero(tok)} token** "
         f"(intervallo {numero(tok_min)} - {numero(tok_max)}; per l'italiano si stimano "
         f"~{config.TOKEN_PER_PAROLA} token per parola).",
         f"- Includendo istruzioni e risposte dell'analisi (+30% circa): **~{numero(tok_fase3)} token** "
         "se ogni trascrizione viene letta una sola volta.",
         f"- Un video medio vale circa {numero(token(media))} token.",
         "",
         "_Sono stime: il conteggio esatto dipende dal modello usato e da come verra' impostata l'analisi._",
         "",
         "### Per categoria di alimentazione",
         ""]
    r += tabella("Categoria", per_cat, parole_cat, ORDINE_CAT + [k for k in per_cat if k not in ORDINE_CAT])
    r += ["", "### Per area tematica principale", ""]
    r += tabella("Area", per_area, parole_area)
    r.append("")

    r += ["## Video senza sottotitoli", ""]
    if senza:
        r += ["| Data | Titolo | Area | Motivo |", "|---|---|---|---|"]
        r += [f"| {s.get('data_pubblicazione', '')} | [{(s.get('titolo') or '').replace('|', '/')}]"
              f"({s.get('url', '')}) | {s.get('area_principale', '')} | {s.get('motivo', '')} |" for s in senza]
        r += ["", "Elenco completo in `dati/senza_sottotitoli.csv` (per un'eventuale trascrizione con Whisper).", ""]
    else:
        r += ["Nessuno.", ""]

    r += ["## Errori", ""]
    if errori:
        r += ["| Fase | Id | Titolo | Errore |", "|---|---|---|---|"]
        r += [f"| {e.get('fase', '')} | {e.get('id', '')} | {(e.get('titolo') or '').replace('|', '/')} | "
              f"{(e.get('errore') or '')[:200].replace('|', '/')} |" for e in errori]
        r += ["", "Per riprovare basta rilanciare `scripts/03_scarica_sottotitoli.py`.", ""]
    else:
        r += ["Nessuno.", ""]

    if mancanti:
        r += ["## Video non ancora elaborati", "",
              f"Sono {len(mancanti)}. Rilancia `scripts/03_scarica_sottotitoli.py` e poi `04` e `05`.", ""]
        r += [f"- {v.get('data_pubblicazione', '')} - {v.get('titolo', '')} ({v['id']})" for v in mancanti[:300]]
        if len(mancanti) > 300:
            r.append(f"- ... e altri {len(mancanti) - 300}")
        r.append("")

    r += ["## Trascrizioni (dalla piu' lunga)", "",
          "| File | Categoria | Area principale | Parole |", "|---|---|---|---|"]
    for d in sorted(dati, key=lambda x: -x["parole"]):
        r.append(f"| [{d['file']}](trascrizioni/{d['file']}) | {d.get('categoria', '')} | "
                 f"{d.get('area_principale', '')} | {numero(d['parole'])} |")
    r.append("")

    REPORT.write_text("\n".join(r), encoding="utf-8")
    print("Report creato: report.md")
    print(f"Video elaborati: {len(dati)} su {len(da_trascrivere)} - senza sottotitoli: {len(senza)} "
          f"- errori: {len(errori)} - mancanti: {len(mancanti)}")
    print(f"Parole totali: {numero(tot_parole)} - token stimati: ~{numero(tok)} "
          f"(~{numero(tok_fase3)} con istruzioni e risposte)")


if __name__ == "__main__":
    main()
