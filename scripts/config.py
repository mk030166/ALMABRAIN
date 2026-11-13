# -*- coding: utf-8 -*-
"""
IMPOSTAZIONI DEL PROGETTO
=========================
Questo e' l'unico file che potresti voler modificare a mano.
Ogni riga che inizia con # e' un commento e non viene eseguita.
"""

# --- Canale -----------------------------------------------------------------
CANALE_URL = "https://www.youtube.com/@AlmaPhysio"

# Includere anche le dirette (tab "Live")? Gli Shorts sono sempre esclusi.
INCLUDI_DIRETTE = False

# --- Fase 2: quali video trascrivere ------------------------------------------
# "tutti"          = tutti i video del canale (prima alimentazione e misti, poi gli altri)
# "alimentazione"  = solo i video ALIMENTAZIONE e MISTO (dati/video_nutrizione.csv)
VIDEO_DA_TRASCRIVERE = "tutti"

# --- Pause tra le richieste a YouTube (secondi, scelte a caso tra min e max) --
PAUSA_METADATI = (1.5, 4.0)      # Fase 1: lettura dei dettagli di ogni video
PAUSA_SOTTOTITOLI = (5.0, 10.0)  # Fase 2: download dei sottotitoli

# Se YouTube ci blocca, attese crescenti (secondi) prima di riprovare.
# Finiti i tentativi lo script si ferma: rilancialo piu' tardi, riprende da solo.
ATTESE_SE_BLOCCATI = [60, 180, 600, 1200]

# Se YouTube chiede di "confermare di non essere un bot", si possono usare i
# cookie del tuo browser (dove sei gia' collegato a YouTube). Esempi:
#   BROWSER_COOKIE = "firefox"    oppure "chrome", "edge", "safari"
BROWSER_COOKIE = None

# --- Paragrafi delle trascrizioni -------------------------------------------
# Un nuovo paragrafo inizia dopo almeno PARAGRAFO_MIN secondi, alla fine di una
# frase o dopo una pausa; comunque non oltre PARAGRAFO_MAX secondi.
PARAGRAFO_MIN = 30
PARAGRAFO_MAX = 60
# Se i sottotitoli hanno la punteggiatura, si aspetta la fine della frase
# fino a questi secondi oltre PARAGRAFO_MAX (cosi' le frasi non vengono spezzate).
PARAGRAFO_TOLLERANZA = 20

# --- Correzioni automatiche degli errori del riconoscimento vocale -----------
# "parola sbagliata": "parola giusta" (non distingue maiuscole/minuscole).
# Aggiungi qui gli errori ricorrenti che noti leggendo le trascrizioni.
CORREZIONI = {
    "Almafisio": "AlmaPhysio",
    "Alma Fisio": "AlmaPhysio",
    "Alma Physio": "AlmaPhysio",
    "Almaphisio": "AlmaPhysio",
}

# --- Stima token per la Fase 3 -----------------------------------------------
# Per l'italiano si stimano circa 1,5 token per parola (intervallo 1,3 - 1,7).
TOKEN_PER_PAROLA = 1.5

# --- Parole chiave per la classificazione -----------------------------------
# Sono "radici": vengono cercate all'inizio di una parola, senza distinguere
# maiuscole/minuscole. Es. "zuccher" trova zucchero, zuccheri, zuccherato.
# Si possono usare espressioni regolari semplici: (a|e) = a oppure e.

# Parole che indicano chiaramente ALIMENTAZIONE
ALIMENTAZIONE_FORTI = [
    "aliment", "nutri", "dieta", "diete", "dietolog", "dietist", "dietetic",
    "digiun", "cibo", "cibi", "mangi", "pasto", "pasti", "colazion", "pranzo", "cena\\b",
    "zuccher", "dolcific", "insulin", "glicem", "glucos", "diabet",
    "carboidrat", "protein", "lipid", "colesterol", "trigliceri",
    "integrator", "integrazione", "vitamin", "magnesio", "omega", "creatin", "collagen",
    "ferro\\b", "zinco", "curcum", "probiotic", "prebiotic",
    "dimagr", "perdere peso", "perdita di peso", "sovrappes", "obesit", "calori", "metaboli", "chetogen", "keto\\b",
    "intestin", "microbiot", "microbiom", "digest", "reflusso", "stitichez", "fibre",
    "frutta", "verdur", "legumi", "uova", "uovo", "carne", "pesce", "latte\\b", "latticin",
    "formagg", "glutine", "lattosio", "cereal", "caff(e|è)", "alcol", "vino",
    "olio d", "frutta secca", "antiossidant", "ultraprocessat", "junk food",
    "fame", "sazi", "steatosi", "fegato grasso", "resistenza insulinica",
    "semi\\b", "semini", "noci\\b", "mandorl", "nocciol", "avena", "chia\\b", "lino\\b",
    "cacao", "cioccolat", "yogurt", "kefir", "fermentat", "miele", "spezie", "zenzero",
    "aglio", "cipoll", "pomodor", "olive\\b", "avocado", "broccol", "bibit", "succhi",
    "snack", "ricett", "t(è|e) verde", "superfood",
]

# Parole legate all'alimentazione ma ambigue (da sole fanno scattare la revisione)
ALIMENTAZIONE_DEBOLI = [
    "grass", "peso\\b", "infiamm", "longevit", "invecchiament", "energia",
    "stanchezz", "ormon", "tiroid", "cortisol", "fegato", "pancia", "gonfior",
    "acqua", "idrataz", "pressione", "ipertension", "osteopor", "stile di vita", "calcio\\b",
    "salute metabolica", "pane", "pasta\\b", "riso\\b", "sale\\b", "bevand",
]

# Parole che indicano ALTRI argomenti (fisioterapia, esercizio, dolore...)
ALTRI_ARGOMENTI = [
    "schiena", "lombalg", "lombare", "cervical", "collo\\b", "ginocch", "spalla", "spalle",
    "anca\\b", "caviglia", "piede", "piedi", "polso", "gomito", "postur",
    "esercizi", "stretching", "allenament", "palestra", "muscol", "tendin", "ernia",
    "sciatic", "fisioterap", "riabilit", "mobilit", "artrosi", "menisc", "legament",
    "dolore", "contrattur", "scoliosi", "corsa\\b", "camminat", "yoga", "pilates",
    "massagg", "fascite", "plantare", "tunnel carpale", "emicrania", "mal di testa",
    "sonno", "dormire", "respiraz", "pavimento pelvico", "mal di", "squat", "addominal",
]
