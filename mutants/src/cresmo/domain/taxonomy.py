"""Domain taxonomy and channel classification for the Cresmo Knowledge Synthesis context.

Provides deterministic mapping of media channels into knowledge domains and category types
(perennial vs. volatile) to guide knowledge retention and indexing.
"""

from __future__ import annotations

# [VOLATILE] politics_br: Brazilian political scenario, inquiries, judiciary/STF/Congress decisions, national journalism.
POLITICS_BR_CHANNELS: frozenset[str] = frozenset(
    {
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
    }
)

# [VOLATILE] geopolitics: Foreign affairs, international armed conflicts, superpower strategy, diplomacy.
GEOPOLITICS_CHANNELS: frozenset[str] = frozenset(
    {
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
    }
)

# [PERENNIAL] tech_ai: Artificial Intelligence, LLMs, software engineering, cloud, DevOps, developer ecosystem.
TECH_AI_CHANNELS: frozenset[str] = frozenset(
    {
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
    }
)

# [PERENNIAL] finance: Financial markets, macroeconomics, Austrian economics, valuation, personal finance.
FINANCE_CHANNELS: frozenset[str] = frozenset(
    {
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
    }
)

# [PERENNIAL] engineering: Pure and applied math, physics, astrophysics, civil/mech/electrical engineering, science.
ENGINEERING_CHANNELS: frozenset[str] = frozenset(
    {
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
    }
)

# [PERENNIAL] architecture: Architectural projects, interiors, sustainable construction, biomimicry, housing comparison.
ARCHITECTURE_CHANNELS: frozenset[str] = frozenset(
    {
        "laion fernandes - arquitetura e interiores",
        "laion fernandes – arquitetura e interiores",
        "planarq campos",
        "ricardo molina usa",
        "ugreen consultoria e educação",
        "ugreen consultoria e educacao",
        "ugreen: decifrando a ciência das construções",
        "ugreen: decifrando a ciencia das construcoes",
    }
)

# [PERENNIAL] history: Ancient and modern history, archaeology, etymology, language evolution, historical docs.
HISTORY_CHANNELS: frozenset[str] = frozenset(
    {
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
    }
)

# [PERENNIAL] philosophy: Classical and modern philosophy, analytical psychology, communication, negotiation, rhetoric.
PHILOSOPHY_CHANNELS: frozenset[str] = frozenset(
    {
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
    }
)

# [PERENNIAL] health: Preventive medicine, nutrition, metabolism, mental models, physical health, self-mastery.
HEALTH_CHANNELS: frozenset[str] = frozenset(
    {
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
    }
)

# [VOLATILE] entertainment: Cinema, series, TV backstage, television history, pop culture.
ENTERTAINMENT_CHANNELS: frozenset[str] = frozenset(
    {
        "canal 90",
        "canal peewee",
        "nerd show",
        "ricardo feltrin",
    }
)

DEFAULT_CHANNEL_DOMAIN: str = "uncategorized"
DEFAULT_CHANNEL_CATEGORY: str = "volatile"


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_classify_channel__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_classify_channel__mutmut)
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


def x_classify_channel__mutmut_orig(channel_name: str) -> tuple[str, str]:
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


def x_classify_channel__mutmut_1(channel_name: str) -> tuple[str, str]:
    """Classify source channel deterministically into (domain, category_type).

    Args:
        channel_name: Human-readable or handle name of the channel.

    Returns:
        tuple[str, str]: (category_name, volatility) where volatility is
        either 'perennial' or 'volatile'.
    """
    name_clean = None

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


def x_classify_channel__mutmut_2(channel_name: str) -> tuple[str, str]:
    """Classify source channel deterministically into (domain, category_type).

    Args:
        channel_name: Human-readable or handle name of the channel.

    Returns:
        tuple[str, str]: (category_name, volatility) where volatility is
        either 'perennial' or 'volatile'.
    """
    name_clean = channel_name.upper().strip()

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


def x_classify_channel__mutmut_3(channel_name: str) -> tuple[str, str]:
    """Classify source channel deterministically into (domain, category_type).

    Args:
        channel_name: Human-readable or handle name of the channel.

    Returns:
        tuple[str, str]: (category_name, volatility) where volatility is
        either 'perennial' or 'volatile'.
    """
    name_clean = channel_name.lower().strip()

    if name_clean not in POLITICS_BR_CHANNELS:
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


def x_classify_channel__mutmut_4(channel_name: str) -> tuple[str, str]:
    """Classify source channel deterministically into (domain, category_type).

    Args:
        channel_name: Human-readable or handle name of the channel.

    Returns:
        tuple[str, str]: (category_name, volatility) where volatility is
        either 'perennial' or 'volatile'.
    """
    name_clean = channel_name.lower().strip()

    if name_clean in POLITICS_BR_CHANNELS:
        return "XXpolitics_brXX", "volatile"
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


