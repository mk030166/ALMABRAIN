# ALMABRAIN – Base di conoscenza sull'alimentazione (canale YouTube AlmaPhysio)

Questi script scaricano **l'elenco dei video** e **le trascrizioni** (dai sottotitoli)
dei video di alimentazione del canale <https://www.youtube.com/@AlmaPhysio>.
Non scaricano i video.

| Fase | Script | Cosa fa | Risultato |
|---|---|---|---|
| Preparazione | `00_verifica_ambiente.py` | controlla che sia tutto installato | messaggi a schermo |
| 1 – Inventario | `01_inventario.py` | elenco di tutti i video (Shorts esclusi) | `dati/elenco_video.csv` |
| 1 – Classificazione | `02_classifica.py` | ALIMENTAZIONE / MISTO / ALTRO | `dati/video_nutrizione.csv`, `dati/riepilogo_fase1.md` |
| 2 – Sottotitoli | `03_scarica_sottotitoli.py` | scarica i sottotitoli italiani | `sottotitoli_raw/*.vtt`, `dati/senza_sottotitoli.csv` |
| 2 – Trascrizioni | `04_crea_trascrizioni.py` | pulisce e crea i testi | `trascrizioni/AAAA-MM-GG_id.md` |
| 2 – Report | `05_report.py` | statistiche e stima token | `report.md` |

Le impostazioni (pause, parole chiave, ecc.) sono in `scripts/config.py`.

---

## 1. Installazione (una volta sola)

### Windows

1. **Python** – scaricalo da <https://www.python.org/downloads/> e, durante
   l'installazione, **spunta la casella "Add python.exe to PATH"**.
2. **Scarica il progetto** – su GitHub apri il repository, scegli il ramo
   `ccr-bc67d6b1-sudbob`, pulsante verde **Code → Download ZIP**, poi estrai lo ZIP
   (es. in `Documenti\ALMABRAIN`).
3. **Apri il terminale nella cartella** – apri la cartella in Esplora file, clicca
   sulla barra dell'indirizzo in alto, scrivi `cmd` e premi Invio.
4. Copia e incolla questi comandi, uno alla volta, premendo Invio dopo ciascuno:

   ```
   py -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   winget install Gyan.FFmpeg
   winget install DenoLand.Deno
   ```
   - il 1° crea un "ambiente virtuale", cioè una cartella `.venv` che contiene i
     pacchetti del progetto senza toccare il resto del computer;
   - il 2° installa **yt-dlp** dentro quell'ambiente;
   - il 3° installa **ffmpeg** (servirà solo in futuro, per un eventuale Whisper);
   - il 4° installa **Deno**, un piccolo motore JavaScript che yt-dlp usa per leggere YouTube.
5. **Chiudi e riapri il terminale** (vedi punto 3) e lancia il controllo:

   ```
   .venv\Scripts\python scripts\00_verifica_ambiente.py
   ```

### Mac

1. Installa **Homebrew** se non ce l'hai (istruzioni su <https://brew.sh>), poi nel Terminale:
   `brew install python ffmpeg deno`
2. Scarica il progetto come ZIP (vedi Windows, punto 2) ed estrailo in `Documenti`.
3. Apri il Terminale, scrivi `cd ` (con lo spazio), **trascina la cartella** del progetto
   nella finestra e premi Invio.
4. Poi:

   ```
   python3 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   .venv/bin/python scripts/00_verifica_ambiente.py
   ```

> Nei comandi seguenti scrivo la versione Windows (`.venv\Scripts\python scripts\...`).
> Su Mac usa `.venv/bin/python scripts/...`.

---

## 2. Fase 1 – Inventario e classificazione

```
.venv\Scripts\python scripts\01_inventario.py --limite 5
```
Prova veloce con 5 video. Se funziona, lancia l'inventario completo (può richiedere
**15-40 minuti**: legge i dettagli di ogni video con una pausa tra l'uno e l'altro):

```
.venv\Scripts\python scripts\01_inventario.py
.venv\Scripts\python scripts\02_classifica.py
```

Si può interrompere in qualsiasi momento con **Ctrl+C**: rilanciando, riprende da dove era rimasto.

**Poi fermati** e controlla `dati/riepilogo_fase1.md` (totali e 15 esempi per categoria).
I casi incerti sono in `dati/da_rivedere.csv`.

### Revisione manuale
Le decisioni manuali vanno in `dati/revisione_manuale.csv` (colonne `id;categoria;motivo`,
categoria = `ALIMENTAZIONE`, `MISTO` o `ALTRO`). Dopo averlo modificato rilancia
`02_classifica.py`: le decisioni manuali hanno sempre la precedenza.

Per **escludere** un video dalla Fase 2 basta cancellarne la riga da `dati/video_nutrizione.csv`.

---

## 3. Fase 2 – Trascrizioni

```
.venv\Scripts\python scripts\03_scarica_sottotitoli.py --limite 3
.venv\Scripts\python scripts\03_scarica_sottotitoli.py
.venv\Scripts\python scripts\04_crea_trascrizioni.py
.venv\Scripts\python scripts\05_report.py
```

- Il download fa una pausa di 5-10 secondi tra un video e l'altro (per circa 300 video, ~45 minuti).
- Se YouTube blocca, lo script aspetta (1, 3, 10, 20 minuti) e riprova; se il blocco continua
  si ferma: **rilancialo più tardi**, salta i video già scaricati.
- I video senza sottotitoli italiani finiscono in `dati/senza_sottotitoli.csv`
  (per riprovarli: `03_scarica_sottotitoli.py --ricontrolla`).

---

## 4. Aggiornare la base in futuro (nuovi video)

Rilancia in ordine gli script da `01` a `05`. Vengono elaborati solo i video nuovi;
le revisioni manuali restano valide.

## Problemi frequenti

| Messaggio | Soluzione |
|---|---|
| `Sign in to confirm you're not a bot` | In `scripts/config.py` imposta `BROWSER_COOKIE = "firefox"` (o `"chrome"`, `"edge"`, `"safari"`): usa il browser in cui sei collegato a YouTube. Con Chrome/Edge chiudi prima il browser. |
| `non riesco a scrivere ... E' aperto in Excel?` | Chiudi il file in Excel e rilancia. |
| `'py' non è riconosciuto...` | Python non è installato o manca la spunta "Add to PATH": reinstallalo. |
| Errori strani di YouTube | Aggiorna yt-dlp: `.venv\Scripts\python -m pip install -U "yt-dlp[default]"` |
