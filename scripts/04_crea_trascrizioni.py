# -*- coding: utf-8 -*-
"""
FASE 2 - PASSO 2: PULIZIA DEI SOTTOTITOLI E CREAZIONE DELLE TRASCRIZIONI
========================================================================
Legge i file .vtt di sottotitoli_raw/ e crea per ogni video
    trascrizioni/AAAA-MM-GG_<id>.md
con in testa titolo, data, durata, URL, categoria e tematiche, e poi il testo in
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
from comune import (ELENCO_VIDEO, SOTTOTITOLI, TRASCRIZIONI, leggi_csv,  # noqa: E402
                    prepara_console, video_da_trascrivere)

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


def ha_punteggiatura(frammenti):
    testo = " ".join(t for _, t in frammenti)
    parole = max(1, len(testo.split()))
    return testo.count(".") + testo.count("?") > parole / 60   # almeno ~1 frase ogni 60 parole


RX_FINE_INTERNA = re.compile(r'[.?!…]["»”]?\s+(?=["«“]?[A-ZÀ-Ý0-9])')


def paragrafi(frammenti, minimo=None, massimo=None):
    minimo = minimo or config.PARAGRAFO_MIN
    massimo = massimo or config.PARAGRAFO_MAX
    # con la punteggiatura si aspetta la fine della frase (entro la tolleranza)
    punt = ha_punteggiatura(frammenti)
    limite = massimo + getattr(config, "PARAGRAFO_TOLLERANZA", 0) if punt else massimo
    out, corrente, t0, t_prec = [], [], None, None

    def chiudi():
        nonlocal corrente, t0
        if corrente:
            out.append((t0, corrente))
        corrente, t0 = [], None

    for t, testo in frammenti:
        if corrente:
            trascorso = t - t0
            pausa = t - t_prec
            fine = corrente[-1].endswith(FINE_FRASE)
            if trascorso >= limite or (trascorso >= minimo and (fine or pausa >= 5)):
                chiudi()
            elif punt and trascorso >= minimo:
                # la frase finisce dentro questo pezzo: chiudo li' e il resto va a capo
                mm = RX_FINE_INTERNA.search(testo)
                if mm:
                    corrente.append(testo[:mm.end()].strip())
                    chiudi()
                    testo = testo[mm.end():].strip()
        t_prec = t
        if not testo:
            continue
        if not corrente:
            t0 = t
        corrente.append(testo)
    chiudi()
    risultato, maiuscola = [], True
    for t, parti in out:
        testo = sistema_testo(" ".join(parti), maiuscola)
        maiuscola = testo.endswith(FINE_FRASE)
        risultato.append((t, testo))
    return risultato


CORREZIONI = [(re.compile(r"(?<![\w])" + re.escape(k) + r"(?![\w])", re.IGNORECASE), v)
              for k, v in getattr(config, "CORREZIONI", {}).items()]


def sistema_testo(s, maiuscola=True):
    s = re.sub(r"\s+", " ", s).strip()
    for rx, giusta in CORREZIONI:
        s = rx.sub(giusta, s)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return (s[:1].upper() + s[1:]) if maiuscola else s


def marcatore(secondi):
    s = int(secondi)
    h, resto = divmod(s, 3600)
    m, s = divmod(resto, 60)
    return f"[{h}:{m:02d}:{s:02d}]" if h else f"[{m:02d}:{s:02d}]"


def virgolette(s):
    return '"' + str(s or "").replace("\\", "\\\\").replace('"', '\\"') + '"'


def voci(s):
    return [x.strip() for x in str(s or "").split("|") if x.strip()]


def lista_yaml(s):
    return "[" + ", ".join(virgolette(x) for x in voci(s)) + "]"


def separa(s):
    return ", ".join(voci(s)) or "-"


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
        f"area_principale: {virgolette(meta.get('area_principale'))}",
        f"aree_secondarie: {lista_yaml(meta.get('aree_secondarie'))}",
        f"argomenti: {lista_yaml(meta.get('argomenti'))}",
        f"pubblico: {lista_yaml(meta.get('pubblico'))}",
        f"formato: {lista_yaml(meta.get('formato'))}",
        f"sottotitoli: {tipo}",
        "---",
        "",
        f"# {meta.get('titolo') or meta['id']}",
        "",
        f"- **Data:** {data}",
        f"- **Durata:** {meta.get('durata', '')}",
        f"- **URL:** {meta.get('url', '')}",
        f"- **Categoria alimentazione:** {meta.get('categoria', '')}",
        f"- **Area principale:** {meta.get('area_principale', '')}",
        f"- **Aree secondarie:** {separa(meta.get('aree_secondarie'))}",
        f"- **Argomenti:** {separa(meta.get('argomenti'))}",
        f"- **Pubblico:** {separa(meta.get('pubblico'))}",
        f"- **Formato:** {separa(meta.get('formato'))}",
        f"- **Sottotitoli:** {tipo}",
        "",
        "## Trascrizione",
        "",
    ]
    corpo = [f"{marcatore(t)} {testo}\n" for t, testo in paragrafi_testo]
    return "\n".join(intestazione) + "\n" + "\n".join(corpo)


# gli automatici sostituiscono i manuali solo se hanno almeno questa quota di parole in piu'
MARGINE_AUTOMATICI = 1.15


def scegli_versione(file_per_tipo):
    """Restituisce (etichetta del tipo, paragrafi) scegliendo la versione piu' completa."""
    risultati = {}
    for tipo, p in file_per_tipo.items():
        testo = p.read_text(encoding="utf-8", errors="replace")
        par = paragrafi(frammenti_unici(leggi_vtt(testo)))
        risultati[tipo] = (par, sum(len(t.split()) for _, t in par))
    if "manuali" in risultati and "automatici" in risultati:
        (par_m, n_m), (par_a, n_a) = risultati["manuali"], risultati["automatici"]
        if n_a > n_m * MARGINE_AUTOMATICI:
            return "automatici (i manuali erano incompleti)", par_a
        return "manuali", par_m
    tipo = next(iter(risultati))
    return tipo, risultati[tipo][0]


