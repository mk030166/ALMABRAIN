# Chiusura Fase C e Fase D "compressa" – restare nel piano Pro

Questo documento SOSTITUISCE `PROMPT_FASE_D.md` (non usarlo più).

## Il problema
Il pilota costa circa 25.000 token per video. Con 650 video di alimentazione sarebbero oltre 16 milioni di token:
incompatibile con il mio abbonamento **Pro**, che non posso cambiare. Obiettivo: ridurre il consumo di almeno
10 volte, senza perdere le informazioni che servono all'app.

Principio guida: **l'autorità dell'app saranno gli studi scientifici (Fase E), non i video.** I video servono come
mappa dei rimedi, delle indicazioni pratiche e degli studi citati, quindi non serve estrarli tutti in modo
esaustivo: basta un sottoinsieme ben scelto. **Tutto ciò che non richiede di capire il testo si fa con Python,
che non consuma token.**

## Decisioni sull'ambito (vincolanti)
1. **Solo alimentazione**: problemi e video dell'area alimentazione (video con categoria ALIMENTAZIONE e MISTO).
   Esclusi per ora i problemi muscolo-scheletrici e le schede esercizio. Il movimento collegato a un problema
   alimentare (es. camminare dopo i pasti per la glicemia) resta solo come breve indicazione di tipo "abitudine".
2. **Niente inglese per ora**: non compilare più `nome_en`. Le chiavi del vocabolario restano in inglese.
3. **Fable non si usa più** dopo il 16 novembre. Per coordinare la Fase D basta Sonnet (`/model`); Opus solo se
   devo prendere decisioni difficili.

## Regole di risparmio per ogni sessione
- `CLAUDE.md` viene riletto a ogni messaggio: riducilo all'essenziale (massimo circa 60 righe: regole, ambito,
  stato attuale) e sposta storico e dettagli in `docs/diario.md`, da leggere solo quando serve.
- Una sessione lunga costa sempre di più, perché ogni messaggio rimanda tutta la conversazione: tra un gruppo di
  lotti e l'altro suggeriscimi di usare `/clear`. Lo stato deve stare sempre nei file (registro, CLAUDE.md),
  mai solo nella conversazione.
- Niente letture di prova o controlli che Python può fare al tuo posto.

## Piano (fermati e aspetta il mio via alla fine di ogni punto)

### Punto 1 – Chiusura Fase C (leggera)
Applica le correzioni già decise, senza rifare lavoro inutile:
- REGOLE_ESTRAZIONE: chiave esistente più generica (dettagli negli esempi), massimo 3 chiavi nuove per video;
  esempi chiari di dose / frequenza / durata / modalità; segnali_allarme solo per sintomi che richiedono attenzione
  medica; vietato usare il titolo; "favorire" solo se il video lo raccomanda davvero, nel dubbio "informativo".
- Schema 1.2: campo `consultare_medico` (sì/no + motivo) nelle indicazioni.
- Chiavi nuove del pilota: proposta di unione dei doppioni preparata **da uno script Python** (nomi simili,
  sinonimi uguali), che io approvo.
- Estrazioni del pilota: aggiornale con uno script dove possibile. Rifai con il modello solo i video la cui
  trascrizione è cambiata in modo rilevante dopo il completamento dei sottotitoli (confronto delle parole fatto
  con Python), e dimmi quanti sono prima di farlo.

### Punto 2 – Problemi e video nell'ambito (solo Python)
- Filtra `problemi.csv` ai problemi dell'area alimentazione e mostrameli.
- Elenca i video ALIMENTAZIONE e MISTO collegati a quei problemi.

### Punto 3 – Selezione intelligente dei video (solo Python, zero token)
Obiettivo: il minimo numero di video che copre il massimo dei rimedi e delle indicazioni.
1. Prepara un **dizionario dei rimedi**: le voci del vocabolario con sinonimi ed esempi, più un elenco di alimenti,
   integratori, nutrienti, piante e spezie comuni. È l'unico passaggio in cui puoi usare il modello, una volta sola.