def x_classify_channel__mutmut_5(channel_name: str) -> tuple[str, str]:
    """Classify source channel deterministically into (domain, category_type).

    Args:
        channel_name: Human-readable or handle name of the channel.

    Returns:
        tuple[str, str]: (category_name, volatility) where volatility is
        either 'perennial' or 'volatile'.
    """
    name_clean = channel_name.lower().strip()

    if name_clean in POLITICS_BR_CHANNELS:
        return "POLITICS_BR", "volatile"
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


def x_classify_channel__mutmut_6(channel_name: str) -> tuple[str, str]:
    """Classify source channel deterministically into (domain, category_type).

    Args:
        channel_name: Human-readable or handle name of the channel.

    Returns:
        tuple[str, str]: (category_name, volatility) where volatility is
        either 'perennial' or 'volatile'.
    """
    name_clean = channel_name.lower().strip()

    if name_clean in POLITICS_BR_CHANNELS:
        return "politics_br", "XXvolatileXX"
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


def x_classify_channel__mutmut_7(channel_name: str) -> tuple[str, str]:
    """Classify source channel deterministically into (domain, category_type).

    Args:
        channel_name: Human-readable or handle name of the channel.

    Returns:
        tuple[str, str]: (category_name, volatility) where volatility is
        either 'perennial' or 'volatile'.
    """
    name_clean = channel_name.lower().strip()

    if name_clean in POLITICS_BR_CHANNELS:
        return "politics_br", "VOLATILE"
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