def main():
    prepara_console()
    confermati = {r["id"]: r for r in video_da_trascrivere()}
    elenco = {r["id"]: r for r in leggi_csv(ELENCO_VIDEO) if r.get("id")}
    TRASCRIZIONI.mkdir(parents=True, exist_ok=True)

    file_vtt = sorted(SOTTOTITOLI.glob("*.vtt"))
    if not file_vtt:
        sys.exit("Nessun file in sottotitoli_raw/: lancia prima scripts/03_scarica_sottotitoli.py")

    # per ogni video possono esserci due versioni (manuali e automatici): raggruppo
    versioni = {}
    for p in file_vtt:
        vid, tipo = p.name.split(".")[0], p.name.split(".")[1]
        versioni.setdefault(vid, {})[tipo] = p

    fatti, vuoti, saltati, integrati = 0, [], 0, 0
    for vid, file_per_tipo in sorted(versioni.items()):
        if vid not in confermati:
            saltati += 1   # non (piu') tra i video da trascrivere
            continue
        meta = {**elenco.get(vid, {}), **confermati[vid]}
        meta["id"] = vid
        tipo, par = scegli_versione(file_per_tipo)
        if tipo.startswith("automatici ("):
            integrati += 1
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
    if integrati:
        print(f"Di cui con sottotitoli automatici al posto dei manuali incompleti: {integrati}")
    if vuoti:
        print(f"Sottotitoli vuoti dopo la pulizia ({len(vuoti)}): {', '.join(vuoti)}")
    if saltati:
        print(f"File ignorati perche' non piu' tra i video da trascrivere: {saltati}")
    print("Prossimo passo:  python scripts/05_report.py")


if __name__ == "__main__":
    main()
