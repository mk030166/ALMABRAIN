# -*- coding: utf-8 -*-
"""
FASE 2 - PASSO 1: DOWNLOAD DEI SOTTOTITOLI
==========================================
Per ogni video di dati/video_nutrizione.csv scarica i sottotitoli in italiano
(manuali se esistono, altrimenti automatici) in formato .vtt nella cartella
sottotitoli_raw/. I file si chiamano  <id>.manuali.vtt  oppure  <id>.automatici.vtt

- Salta i video gia' scaricati: si puo' interrompere (Ctrl+C) e rilanciare.
- Pausa di qualche secondo tra un video e l'altro (vedi config.py).
- Se YouTube blocca, aspetta sempre di piu'; se insiste, si ferma e salva.
- I video senza sottotitoli italiani vanno in dati/senza_sottotitoli.csv
  (non vengono ricontrollati ai lanci successivi, salvo --ricontrolla).

Per escludere un video basta cancellarne la riga da dati/video_nutrizione.csv.

Uso:
    python scripts/03_scarica_sottotitoli.py
    python scripts/03_scarica_sottotitoli.py --limite 5      (prova con 5 video)
    python scripts/03_scarica_sottotitoli.py --ricontrolla   (riprova i "senza sottotitoli")
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import yt_dlp  # noqa: E402

import config  # noqa: E402
from comune import (ERRORI, SENZA_SOTTOTITOLI, SOTTOTITOLI, VIDEO_NUTRIZIONE, Bloccato,  # noqa: E402
                    con_pazienza, leggi_csv, opzioni_ytdlp, pausa, prepara_console, scrivi_csv)

CAMPI_SENZA = ["id", "titolo", "data_pubblicazione", "durata", "categoria", "url", "motivo"]
CAMPI_ERRORI = ["fase", "id", "titolo", "errore"]


def gia_scaricato(vid):
    return any(SOTTOTITOLI.glob(f"{vid}.*.vtt"))


def scegli_traccia(info):
    """Restituisce (tipo, lingua) oppure (None, motivo)."""
    manuali = info.get("subtitles") or {}
    for lingua in sorted(manuali, key=lambda k: (k != "it", k)):
        if lingua.lower().startswith("it") and "live_chat" not in lingua:
            return "manuali", lingua
    auto = info.get("automatic_captions") or {}
    origini = [k for k in auto if k.endswith("-orig")]
    if "it-orig" in auto:
        return "automatici", "it-orig"
    if "it" in auto and not origini:
        return "automatici", "it"
    if origini:
        return None, f"solo sottotitoli automatici in altra lingua ({', '.join(origini)})"
    return None, "nessun sottotitolo disponibile"


def scarica(vid):
    """Scarica la traccia migliore. Restituisce (tipo, percorso) o (None, motivo)."""
    url = f"https://www.youtube.com/watch?v={vid}"
    with yt_dlp.YoutubeDL(opzioni_ytdlp()) as ydl:
        info = ydl.extract_info(url, download=False)
    tipo, lingua = scegli_traccia(info)
    if not tipo:
        return None, lingua

    modello = str(SOTTOTITOLI / "%(id)s.%(ext)s")
    opz = opzioni_ytdlp(
        writesubtitles=(tipo == "manuali"),
        writeautomaticsub=(tipo == "automatici"),
        subtitleslangs=[lingua],
        subtitlesformat="vtt",
        outtmpl={"default": modello, "subtitle": modello},
    )
    with yt_dlp.YoutubeDL(opz) as ydl:
        ydl.process_ie_result(info, download=True)

    scaricato = SOTTOTITOLI / f"{vid}.{lingua}.vtt"
    if not scaricato.exists() or scaricato.stat().st_size < 20:
        raise RuntimeError(f"il file dei sottotitoli ({lingua}) non e' stato creato")
    finale = SOTTOTITOLI / f"{vid}.{tipo}.vtt"
    scaricato.replace(finale)
    return tipo, finale


def main():
    prepara_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limite", type=int, default=0, help="elabora al massimo N video")
    ap.add_argument("--ricontrolla", action="store_true",
                    help="riprova anche i video gia' segnati senza sottotitoli")
    args = ap.parse_args()

    video = leggi_csv(VIDEO_NUTRIZIONE)
    if not video:
        sys.exit("Non trovo dati/video_nutrizione.csv: completa prima la Fase 1.")
    SOTTOTITOLI.mkdir(parents=True, exist_ok=True)

    senza = {r["id"]: r for r in leggi_csv(SENZA_SOTTOTITOLI) if r.get("id")}
    if args.ricontrolla:
        senza = {}
    errori = [e for e in leggi_csv(ERRORI) if e.get("fase") != "sottotitoli"]

    da_fare = [v for v in video if not gia_scaricato(v["id"]) and v["id"] not in senza]
    if args.limite:
        da_fare = da_fare[: args.limite]
    print(f"Video confermati: {len(video)}  -  gia' scaricati: "
          f"{sum(gia_scaricato(v['id']) for v in video)}  -  senza sottotitoli (gia' noti): "
          f"{sum(v['id'] in senza for v in video)}  -  da scaricare ora: {len(da_fare)}")
    if da_fare:
        minuti = len(da_fare) * (sum(config.PAUSA_SOTTOTITOLI) / 2 + 4) / 60
        print(f"Tempo stimato: circa {minuti:.0f} minuti. Ctrl+C per interrompere, "
              "rilanciando riprende da dove era rimasto.\n")

    conteggio = {"manuali": 0, "automatici": 0, "senza": 0, "errori": 0}

    def salva():
        scrivi_csv(SENZA_SOTTOTITOLI, CAMPI_SENZA, list(senza.values()))
        scrivi_csv(ERRORI, CAMPI_ERRORI, errori)

    try:
        for i, v in enumerate(da_fare, 1):
            vid = v["id"]
            print(f"[{i}/{len(da_fare)}] {vid}  {v.get('titolo', '')[:70]}", flush=True)
            try:
                tipo, esito = con_pazienza(lambda: scarica(vid), "sottotitoli")
                if tipo:
                    conteggio[tipo] += 1
                    print(f"   ok: sottotitoli {tipo}")
                else:
                    conteggio["senza"] += 1
                    print(f"   nessun sottotitolo italiano: {esito}")
                    senza[vid] = {**{k: v.get(k) for k in CAMPI_SENZA}, "motivo": esito}
            except Bloccato:
                raise
            except Exception as err:  # noqa: BLE001
                conteggio["errori"] += 1
                msg = str(err).replace("\n", " ")[:500]
                print(f"   ERRORE: {msg[:200]}")
                errori.append({"fase": "sottotitoli", "id": vid, "titolo": v.get("titolo"), "errore": msg})
            salva()
            if i < len(da_fare):
                pausa(config.PAUSA_SOTTOTITOLI)
    except Bloccato:
        print("\nYouTube continua a bloccare le richieste anche dopo le attese.\n"
              "Il lavoro fatto e' salvato: rilancia lo script tra qualche ora.\n"
              "Se succede spesso, imposta BROWSER_COOKIE in scripts/config.py.")
    except KeyboardInterrupt:
        print("\nInterrotto. Il lavoro fatto e' salvato.")
    salva()

    # pulizia di eventuali file parziali lasciati da yt-dlp
    for p in SOTTOTITOLI.glob("*.part"):
        p.unlink(missing_ok=True)

    print(f"\nScaricati ora: {conteggio['manuali']} manuali, {conteggio['automatici']} automatici. "
          f"Senza sottotitoli: {conteggio['senza']}. Errori: {conteggio['errori']}.")
    print("Prossimo passo:  python scripts/04_crea_trascrizioni.py")


if __name__ == "__main__":
    main()
