# -*- coding: utf-8 -*-
"""
SCHEMA DELLE TEMATICHE (usato da 06_tematiche.py)
=================================================
AREE -> ARGOMENTI -> parole chiave (radici cercate all'inizio di una parola,
senza distinguere maiuscole/minuscole; si possono usare espressioni regolari).
Si possono aggiungere/togliere aree, argomenti e parole liberamente.
"""

AREE = {
    "ALIMENTAZIONE": {
        "Alimenti e bevande": [
            "cib[oi]", "aliment", "frutt", "verdur", "legumi", "lenticch", "uov[oa]", "carne", "pesce",
            "sardine", "latte\\b", "latticin", "formagg", "pane\\b", "pasta\\b", "riso\\b", "avena",
            "olio d", "olio di (oliva|cocco)", "aglio", "spezi", "zenzero", "curcum", "cannella",
            "chiodi? di garofano", "peperoncino", "cardamomo", "t[èe]\\b", "t[èe] verde", "matcha",
            "tisan", "infusi", "bevand", "bevi\\b", "caff[èe]", "cacao", "cioccolat", "miele", "semi\\b",
            "noci\\b", "arachidi", "frutta secca", "kefir", "yogurt", "fermentat", "aceto", "funghi",
            "banana", "datteri", "melograno", "barbabietola", "carot", "pomodor", "broccol",
            "quinoa", "soia", "brodo", "sushi", "burro", "sale\\b", "alcol", "vino", "mangi", "acqua",
        ],
        "Integratori, vitamine e minerali": [
            "integrator", "supplement", "vitamin", "magnesio", "omega", "creatin", "collagen", "zinco",
            "ferro\\b", "potassio", "iodio", "berberina", "spermidina", "coenzima", "glicina",
            "probiotic", "fermenti lattici", "adattogen", "astaxantina", "ergotioneina", "acido folico",
            "nutrient", "carenz",
        ],
        "Diete e digiuno": [
            "diet", "digiun", "chetogen", "keto\\b", "colazion", "pasto", "pasti", "cena\\b",
            "carboidrat", "protein", "zuccher", "dolcific", "calori", "restrizione calorica",
            "mangiare intuitivo", "nutrizion",
        ],
        "Peso e metabolismo": [
            "dimagr", "perdere peso", "perdi peso", "perdita di peso", "peso\\b", "grasso", "pancia",
            "obesit", "sovrappes", "metabolism", "ingrass", "fame", "sazi", "brucia",
        ],
    },
    "DOLORE E FISIOTERAPIA": {
        "Schiena e lombare": [
            "schiena", "lombal", "lombare", "ernia", "erni[ae] (del disco|lombare|discale)", "sciatic",
            "discopatia", "colpo della strega", "spondil", "iperlordosi", "lordosi", "scoliosi",
            "sacroiliac", "colonna", "l4", "l5", "vertebr", "gobba",
        ],
        "Collo, cervicale e mal di testa": [
            "cervical", "collo\\b", "colpo di frusta", "cervicobrachialgia", "mal di testa", "cefalea",
            "emicrania", "temporo ?mandibolare", "craniomandibolar", "bruxismo",
        ],
        "Spalla": ["spall[ae]", "cuffia dei rotatori", "sovraspinato", "scapol", "trapezio", "clavicola"],
        "Ginocchio": [
            "ginocch", "menisc", "crociato", "rotule", "condropatia", "osgood", "ginocchio (varo|valgo)",
            "bandelletta",
        ],
        "Anca, bacino e glutei": [
            "anca\\b", "glute", "piriforme", "pubalgia", "inguin", "trocanter", "psoas", "bacino",
            "sedere", "protesi all'anca",
        ],
        "Piede e caviglia": [
            "piede", "piedi", "caviglia", "fascite", "alluce", "metatars", "spina calcaneare", "plantar",
            "scarpe", "pronazione", "supinazione", "tallon",
        ],
        "Gomito, polso e mano": [
            "gomito", "epicondil", "polso", "tunnel carpale", "dit[ao]\\b", "pollice", "rizoartrosi",
            "mani\\b", "radio e ulna", "formicolio",
        ],
        "Articolazioni, tendini e muscoli": [
            "artrosi", "artrit", "articola", "cartilagin", "tendin", "tendine", "contrattur",
            "stiramento muscolare", "crampi", "rigidit", "scrocchi",
        ],
        "Dolore cronico e fibromialgia": [
            "dolore", "dolori", "fibromialgia", "sensibilizzazione", "dolore persistente", "neuropatia",
        ],
        "Riabilitazione e terapie": [
            "riabilita", "fisioterap", "manipolazion", "chiroprat", "osteopat", "fibrolisi", "tecar",
            "laser", "infiltrazion", "chirurgi", "operazion", "operar", "protesi", "frattur", "taping",
            "dry needling", "agopuntura", "ozonoterapia", "teleriabilitazione", "mulligan", "manovra",
            "trazion[ei] per", "terapie (fisiche|inutili)", "plantari", "massaggio", "neurodinamica",
            "decompressione",
        ],
    },
    "ESERCIZIO E MOVIMENTO": {
        "Ginnastica e allenamenti guidati": [
            "ginnastica", "allenament", "lezione", "routine", "classe di", "esercizi", "esercizio",
            "allenar", "workout",
        ],
        "Forza e massa muscolare": [
            "muscol", "forza\\b", "sarcopenia", "squat", "flessioni", "trazioni", "pesi\\b", "isometric",
            "glutei", "addominal", "core\\b", "calisthenics", "giubbotto zavorrato", "sbarra", "appender", "braccia", "gambe sottili",
            "cosce",
        ],
        "Stretching, yoga e mobilità": [
            "stretching", "yoga", "mobilit", "pilates", "flessibilit", "stiramento", "allungament",
            "risveglio articolare", "tai chi",
        ],
        "Postura": ["postur", "seduti davanti", "scrivania", "come stare seduti"],
        "Camminata, corsa e sport": [
            "cammin", "10\\.?000 passi", "passeggiat", "corsa", "correre", "runner", "maratona", "basket",
            "calcio\\b", "sport", "salto", "bici", "corda", "atlet", "golf", "nuoto", "vo2", "zona 2",
            "interval",
        ],
        "Equilibrio e prevenzione cadute": ["equilibrio", "cadut", "propriocetti"],
    },
    "CUORE E CIRCOLAZIONE": {
        "Pressione arteriosa": ["pression", "ipertens", "sistolica", "diastolica"],
        "Arterie, infarto e ictus": [
            "arteri", "infart", "ictus", "cuore", "cardi", "placc[ah]e? (nelle|arterios)", "placca arterios",
            "coagul", "trombosi", "emorragia", "ischemic", "stent", "calcium score", "vasi sanguigni",
            "attacco di cuore", "attacchi di cuore",
        ],
        "Circolazione, vene e gambe gonfie": [
            "circolazion", "vene\\b", "varic", "gambe gonfie", "gambe pesanti", "edema", "caviglie gonfie",
            "piedi freddi",
        ],
        "Colesterolo, glicemia e diabete": [
            "colesterol", "trigliceri", "statin", "glicemi", "zucchero nel sangue", "zucchero [eè] alto", "diabet", "insulin", "glucos", "ldl",
        ],
    },
    "CERVELLO, SONNO E MENTE": {
        "Sonno": ["sonno", "dormi", "insonni", "andare a letto", "notte", "notturn", "materasso", "cuscino", "letto"],
        "Memoria, demenza e cervello": [
            "demenza", "alzheimer", "memoria", "cervell", "cognitiv", "neurolog", "parkinson", "mente lucida",
        ],
        "Ansia, stress e umore": [
            "ansia", "stress", "depressi", "serotonin", "dopamin", "cortisol", "umore", "esaurimento",
            "emozion", "paura", "solitudine",
        ],
        "Crescita personale e filosofia": [
            "abitudin", "autodisciplina", "stoic", "seneca", "marco aurelio", "taois", "nietzsche",
            "peterson", "felicit", "autostima", "forza di volont", "ego\\b", "pensieri", "rimandare",
            "persone di successo", "minimalista", "bibbia", "senso della vita", "lasciare andare",
            "persone negative", "sforzo inverso", "imparare", "intelligent", "decision", "scelte difficili",
            "perdere tempo", "rubano il tempo", "motivat", "pigro", "cellulare",
        ],
        "Respirazione e meditazione": [
            "respira", "meditazion", "wim hof", "nervo vago", "rilassament", "buteyko", "diaframma",
            "toni binaurali",
        ],
    },
    "LONGEVITÀ E INVECCHIAMENTO": {
        "Longevità e anti-età": [
            "longevit", "invecchia", "anti-?et[àa]", "centenari", "vivere a lungo", "vivere più a lungo",
            "vivr[aà]i 100", "100 anni", "telomer", "mitocondri", "senolitic", "pi[uù] giovane", "ringiovan",
            "allunga(re)? la vita", "elisir", "rapamicina", "staminali", "anni di vita", "zone in cui si vive",
            "okinawa", "blue zone", "zone azzurre", "dna",
        ],
    },
    "UOMO, DONNA E SESSUALITÀ": {
        "Prostata e salute maschile": [
            "prostat", "psa\\b", "testosteron", "erezion", "erettil", "eiaculazion", "pene\\b", "viagra",
            "cialis", "infertilit[aà] maschile",
        ],
        "Salute femminile": [
            "menopausa", "gravidanza", "parto", "cesareo", "endometriosi", "vulvodinia", "seno\\b",
            "mammografia", "diastasi", "incinta", "prodotti femminili", "ormonale nelle donne",
        ],
        "Pavimento pelvico e vescica": [
            "pavimento pelvico", "incontinenza", "vescica", "minzion", "nicturia", "pip[iì]\\b",
            "urinar", "cistite", "pudendo", "dolore pelvico", "perdite\\b", "emorroidi",
        ],
        "Sessualità": ["sessual", "orgasmo", "libido", "masturbazion", "sesso"],
    },
    "ORGANI E MALATTIE": {
        "Tumori": ["tumor", "cancr", "metastasi", "midollo", "chemioterapia", "melanoma", "linfoma", "oncolog"],
        "Intestino e digestione": [
            "intestin", "colon\\b", "stitichez", "stipsi", "gonfior", "pancia gonfia", "stomaco gonfio",
            "gas\\b", "flatulenz", "reflusso", "stomaco", "gastrit", "diverticol", "digest", "cacca",
            "feci", "candida", "vermi intestinali", "microbiot", "permeabilit",
        ],
        "Fegato, reni e pancreas": [
            "fegato", "ren[ei]\\b", "renal", "pancreas", "cistifellea", "calcoli", "epatic", "cirrosi",
            "acido urico", "gotta", "steatosi", "nefrolog",
        ],
        "Vie respiratorie e difese immunitarie": [
            "polmon", "catarro", "muco", "gola", "tosse", "raffreddore", "virus", "covid", "vaccin",
            "sistema immunitario", "infezion", "antibiotic", "asma", "febbre", "influenz", "ammalar",
            "ammali", "aids", "herpes", "batteri", "coronavirus", "zanzar",
        ],
        "Ormoni e tiroide": ["tiroid", "ormon", "ipotiroid"],
        "Infiammazione": ["infiamm", "antinfiammator", "anti infiammator"],
        "Ossa e osteoporosi": [
            "osteopor", "ossa\\b", "osse[oa]\\b", "densit[aà] ossea", "mineralizzazione ossea", "midollo osseo",
        ],
    },
    "PELLE, DENTI E SENSI": {
        "Pelle, capelli e aspetto": [
            "pelle", "rughe", "viso", "macchie", "acne", "capell", "unghie", "verruche", "eczema",
            "crema solare", "borse sotto", "doppio mento", "lifting", "guance", "cellulite", "porri",
            "bellezza", "funghi? (delle|dalle|sotto le) unghie", "piede d'atleta", "odore",
        ],
        "Denti e bocca": [
            "denti", "gengiv", "carie", "alito", "alitosi", "bocca", "dentifricio", "afta", "mascella",
            "tartaro", "colluttorio",
        ],
        "Occhi e vista": ["occhi", "vista", "cataratta", "oculari", "vedere meglio"],
        "Orecchie, acufene e vertigini": ["acufen", "udito", "orecchi", "cerume", "vertigin", "auricolari"],
    },
    "FARMACI, ESAMI E SANITÀ": {
        "Farmaci e sostanze": [
            "(?<!senza )farmac", "statine", "aspirina", "ibuprofene", "tachipirina", "metformina", "losartan",
            "valium", "diazepam", "sonnifer", "ozempic", "glp-1", "pillol", "cannabi", "cbd", "marijuana",
            "medicin[ae]\\b", "antidepressiv",
        ],
        "Esami, analisi e diagnosi": [
            "analisi", "esam[ei]", "test\\b", "screening", "risonanza", "psa\\b", "valore", "parametro",
            "biopsia", "diagnosi", "sintomi", "segni", "segnal", "check up",
        ],
        "Critica del sistema sanitario": [
            "business", "big farma", "industria", "sanit[aà]", "medici lo nascondono", "inutil",
            "truffa", "inganno", "fabbrica di malati", "nascost", "non ti dicono", "nessuno ti dice",
            "il tuo medico non", "osceno", "fiducia nel sistema",
        ],
    },
    "AMBIENTE E ABITUDINI QUOTIDIANE": {
        "Tossine e ambiente": [
            "plastica", "pesticid", "tossin", "inquin", "padella", "friggitrice", "wifi", "telefonin",
            "prodotti per la casa", "dal tuo bagno", "tatuaggi", "riscaldamento globale", "ftalati",
            "microplastic", "disintossic", "depura",
        ],
        "Abitudini e routine quotidiane": [
            "sauna", "doccia", "sole\\b", "infrarossi", "routine mattutina", "abitudine sotto",
            "seduto", "stai seduto", "mattin", "serali", "sera\\b",
        ],
    },
    "CANALE E VARIE": {
        "Comunicazioni del canale": [
            "almaphysio", "physiotherapy", "fisioterapia espa", "canale", "africa", "una sorpresa", "top almaphysio", "netflix", "libri",
            "100 libri", "studio sui gemelli",
        ],
    },
}

