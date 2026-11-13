#!/usr/bin/env python3
"""Procedural medicine and drug name generator inspired by Fantasy Name Generators.

Comprehensive pharmaceutical morpheme database based on WHO INN stems, USAN rules,
ATC chemical classes, and clinical trade branding. Generates single entities and
dual-compound formulations with phonotactic boundary elision.
"""

import random
import re
import sys

# --- Morpheme Banks (Exhaustive Pharmaceutical / USAN / INN) ---

PREFIXES: tuple[str, ...] = (
    # A
    "Aba", "Abac", "Abare", "Abe", "Acal", "Acet", "Acetyl", "Acita", "Acladi",
    "Acro", "Acti", "Acu", "Acyl", "Adal", "Adde", "Adede", "Adeno", "Adip",
    "Afata", "Afini", "Agane", "Albu", "Alcur", "Aldo", "Alem", "Aleva", "Alfa",
    "Algluco", "Aliske", "Allop", "Allot", "Almo", "Amant", "Amben", "Ambris",
    "Amik", "Amle", "Amlo", "Amox", "Amphe", "Ampi", "Anas", "Ancro", "Angio",
    "Anso", "Apex", "Apre", "Apti", "Aque", "Arbupo", "Arga", "Arip", "Ase",
    "Asti", "Ataza", "Aten", "Atomo", "Ator", "Atrac", "Avana", "Axiti", "Azaci",
    "Azath", "Azela", "Azith", "Aztre",
    # B
    "Baclo", "Bacter", "Balsal", "Barici", "Beda", "Beme", "Benaze", "Bendi",
    "Beni", "Bento", "Bera", "Besi", "Beva", "Bex", "Bical", "Bimat", "Bio",
    "Bipro", "Briva", "Broma", "Budes", "Bupren", "Bupi", "Bupro", "Buser",
    "Buspi", "Butor",
    # C
    "Caba", "Caboz", "Caff", "Calci", "Cande", "Capro", "Carba", "Carbi", "Cardi",
    "Carfe", "Carvi", "Casp", "Ceclo", "Cef", "Ceftri", "Cefuro", "Cele", "Ceph",
    "Cere", "Ceti", "Cevi", "Chlo", "Cilosta", "Cimet", "Cinac", "Cipro", "Cita",
    "Clad", "Clal", "Clari", "Clem", "Clinda", "Cloba", "Clomi", "Clon", "Clop",
    "Clor", "Cloza", "Cobi", "Coles", "Cori", "Cortic", "Crin", "Cris", "Cyclo",
    "Cypro",
    # D
    "Daba", "Dacla", "Dapagli", "Dapso", "Darb", "Dasa", "Deci", "Defla", "Dela",
    "Dema", "Deno", "Derma", "Deslo", "Desmo", "Dexa", "Dexlans", "Diac", "Diaze",
    "Diclo", "Dilti", "Diphen", "Diso", "Doba", "Dola", "Done", "Dora", "Dorna",
    "Doxa", "Doxo", "Dron", "Dulo", "Duta",
    # E
    "Echo", "Eculi", "Edoxa", "Efavi", "Eflorn", "Elag", "Elet", "Elig", "Eliquis",
    "Elot", "Eltrom", "Eme", "Emoxi", "Empi", "Empa", "Ena", "Encor", "Enoxa",
    "Enta", "Enza", "Epi", "Eplere", "Epopro", "Epro", "Epti", "Erib", "Erloti",
    "Ergo", "Ertap", "Erythr", "Escita", "Esome", "Estro", "Eszopi", "Etane",
    "Eto", "Etra", "Ever", "Evolo", "Exene", "Exem", "Exete", "Ezeti",
    # F
    "Faci", "Famo", "Febux", "Felo", "Fenbu", "Feno", "Fenta", "Feso", "Fex",
    "Fida", "Filtro", "Fina", "Fingo", "Flav", "Flecai", "Fludar", "Flum", "Flun",
    "Fluor", "Fluox", "Fluti", "Fluva", "Fondap", "Formo", "Fosam", "Fosfo",
    "Fosin", "Furo",
    # G
    "Gaba", "Gado", "Galant", "Gani", "Ganci", "Gati", "Gefiti", "Gemci", "Gemfi",
    "Geno", "Geva", "Gila", "Gla", "Glicla", "Glime", "Glipi", "Gluc", "Golu",
    "Goni", "Goser", "Grani",
    # H
    "Haemo", "Halo", "Hemi", "Hepar", "Huma", "Hura", "Hydra", "Hydro", "Hylan",
    # I
    "Ibra", "Ibru", "Ibu", "Ico", "Idaru", "Ifos", "Ila", "Ilu", "Imat", "Imi",
    "Immu", "Inda", "Indo", "Inot", "Ipra", "Irbe", "Irino", "Isavu", "Iso",
    "Isotret", "Iva", "Ixaze",
    # K - L
    "Kanu", "Keta", "Keto", "Klex", "Labe", "Laci", "Laco", "Lactu", "Lami",
    "Lamo", "Lanre", "Lanso", "Lapa", "Laro", "Lasmi", "Lata", "Ledi", "Leflu",
    "Lemo", "Lena", "Lenti", "Lera", "Letro", "Leuco", "Leval", "Levet", "Levo",
    "Lido", "Lina", "Line", "Lio", "Lipi", "Lira", "Lisi", "Liva", "Lodi",
    "Lome", "Lopi", "Lora", "Losa", "Lova", "Loxo", "Luma", "Luras", "Lute",
    # M
    "Maci", "Mara", "Mavre", "Mebend", "Meca", "Meclo", "Medro", "Meflo", "Mega",
    "Mela", "Melo", "Mepoli", "Mequi", "Mercap", "Mero", "Mesal", "Mester",
    "Metfo", "Metha", "Methodo", "Metho", "Methy", "Metocl", "Metron", "Mica",
    "Micon", "Mida", "Mido", "Mife", "Miga", "Mina", "Mino", "Mira", "Mirta",
    "Mito", "Mivac", "Mizo", "Moclo", "Moda", "Moexi", "Mome", "Mont", "Morp",
    "Moxi", "Mupir", "Myco",
    # N
    "Nabi", "Nado", "Nafci", "Nafto", "Nalo", "Naltr", "Nandro", "Napa", "Napro",
    "Nara", "Naso", "Nata", "Nateg", "Nedo", "Nefa", "Nela", "Nelo", "Neo",
    "Neti", "Nevi", "Nex", "Nico", "Nife", "Nilo", "Nima", "Nintra", "Nirapa",
    "Niso", "Niti", "Nitro", "Niva", "Nivo", "Nola", "Nore", "Norfl", "Nortri",
    "Novi", "Nutri", "Nutro",
    # O
    "Obinu", "Ocri", "Octre", "Oflo", "Olan", "Olapa", "Olme", "Olo", "Omal",
    "Ome", "Onda", "Opi", "Opre", "Orex", "Orli", "Orphe", "Osel", "Osim",
    "Ospem", "Otelo", "Oxali", "Oxaze", "Oxcar", "Oxybu", "Oxyco",
    # P
    "Pali", "Palonos", "Pancre", "Pani", "Panto", "Parox", "Pazo", "Pega",
    "Pelo", "Pembre", "Pemi", "Peme", "Penfl", "Peni", "Pentox", "Pera", "Peri",
    "Perin", "Pha", "Phar", "Pheno", "Piloc", "Pime", "Pimo", "Pindo", "Piog",
    "Pipe", "Pira", "Pirfe", "Piro", "Pita", "Pito", "Pleca", "Pomal", "Pona",
    "Posa", "Prami", "Pras", "Prav", "Prazo", "Pred", "Prega", "Prepo", "Priloc",
    "Prima", "Procai", "Profe", "Prole", "Prome", "Prop", "Prot", "Pruca",
    # Q - R
    "Queti", "Quina", "Rabe", "Ralox", "Ralte", "Rami", "Rani", "Rano", "Rasa",
    "Ravu", "Reba", "Refli", "Regora", "Rela", "Remi", "Reno", "Repa", "Resli",
    "Reta", "Ribo", "Rifa", "Rilu", "Rime", "Risa", "Rised", "Rispe", "Rito",
    "Riva", "Rixo", "Romi", "Ropi", "Rosu", "Roxa", "Ruba", "Rufa", "Ruxo",
    # S
    "Sacro", "Salme", "Saprop", "Saqui", "Sara", "Sari", "Savu", "Saxagli",
    "Secu", "Sele", "Selu", "Sema", "Sevo", "Sila", "Silde", "Silo", "Simva",
    "Sina", "Sita", "Sive", "Sofos", "Solif", "Soma", "Soni", "Sora", "Sota",
    "Spiri", "Spiron", "Stav", "Stela", "Stiri", "Sucre", "Sufen", "Sugam",
    "Sulb", "Sulfa", "Sulo", "Suma", "Suni",
    # T
    "Taba", "Tafa", "Tafami", "Tala", "Tali", "Tamoxi", "Tamsu", "Tava", "Taza",
    "Tazo", "Tebi", "Teco", "Teda", "Tego", "Tela", "Telmi", "Temo", "Teno",
    "Tepa", "Terbi", "Terif", "Teta", "Tetra", "Tezo", "Theop", "Thera", "Thio",
    "Tiaga", "Tica", "Tige", "Tilu", "Timo", "Tio", "Tiro", "Tivi", "Tofa",
    "Tola", "Tolva", "Topi", "Tora", "Tore", "Trabi", "Trade", "Trama", "Tran",
    "Trasto", "Travo", "Trazo", "Treme", "Trepro", "Treti", "Triam", "Tria",
    "Trifu", "Trim", "Triva", "Tropi", "Troxi",
    # U - V
    "Ubro", "Ulip", "Ume", "Upa", "Uro", "Urso", "Uste", "Vala", "Valg", "Valp",
    "Valsa", "Vanda", "Vapri", "Varde", "Vare", "Vaso", "Veda", "Vela", "Vemf",
    "Vemur", "Vene", "Veno", "Vera", "Viba", "Vibra", "Viga", "Vila", "Vildagli",
    "Vimce", "Vino", "Vivo", "Vora", "Vori", "Vorti", "Voxil",
    # X - Z
    "Xala", "Xanth", "Xeno", "Xica", "Ximo", "Xylom", "Zafi", "Zale", "Zana",
    "Zano", "Zico", "Zido", "Zila", "Zile", "Zinco", "Zipra", "Zirco", "Zithro",
    "Zoa", "Zofi", "Zol", "Zoled", "Zolmi", "Zoni", "Zopic", "Zoti",
)

