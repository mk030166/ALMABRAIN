# -*- coding: utf-8 -*-
"""
FASE 2 - PASSO 3: REPORT FINALE
===============================
Crea report.md con: video elaborati, video senza sottotitoli, errori,
parole totali trascritte e stima dei token per la Fase 3 (analisi con Claude).

Uso:  python scripts/05_report.py
"""
import os
import re
import sys
from collections import Counter
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from comune import (ERRORI, REPORT, SENZA_SOTTOTITOLI, TRASCRIZIONI, VIDEO_NUTRIZIONE,  # noqa: E402
                    leggi_csv, prepara_console)

RX_MARCATORE = re.compile(r"^\[\d+(?::\d{2}){1,2}\]\s*", re.MULTILINE)


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


def main():
    prepara_console()
    confermati = leggi_csv(VIDEO_NUTRIZIONE)
    senza = leggi_csv(SENZA_SOTTOTITOLI)
    errori = [e for e in leggi_csv(ERRORI)]
    trascrizioni = sorted(TRASCRIZIONI.glob("*.md"))

    dati = []
    for p in trascrizioni:
        meta, parole = leggi_trascrizione(p)
        dati.append({"file": p.name, "parole": parole, **meta})

    tot_parole = sum(d["parole"] for d in dati)
    per_cat = Counter(d.get("categoria", "?") for d in dati)
    parole_cat = Counter()
    for d in dati:
        parole_cat[d.get("categoria", "?")] += d["parole"]
    per_tipo = Counter(d.get("sottotitoli", "?") for d in dati)

    tok = tot_parole * config.TOKEN_PER_PAROLA
    tok_min, tok_max = tot_parole * 1.3, tot_parole * 1.7
    # In un'analisi servono anche istruzioni e risposte: +30% circa
    tok_fase3 = tok * 1.3
    media = tot_parole / len(dati) if dati else 0

    elaborati_id = {d.get("id") for d in dati}
    mancanti = [v for v in confermati
                if v["id"] not in elaborati_id and v["id"] not in {s["id"] for s in senza}
                and v["id"] not in {e.get("id") for e in errori}]

    r = [f"# Report base di conoscenza AlmaPhysio - Alimentazione",
         "",
         f"_Generato il {datetime.now():%Y-%m-%d %H:%M}_",
         "",
         "## Riepilogo",
         "",
         "| Voce | Valore |",
         "|---|---|",
         f"| Video confermati (ALIMENTAZIONE + MISTO) | {len(confermati)} |",
         f"| Video elaborati (trascrizione creata) | {len(dati)} |",
         f"| - di cui ALIMENTAZIONE | {per_cat.get('ALIMENTAZIONE', 0)} |",
         f"| - di cui MISTO | {per_cat.get('MISTO', 0)} |",
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
         f"- Testo delle trascrizioni: circa **{numero(tok)} token** "
         f"(intervallo {numero(tok_min)} - {numero(tok_max)}; per l'italiano si stimano "
         f"~{config.TOKEN_PER_PAROLA} token per parola).",
         f"- ALIMENTAZIONE: ~{numero(parole_cat.get('ALIMENTAZIONE', 0) * config.TOKEN_PER_PAROLA)} token; "
         f"MISTO: ~{numero(parole_cat.get('MISTO', 0) * config.TOKEN_PER_PAROLA)} token.",
         f"- Includendo istruzioni e risposte dell'analisi (+30% circa): **~{numero(tok_fase3)} token** "
         "se ogni trascrizione viene letta una sola volta.",
         f"- Un video medio vale circa {numero(media * config.TOKEN_PER_PAROLA)} token.",
         "",
         "_Sono stime: il conteggio esatto dipende dal modello usato e da come verra' impostata l'analisi._",
         ""]

    r += ["## Video senza sottotitoli", ""]
    if senza:
        r += ["| Data | Titolo | Motivo |", "|---|---|---|"]
        r += [f"| {s.get('data_pubblicazione', '')} | [{(s.get('titolo') or '').replace('|', '/')}]"
              f"({s.get('url', '')}) | {s.get('motivo', '')} |" for s in senza]
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
              "Rilancia `scripts/03_scarica_sottotitoli.py` e poi `04` e `05`.", ""]
        r += [f"- {v.get('data_pubblicazione', '')} - {v.get('titolo', '')} ({v['id']})" for v in mancanti]
        r.append("")

    r += ["## Trascrizioni (dalla piu' lunga)", "", "| File | Categoria | Parole |", "|---|---|---|"]
    for d in sorted(dati, key=lambda x: -x["parole"]):
        r.append(f"| [{d['file']}](trascrizioni/{d['file']}) | {d.get('categoria', '')} | {numero(d['parole'])} |")
    r.append("")

    REPORT.write_text("\n".join(r), encoding="utf-8")
    print(f"Report creato: report.md")
    print(f"Video elaborati: {len(dati)} - senza sottotitoli: {len(senza)} - errori: {len(errori)}")
    print(f"Parole totali: {numero(tot_parole)} - token stimati: ~{numero(tok)} "
          f"(~{numero(tok_fase3)} con istruzioni e risposte)")


if __name__ == "__main__":
    main()
