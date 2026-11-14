# -*- coding: utf-8 -*-
"""
FASE 2 - PASSO 1b: COMPLETAMENTO DEI SOTTOTITOLI INCOMPLETI
===========================================================
Alcuni sottotitoli "manuali" caricati dal canale coprono solo una parte del parlato.
Questo script misura la completezza di ogni sottotitolo manuale:
  - parole al minuto (un parlato completo ne ha circa 120-160);
  - fino a che punto del video arrivano i sottotitoli;
  - buchi lunghi senza sottotitoli in mezzo al video.
Per i video incompleti scarica ANCHE i sottotitoli automatici di YouTube
(<id>.automatici.vtt, accanto a <id>.manuali.vtt). Poi 04_crea_trascrizioni.py
usa da solo la versione piu' completa.

Risultato: dati/copertura_sottotitoli.csv (una riga per video, con le misure e l'esito).
Si puo' interrompere (Ctrl+C) e rilanciare: salta i video gia' completati.

Uso:
    python scripts/03b_completa_sottotitoli.py --solo-analisi   (misura soltanto, non scarica)
    python scripts/03b_completa_sottotitoli.py --limite 3        (prova con 3 video)
    python scripts/03b_completa_sottotitoli.py                   (tutti i video incompleti)
Poi:  python scripts/04_crea_trascrizioni.py  e  python scripts/05_report.py
"""
import argparse
import importlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402
from comune import (DATI, ELENCO_VIDEO, ERRORI, SOTTOTITOLI, Bloccato, con_pazienza,  # noqa: E402
                    leggi_csv, pausa, prepara_console, scrivi_csv)

trascrizioni = importlib.import_module("04_crea_trascrizioni")
download = importlib.import_module("03_scarica_sottotitoli")

COPERTURA = DATI / "copertura_sottotitoli.csv"
CAMPI = ["id", "durata_s", "parole", "parole_minuto", "copertura_pct", "buchi_s",
         "incompleto", "motivo", "esito"]

# Soglie: sotto queste il sottotitolo manuale e' considerato incompleto
MIN_PAROLE_MINUTO = 110
MIN_COPERTURA = 0.85          # i sottotitoli devono arrivare almeno all'85% del video
MAX_BUCHI_S = 60              # secondi totali di buchi interni (oltre 15 s ciascuno)
BUCO_MINIMO_S = 15

RX_CUE = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})\s*-->\s*(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})")


def secondi(h, m, s, ms):
    return int(h or 0) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000


def misura(testo_vtt, durata):
    """Restituisce (parole, parole_minuto, copertura, buchi_s)."""
    tempi = [(secondi(*m.groups()[:4]), secondi(*m.groups()[4:])) for m in RX_CUE.finditer(testo_vtt)]
    frammenti = trascrizioni.frammenti_unici(trascrizioni.leggi_vtt(testo_vtt))
    parole = sum(len(t.split()) for _, t in frammenti)
    if not tempi or durata <= 0:
        return parole, 0.0, 0.0, 0.0
    tempi.sort()
    fine = max(e for _, e in tempi)
    buchi, fine_prec = 0.0, tempi[0][1]
    for inizio, fine_cue in tempi[1:]:
        if inizio - fine_prec > BUCO_MINIMO_S:
            buchi += inizio - fine_prec
        fine_prec = max(fine_prec, fine_cue)
    return parole, parole / (durata / 60), min(1.0, fine / durata), buchi


def valuta(parole_minuto, copertura, buchi):
    motivi = []
    if parole_minuto < MIN_PAROLE_MINUTO:
        motivi.append(f"{parole_minuto:.0f} parole/min")
    if copertura < MIN_COPERTURA:
        motivi.append(f"arriva al {copertura:.0%} del video")
    if buchi > MAX_BUCHI_S:
        motivi.append(f"{buchi:.0f} s di buchi")
    return motivi


