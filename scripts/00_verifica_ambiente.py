# -*- coding: utf-8 -*-
"""
PREPARAZIONE - controlla che tutto il necessario sia installato
e che YouTube sia raggiungibile. Non modifica nulla.

Uso:  python scripts/00_verifica_ambiente.py
"""
import shutil
import subprocess
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from comune import prepara_console, opzioni_ytdlp  # noqa: E402
import config  # noqa: E402

prepara_console()
tutto_ok = True


def riga(esito, nome, dettaglio):
    global tutto_ok
    simbolo = {"ok": "[OK]   ", "avviso": "[AVVISO]", "no": "[MANCA]"}[esito]
    if esito == "no":
        tutto_ok = False
    print(f"{simbolo} {nome}: {dettaglio}")


print("\n=== Verifica dell'ambiente ===\n")

# 1. Python
v = sys.version_info
if v >= (3, 9):
    riga("ok", "Python", f"{v.major}.{v.minor}.{v.micro}")
else:
    riga("no", "Python", f"{v.major}.{v.minor} e' troppo vecchio: serve 3.9 o superiore")

# 2. yt-dlp
try:
    import yt_dlp
    riga("ok", "yt-dlp", yt_dlp.version.__version__)
except ImportError:
    yt_dlp = None
    riga("no", "yt-dlp", "non installato -> vedi README, passo 'Installazione'")

# 3. ffmpeg (non indispensabile per i sottotitoli, ma richiesto dal progetto)
percorso = shutil.which("ffmpeg")
if percorso:
    try:
        ver = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True).stdout.split("\n")[0]
    except Exception:  # noqa: BLE001
        ver = percorso
    riga("ok", "ffmpeg", ver)
else:
    riga("avviso", "ffmpeg", "non trovato (non serve per i sottotitoli, servira' per un eventuale Whisper)")

# 4. Motore JavaScript (yt-dlp lo usa per decifrare alcune pagine di YouTube)
js = [n for n in ("deno", "node", "bun") if shutil.which(n)]
if js:
    riga("ok", "Motore JavaScript", ", ".join(js))
else:
    riga("avviso", "Motore JavaScript", "nessuno trovato (consigliato Deno, vedi README). "
                                         "Di solito i sottotitoli funzionano lo stesso.")

# 5. Prova di collegamento a YouTube
if yt_dlp:
    print("\nProvo a leggere 1 video dal canale (pochi secondi)...")
    try:
        with yt_dlp.YoutubeDL(opzioni_ytdlp(extract_flat="in_playlist", playlistend=1)) as ydl:
            info = ydl.extract_info(config.CANALE_URL + "/videos", download=False)
        primo = next(iter(info.get("entries") or []), None)
        if primo:
            riga("ok", "YouTube", f"raggiungibile. Ultimo video: \"{primo.get('title')}\"")
        else:
            riga("no", "YouTube", "risposta vuota: il canale non mostra video?")
    except Exception as e:  # noqa: BLE001
        riga("no", "YouTube", f"errore di collegamento: {str(e)[:300]}")

print("\n" + ("Tutto pronto! Puoi lanciare la Fase 1." if tutto_ok
              else "Qualcosa manca: sistemalo seguendo il README e rilancia questo controllo."))