INFIXES: tuple[str, ...] = (
    "ba", "be", "bi", "bo", "bu",
    "ca", "ce", "ci", "clo", "co", "cor", "cro", "cu",
    "da", "de", "di", "do", "dopa", "dra", "du",
    "fa", "fe", "fen", "fi", "fla", "flo", "fo", "fu",
    "ga", "ge", "gi", "gla", "glo", "go", "gra", "gu",
    "la", "le", "li", "lo", "lu",
    "ma", "me", "mi", "mo", "mu",
    "na", "ne", "ni", "no", "nu",
    "pa", "pe", "pen", "pi", "pla", "ple", "plo", "po", "pra", "pro", "pu",
    "ra", "re", "ri", "ro", "ru",
    "sa", "se", "si", "so", "ste", "su",
    "ta", "te", "ti", "to", "tra", "tri", "tro", "tu",
    "va", "ve", "vi", "vo", "vu",
    "xa", "xe", "xi", "xo", "xu",
    "za", "ze", "zi", "zo", "zu",
)

SUFFIXES_INN: tuple[str, ...] = (
    # A
    "abine",    # Nucleoside antimetabolites (e.g. Gemcitabine)
    "ac",       # Anti-inflammatory agents, ibufenac derivatives
    "adol",     # Analgesics
    "afil",     # PDE-5 inhibitors (e.g. Sildenafil, Tadalafil)
    "algron",   # Alpha-1 adrenoreceptor agonists
    "alol",     # Combined alpha and beta blockers (e.g. Labetalol)
    "amivir",   # Neuraminidase inhibitors (e.g. Oseltamivir)
    "anib",     # Angiogenesis inhibitors (e.g. Pazopanib)
    "anserin",  # 5-HT2 receptor antagonists
    "april",    # ACE inhibitors (e.g. Enalapril, Ramipril, Captopril)
    "arol",     # Anticoagulants (e.g. Dicumarol)
    "artan",    # Angiotensin II receptor antagonists (e.g. Losartan, Valsartan)
    "ase",      # Enzymes (general biocatalysts)
    "asone",    # Corticosteroid derivatives
    "ast",      # Antiasthmatics, leukotriene inhibitors (e.g. Montelukast)
    "azenil",   # Benzodiazepine receptor agonists/antagonists
    "azepam",   # Classical benzodiazepines (e.g. Diazepam, Clonazepam)
    "azepate",  # Benzodiazepine salts
    "azolam",   # Triazolo-benzodiazepines (e.g. Alprazolam, Midazolam)
    "azone",    # Anti-inflammatory pyrazolone derivatives
    "azosin",   # Alpha-1 blockers (e.g. Doxazosin, Prazosin)
    # B
    "bactam",   # Beta-lactamase inhibitors (e.g. Sulbactam, Tazobactam)
    "bamate",   # Carbamate tranquilizers (e.g. Meprobamate)
    "barbital", # Barbiturate sedatives (e.g. Phenobarbital)
    "bendazole",# Anthelmintics (e.g. Albendazole, Mebendazole)
    "bermin",   # Vascular growth factors
    "betasol",  # Topical corticosteroid derivatives (e.g. Clobetasol)
    "bloc",     # Adrenergic / receptor antagonists (trade brand stem)
    "bufen",    # NSAID fenbufen derivatives
    "butazone", # Phenylbutazone analgesics
    # C
    "caine",    # Local anesthetics (e.g. Lidocaine, Bupivacaine)
    "calciol",  # Vitamin D analogues (e.g. Calcitriol)
    "capone",   # COMT inhibitors for Parkinson's (e.g. Entacapone)
    "cavir",    # Carbocyclic nucleosides (e.g. Abacavir)
    "cidin",    # Natural peptide antibiotics (e.g. Gramicidin)
    "cillin",   # Penicillin antibiotics (e.g. Amoxicillin, Ampicillin)
    "clidine",  # Muscarinic receptor agonists
    "cog",      # Blood coagulation factors
    "conazole", # Systemic azole antifungals (e.g. Fluconazole, Ketoconazole)
    "coxib",    # Selective COX-2 inhibitors (e.g. Celecoxib, Etoricoxib)
    "criptine", # Dopamine receptor agonists (e.g. Bromocriptine)
    "curium",   # Neuromuscular blocking agents (e.g. Atracurium)
    "curonium", # Steroidal neuromuscular blockers (e.g. Rocuronium)
    "cycline",  # Tetracycline antibiotics (e.g. Doxycycline, Minocycline)
    # D
    "dapsone",  # Antimycobacterials
    "denu",     # Nucleoside mimics
    "derm",     # Dermatological barrier agents
    "dex",      # Dextrorotatory / commercial steroid suffix
    "dilol",    # Vasodilating beta-blockers (e.g. Carvedilol)
    "dipine",   # Dihydropyridine calcium channel blockers (e.g. Amlodipine)
    "dopa",     # Dopaminergic agents (e.g. Levodopa)
    "doxil",    # Anthracycline liposomal variants
    "dronate",  # Bisphosphonates (e.g. Alendronate, Zoledronate)
    "dutant",   # Neurokinin tachykinin antagonists
    # E
    "ectin",    # Antiparasitics (e.g. Ivermectin)
    "emp",      # Empiric broad-spectrum stem
    "epate",    # Carboxylic esters
    "eptacog",  # Recombinant blood factors
    "erol",     # Bronchodilators / phenethylamines (e.g. Salbutamol, Formoterol)
    "eridine",  # Opioid analgesics (e.g. Pethidine)
    "etaner",   # Fusion protein receptor decoys (e.g. Etanercept)
    "exate",    # Antimetabolites (e.g. Methotrexate)
    # F
    "farnib",   # Farnesyltransferase inhibitors
    "fen",      # Fenamic / profen analgesics
    "fenac",    # Acetic acid NSAIDs (e.g. Diclofenac, Nepafenac)
    "fentanyl", # Synthetic opioid analgesics (e.g. Fentanyl, Sufentanil)
    "fiban",    # Glycoprotein IIb/IIIa antagonists (e.g. Tirofiban)
    "fibrate",  # PPAR-alpha lipid regulators (e.g. Fenofibrate)
    "fovir",    # Acyclic nucleotide antivirals (e.g. Tenofovir)
    "formine",  # Biguanide antidiabetics (e.g. Metformin)
    "frine",    # Sympathomimetic vasoconstrictors (e.g. Phenylephrine)
    "fungin",   # Echinocandin antifungals (e.g. Caspofungin, Anidulafungin)
    # G
    "gard",     # Barrier / prophylactic protective agent
    "giline",   # MAO-B inhibitors (e.g. Selegiline, Rasagiline)
    "gliflozin",# SGLT2 glucose cotransporter inhibitors (e.g. Empagliflozin)
    "gliptin",  # DPP-4 dipeptidyl peptidase inhibitors (e.g. Sitagliptin)
    "glitazone",# Thiazolidinedione insulin sensitizers (e.g. Pioglitazone)
    "glutide",  # GLP-1 receptor agonists (e.g. Semaglutide, Liraglutide)
    "gestrel",  # Synthetic progestogens (e.g. Levonorgestrel)
    "grel",     # ADP platelet aggregation inhibitors (e.g. Clopidogrel)
    "grelor",   # Direct P2Y12 platelet antagonists (e.g. Ticagrelor)
    # K - L
    "kacin",    # Aminoglycosides related to amikacin
    "kiren",    # Renin inhibitors (e.g. Aliskiren)
    "lan",      # Prostaglandin / vasodilator analogues
    "lase",     # Thrombolytic or metabolic enzymes
    "letra",    # Fixed-dose combination antiretrovirals
    "leukon",   # Interleukin / cytokine modifiers
    "lutamide", # Androgen receptor inhibitors (e.g. Enzalutamide, Apalutamide)
    # M
    "mab",      # Monoclonal antibodies (e.g. Infliximab)
    "melagon",  # Melanocortin receptor agonists
    "meline",   # Muscarinic cholinergic modulators
    "mentin",   # Beta-lactamase inhibitor combos
    "mestane",  # Aromatase inhibitors (e.g. Exemestane)
    "micin",    # Micromonospora-derived aminoglycosides (e.g. Gentamicin)
    "mine",     # Bioactive amines
    "mustine",  # Alkylating antineoplastics (e.g. Carmustine)
    "mycin",    # Streptomyces-derived antibiotics (e.g. Erythromycin)
    # N
    "namic",    # Fenamate anti-inflammatory acids
    "navir",    # HIV/HCV protease inhibitors (e.g. Ritonavir, Darunavir)
    "nidazole", # Nitroimidazole antiparasitics (e.g. Metronidazole)
    # O
    "olol",     # Beta-blockers (e.g. Propranolol, Atenolol, Bisoprolol)
    "one",      # Bioactive steroid / ketone backbone
    "onide",    # Acetonide corticosteroids (e.g. Budesonide, Desonide)
    "operidol", # Butyrophenone neuroleptics (e.g. Haloperidol)
    "orphan",   # Morphine-related opioid modulators (e.g. Dextrorphan)
    "oxacin",   # Quinolone/fluoroquinolone antibiotics (e.g. Ciprofloxacin)
    "oxime",    # Hydroxyimino derivatives
    # P
    "pamide",   # Diuretic sulfonamides (e.g. Indapamide)
    "panib",    # Receptor tyrosine kinase inhibitors
    "parib",    # PARP inhibitors (e.g. Olaparib, Niraparib)
    "parin",    # Low-molecular-weight heparins (e.g. Enoxaparin)
    "penem",    # Carbapenem broad-spectrum antibiotics (e.g. Meropenem)
    "peridone", # Neuroleptic antipsychotics (e.g. Risperidone)
    "phen",     # Analgesic / antipyretic core
    "prazole",  # Proton pump inhibitors (e.g. Omeprazole, Pantoprazole)
    "pressin",  # Vasopressin / antidiuretic peptides
    "pril",     # ACE inhibitors (e.g. Captopril, Lisinopril)
    "prost",    # Prostaglandin analogues (e.g. Latanoprost)
    # R
    "racil",    # Uracil-related antineoplastics (e.g. Fluorouracil)
    "rate",     # Therapeutic salt / conjugated ester
    "relin",    # Gonadotropin-releasing peptides
    "retin",    # Retinoic acid analogues (e.g. Tretinoin, Alitretinoin)
    "rolac",    # NSAID acetic acids (e.g. Ketorolac)
    "ronate",   # Bisphosphonate salts (e.g. Risedronate)
    "rubicin",  # Anthracycline antineoplastics (e.g. Doxorubicin)
    # S
    "salan",    # Brominated salicylanilides
    "semide",   # Loop diuretics (e.g. Furosemide, Torsemide)
    "set",      # Serotonin 5-HT3 receptor antagonists
    "setron",   # Serotonin antiemetics (e.g. Ondansetron, Granisetron)
    "side",     # Glycoside / cardiotonic active
    "sine",     # Basic amine pharmacophore
    "sone",     # Glucocorticoid steroids (e.g. Prednisone, Dexamethasone)
    "statin",   # HMG-CoA reductase inhibitors (e.g. Atorvastatin, Rosuvastatin)
    "steride",  # 5-alpha reductase inhibitors (e.g. Finasteride, Dutasteride)
    "stine",    # Vinca alkaloids (e.g. Vinblastine)
    "syn",      # Synthetic regulatory peptide
    # T
    "tadine",   # Tricyclic antihistamines / antivirals (e.g. Loratadine)
    "taxel",    # Taxane antimicrotubular antineoplastics (e.g. Paclitaxel)
    "telase",   # Recombinant tissue plasminogen enzymes
    "terol",    # Beta-2 bronchodilators (e.g. Formoterol, Salmeterol)
    "tiazem",   # Benzothiazepine calcium blockers (e.g. Diltiazem)
    "tide",     # Bioactive synthetic peptides
    "tine",     # Neurotransmitter uptake inhibitors (e.g. Fluoxetine)
    "tinib",    # Tyrosine kinase inhibitors (e.g. Imatinib, Erlotinib)
    "tiapine",  # Dibenzothiazepine antipsychotics (e.g. Quetiapine)
    "tracin",   # Polypeptide antibiotics (e.g. Bacitracin)
    "tretin",   # Systemic retinoids (e.g. Acitretin)
    "trim",     # Dihydrofolate reductase inhibitors (e.g. Trimethoprim)
    "triptan",  # 5-HT1B/1D antimigraine agonists (e.g. Sumatriptan)
    "trope",    # Neurotropic / endocrine targeting molecules
    # U - Z
    "uracil",   # Pyrimidine uracil analogues
    "vaptan",   # Vasopressin V2 receptor antagonists (e.g. Tolvaptan)
    "verine",   # Spasmolytics
    "vir",      # Antivirals (e.g. Acyclovir, Ganciclovir)
    "vital",    # Tonic / metabolic support formulation
    "vudine",   # Zidovudine-related antiretroviral nucleosides
    "xime",     # Cephalosporin oximes (e.g. Cefuroxime)
    "zepam",    # Benzodiazepine tranquilizers
    "zepine",   # Tricyclic antiepileptics (e.g. Carbamazepine)
    "zine",     # Phenothiazines / Piperazines
    "zolamide", # Carbonic anhydrase inhibitors (e.g. Acetazolamide)
    "zole",     # Azole antifungals / antiparasitics
    "zumab",    # Humanized monoclonal antibodies (e.g. Trastuzumab)
)