# Aree che non devono diventare "principali" solo per parole generiche
AREE_SECONDARIE_SOLO = {"CANALE E VARIE"}

PUBBLICO = {
    "Over 50 e anziani": [
        "over ?(40|50|60|65|70)", "dopo i (40|50|60|65|70)", "pi[uù] di (40|50|60|65|70) anni", "anzian", "nonni", "nonna", "terza et[àa]",
        "(50|60|65|70) anni", "persone anziane", "senior",
    ],
    "Donne": ["donn[ae]", "femminil", "menopausa", "gravidanza", "mamma", "madre"],
    "Uomini": ["uomin[io]", "maschil", "prostat", "testosteron", "pene\\b"],
    "Sportivi": ["sportiv", "atlet", "runner", "maratona", "basket", "calcio\\b", "palestra", "calisthenics"],
    "Principianti": ["principianti", "da principiante"],
    "Bambini": ["bambin"],
}

FORMATO = {
    "Esercizi pratici": [
        "\\d+ esercizi", "esercizi (per|di|da|con|a casa|correttivi|in)", "esercizio (per|di|che)", "stretching",
        "rinforzo", "4 zampe", "manovra", "automassaggio", "trazioni? (per|fantastiche)", "manipolazion",
        "fisioterapia (milano|schiena|ginocchio|spalla|anca|cervicale|caviglia)\\s*-", "allenati", "pancia piatta",
        "ginnastica", "lezione", "routine di", "classe di", "yoga con", "yoga per", "meditazione guidata",
        "pratica serale", "\\d+ min(uti)? (di|con)", "^\\d+ giorno:", "allenamento per principianti",
        "esercizi con gianluca", "per nonni", "seguimi",
    ],
    "Testimonianza o caso clinico": [
        "testimonianza", "storie vere", "storia (vera|a lieto fine)", "ecco cosa succede (al|alla|ai) su[oia]",
        "la mia storia", "ho mangiato", "mia madre", "mio padre", "mia nonna", "caso medico", "ha iniziato",
        "ha fatto", "prende un", "trascura", "soffre di", "così ho", "ho risolto", "ho curato",
        "ho iniziato", "ho bevuto", "non mi ammalo", "ho \\d+ anni", "mangiava", "masticava",
    ],
    "Short": ["#?shorts\\b"],
    "Reazione o analisi di studi": [
        "studio", "studi\\b", "ricerca", "scienza", "scientific", "reagisce", "dibattito",
    ],
}
