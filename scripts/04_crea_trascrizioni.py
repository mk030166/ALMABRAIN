# -*- coding: utf-8 -*-
"""
FASE 2 - PASSO 2: PULIZIA DEI SOTTOTITOLI E CREAZIONE DELLE TRASCRIZIONI
========================================================================
Legge i file .vtt di sottotitoli_raw/ e crea per ogni video
    trascrizioni/AAAA-MM-GG_<id>.md
con in testa titolo, data, durata, URL, categoria, e poi il testo in
paragrafi leggibili, ognuno con un marcatore di tempo [mm:ss].

Pulizia:
 - elimina i codici di tempo parola-per-parola e la formattazione;
 - elimina le righe ripetute tipiche dei sottotitoli automatici "a rullo";
 - elimina annotazioni come [Musica], [Applausi];
 - unisce il testo in paragrafi di circa 30-60 secondi (vedi config.py).

Si puo' rilanciare quando si vuole: rigenera tutte le trascrizioni.

Uso:  python scripts/04_crea_trascrizioni.py
"""
import html
import os
import re
import sys
from collections import deque

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from comune import (CLASSIFICAZIONE, ELENCO_VIDEO, SOTTOTITOLI, TRASCRIZIONI,  # noqa: E402
                    VIDEO_NUTRIZIONE, leggi_csv, prepara_console)

RX_TEMPO = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})")
RX_TAG = re.compile(r"<[^>]*>")
RX_ANNOTAZIONE = re.compile(r"\[[^\]]{0,40}\]|\([A-Za-zÀ-ÿ ]{0,25}(musica|applausi|risate)[A-Za-zÀ-ÿ ]{0,15}\)",
                            re.IGNORECASE)
FINE_FRASE = (".", "?", "!", "…", '."', '?"', '!"')


def a_secondi(testo):
    m = RX_TEMPO.search(testo)
    if not m:
        return None
    h, mi, s, ms = m.groups()
    return int(h or 0) * 3600 + int(mi) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000


def leggi_vtt(testo):
    """Restituisce una lista di (inizio_secondi, [righe di testo])."""
    testo = testo.replace("\r\n", "\n").replace("\r", "\n").lstrip("﻿")
    blocchi = re.split(r"\n[ \t]*\n", testo)
    cue = []
    for b in blocchi:
        righe = b.split("\n")
        idx = next((i for i, r in enumerate(righe) if "-->" in r), None)
        if idx is None:
            continue  # intestazione WEBVTT, NOTE, STYLE...
        inizio = a_secondi(righe[idx].split("-->")[0])
        if inizio is None:
            continue
        cue.append((inizio, righe[idx + 1:]))
    return cue


def pulisci_riga(r):
    r = RX_TAG.sub("", r)
    r = html.unescape(r).replace(" ", " ")
    r = RX_ANNOTAZIONE.sub(" ", r)
    r = re.sub(r"^\s*(>>|-)\s*", "", r)        # segni di cambio interlocutore
    return re.sub(r"\s+", " ", r).strip()


def frammenti_unici(cue):
    """Toglie le ripetizioni dei sottotitoli 'a rullo'. -> [(secondi, testo)]"""
    risultato = []
    recenti = deque(maxlen=4)
    for inizio, righe in cue:
        for r in righe:
            t = pulisci_riga(r)
            if not t:
                continue
            chiave = t.lower()
            if chiave in recenti:
                continue
            # la riga nuova completa quella precedente (stesso inizio, piu' lunga)
            if risultato and chiave.startswith(risultato[-1][1].lower()) and len(t) > len(risultato[-1][1]):
                risultato[-1] = (risultato[-1][0], t)
                recenti.append(chiave)
                continue
            # la riga nuova e' gia' contenuta nella precedente
            if risultato and risultato[-1][1].lower().endswith(chiave):
                recenti.append(chiave)
                continue
            recenti.append(chiave)
            risultato.append((inizio, t))
    return risultato