# --- Phonotactic Morpheme Cleaning & Sandhi Logic ---

def clean_join(parts: list[str]) -> str:
    """Join morphemes applying phonotactic sandhi, boundary de-duplication, and elision.

    >>> clean_join(["Uro", "oxime"])
    'Uroxime'
    >>> clean_join(["Caff", "criptine"])
    'Cafcriptine'
    >>> clean_join(["Clal", "lan"])
    'Clalan'
    >>> clean_join(["Adede", "eptacog"])
    'Adedeptacog'
    >>> clean_join(["Amlo", "april"])
    'Amlapril'
    >>> clean_join(["Bex", "xime"])
    'Bexime'
    """
    vowels = "aeiou"
    res = parts[0].lower()

    for next_part in parts[1:]:
        b = next_part.lower()
        if not b:
            continue

        # 1. Deduplicate identical characters at boundary (e.g. Uro + oxime -> Uroxime, Clal + lan -> Clalan)
        while res and b and res[-1] == b[0]:
            b = b[1:]
        if not b:
            continue

        # 2. Vowel hiatus resolution: elide terminal vowel of prefix before suffix vowel
        # (e.g. Amlo + april -> Amlapril, Uro + oxime -> Uroxime)
        if res[-1] in vowels and b[0] in vowels:
            if res[-1] == b[0] or res[-1] in ("a", "o", "e"):
                res = res[:-1]

        # 3. Double consonant reduction before another consonant (e.g. Caff + criptine -> Cafcriptine)
        if len(res) >= 2 and res[-1] == res[-2] and res[-1] not in vowels and b[0] not in vowels:
            res = res[:-1]

        # 4. Awkward consonant clusters at boundary (xc -> c, xs -> s, xx -> x)
        if res.endswith("x") and b[0] in ("c", "s", "x"):
            res = res[:-1]

        res += b

    # Clean residual triple identical letters or duplicated vowels (aa, ii, oo, uu)
    res = re.sub(r"([a-z])\1{2,}", r"\1", res)
    res = re.sub(r"(aa|ii|oo|uu)", lambda m: m.group(1)[0], res)

    return res.capitalize()