2. Uno script legge tutte le trascrizioni e per ogni video calcola: rimedi citati, numero di menzioni di studi
   (parole come studio, ricerca, meta-analisi, pubblicato, università, rivista, anni), dosi e numeri (mg, grammi,
   minuti, volte al giorno), lunghezza e data.
3. Per ogni problema scegli i video con un criterio di **copertura**: prima i più recenti e ricchi; poi aggiungi un
   video solo se porta rimedi non ancora coperti; aggiungi un tetto per problema (es. 8-12 video). I video recenti
   valgono di più, perché l'app deve basarsi sulle indicazioni più aggiornate.
4. Mostrami: video selezionati per problema, rimedi coperti, video esclusi e perché, stima dei token.
   Obiettivo indicativo: **circa 200-250 video invece di 650**.

### Punto 4 – Trascrizioni compattate e lotti (solo Python)
Per ogni lotto prepara **un unico file** di input (meno letture = meno spese fisse):
- togli intestazione YAML, marcatori di tempo (l'app non rimanda ai video), saluti, presentazioni, avvertenze
  ripetute ("non voglio sostituirmi al medico"), inviti a iscriversi o a scaricare materiali, sponsor;
- per ogni video lascia solo: id, data, problemi e testo compattato;
- lotti di 8-10 video dello stesso problema;
- allega il **vocabolario filtrato** per quel problema, in forma compatta (una riga per chiave: `chiave = nome`).
Mostrami quanto si riduce il testo rispetto alle trascrizioni originali.

### Punto 5 – Formato di estrazione compatto
- Il sub-agente non scrive JSON lungo: scrive un **formato a righe** con campi brevi, una riga per elemento.
  Per esempio `I|tipo|chiave|orientamento|problemi|dose|frequenza|durata|modalita|precauzioni|medico|studi`
  per le indicazioni, e righe `S|...` per gli studi, `A|...` per i segnali d'allarme, `D|...` per le
  affermazioni dubbie, `N|...` per le chiavi nuove.
- Uno **script Python converte** le righe nel JSON dello schema 1.2 e le valida. I token si spendono per capire,
  non per scrivere parentesi e nomi dei campi.
- Campi tolti o ridotti rispetto al pilota: schede esercizio (fuori ambito), minuto del video, sintesi lunga
  (al massimo una frase).

### Punto 6 – Prova comparativa Haiku contro Sonnet
Sui 2 video del pilota già usati per il confronto, più altri 4 del pilota (in tutto 6, misti tra semplici e ricchi
di studi), fai estrarre con il formato compatto sia da un sub-agente `haiku` sia da uno `sonnet`. Confrontali con le
estrazioni di riferimento del pilota, con uno script dove possibile: indicazioni trovate, studi, dosi, errori.
Misura i token per video di ciascuno.
Proposta da verificare: **Haiku per i video semplici, Sonnet solo per quelli ricchi di studi e dosi**, con
l'instradamento deciso da Python in base ai conteggi del punto 3.
Mostrami i risultati e aspetta la mia scelta.

### Punto 7 – Piano di consumo
Con i numeri misurati, calcola: token per lotto, lotti per finestra di utilizzo del piano Pro, giorni necessari.
Proponi un ritmo sostenibile (es. N lotti per finestra, lasciando margine per il resto del lavoro) e aspetta il mio via.

### Punto 8 – Esecuzione a blocchi
Ad ogni "continua la Fase D":
1. prendi i lotti successivi dal registro (`conoscenza/stato_estrazione.csv`);
2. avvia i sub-agenti, al massimo 2 in parallelo e solo su problemi diversi;
3. converti e valida con Python, aggiorna il registro;
4. alla fine di ogni gruppo di lotti, uno script propone l'unione delle chiavi nuove simili; me la mostri;
5. mostrami l'avanzamento in 5 righe, aggiorna CLAUDE.md e suggeriscimi `/clear`.

## Dopo la Fase D
Anche la Fase E (letteratura) seguirà gli stessi principi: ricerca su PubMed e download degli abstract con Python
(gratis), lettura con il modello solo degli studi più importanti, preferendo 1-2 revisioni sistematiche recenti
per ogni rimedio.

## Inizia
Comincia dal Punto 1. Prima di tutto riduci CLAUDE.md come indicato e mostrami la nuova versione.
