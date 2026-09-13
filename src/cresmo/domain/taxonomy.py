"""Domain taxonomy and channel classification for the Cresmo Knowledge Synthesis context.

Provides deterministic mapping of media channels into knowledge domains and category types
(perennial vs. volatile) to guide knowledge retention and indexing.
"""

from __future__ import annotations

# [VOLATILE] politics_br: Brazilian political scenario, inquiries, judiciary/STF/Congress decisions, national journalism.
POLITICS_BR_CHANNELS: frozenset[str] = frozenset({
    "ancapsu",
    "alexandre garcia",
    "ana paula henkel",
    "andré marsiglia",
    "andre marsiglia",
    "auriverde brasil",
    "band jornalismo",
    "brasil paralelo",
    "canal tragicômico",
    "canal tragicomico",
    "claudio dantas",
    "cláudio dantas",
    "cnn brasil",
    "cortes de direita",
    "deltan dallagnol",
    "estadão",
    "estadao",
    "felipe moura brasil",
    "fernão lara mesquita",
    "fernao lara mesquita",
    "folha de s.paulo",
    "folha de s. paulo",
    "folha de sao paulo",
    "gazeta do povo",
    "ideias radicais",
    "josé nêumanne pinto",
    "jose neumanne pinto",
    "leandro ruschel",
    "luís ernesto lacombe",
    "luis ernesto lacombe",
    "metrópoles",
    "metropoles",
    "na direita cortes",
    "nando moura",
    "o povo",
    "oiluiz tv",
    "paulo figueiredo show",
    "renato battista",
    "revista oeste",
    "rádio cbn",
    "radio cbn",
    "sbt news",
    "tv band rio",
    "veja+",
    "visão libertária",
    "visao libertaria",
    "paulo baltokoski",
    "jeffrey chiquini",
    "spotniks",
})

# [VOLATILE] geopolitics: Foreign affairs, international armed conflicts, superpower strategy, diplomacy.
GEOPOLITICS_CHANNELS: frozenset[str] = frozenset({
    "behind asia",
    "china uncensored",
    "china unscripted",
    "heni ozi cukier",
    "hoje no mundo militar",
    "knowledgia",
    "makarov",
    "professor ricardo marcílio",
    "professor ricardo marcilio",
    "serpentza",
    "spectacles",
    "world revolving",
})

# [PERENNIAL] tech_ai: Artificial Intelligence, LLMs, software engineering, cloud, DevOps, developer ecosystem.
TECH_AI_CHANNELS: frozenset[str] = frozenset({
    "ag grid",
    "ai engineer",
    "ai progbr",
    "ai search",
    "anderson adelino | ia e automações",
    "anderson adelino | ia e automacoes",
    "andrej karpathy",
    "augusto galego",
    "austin marchese",
    "ben ai",
    "boot dev",
    "brain station",
    "chrome for developers",
    "cloud codes",
    "cododev",
    "cole medin",
    "cyberflow",
    "código fonte tv",
    "codigo fonte tv",
    "dataquest",
    "dev aprender | jhonatan de souza",
    "devops toolbox",
    "eli rigobeli - ai",
    "estudio 68 by micah 6 ai",
    "estúdio 68 by micah 6 ai",
    "fabio akita",
    "fábio akita",
    "filipe deschamps",
    "fireship",
    "freecodecamp.org",
    "freecodecamp",
    "google deepmind",
    "google for developers",
    "ibm technology",
    "italo diego teotonio",
    "ítalo diego teotônio",
    "jeff geerling",
    "josé ángel ai",
    "jose angel ai",
    "julian goldie seo",
    "lucas montano",
    "maestros da ia",
    "mano deyvin",
    "marie haynes",
    "matheus battisti - hora de codar",
    "matheus battisti – hora de codar",
    "mindmesh ai",
    "mischa van den burg",
    "nate friedman",
    "nate herk | ai automation",
    "networkchuck",
    "neurix",
    "onde eu clico",
    "privacy matters",
    "riley brown",
    "rob braxman tech",
    "safesrc",
    "sandeco channel - decomplicated ia",
    "sandeep swadia",
    "systemdr - scalable system design",
    "systemdr – scalable system design",
    "tech with tim",
    "tool drop",
    "two minute papers",
    "vini - ai coders academy",
    "vini – ai coders academy",
    "well pires",
    "worldofai",
    "xperiun | data analytics",
    "yurirdev",
    "inteligência mil grau",
    "inteligencia mil grau",
    "sancler miranda",
    "ronnald hawk",
    "elton machado",
    "jeff su",
    "paul j lipsky",
    "ana jords",
})

