# -*- coding: utf-8 -*-
"""
FASE 1 - PASSO 1: INVENTARIO DEI VIDEO DEL CANALE
=================================================
Scarica (senza scaricare i video!) l'elenco dei video della tab "Video"
del canale - Shorts esclusi - con id, titolo, data, durata, descrizione, URL.

Risultato: dati/elenco_video.csv  (separatore ; - UTF-8 con BOM per Excel)

E' rilanciabile: i dettagli gia' letti restano in dati/metadati_cache.jsonl
e vengono richiesti a YouTube solo i video nuovi.

Uso:
    python scripts/01_inventario.py               (tutto il canale)
    python scripts/01_inventario.py --limite 10   (prova con 10 video)
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import yt_dlp  # noqa: E402

import config  # noqa: E402
from comune import (CACHE_METADATI, ELENCO_VIDEO, ERRORI, Bloccato, con_pazienza,  # noqa: E402
                    formatta_data, formatta_durata, leggi_csv, opzioni_ytdlp, pausa,
                    prepara_console, scrivi_csv)

CAMPI_ELENCO = ["id", "titolo", "data_pubblicazione", "durata", "durata_secondi",
                "url", "sottotitoli_it", "descrizione"]


def elenco_rapido():
    """Elenco 'piatto' della tab Video (e facoltativamente Live)."""
    tab = ["/videos"] + (["/streams"] if config.INCLUDI_DIRETTE else [])
    trovati, visti = [], set()
    with yt_dlp.YoutubeDL(opzioni_ytdlp(extract_flat="in_playlist")) as ydl:
        for t in tab:
            print(f"Leggo l'elenco della tab {t} ...", flush=True)
            info = con_pazienza(lambda: ydl.extract_info(config.CANALE_URL + t, download=False),
                                "elenco video")
            for e in info.get("entries") or []:
                vid = e.get("id")
                if vid and vid not in visti:
                    visti.add(vid)
                    trovati.append(e)
    return trovati


def tracce_italiane(info):
    """Restituisce (lingue sottotitoli manuali 'it', True/False auto in italiano)."""
    manuali = [k for k in (info.get("subtitles") or {}) if k.lower().startswith("it")]
    auto = info.get("automatic_captions") or {}
    origini = [k for k in auto if k.endswith("-orig")]
    if origini:
        auto_it = any(k.lower().startswith("it") for k in origini)
    else:
        auto_it = "it" in auto
    return manuali, auto_it


def dettagli_video(ydl, vid):
    info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
    manuali, auto_it = tracce_italiane(info)
    return {
        "id": vid,
        "titolo": info.get("title"),
        "upload_date": info.get("upload_date"),
        "durata_secondi": info.get("duration"),
        "url": info.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}",
        "descrizione": info.get("description") or "",
        "live_status": info.get("live_status"),
        "lingua": info.get("language"),
        "sub_manuali_it": manuali,
        "sub_auto_it": auto_it,
    }


def carica_cache():
    cache = {}
    if CACHE_METADATI.exists():
        with open(CACHE_METADATI, encoding="utf-8") as f:
            for r in f:
                r = r.strip()
                if r:
                    try:
                        d = json.loads(r)
                        cache[d["id"]] = d
                    except (json.JSONDecodeError, KeyError):
                        pass
    return cache


def descrivi_sottotitoli(d):
    if d.get("sub_manuali_it"):
        return "manuali"
    if d.get("sub_auto_it"):
        return "automatici"
    return "nessuno"


def main():
    prepara_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limite", type=int, default=0, help="elabora solo i primi N video (per prova)")
    args = ap.parse_args()

    entries = elenco_rapido()
    if args.limite:
        entries = entries[: args.limite]
    print(f"Video trovati nella tab: {len(entries)}\n")

    cache = carica_cache()
    nuovi = [e for e in entries if e["id"] not in cache]
    print(f"Dettagli gia' in memoria: {len(entries) - len(nuovi)}  -  da leggere ora: {len(nuovi)}")
    if nuovi:
        stima_min = len(nuovi) * (sum(config.PAUSA_METADATI) / 2 + 2) / 60
        print(f"Tempo stimato: circa {stima_min:.0f} minuti. Puoi interrompere con Ctrl+C "
              "e rilanciare: riprende da dove era rimasto.\n")

    errori = leggi_csv(ERRORI)
    CACHE_METADATI.parent.mkdir(parents=True, exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(opzioni_ytdlp()) as ydl, open(CACHE_METADATI, "a", encoding="utf-8") as fc:
            for i, e in enumerate(nuovi, 1):
                vid = e["id"]
                print(f"[{i}/{len(nuovi)}] {vid}  {(e.get('title') or '')[:70]}", flush=True)
                try:
                    d = con_pazienza(lambda: dettagli_video(ydl, vid), "dettagli video")
                except Bloccato:
                    raise
                except Exception as err:  # noqa: BLE001
                    print(f"   ERRORE: {str(err)[:200]}")
                    errori.append({"fase": "inventario", "id": vid, "titolo": e.get("title"),
                                   "errore": str(err)[:500]})
                    # tengo almeno i dati dell'elenco rapido
                    d = {"id": vid, "titolo": e.get("title"), "upload_date": None,
                         "durata_secondi": e.get("duration"),
                         "url": f"https://www.youtube.com/watch?v={vid}",
                         "descrizione": e.get("description") or "", "incompleto": True}
                    cache[vid] = d
                    continue
                cache[vid] = d
                fc.write(json.dumps(d, ensure_ascii=False) + "\n")
                fc.flush()
                if i < len(nuovi):
                    pausa(config.PAUSA_METADATI)
    except Bloccato:
        print("\nYouTube continua a bloccare le richieste. Salvo quanto fatto finora: "
              "rilancia lo script tra un'ora circa e riprendera' da qui.")
    except KeyboardInterrupt:
        print("\nInterrotto. Salvo quanto fatto finora.")

    righe = []
    for e in entries:
        d = cache.get(e["id"])
        if not d:
            continue
        righe.append({
            "id": d["id"],
            "titolo": d.get("titolo") or e.get("title"),
            "data_pubblicazione": formatta_data(d.get("upload_date")),
            "durata": formatta_durata(d.get("durata_secondi") or e.get("duration")),
            "durata_secondi": d.get("durata_secondi") or e.get("duration") or "",
            "url": d.get("url"),
            "sottotitoli_it": "?" if d.get("incompleto") else descrivi_sottotitoli(d),
            "descrizione": d.get("descrizione", ""),
        })
    righe.sort(key=lambda r: r["data_pubblicazione"] or "", reverse=True)
    scrivi_csv(ELENCO_VIDEO, CAMPI_ELENCO, righe)
    if errori:
        scrivi_csv(ERRORI, ["fase", "id", "titolo", "errore"], errori)

    mancanti = len(entries) - len(righe)
    print(f"\nFatto. Salvati {len(righe)} video in {ELENCO_VIDEO.relative_to(ELENCO_VIDEO.parent.parent)}")
    if mancanti:
        print(f"Mancano ancora i dettagli di {mancanti} video: rilancia lo script per completarli.")
    print("Prossimo passo:  python scripts/02_classifica.py")


if __name__ == "__main__":
    main()