def paragrafi(frammenti, minimo=None, massimo=None):
    minimo = minimo or config.PARAGRAFO_MIN
    massimo = massimo or config.PARAGRAFO_MAX
    out, corrente, t0, t_prec = [], [], None, None
    for t, testo in frammenti:
        if corrente:
            trascorso = t - t0
            pausa = t - t_prec
            fine = corrente[-1].endswith(FINE_FRASE)
            if trascorso >= massimo or (trascorso >= minimo and (fine or pausa >= 5)):
                out.append((t0, corrente))
                corrente, t0 = [], None
        if not corrente:
            t0 = t
        corrente.append(testo)
        t_prec = t
    if corrente:
        out.append((t0, corrente))
    risultato, maiuscola = [], True
    for t, parti in out:
        testo = sistema_testo(" ".join(parti), maiuscola)
        maiuscola = testo.endswith(FINE_FRASE)
        risultato.append((t, testo))
    return risultato


def sistema_testo(s, maiuscola=True):
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return (s[:1].upper() + s[1:]) if maiuscola else s


def marcatore(secondi):
    s = int(secondi)
    h, resto = divmod(s, 3600)
    m, s = divmod(resto, 60)
    return f"[{h}:{m:02d}:{s:02d}]" if h else f"[{m:02d}:{s:02d}]"


def virgolette(s):
    return '"' + str(s or "").replace("\\", "\\\\").replace('"', '\\"') + '"'


def crea_md(meta, tipo, paragrafi_testo):
    data = meta.get("data_pubblicazione") or "data-sconosciuta"
    intestazione = [
        "---",
        f"id: {meta['id']}",
        f"titolo: {virgolette(meta.get('titolo'))}",
        f"data: {data}",
        f"durata: {virgolette(meta.get('durata'))}",
        f"url: {meta.get('url') or 'https://www.youtube.com/watch?v=' + meta['id']}",
        f"categoria: {meta.get('categoria', '')}",
        f"sottotitoli: {tipo}",
        "---",
        "",
        f"# {meta.get('titolo') or meta['id']}",
        "",
        f"- **Data:** {data}",
        f"- **Durata:** {meta.get('durata', '')}",
        f"- **URL:** {meta.get('url', '')}",
        f"- **Categoria:** {meta.get('categoria', '')}",
        f"- **Sottotitoli:** {tipo}",
        "",
        "## Trascrizione",
        "",
    ]
    corpo = [f"{marcatore(t)} {testo}\n" for t, testo in paragrafi_testo]
    return "\n".join(intestazione) + "\n" + "\n".join(corpo)


def main():
    prepara_console()
    confermati = {r["id"]: r for r in leggi_csv(VIDEO_NUTRIZIONE) if r.get("id")}
    tutti = {r["id"]: r for r in leggi_csv(CLASSIFICAZIONE) if r.get("id")}
    elenco = {r["id"]: r for r in leggi_csv(ELENCO_VIDEO) if r.get("id")}
    TRASCRIZIONI.mkdir(parents=True, exist_ok=True)

    file_vtt = sorted(SOTTOTITOLI.glob("*.vtt"))
    if not file_vtt:
        sys.exit("Nessun file in sottotitoli_raw/: lancia prima scripts/03_scarica_sottotitoli.py")

    fatti, vuoti, saltati = 0, [], 0
    for p in file_vtt:
        vid, tipo = p.name.split(".")[0], p.name.split(".")[1]
        if vid not in confermati:
            saltati += 1   # non (piu') tra i video confermati
            continue
        meta = {**elenco.get(vid, {}), **tutti.get(vid, {}), **confermati[vid]}
        meta["id"] = vid
        testo = p.read_text(encoding="utf-8", errors="replace")
        par = paragrafi(frammenti_unici(leggi_vtt(testo)))
        if not par:
            vuoti.append(vid)
            continue
        nome = f"{meta.get('data_pubblicazione') or 'senza-data'}_{vid}.md"
        # elimina eventuali versioni precedenti con data diversa
        for vecchio in TRASCRIZIONI.glob(f"*_{vid}.md"):
            if vecchio.name != nome:
                vecchio.unlink()
        (TRASCRIZIONI / nome).write_text(crea_md(meta, tipo, par), encoding="utf-8")
        fatti += 1

    print(f"Trascrizioni create/aggiornate: {fatti}")
    if vuoti:
        print(f"Sottotitoli vuoti dopo la pulizia ({len(vuoti)}): {', '.join(vuoti)}")
    if saltati:
        print(f"File ignorati perche' non piu' tra i video confermati: {saltati}")
    print("Prossimo passo:  python scripts/05_report.py")


if __name__ == "__main__":
    main()
