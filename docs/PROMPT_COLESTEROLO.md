# Seconda fetta verticale: COLESTEROLO ALTO

Obiettivo: portare il problema "colesterolo alto" dai video all'app, come fatto per la glicemia alta, con il
metodo compresso di `docs/PROMPT_FASE_D_PRO.md` e **misurando i consumi di ogni passo**, per capire quanto costa
davvero un nuovo percorso con il piano Pro.

Valgono tutte le regole già in CLAUDE.md: Sonnet; alla fine di ogni passo fermati e aspetta il mio via; Python per
tutto ciò che non richiede di capire il testo; numeri dei riepiloghi sempre calcolati da Python; nessun riferimento a
video, canale o autori; testi scritti da zero; le regole di presentazione decise per la glicemia (due livelli di
testo, glossario, etichette per esito, nessuna nota interna, nessun codice interno visibile, campi vuoti nascosti).

## Registro dei consumi
Crea `conoscenza/consumi.csv` (passo; problema; token stimati o misurati; operazioni; durata; note) e aggiungi una
riga alla fine di ogni passo. Se sono disponibili, inserisci anche i dati della glicemia, come riferimento.

## Passo C1 – Video e selezione (solo Python)
1. Individua in `problemi.csv` il problema del colesterolo (ed eventualmente trigliceridi, se è un problema a parte:
   in quel caso proponimi se unirli).
2. Elenca i video ALIMENTAZIONE e MISTO collegati.
3. Selezione per copertura (Punto 3 del piano PRO): dizionario dei rimedi (vocabolario esistente + termini tipici del
   colesterolo: steroli e stanoli vegetali, beta-glucani, avena, psillio, riso rosso fermentato, bergamotto, omega-3,
   frutta secca, soia, legumi, grassi saturi e trans, uova, burro, olio d'oliva, aglio, statine...); conteggio con
   Python di rimedi, menzioni di studi e dosi in ogni trascrizione; scelta dei più recenti e ricchi, poi un video in
   più solo se porta rimedi nuovi; **tetto: 10-12 video**.
4. Mostrami: video scelti, rimedi coperti, video esclusi e perché, token stimati. Aspetta il mio via.

## Passo C2 – Estrazione compressa
1. Python prepara **un unico file di input per lotto**: regole di estrazione in versione compatta (una pagina),
   vocabolario filtrato in forma compatta, trascrizioni compattate (senza intestazione, marcatori di tempo, saluti,
   avvertenze ripetute, inviti, sponsor). Mostrami la riduzione del testo.
2. Formato di uscita **a righe** (I|..., S|..., A|..., D|..., N|...) e uno script Python che lo converte nello
   schema 1.2 e lo valida. Al massimo 3 operazioni per lotto.
3. **Prova sul primo lotto**, con due modi, misurando token e qualità:
   a. tu nella sessione principale (Sonnet): leggi il file del lotto e scrivi il file a righe;
   b. un sub-agente `haiku` sullo stesso lotto.
   Confronta con Python: indicazioni, chiavi, studi, dosi, numeri ritrovati nelle trascrizioni, errori del
   convertitore. Dimmi quale modo conviene. Aspetta la mia scelta prima degli altri lotti.
4. Dopo l'estrazione: proposta di unione delle chiavi nuove fatta da Python, che approvo io.

## Passo C3 – Studi e sicurezza (Fase E)
1. Raggruppa le indicazioni per chiave (Python). **Riusa** ciò che vale anche qui: schede di sicurezza degli
   integratori già scaricate, fonti ufficiali, glossario. Attenzione: le revisioni della glicemia **non** valgono per il
   colesterolo, perché l'esito è diverso (LDL, colesterolo totale, trigliceridi, eventi cardiovascolari). Servono
   ricerche nuove per questo esito.
2. PubMed con Python: per ogni rimedio 1-2 revisioni sistematiche o meta-analisi recenti con esito LDL o lipidi;
   ritrovamento degli studi citati nei video, senza insistere su quelli non trovati.
3. **Fonti ufficiali in più** (con Python, solo le sezioni utili):
   - Registro UE delle indicazioni sulla salute autorizzate (EU Register of nutrition and health claims): steroli e
     stanoli vegetali, beta-glucani di avena e orzo, e altre voci pertinenti, con le quantità e le condizioni d'uso
     previste;
   - riso rosso fermentato (monacoline): parere EFSA sulla sicurezza (2018), limiti di legge UE sulle monacoline
     (Regolamento (UE) 2022/860), scheda NCCIH. È il punto più delicato del percorso: contiene la stessa sostanza di un
     farmaco (lovastatina), con gli stessi rischi e interazioni;
   - NCCIH, NIH ODS o LiverTox per gli altri integratori nuovi (bergamotto, omega-3, ecc.);
   - per i segnali d'allarme: pagine ufficiali MedlinePlus o NIDDK/NHLBI sui sintomi di infarto e ictus.
4. Prima di leggere gli abstract mostrami l'elenco dei rimedi e delle fonti trovate, con la stima dei token, e aspetta
   il mio via. Poi lettura in un unico passaggio, come per la glicemia (output a righe, convertito da Python).
5. Livelli di evidenza ed esiti come per la glicemia (confermato, incerto, smentito, non pertinente, senza prove).

## Passo C4 – Percorso e schede (Fase F)
1. Stessa struttura del percorso glicemia (avvertenza breve, riquadro "quando chiamare subito il 112", cos'è, 5 passi,
   tappe, prove limitate raggruppate, falsi miti e promesse non dimostrate, da valutare col medico, avvertenze di
   sicurezza, riferimenti con titolo, rivista e anno).
2. **Schede condivise tra percorsi**: molti rimedi compaiono in entrambi (dieta mediterranea, fibre, legumi, olio
   d'oliva, movimento, peso...). Prima di generare proponimi come evitare i doppioni: per esempio una scheda unica per
   rimedio, con le prove distinte per problema ("per la glicemia: ...", "per il colesterolo: ...").
3. **Farmaci per il colesterolo (statine e altri)**: l'app non deve mai scoraggiare una terapia prescritta. Le
   affermazioni dei video contro le statine vanno trattate nei falsi miti solo se smentite dalle fonti, e sempre con
   "non sospendere né ridurre i farmaci senza il medico". Nessun consiglio su dosi di farmaci.
4. Prima mostrami l'indice del percorso e una scheda di esempio (riso rosso fermentato, perché è la più delicata).
   Dopo la mia approvazione genera il resto, con i controlli Python già usati per la glicemia.

## Passo C5 – App
1. Aggiungi il percorso nell'app: attiva la zona o il sistema corrispondente (es. "Cuore e circolazione" o un sistema
   "Colesterolo e grassi nel sangue"; proponimi tu la collocazione migliore nella mappa e nei sistemi).
2. Le schede condivise devono mostrare le prove del percorso da cui si arriva.
3. Rilancia g1_prepara_app.py e i controlli; commit; aggiorna CLAUDE.md e il registro dei consumi; fermati.

## Inizia
Dal Passo C1.