def x_classify_channel__mutmut_8(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in GEOPOLITICS_CHANNELS:
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


def x_classify_channel__mutmut_9(channel_name: str) -> tuple[str, str]:
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
        return "XXgeopoliticsXX", "volatile"
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


def x_classify_channel__mutmut_10(channel_name: str) -> tuple[str, str]:
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
        return "GEOPOLITICS", "volatile"
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


def x_classify_channel__mutmut_11(channel_name: str) -> tuple[str, str]:
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
        return "geopolitics", "XXvolatileXX"
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


def x_classify_channel__mutmut_12(channel_name: str) -> tuple[str, str]:
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
        return "geopolitics", "VOLATILE"
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


def x_classify_channel__mutmut_13(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in TECH_AI_CHANNELS:
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


def x_classify_channel__mutmut_14(channel_name: str) -> tuple[str, str]:
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
        return "XXtech_aiXX", "perennial"
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


def x_classify_channel__mutmut_15(channel_name: str) -> tuple[str, str]:
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
        return "TECH_AI", "perennial"
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


def x_classify_channel__mutmut_16(channel_name: str) -> tuple[str, str]:
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
        return "tech_ai", "XXperennialXX"
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


def x_classify_channel__mutmut_17(channel_name: str) -> tuple[str, str]:
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
        return "tech_ai", "PERENNIAL"
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


def x_classify_channel__mutmut_18(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in FINANCE_CHANNELS:
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


def x_classify_channel__mutmut_19(channel_name: str) -> tuple[str, str]:
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
        return "XXfinanceXX", "perennial"
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


def x_classify_channel__mutmut_20(channel_name: str) -> tuple[str, str]:
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
        return "FINANCE", "perennial"
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


def x_classify_channel__mutmut_21(channel_name: str) -> tuple[str, str]:
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
        return "finance", "XXperennialXX"
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


def x_classify_channel__mutmut_22(channel_name: str) -> tuple[str, str]:
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
        return "finance", "PERENNIAL"
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


def x_classify_channel__mutmut_23(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in ENGINEERING_CHANNELS:
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


def x_classify_channel__mutmut_24(channel_name: str) -> tuple[str, str]:
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
        return "XXengineeringXX", "perennial"
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


def x_classify_channel__mutmut_25(channel_name: str) -> tuple[str, str]:
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
        return "ENGINEERING", "perennial"
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


def x_classify_channel__mutmut_26(channel_name: str) -> tuple[str, str]:
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
        return "engineering", "XXperennialXX"
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


def x_classify_channel__mutmut_27(channel_name: str) -> tuple[str, str]:
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
        return "engineering", "PERENNIAL"
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


def x_classify_channel__mutmut_28(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in ARCHITECTURE_CHANNELS:
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


def x_classify_channel__mutmut_29(channel_name: str) -> tuple[str, str]:
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
        return "XXarchitectureXX", "perennial"
    if name_clean in HISTORY_CHANNELS:
        return "history", "perennial"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_30(channel_name: str) -> tuple[str, str]:
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
        return "ARCHITECTURE", "perennial"
    if name_clean in HISTORY_CHANNELS:
        return "history", "perennial"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_31(channel_name: str) -> tuple[str, str]:
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
        return "architecture", "XXperennialXX"
    if name_clean in HISTORY_CHANNELS:
        return "history", "perennial"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_32(channel_name: str) -> tuple[str, str]:
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
        return "architecture", "PERENNIAL"
    if name_clean in HISTORY_CHANNELS:
        return "history", "perennial"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_33(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in HISTORY_CHANNELS:
        return "history", "perennial"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_34(channel_name: str) -> tuple[str, str]:
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
        return "XXhistoryXX", "perennial"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_35(channel_name: str) -> tuple[str, str]:
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
        return "HISTORY", "perennial"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_36(channel_name: str) -> tuple[str, str]:
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
        return "history", "XXperennialXX"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_37(channel_name: str) -> tuple[str, str]:
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
        return "history", "PERENNIAL"
    if name_clean in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_38(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in PHILOSOPHY_CHANNELS:
        return "philosophy", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_39(channel_name: str) -> tuple[str, str]:
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
        return "XXphilosophyXX", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_40(channel_name: str) -> tuple[str, str]:
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
        return "PHILOSOPHY", "perennial"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_41(channel_name: str) -> tuple[str, str]:
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
        return "philosophy", "XXperennialXX"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_42(channel_name: str) -> tuple[str, str]:
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
        return "philosophy", "PERENNIAL"
    if name_clean in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_43(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in HEALTH_CHANNELS:
        return "health", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_44(channel_name: str) -> tuple[str, str]:
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
        return "XXhealthXX", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_45(channel_name: str) -> tuple[str, str]:
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
        return "HEALTH", "perennial"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_46(channel_name: str) -> tuple[str, str]:
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
        return "health", "XXperennialXX"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_47(channel_name: str) -> tuple[str, str]:
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
        return "health", "PERENNIAL"
    if name_clean in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_48(channel_name: str) -> tuple[str, str]:
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
    if name_clean not in ENTERTAINMENT_CHANNELS:
        return "entertainment", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_49(channel_name: str) -> tuple[str, str]:
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
        return "XXentertainmentXX", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_50(channel_name: str) -> tuple[str, str]:
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
        return "ENTERTAINMENT", "volatile"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_51(channel_name: str) -> tuple[str, str]:
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
        return "entertainment", "XXvolatileXX"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY


def x_classify_channel__mutmut_52(channel_name: str) -> tuple[str, str]:
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
        return "entertainment", "VOLATILE"

    return DEFAULT_CHANNEL_DOMAIN, DEFAULT_CHANNEL_CATEGORY

mutants_x_classify_channel__mutmut['_mutmut_orig'] = x_classify_channel__mutmut_orig # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_1'] = x_classify_channel__mutmut_1 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_2'] = x_classify_channel__mutmut_2 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_3'] = x_classify_channel__mutmut_3 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_4'] = x_classify_channel__mutmut_4 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_5'] = x_classify_channel__mutmut_5 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_6'] = x_classify_channel__mutmut_6 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_7'] = x_classify_channel__mutmut_7 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_8'] = x_classify_channel__mutmut_8 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_9'] = x_classify_channel__mutmut_9 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_10'] = x_classify_channel__mutmut_10 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_11'] = x_classify_channel__mutmut_11 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_12'] = x_classify_channel__mutmut_12 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_13'] = x_classify_channel__mutmut_13 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_14'] = x_classify_channel__mutmut_14 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_15'] = x_classify_channel__mutmut_15 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_16'] = x_classify_channel__mutmut_16 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_17'] = x_classify_channel__mutmut_17 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_18'] = x_classify_channel__mutmut_18 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_19'] = x_classify_channel__mutmut_19 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_20'] = x_classify_channel__mutmut_20 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_21'] = x_classify_channel__mutmut_21 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_22'] = x_classify_channel__mutmut_22 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_23'] = x_classify_channel__mutmut_23 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_24'] = x_classify_channel__mutmut_24 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_25'] = x_classify_channel__mutmut_25 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_26'] = x_classify_channel__mutmut_26 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_27'] = x_classify_channel__mutmut_27 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_28'] = x_classify_channel__mutmut_28 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_29'] = x_classify_channel__mutmut_29 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_30'] = x_classify_channel__mutmut_30 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_31'] = x_classify_channel__mutmut_31 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_32'] = x_classify_channel__mutmut_32 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_33'] = x_classify_channel__mutmut_33 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_34'] = x_classify_channel__mutmut_34 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_35'] = x_classify_channel__mutmut_35 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_36'] = x_classify_channel__mutmut_36 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_37'] = x_classify_channel__mutmut_37 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_38'] = x_classify_channel__mutmut_38 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_39'] = x_classify_channel__mutmut_39 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_40'] = x_classify_channel__mutmut_40 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_41'] = x_classify_channel__mutmut_41 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_42'] = x_classify_channel__mutmut_42 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_43'] = x_classify_channel__mutmut_43 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_44'] = x_classify_channel__mutmut_44 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_45'] = x_classify_channel__mutmut_45 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_46'] = x_classify_channel__mutmut_46 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_47'] = x_classify_channel__mutmut_47 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_48'] = x_classify_channel__mutmut_48 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_49'] = x_classify_channel__mutmut_49 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_50'] = x_classify_channel__mutmut_50 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_51'] = x_classify_channel__mutmut_51 # type: ignore # mutmut generated
mutants_x_classify_channel__mutmut['x_classify_channel__mutmut_52'] = x_classify_channel__mutmut_52 # type: ignore # mutmut generated
