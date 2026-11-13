# -*- coding: utf-8 -*-
"""Funzioni comuni a tutti gli script (non va lanciato direttamente)."""
import csv
import random
import sys
import time
from pathlib import Path

import config

RADICE = Path(__file__).resolve().parent.parent
DATI = RADICE / "dati"
SOTTOTITOLI = RADICE / "sottotitoli_raw"
TRASCRIZIONI = RADICE / "trascrizioni"

# File principali
ELENCO_VIDEO = DATI / "elenco_video.csv"
CACHE_METADATI = DATI / "metadati_cache.jsonl"
CLASSIFICAZIONE = DATI / "classificazione_completa.csv"
VIDEO_NUTRIZIONE = DATI / "video_nutrizione.csv"
DA_RIVEDERE = DATI / "da_rivedere.csv"
REVISIONE_MANUALE = DATI / "revisione_manuale.csv"
TEMATICHE = DATI / "tematiche.csv"
SENZA_SOTTOTITOLI = DATI / "senza_sottotitoli.csv"
ERRORI = DATI / "errori.csv"
REPORT = RADICE / "report.md"


def prepara_console():
    """Evita errori con le lettere accentate nel terminale di Windows."""
    for flusso in (sys.stdout, sys.stderr):
        try:
            flusso.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def scrivi_csv(percorso, campi, righe):
    """CSV con separatore ; e UTF-8 con BOM: si apre bene in Excel."""
    percorso = Path(percorso)
    percorso.parent.mkdir(parents=True, exist_ok=True)
    temporaneo = percorso.with_suffix(".tmp")
    with open(temporaneo, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campi, delimiter=";", extrasaction="ignore")
        w.writeheader()
        for r in righe:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in campi})
    try:
        temporaneo.replace(percorso)
    except PermissionError:
        temporaneo.unlink(missing_ok=True)
        sys.exit(f"\nERRORE: non riesco a scrivere {percorso.name}. "
                 "E' aperto in Excel? Chiudilo e rilancia lo script.")


def leggi_csv(percorso):
    """Legge un CSV anche se e' stato risalvato da Excel (; o , - UTF-8 o Windows)."""
    percorso = Path(percorso)
    if not percorso.exists():
        return []
    grezzo = percorso.read_bytes()
    for codifica in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            testo = grezzo.decode(codifica)
            break
        except UnicodeDecodeError:
            continue
    prima_riga = testo.split("\n", 1)[0]
    separatore = ";" if prima_riga.count(";") >= prima_riga.count(",") else ","
    righe = list(csv.DictReader(testo.splitlines(keepends=True), delimiter=separatore))
    # ripulisce eventuali spazi nei nomi delle colonne
    return [{(k or "").strip(): (v or "").strip() if isinstance(v, str) else v
             for k, v in r.items()} for r in righe]


CAMPI_TEMATICHE = ("area_principale", "aree_secondarie", "argomenti", "pubblico", "formato")


def video_da_trascrivere():
    """Elenco dei video per la Fase 2, con tutti i dati disponibili (anche le tematiche).
    Ordine: prima ALIMENTAZIONE e MISTO, poi gli altri; in ogni gruppo dal piu' recente."""
    if config.VIDEO_DA_TRASCRIVERE == "alimentazione":
        base = leggi_csv(VIDEO_NUTRIZIONE)
    else:
        base = leggi_csv(CLASSIFICAZIONE)
    tematiche = {r["id"]: r for r in leggi_csv(TEMATICHE) if r.get("id")}
    elenco = []
    for r in base:
        if not r.get("id"):
            continue
        t = tematiche.get(r["id"], {})
        elenco.append({**r, **{k: t.get(k, "") for k in CAMPI_TEMATICHE}})
    elenco.sort(key=lambda m: m.get("data_pubblicazione") or "", reverse=True)
    elenco.sort(key=lambda m: 0 if m.get("categoria") in ("ALIMENTAZIONE", "MISTO") else 1)
    return elenco


def formatta_durata(secondi):
    try:
        s = int(round(float(secondi)))
    except (TypeError, ValueError):
        return ""
    h, resto = divmod(s, 3600)
    m, s = divmod(resto, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def formatta_data(aaaammgg):
    d = str(aaaammgg or "")
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 and d.isdigit() else d


def pausa(intervallo):
    time.sleep(random.uniform(*intervallo))


def opzioni_ytdlp(**extra):
    """Opzioni di base per yt-dlp: niente download di video, output silenzioso."""
    opz = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "ignore_no_formats_error": True,
        "noprogress": True,
        "extractor_args": {"youtube": {"lang": ["it"]}},
    }
    if config.BROWSER_COOKIE:
        opz["cookiesfrombrowser"] = (config.BROWSER_COOKIE,)
    opz.update(extra)
    return opz


SEGNALI_BLOCCO = ("429", "too many requests", "sign in to confirm", "rate-limit",
                  "rate limit", "confirm you're not a bot", "confirm you’re not a bot",
                  "temporarily blocked", "unusual traffic")


def e_un_blocco(errore):
    msg = str(errore).lower()
    return any(s in msg for s in SEGNALI_BLOCCO)


class Bloccato(Exception):
    """YouTube continua a bloccarci anche dopo tutte le attese."""


def con_pazienza(funzione, descrizione=""):
    """Esegue funzione(); se YouTube ci blocca aspetta sempre di piu' e riprova."""
    for tentativo, attesa in enumerate([0] + list(config.ATTESE_SE_BLOCCATI)):
        if attesa:
            print(f"   YouTube ci sta rallentando ({descrizione}). "
                  f"Aspetto {attesa // 60} min {attesa % 60} s e riprovo "
                  f"(tentativo {tentativo}/{len(config.ATTESE_SE_BLOCCATI)})...", flush=True)
            time.sleep(attesa)
        try:
            return funzione()
        except Exception as e:  # noqa: BLE001
            if not e_un_blocco(e):
                raise
            ultimo = e
    raise Bloccato(str(ultimo))