def make_word() -> str:
    """Generate a single realistic pharmaceutical word using phonotactic joining."""
    prefix = random.choice(PREFIXES)
    suffix = random.choice(SUFFIXES_INN)

    # 40% chance of adding connective infix for 3-syllable medicines
    if random.random() < 0.40:
        infix = random.choice(INFIXES)
        parts = [prefix, infix, suffix]
    else:
        parts = [prefix, suffix]

    return clean_join(parts)


def generate_medicine(force_compound: bool | None = None) -> str:
    """Generate a single entity or a compound pair (brand + generic / dual active).

    >>> isinstance(generate_medicine(force_compound=False), str)
    True
    >>> len(generate_medicine(force_compound=True).split())
    2
    """
    is_compound = random.random() < 0.45 if force_compound is None else force_compound

    if not is_compound:
        return make_word()

    word1 = make_word()
    word2 = make_word()
    while word2 == word1:
        word2 = make_word()

    return f"{word1} {word2}"


def generate_batch(count: int = 15) -> list[str]:
    """Generate a batch containing both single and compound medicine names."""
    return [generate_medicine() for _ in range(count)]


# --- Self-Validation & Execution ---

if __name__ == "__main__":
    # Regression tests (Rule 6 - Stangler Fast)
    assert clean_join(["Uro", "oxime"]) == "Uroxime", "Failed Uro + oxime deduplication"
    assert clean_join(["Caff", "criptine"]) == "Cafcriptine", "Failed Caff + criptine reduction"
    assert clean_join(["Clal", "lan"]) == "Clalan", "Failed Clal + lan deduplication"
    assert clean_join(["Adede", "eptacog"]) == "Adedeptacog", "Failed Adede + eptacog hiatus"
    assert clean_join(["Amlo", "april"]) == "Amlapril", "Failed Amlo + april hiatus"
    assert clean_join(["Bex", "xime"]) == "Bexime", "Failed Bex + xime deduplication"

    # General invariants
    single_test = generate_medicine(force_compound=False)
    assert " " not in single_test, f"Single name should not contain spaces: {single_test}"
    assert single_test[0].isupper(), f"Must start with uppercase: {single_test}"

    compound_test = generate_medicine(force_compound=True)
    parts = compound_test.split()
    assert len(parts) == 2, f"Compound name should have 2 words: {compound_test}"
    assert parts[0][0].isupper() and parts[1][0].isupper(), "Both parts must be capitalized"

    batch_test = generate_batch(10)
    assert len(batch_test) == 10, "Batch size must match count"

    # Stats & Execution
    total_prefixes = len(PREFIXES)
    total_infixes = len(INFIXES)
    total_suffixes = len(SUFFIXES_INN)
    combinatorial_space = (
        (total_prefixes * total_suffixes)
        + (total_prefixes * total_infixes * total_suffixes)
    )

    batch_size = 50
    count = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else batch_size
    names = generate_batch(count)

    print(
        f"\n🧬 Database Stats: {total_prefixes} prefixes × {total_infixes} infixes × {total_suffixes} USAN/INN suffixes"
    )
    print(f"🔬 Single entity combinatorial space: {combinatorial_space:,} unique names")
    print(f"🧪 Compound dual-therapy combinations: ~{combinatorial_space**2:,} unique pairs\n")

    print(f"💊 Generated {count} Medicine Names (Phonotactically Cleaned):\n")
    for i, name in enumerate(names, 1):
        kind = "Dual/Compound" if " " in name else "Single Entity"
        print(f"  {i:02d}. {name:<32} [{kind}]")
    print()
