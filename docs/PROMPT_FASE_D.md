# Fase D – Estrazione completa (abbonamento Pro, senza API)

## Contesto
Stiamo lavorando al progetto descritto in `CLAUDE.md` e in `PROMPT_CLAUDE_CODE.md`. Le fasi A, B e C sono
concluse: in `CLAUDE.md` trovi dove sono l'elenco dei problemi approvato (Fase B) e lo schema JSON validato con
il pilota (Fase C). Se qualcosa non torna, fermati e chiedimelo prima di procedere.
Ora inizia la Fase D: estrarre le informazioni da tutte le trascrizioni pertinenti, secondo lo schema approvato.

## Vincoli
- **Non uso le API di Claude e non ho una chiave API**: niente script che chiamano Claude via API. Tutto il
  lavoro con Claude avviene dentro Claude Code, con il mio **abbonamento Pro**, che ha limiti di utilizzo
  (finestre di alcune ore e un tetto settimanale). Il lavoro sarà distribuito su più sessioni e più giorni:
  deve potersi interrompere in qualsiasi momento e riprendere senza perdere nulla e senza rifare lavoro già fatto.
- Tutto ciò che si può fare senza Claude (preparazione, conteggi, controlli) va fatto con script Python, che non
  consumano i limiti. Usa l'ambiente esistente: `.venv\Scripts\python` (Windows).
- Le trascrizioni in `trascrizioni/` non vanno mai modificate.
- Valgono tutte le regole sui contenuti di `PROMPT_CLAUDE_CODE.md`: nessun nome di autori o del canale, nessun
  link ai video, nessuna citazione testuale, descrizioni scritte con parole proprie, studi riportati così come
  citati (la verifica avverrà nella Fase E).
- Spiegami passo passo cosa fai. Chiedimi conferma prima di avviare l'estrazione su larga scala.

## Cosa fare

### 1. Preparazione con Python (nessun consumo dei limiti)
Crea `scripts/07_prepara_estrazione.py`, che genera `conoscenza/stato_estrazione.csv` (separatore `;`, UTF-8 con
BOM) con una riga per trascrizione e queste colonne: id, file, data, area_principale, argomenti, problemi
(quelli della lista approvata a cui il video si collega), parole, token_stimati, priorita, stato
(`da_fare` / `fatto` / `errore` / `escluso`), lotto, data_elaborazione, note.
- **Esclusioni** (stato `escluso`, motivo nelle note): video non collegati a nessun problema approvato; video
  troppo brevi per contenere indicazioni utili (es. sotto le 150 parole). Segnala a parte i **probabili doppioni**
  (Short che riprendono un video lungo, titoli quasi identici): li decidiamo insieme.
- **Priorità**: prima i problemi più importanti per l'app (secondo l'ordine concordato nella Fase B); dentro ogni
  problema dai video più recenti ai più vecchi, perché le indicazioni recenti contano di più.
- **Lotti**: gruppi di trascrizioni dello stesso problema da circa 20-25.000 token ciascuno (di solito 6-10 video).
- Lo script deve essere rilanciabile: non deve toccare le righe già `fatto`.
- Mostrami un riepilogo: video da elaborare, esclusi (per motivo), possibili doppioni, token totali, numero di lotti.

### 2. Sub-agente estrattore con un modello più economico
Crea `.claude/agents/estrattore.md`, un sub-agente con:
- `model: sonnet`;
- strumenti limitati alla lettura e scrittura di file (Read, Write, Glob);
- istruzioni complete e autosufficienti: lo schema JSON approvato (o il percorso del file che lo contiene),
  tutte le regole sui contenuti, e un esempio di estrazione ben fatta preso dal pilota.

Il sub-agente riceve un lotto (elenco di file), legge le trascrizioni, scrive un file per video in
`conoscenza/estrazioni/<id>.json` e restituisce **solo un riepilogo brevissimo** (id elaborati ed eventuali
problemi), così la sessione principale non si riempie di testo.
La sessione principale fa da coordinatore: **non legge le trascrizioni**, assegna i lotti, controlla i risultati
e aggiorna il registro.

### 3. Controllo qualità automatico (nessun consumo dei limiti)
Crea `scripts/08_valida_estrazioni.py`, che per ogni video del registro:
- verifica che il JSON esista, sia valido e rispetti lo schema (campi obbligatori, tipi, valori ammessi);
- verifica che non compaiano nomi vietati (elenco in un file di configurazione: nomi degli autori, del canale, ecc.);
- verifica che non ci siano frasi copiate dalla trascrizione (es. 12 o più parole consecutive identiche);
- aggiorna lo stato nel registro (`fatto` oppure `errore`, con il motivo nelle note) e produce un breve report.
I video in `errore` tornano da elaborare nel giro successivo.
Inoltre, ogni circa 10 lotti, controlla tu a campione 2-3 estrazioni confrontandole con le trascrizioni, e
segnalami se il sub-agente sbaglia in modo sistematico (in quel caso correggiamo le sue istruzioni).

### 4. Prova e stima prima di partire
Esegui una prova con i primi 2 lotti, poi valida. Misura il consumo (comando `/usage`, se disponibile, oppure
`/status`) e dimmi:
- quanti lotti è realistico fare in una finestra di utilizzo del piano Pro;
- quante sessioni o giorni servono in totale.
Se il totale è eccessivo, proponimi come ridurlo: limitarsi ai problemi prioritari, escludere i doppioni, usare
`haiku` per i video più semplici e brevi, oppure passare temporaneamente a un piano con limiti più alti.
**Aspetta la mia scelta** prima di continuare.

### 5. Ciclo di lavoro di ogni sessione
Quando ti scrivo **"continua la Fase D"**:
1. leggi `CLAUDE.md` e `conoscenza/stato_estrazione.csv`;
2. avvia i lotti successivi con il sub-agente, al massimo 2-3 in parallelo;
3. dopo ogni gruppo di lotti esegui `08_valida_estrazioni.py` e aggiorna il registro;
4. alla fine della sessione mostrami: lotti fatti in questa sessione, totale fatto / da fare, errori, stima delle
   sessioni rimanenti;
5. aggiorna `CLAUDE.md` con lo stato dei lavori.
Se il limite di utilizzo si esaurisce a metà di un lotto non è un problema: alla ripresa la validazione individua i
video incompleti e li rimette in coda.

### 6. Fine della Fase D
Quando non ci sono più video `da_fare` né in `errore`, crea `conoscenza/report_estrazione.md` con: video elaborati
per problema, indicazioni estratte per tipo (alimenti, integratori, esercizi, abitudini, terapie), numero di studi
citati, affermazioni dubbie, video esclusi e perché. Aggiorna `CLAUDE.md` e **fermati prima della Fase E**.

## Inizia
Comincia dal punto 1 e mostrami il riepilogo della preparazione.