# [PERENNIAL] finance: Financial markets, macroeconomics, Austrian economics, valuation, personal finance.
FINANCE_CHANNELS: frozenset[str] = frozenset({
    "andrei jikh",
    "breno perrucho - jovens de negócios",
    "breno perrucho – jovens de negócios",
    "breno perrucho - jovens de negocios",
    "brian feroldi",
    "bruno perini - você mais rico",
    "bruno perini – você mais rico",
    "bruno perini - voce mais rico",
    "capital global",
    "clube do valor",
    "curioso mercado",
    "dinheiro com você - por william ribeiro",
    "dinheiro com você – por william ribeiro",
    "dinheiro com voce - por william ribeiro",
    "dividendos news",
    "eo",
    "exame",
    "fernando ulrich",
    "helio beltrão",
    "hélio beltrão",
    "helio beltrao",
    "instituto mises brasil",
    "investidor sardinha l raul sena",
    "investidor sardinha | raul sena",
    "investidor sardinha",
    "market makers",
    "o conselho | flávio augusto",
    "o conselho | flavio augusto",
    "o primo rico",
    "rafael quintanilha – quantbrasil",
    "rafael quintanilha - quantbrasil",
    "rafael quintanilha",
    "renato augusto",
    "tapa da mão invisível",
    "tapa da mao invisivel",
    "conhecimento disruptivo",
    "adam erhart",
    "bruno okamoto",
    "bruno ávila",
    "bruno avila",
})

# [PERENNIAL] engineering: Pure and applied math, physics, astrophysics, civil/mech/electrical engineering, science.
ENGINEERING_CHANNELS: frozenset[str] = frozenset({
    "3blue1brown",
    "anton petrov",
    "braintruffle",
    "ciência todo dia",
    "ciencia todo dia",
    "engenheiro matheus",
    "floatheadphysics",
    "hank green",
    "hindemburg melao jr.",
    "hindemburg melão jr.",
    "infinitamente",
    "kurzgesagt – in a nutshell",
    "kurzgesagt - in a nutshell",
    "matematizei",
    "practical engineering",
    "real science",
    "scienceclic english",
    "simulation sandbox",
    "somos míopes porque somos breves",
    "somos miopes porque somos breves",
    "steve mould",
    "technology connections",
    "veritasium",
    "ponto em comum",
})

# [PERENNIAL] architecture: Architectural projects, interiors, sustainable construction, biomimicry, housing comparison.
ARCHITECTURE_CHANNELS: frozenset[str] = frozenset({
    "laion fernandes - arquitetura e interiores",
    "laion fernandes – arquitetura e interiores",
    "planarq campos",
    "ricardo molina usa",
    "ugreen consultoria e educação",
    "ugreen consultoria e educacao",
    "ugreen: decifrando a ciência das construções",
    "ugreen: decifrando a ciencia das construcoes",
})

# [PERENNIAL] history: Ancient and modern history, archaeology, etymology, language evolution, historical docs.
HISTORY_CHANNELS: frozenset[str] = frozenset({
    "estranha história",
    "estranha historia",
    "etimosofia",
    "história simples",
    "historia simples",
    "jaydone history",
    "marcelo andrade",
    "periscopefilm",
    "robwords",
    "study of antiquity and the middle ages",
    "the present past",
    "words unravelled",
})

# [PERENNIAL] philosophy: Classical and modern philosophy, analytical psychology, communication, negotiation, rhetoric.
PHILOSOPHY_CHANNELS: frozenset[str] = frozenset({
    "a odisseia interior",
    "a psique",
    "big think",
    "clóvis de barros",
    "clovis de barros",
    "design theory",
    "jefferson fisher",
    "lara brenner",
    "marcos campos",
    "metaforando",
    "paulo cruz",
    "sprouts",
    "descobri depois de adulta",
    "descobri depois de adulta podcast",
    "ted-ed",
})

# [PERENNIAL] health: Preventive medicine, nutrition, metabolism, mental models, physical health, self-mastery.
HEALTH_CHANNELS: frozenset[str] = frozenset({
    "dr. bruno salles, phd | psicólogo & neurocientista",
    "dr. bruno salles, phd | psicologo & neurocientista",
    "chris voss & the black swan group",
    "el professor da oratória",
    "el professor da oratoria",
    "ernesto reis",
    "rationality rules",
    "arata academy",
    "artem kirsanov",
    "dr. eric berg dc",
    "sajjaad khader",
    "sleepwise",
    "smarter while you sleep",
})

# [VOLATILE] entertainment: Cinema, series, TV backstage, television history, pop culture.
ENTERTAINMENT_CHANNELS: frozenset[str] = frozenset({
    "canal 90",
    "canal peewee",
    "nerd show",
    "ricardo feltrin",
})

DEFAULT_CHANNEL_DOMAIN: str = "uncategorized"
DEFAULT_CHANNEL_CATEGORY: str = "volatile"


def classify_channel(channel_name: str) -> tuple[str, str]:
    """Classify source channel deterministically into (domain, category_type).

    Args:
        channel_name: Human-readable or handle name of the channel.

    Returns:
        tuple[str, str]: (category_name, volatility) where volatility is
        either 'perennial' or 'volatile'.
    """
    name_clean = channel_name.lower().strip()

    if name_clean in POLITICS_BR_CHANNELS:
        return "politics_br", "volatile"
    if name_clean in GEOPOLITICS_CHANNELS:
        return "geopolitics", "volatile"
    if name_clean in TECH_AI_CHANNELS:
        return "tech_ai", "perennial"
    if name_clean in FINANCE_CHANNELS:
        return "finance", "perennial"
    if name_clean in ENGINEERING_CHANNELS:
        return "engineering", "perennial"
    if name_clean in ARCHITECTURE_CHANNELS:
        return "architecture", "perennial"
    if name_clean in HISTORY_CHANNELS:
        return "history", "perennial"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY
