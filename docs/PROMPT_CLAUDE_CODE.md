# Progetto: app PWA di percorsi di benessere basata sulla base di conoscenza ALMABRAIN

## Chi sono e come lavorare con me
- Non sono un programmatore: spiegami in italiano, passo passo, cosa fai e perché, prima di eseguire
  comandi. Chiedimi conferma solo per decisioni importanti o azioni difficili da annullare.
- Preferisco soluzioni in HTML + CSS + JavaScript puro, senza framework complessi se non indispensabili.
- Lavora per fasi: alla fine di ogni fase fermati, mostrami i risultati in modo comprensibile e aspetta il mio via.
- Primo compito: crea in questa cartella un file `CLAUDE.md` che riassuma queste regole, il progetto e lo
  stato dei lavori, così lo ritrovi nelle sessioni future. Aggiornalo alla fine di ogni fase.

## Situazione attuale (cosa c'è in questa cartella)
- `trascrizioni/AAAA-MM-GG_<id>.md`: 1.494 trascrizioni in italiano di video su salute, alimentazione,
  fisioterapia ed esercizio (2015-2026). Ogni file inizia con un'intestazione YAML (id, titolo, data,
  durata, url, categoria, area_principale, aree_secondarie, argomenti, pubblico, formato, sottotitoli),
  seguita dal testo in paragrafi con marcatori di tempo [mm:ss]. Totale: circa 2,5 milioni di parole
  (circa 3,8 milioni di token).
- `dati/tematiche.csv`: per ogni video area principale, aree secondarie, argomenti, pubblico e formato
  (separatore `;`, UTF-8 con BOM). Schema delle 12 aree e dei loro argomenti: `scripts/tematiche_config.py`.
- `dati/classificazione_completa.csv` (categoria alimentazione: ALIMENTAZIONE / MISTO / ALTRO),
  `dati/elenco_video.csv` (con le descrizioni complete), `dati/revisione_*.csv` (correzioni manuali).
- `scripts/`: script Python 01-06 che hanno prodotto questi dati; servono per aggiornare la base con i
  video nuovi (ordine: 01, 02, 06, 03, 04, 05). Non modificarli senza motivo. Ambiente Python in `.venv`.
- `report.md`: statistiche (video, parole, token per area).

Note sulla qualità del materiale:
- I sottotitoli automatici contengono errori di riconoscimento vocale (es. "bagnesio" = magnesio,
  "Fmingham HeST study" = Framingham Heart Study, "omebrazolo" = omeprazolo): interpreta dal contesto.
- Molti titoli sono sensazionalistici: conta il contenuto, non il titolo.
- I video vanno dal 2015 al 2026 e su alcuni temi le indicazioni sono cambiate nel tempo.

## Obiettivo finale
Una PWA (installabile e funzionante offline) che, SENZA fare riferimento ai singoli video né ai loro
autori, aiuti l'utente a esplorare possibili percorsi per un problema fisico:
1. L'utente sceglie il problema da una **mappa interattiva di un corpo umano stilizzato** (SVG cliccabile:
   testa e collo, spalle, schiena, anca e bacino, ginocchio, piede e caviglia, gomito-polso-mano, ...)
   oppure da una **vista "sistemi"** per i temi non muscolo-scheletrici (cuore e circolazione, metabolismo
   e glicemia, intestino e digestione, sonno e mente, pelle, ecc.).
2. L'app mostra un **percorso suggerito** per quel problema: informazioni essenziali; **segnali d'allarme**
   (quando andare subito dal medico); abitudini e alimentazione; **schede dei prodotti naturali/integratori**
   (cos'è, come si usa, dosaggi riportati negli studi, precauzioni, interazioni con farmaci,
   controindicazioni, livello di evidenza); **routine di esercizi** (esecuzione passo passo, serie e
   ripetizioni, livelli di difficoltà, precauzioni); **riferimenti alla letteratura scientifica**.
3. Ogni contenuto è un suggerimento informativo che richiede l'avallo di un medico: avvertenza ben visibile
   in ogni percorso.
4. Basato sulle indicazioni più recenti e meglio documentate: se un'indicazione è cambiata nel tempo,
   prevale la più recente (il cambiamento va registrato nei dati).
5. Multilingua fin dall'inizio: prima l'italiano, poi una versione internazionale (inglese per primo).
   Testi dell'interfaccia e contenuti separati per lingua.

## Regole sui contenuti (vincolanti)
- Nessun riferimento a: nomi degli autori dei video o di altre persone che vi compaiono, nome del canale
  o dello studio, link ai video.
- Le trascrizioni sono protette da diritto d'autore: usale solo come materiale di partenza per individuare
  temi, indicazioni e studi citati. **Nessuna citazione testuale e nessuna parafrasi ravvicinata**: i testi
  dell'app vanno scritti da zero, con parole proprie.
- **La fonte di autorità sono gli studi scientifici, non i video.** Ogni indicazione mostrata nell'app deve
  poggiare su riferimenti verificati (PubMed / DOI). Indicazioni senza supporto adeguato o non plausibili
  (es. rimedi casalinghi senza studi) vanno escluse, oppure tenute nei dati come "evidenza insufficiente"
  e non mostrate come raccomandazioni.
- **Livello di evidenza** per ogni indicazione, per esempio: A = revisioni sistematiche/meta-analisi o più
  RCT concordanti; B = singoli RCT o grandi studi osservazionali; C = studi piccoli o preliminari, su animali
  o in vitro; D = solo opinione o nessuno studio.
- Integratori e prodotti naturali: sempre precauzioni, interazioni con farmaci e categorie a rischio
  (gravidanza, allattamento, bambini, malattie renali o epatiche, anticoagulanti, ecc.).
- Linguaggio informativo, mai diagnostico; nessuna promessa di guarigione; nessun tono sensazionalistico.

## Piano di lavoro (fermati alla fine di ogni fase e aspetta il mio via)

**Fase A – Preparazione.** Verifica la cartella e i dati (conta trascrizioni e aree). Proponi la struttura
delle nuove cartelle (es. `conoscenza/`, `letteratura/`, `app/`) e crea `CLAUDE.md`. Consigliami se e come
usare git: le trascrizioni e i dati derivati dai video NON devono finire in un repository pubblico.

**Fase B – Elenco dei problemi.** Partendo da `dati/tematiche.csv`, dagli argomenti e dai titoli, proponi
l'elenco dei problemi/condizioni che l'app coprirà (es. lombalgia, cervicalgia, dolore di spalla, artrosi del
ginocchio, fascite plantare, glicemia alta, colesterolo alto, pressione alta, stitichezza, insonnia, ...),
indicando per ciascuno la regione del corpo o il sistema e quanti video lo trattano. Mostrami la lista in una
tabella e aspetta la mia approvazione.

**Fase C – Estrazione strutturata: progetto pilota.** Proponimi prima uno schema JSON. Poi scegli un solo
problema (propongo lombalgia o glicemia alta) e i relativi video, e per ogni video produci
`conoscenza/estrazioni/<id>.json` con: problemi trattati; per ogni indicazione il tipo (alimento,
integratore, esercizio, abitudine, terapia, altro), una descrizione sintetica scritta da te, le dosi, frequenze
e durate citate, le precauzioni e controindicazioni citate, gli studi citati (autori, anno, rivista, tipo di
studio, risultato così come riportato) e la data del video; gli esercizi descritti (nome, esecuzione,
serie/ripetizioni, livello, precauzioni); i segnali d'allarme; le affermazioni dubbie o non supportate.
Mostrami il risultato e affiniamo lo schema prima di estendere.

**Fase D – Estrazione completa.** Estendi a tutti i problemi approvati, per blocchi, con un registro di
avanzamento (`conoscenza/stato_estrazione.csv`) per poter interrompere e riprendere. Il volume è grande
(circa 3,8 milioni di token): proponimi la strategia più sostenibile (es. più sessioni a blocchi, oppure uno
script che usa l'API di Claude con una mia chiave, con stima dei costi) e aspetta la mia scelta.

**Fase E – Letteratura scientifica.** Raccogli tutti gli studi citati, eliminando i doppioni; verificali e
completali con PubMed (E-utilities) e Crossref (PMID, DOI, titolo, abstract). Scarica il testo completo solo
quando è open access (PubMed Central). Salva in `letteratura/` un indice (CSV/JSON) e gli abstract. Segnala
gli studi non trovati o che non dicono ciò che viene loro attribuito. Cerca anche revisioni sistematiche
recenti sui problemi approvati, per verificare e aggiornare le indicazioni.

**Fase F – Percorsi e schede.** Per ogni problema genera `conoscenza/percorsi/<problema>.json` (percorso a
tappe, segnali d'allarme, abitudini, alimentazione, prodotti con livello di evidenza e precauzioni, routine di
esercizi, riferimenti). Crea schede riutilizzabili per prodotti (`conoscenza/prodotti/`) ed esercizi
(`conoscenza/esercizi/`). Prepara due elenchi: i contenuti da far rivedere a un medico/fisioterapista, e gli
aspetti legali da verificare con un professionista prima della pubblicazione (diritti sui contenuti,
normativa sui software medici come il regolamento UE MDR, privacy, indicazioni sugli integratori).

**Fase G – App PWA.** In `app/`: `index.html`, CSS, JavaScript puro, `manifest.json`, service worker per
l'uso offline; mappa SVG del corpo cliccabile e accessibile anche da tastiera; vista sistemi; pagine dei
percorsi, schede prodotti ed esercizi; ricerca; avvertenze mediche; file di lingua (`i18n/it.json`, poi
`en.json`). Mobile-first e leggibile da persone anziane (caratteri grandi, alto contrasto). I contenuti
vengono dai JSON delle fasi precedenti. Spiegami come provarla sul mio computer e poi come pubblicarla.

**Fase H – Versione internazionale.** Traduzione di contenuti e interfaccia (inglese per primo), con
adattamento di unità di misura e note normative.

## Inizia
Comincia dalla Fase A: spiegami cosa trovi e cosa proponi, poi aspetta il mio via.