def main():
    prepara_console()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--solo-analisi", action="store_true", help="misura soltanto, non scarica nulla")
    ap.add_argument("--limite", type=int, default=0, help="scarica al massimo N video")
    args = ap.parse_args()

    durate = {r["id"]: float(r.get("durata_secondi") or 0) for r in leggi_csv(ELENCO_VIDEO) if r.get("id")}
    precedenti = {r["id"]: r for r in leggi_csv(COPERTURA) if r.get("id")}
    righe = {}
    for p in sorted(SOTTOTITOLI.glob("*.manuali.vtt")):
        vid = p.name.split(".")[0]
        durata = durate.get(vid, 0)
        parole, ppm, cop, buchi = misura(p.read_text(encoding="utf-8", errors="replace"), durata)
        motivi = valuta(ppm, cop, buchi) if durata else ["durata sconosciuta"]
        auto = SOTTOTITOLI / f"{vid}.automatici.vtt"
        esito = "automatici gia' scaricati" if auto.exists() else (
            precedenti.get(vid, {}).get("esito", "") if motivi else "completo")
        righe[vid] = {"id": vid, "durata_s": int(durata), "parole": parole,
                      "parole_minuto": f"{ppm:.0f}", "copertura_pct": f"{cop * 100:.0f}",
                      "buchi_s": f"{buchi:.0f}", "incompleto": "SI" if motivi else "NO",
                      "motivo": ", ".join(motivi), "esito": esito}

    def salva():
        scrivi_csv(COPERTURA, CAMPI, sorted(righe.values(), key=lambda r: r["id"]))

    incompleti = [r for r in righe.values() if r["incompleto"] == "SI"]
    da_fare = [r for r in incompleti if not r["esito"].startswith("automatici")
               and not r["esito"].startswith("nessun")]
    salva()
    print(f"Sottotitoli manuali analizzati: {len(righe)}")
    print(f"Incompleti: {len(incompleti)}  -  automatici gia' scaricati o non disponibili: "
          f"{len(incompleti) - len(da_fare)}  -  da scaricare: {len(da_fare)}")
    print(f"Dettagli in {COPERTURA.relative_to(DATI.parent)}")
    if args.solo_analisi or not da_fare:
        return

    if args.limite:
        da_fare = da_fare[: args.limite]
    minuti = len(da_fare) * (sum(config.PAUSA_SOTTOTITOLI) / 2 + 4) / 60
    print(f"Tempo stimato: circa {minuti:.0f} minuti. Ctrl+C per interrompere, rilanciando riprende.\n")
    errori = [e for e in leggi_csv(ERRORI) if e.get("fase") != "completamento"]
    try:
        for i, r in enumerate(da_fare, 1):
            vid = r["id"]
            print(f"[{i}/{len(da_fare)}] {vid}  ({r['motivo']})", flush=True)
            try:
                tipo, esito = con_pazienza(lambda: download.scarica(vid, solo_automatici=True),
                                           "sottotitoli automatici")
                r["esito"] = "automatici scaricati" if tipo else f"nessun automatico: {esito}"
                print(f"   {r['esito']}")
            except Bloccato:
                raise
            except Exception as err:  # noqa: BLE001
                msg = str(err).replace("\n", " ")[:300]
                r["esito"] = f"errore: {msg[:120]}"
                errori.append({"fase": "completamento", "id": vid, "titolo": "", "errore": msg})
                print(f"   ERRORE: {msg[:150]}")
            salva()
            if i < len(da_fare):
                pausa(config.PAUSA_SOTTOTITOLI)
    except Bloccato:
        print("\nYouTube continua a bloccare: il lavoro fatto e' salvato, rilancia piu' tardi.")
    except KeyboardInterrupt:
        print("\nInterrotto. Il lavoro fatto e' salvato.")
    salva()
    scrivi_csv(ERRORI, ["fase", "id", "titolo", "errore"], errori)
    print("\nProssimo passo:  python scripts/04_crea_trascrizioni.py  (sceglie da solo la versione piu' completa)")


if __name__ == "__main__":
    main()
