#!/usr/bin/env python3
"""Generate 8 analytical MusicXML collections from the harmonic matrix.

Output directory: PES / playground / notas / partituras /

Collections
-----------
1. 1_escalas_completas: Escala nota por nota.
2. 2_campos_harmonicos_das_escalas: Os acordes que pertencem à escala.
3. 3_acordes: Procurar onde aparece um determinado acorde.
4. 4_transposicao_cromatica: O mesmo acorde passando pelas 12 notas.
5. 5_identidade_modal: A mesma tônica em modos diferentes.
6. 6_progressoes_com_movimento_interno_suave: Como ligar um acorde ao outro suavemente.
7. 7_estruturas_iguais: Eliminar repetições da tabela (classes de conjuntos / Forte).
8. 8_frequencias_musicais: Transformar notas musicais em frequências (acústica, afinação, série harmônica).
"""

from __future__ import annotations

import unicodedata
from itertools import combinations
from pathlib import Path

from music21 import (
    chord as m21chord,
    clef,
    expressions,
    metadata as m21meta,
    meter,
    note,
    stream,
    tempo,
)

from notas import gerar_dataframe_longo

# ---------------------------------------------------------------------------
# Directory defaults
# ---------------------------------------------------------------------------
DEFAULT_PARTITURAS_DIR = Path(__file__).resolve().parent / "partituras"

# ---------------------------------------------------------------------------
# Mappings (shared with partitura_musicxml.py)
# ---------------------------------------------------------------------------
NOTA_PARA_PC: dict[str, str] = {
    "Dó": "C", "Réb": "D-", "Ré": "D", "Mib": "E-", "Mi": "E",
    "Fá": "F", "Fa#": "F#", "Sol": "G", "Láb": "A-", "Lá": "A",
    "Sib": "B-", "Si": "B",
}

CIFRAS: dict[str, str] = {
    "Dó": "C", "Réb": "Db", "Ré": "D", "Mib": "Eb", "Mi": "E",
    "Fá": "F", "Fa#": "F#", "Sol": "G", "Láb": "Ab", "Lá": "A",
    "Sib": "Bb", "Si": "B",
}

SUFIXOS_ACORDE: dict[str, str] = {
    "Acorde Maior": "",
    "Acorde Menor": "m",
    "Diminuta": "dim",
    "Aumentada": "aug",
    "Suspensão por Quarta": "sus4",
    "Suspensão por Segunda": "sus2",
    "Sétima Maior": "maj7",
    "Sétima Menor": "7",
    "Sétima Diminuta": "dim7",
}

GRAUS_ORDEM = ["I", "II", "III", "IV", "V", "VI", "VII"]

MODOS_BRILHO = [
    "Lídio",
    "Jônio / Maior",
    "Mixolídio",
    "Dórico",
    "Eólio / Menor Natural",
    "Frígio",
    "Lócrio",
    "Menor Harmônica",
    "Menor Melódica (asc.)",
]

NOME_NOTA_PARA_MIDI: dict[str, int] = {
    "Dó": 0, "Réb": 1, "Ré": 2, "Mib": 3, "Mi": 4,
    "Fá": 5, "Fa#": 6, "Sol": 7, "Láb": 8, "Lá": 9,
    "Sib": 10, "Si": 11,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _san(nome: str) -> str:
    """Filesystem-safe name: strip accents, replace specials."""
    nfkd = unicodedata.normalize("NFKD", nome)
    ascii_safe = "".join(c for c in nfkd if not unicodedata.combining(c))
    return (
        ascii_safe
        .replace("#", "sharp")
        .replace("/", "-")
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
    )


def _cifra(nota_grau: str, tipo_acorde: str) -> str:
    return f"{CIFRAS.get(nota_grau, nota_grau)}{SUFIXOS_ACORDE.get(tipo_acorde, '')}"


def _ascending_pitches(nomes: list[str], start_octave: int = 4) -> list[str]:
    """Return music21 pitch strings ensuring each successive pitch is higher.

    Whenever a note's chromatic index is <= the previous note's index,
    the octave increments — guaranteeing strictly ascending frequencies.
    """
    if not nomes:
        return []
    result = []
    octave = start_octave
    prev_idx = -1
    for i, nome in enumerate(nomes):
        idx = NOME_NOTA_PARA_MIDI.get(nome, 0)
        pc = NOTA_PARA_PC.get(nome, "C")
        if i > 0 and idx <= prev_idx:
            octave += 1
        result.append(f"{pc}{octave}")
        prev_idx = idx
    return result


def _single_pitch(nome: str, octave: int = 4) -> str:
    """Single note pitch string at a given octave."""
    pc = NOTA_PARA_PC.get(nome, "C")
    return f"{pc}{octave}"


def _freq_str(hz: float) -> str:
    """Format frequency for filenames: 440.00 → '440_00'."""
    return f"{hz:.2f}".replace(".", "_")


# ---------------------------------------------------------------------------
# Didactic annotations per collection
# ---------------------------------------------------------------------------
OBSERVACOES: dict[int, str] = {
    1: (
        "1. Escalas completas: o que você encontra na tabela são escalas nota por nota. "
        "Esta partitura apresenta a escala diatônica ou sintética correspondente ao modo "
        "selecionado sobre a tônica fundamental indicada, disposta em sucessão melódica ascendente."
    ),
    2: (
        "2. Campos harmônicos das escalas: os acordes que pertencem à escala. "
        "Cada acorde é formado exclusivamente pelas notas da escala diatônica do modo indicado, "
        "representando as funções harmônicas naturais (tônica, subdominante, dominante e relativas)."
    ),
    3: (
        "3. Acordes: procurar onde aparece um determinado acorde. "
        "Fixa-se um tipo de acorde e observa-se como ele se manifesta em cada grau da escala "
        "para uma dada tônica e modo ao longo dos degraus escalares."
    ),
    4: (
        "4. Transposição cromática: o mesmo acorde passando pelas 12 notas. "
        "Fixa-se o tipo de acorde e varrem-se as doze notas cromáticas em progressão ascendente de frequência."
    ),
    5: (
        "5. Identidade modal: a mesma tônica em modos diferentes. "
        "Fixa-se a tônica fundamental e o grau ordinal, projetando todos os modos em sucessão "
        "sobre o mesmo centro acústico ao longo do ciclo de brilho modal."
    ),
    6: (
        "6. Progressões com movimento interno suave: como ligar um acorde ao outro suavemente. "
        "Para cada par de graus consecutivos, seleciona-se a combinação de acordes com menor "
        "deslocamento intervalar (distância euclidiana mínima no espaço de alturas), "
        "priorizando notas comuns retidas e movimentos por semitom."
    ),
    7: (
        "7. Estruturas iguais: essa abordagem serve para eliminar repetições da tabela. "
        "Cada acorde é reduzido à sua classe de conjuntos (Pitch-Class Set / Forma Prima de Allen Forte) "
        "e vetor intervalar, agrupando estruturas com a mesma sonoridade intrínseca."
    ),
    8: (
        "8. Frequências musicais: transformar notas musicais em frequências e serve para acústica musical, "
        "frequência, afinação, série harmônica e relações matemáticas entre alturas. "
        "Ordena-se pela frequência do grau em Hz e cruzam-se as correspondências de tônica e modo."
    ),
}


# ---------------------------------------------------------------------------
# Score building primitives
# ---------------------------------------------------------------------------
BPM = 120


def _new_score(titulo: str, compositor: str = "Sistema Harmônico Pitagórico") -> stream.Score:
    s = stream.Score()
    s.metadata = m21meta.Metadata()
    s.metadata.title = titulo
    s.metadata.composer = compositor
    return s


def _add_observacao(part: stream.Part, texto: str) -> None:
    """Insert a didactic text annotation at the current position."""
    te = expressions.TextExpression(texto)
    te.placement = "below"
    te.style.fontSize = 9
    te.style.fontStyle = "italic"
    part.append(te)


def _make_sound(pitches: str | list[str], ql: float = 1.0) -> note.Note | m21chord.Chord:
    """Create a Note (single pitch) or Chord (list of pitches)."""
    if isinstance(pitches, str):
        return note.Note(pitches, quarterLength=ql)
    return m21chord.Chord(pitches, quarterLength=ql)


def _add_pair_measures(
    part: stream.Part,
    base: str | list[str],
    current: str | list[str],
    label_above: str | None = None,
    lyric_text: str | None = None,
) -> None:
    """Create 2 measures for each element in 4/4 meter.

    Measure 1: Base (2 eighths) | Current (1 quarter) | Base (2 eighths) | Current (1 quarter)
    Measure 2: Base (2 eighths) | Current (1 quarter) | Current (1 quarter) | Current (1 quarter)
    """
    # --- Measure 1 ---
    m1 = stream.Measure()

    # Tempo 1 (pos 1): Base as 2 eighth notes (0.5 ql each)
    b1_1 = _make_sound(base, ql=0.5)
    b1_2 = _make_sound(base, ql=0.5)
    if label_above:
        te = expressions.TextExpression(label_above)
        te.placement = "above"
        te.style.fontWeight = "bold"
        te.style.fontSize = 12
        m1.insert(0, te)
    m1.append(b1_1)
    m1.append(b1_2)

    # Tempo 2 (pos 2): Current (1 quarter = 1.0 ql)
    c1 = _make_sound(current, ql=1.0)
    if lyric_text:
        c1.lyric = lyric_text
    m1.append(c1)

    # Tempo 3 (pos 3): Base as 2 eighth notes (0.5 ql each)
    b2_1 = _make_sound(base, ql=0.5)
    b2_2 = _make_sound(base, ql=0.5)
    m1.append(b2_1)
    m1.append(b2_2)

    # Tempo 4 (pos 4): Current (1 quarter = 1.0 ql)
    c2 = _make_sound(current, ql=1.0)
    m1.append(c2)

    part.append(m1)

    # --- Measure 2 ---
    m2 = stream.Measure()

    # Tempo 1 (pos 1): Base as 2 eighth notes (0.5 ql each)
    m2_b1_1 = _make_sound(base, ql=0.5)
    m2_b1_2 = _make_sound(base, ql=0.5)
    m2.append(m2_b1_1)
    m2.append(m2_b1_2)

    # Tempo 2 (pos 2): Current (1 quarter = 1.0 ql)
    m2_c1 = _make_sound(current, ql=1.0)
    if lyric_text:
        m2_c1.lyric = lyric_text
    m2.append(m2_c1)

    # Tempo 3 (pos 3): Current (1 quarter = 1.0 ql)
    m2_c2 = _make_sound(current, ql=1.0)
    m2.append(m2_c2)

    # Tempo 4 (pos 4): Current (1 quarter = 1.0 ql)
    m2_c3 = _make_sound(current, ql=1.0)
    m2.append(m2_c3)

    part.append(m2)


def _init_part(part: stream.Part) -> None:
    """Insert clef, time signature, tempo at start."""
    part.insert(0, clef.TrebleClef())
    part.insert(0, meter.TimeSignature("4/4"))
    part.insert(0, tempo.MetronomeMark(text="Moderato", number=BPM))


def _write(score: stream.Score, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    score.write("musicxml", fp=str(path))


# ---------------------------------------------------------------------------
# Pitch-class set theory helpers (Abordagem 7: Estruturas Iguais)
# ---------------------------------------------------------------------------
def _pc_set(nomes: list[str]) -> frozenset[int]:
    return frozenset(NOME_NOTA_PARA_MIDI[n] for n in nomes if n in NOME_NOTA_PARA_MIDI)


def _normal_order(pcs: frozenset[int]) -> tuple[int, ...]:
    """Compute the normal order of a pitch-class set."""
    if not pcs:
        return ()
    pcs_sorted = sorted(pcs)
    n = len(pcs_sorted)
    if n == 1:
        return tuple(pcs_sorted)

    best = None
    for rotation in range(n):
        candidate = tuple(pcs_sorted[(rotation + i) % n] for i in range(n))
        span = (candidate[-1] - candidate[0]) % 12
        if best is None or span < best_span or (
            span == best_span and candidate < best
        ):
            best = candidate
            best_span = span
    return best


def _prime_form(pcs: frozenset[int]) -> tuple[int, ...]:
    """Compute Forte prime form (transposition + inversion to most compact)."""
    no = _normal_order(pcs)
    if not no:
        return ()
    t0 = tuple((p - no[0]) % 12 for p in no)

    inv_pcs = frozenset((12 - p) % 12 for p in pcs)
    no_inv = _normal_order(inv_pcs)
    t0_inv = tuple((p - no_inv[0]) % 12 for p in no_inv)

    return min(t0, t0_inv)


def _interval_vector(pcs: frozenset[int]) -> tuple[int, ...]:
    """6-element interval vector (ic 1–6)."""
    vec = [0] * 6
    for a, b in combinations(sorted(pcs), 2):
        ic = (b - a) % 12
        if ic > 6:
            ic = 12 - ic
        vec[ic - 1] += 1
    return tuple(vec)


def _forte_label(pcs: frozenset[int]) -> str:
    """Simple Forte-style label from prime form, e.g. [0,3,7]."""
    pf = _prime_form(pcs)
    return "[" + ",".join(str(p) for p in pf) + "]"


# ---------------------------------------------------------------------------
# Voice-leading distance (Abordagem 6: Progressões com Movimento Suave)
# ---------------------------------------------------------------------------
def _vl_distance(chord_a: list[str], chord_b: list[str]) -> int:
    """Sum of minimal semitone displacements between two collections."""
    pcs_a = sorted(NOME_NOTA_PARA_MIDI.get(n, 0) for n in chord_a)
    pcs_b = sorted(NOME_NOTA_PARA_MIDI.get(n, 0) for n in chord_b)
    while len(pcs_a) < len(pcs_b):
        pcs_a.append(pcs_a[-1] if pcs_a else 0)
    while len(pcs_b) < len(pcs_a):
        pcs_b.append(pcs_b[-1] if pcs_b else 0)
    return sum(min(abs(a - b), 12 - abs(a - b)) for a, b in zip(pcs_a, pcs_b))


# ===================================================================
# Collection 1: 1_escalas_completas
# ===================================================================
def colecao_1(df, base: Path) -> int:
    """partituras/1_escalas_completas/[Tônica]/[Modo].musicxml"""
    root = base / "1_escalas_completas"
    count = 0
    for tonica in df["Tônica Fundamental"].unique():
        for modo in df["Modo"].unique():
            sub = df[(df["Tônica Fundamental"] == tonica) & (df["Modo"] == modo)]
            if sub.empty:
                continue
            graus = sub.drop_duplicates(subset=["Grau"])
            graus = graus.set_index("Grau").reindex(GRAUS_ORDEM).dropna(subset=["Nota do Grau"])

            scale_notes = list(graus["Nota do Grau"])
            scale_pitches = _ascending_pitches(scale_notes)

            titulo = f"Escala {tonica} {modo}"
            score = _new_score(titulo)
            part = stream.Part()
            part.partName = titulo
            _init_part(part)
            _add_observacao(part, OBSERVACOES[1])

            base_pitch = scale_pitches[0]  # degree I as reference
            for (grau_label, row), pitch in zip(graus.iterrows(), scale_pitches):
                nota = row["Nota do Grau"]
                freq = row["Frequência do Grau (Hz)"]
                _add_pair_measures(part, base_pitch, pitch,
                                   label_above=f"{grau_label}",
                                   lyric_text=f"{nota} ({freq}Hz)")

            score.append(part)
            fp = root / _san(tonica) / f"{_san(modo)}.musicxml"
            _write(score, fp)
            count += 1
    return count


# ===================================================================
# Collection 2: 2_campos_harmonicos_das_escalas
# ===================================================================
def _acorde_diatonico(notas_acorde: list[str], notas_escala: set[str]) -> bool:
    """True if all chord tones belong to the diatonic scale."""
    return all(n in notas_escala for n in notas_acorde)


def colecao_2(df, base: Path) -> int:
    """partituras/2_campos_harmonicos_das_escalas/[Tônica]/[Modo].musicxml"""
    root = base / "2_campos_harmonicos_das_escalas"
    count = 0

    for tonica in df["Tônica Fundamental"].unique():
        for modo in df["Modo"].unique():
            sub = df[(df["Tônica Fundamental"] == tonica) & (df["Modo"] == modo)]
            if sub.empty:
                continue

            graus_uniq = sub.drop_duplicates(subset=["Grau"]).set_index("Grau").reindex(GRAUS_ORDEM)
            notas_escala = set(graus_uniq["Nota do Grau"].dropna())

            titulo = f"Campo Harmônico {tonica} {modo}"
            score = _new_score(titulo)
            part = stream.Part()
            part.partName = titulo
            _init_part(part)
            _add_observacao(part, OBSERVACOES[2])

            base_pitches = None
            for grau_label in GRAUS_ORDEM:
                grau_rows = sub[sub["Grau"] == grau_label]
                for _, row in grau_rows.iterrows():
                    notas_ac = row["Notas do Acorde"].split()
                    if _acorde_diatonico(notas_ac, notas_escala):
                        cifra = _cifra(row["Nota do Grau"], row["Tipo de Acorde"])
                        pitches = _ascending_pitches(notas_ac)
                        if base_pitches is None:
                            base_pitches = pitches  # degree I chord as reference
                        _add_pair_measures(part, base_pitches, pitches,
                                           label_above=f"{grau_label}: {cifra}",
                                           lyric_text=row["Notas do Acorde"])
                        break

            score.append(part)
            fp = root / _san(tonica) / f"{_san(modo)}.musicxml"
            _write(score, fp)
            count += 1
    return count


# ===================================================================
# Collection 3: 3_acordes
# ===================================================================
def colecao_3(df, base: Path) -> int:
    """partituras/3_acordes/[Tipo de Acorde]/[Tônica]/[Modo].musicxml"""
    root = base / "3_acordes"
    count = 0

    for tipo_acorde in df["Tipo de Acorde"].unique():
        for tonica in df["Tônica Fundamental"].unique():
            for modo in df["Modo"].unique():
                sub = df[
                    (df["Tipo de Acorde"] == tipo_acorde)
                    & (df["Tônica Fundamental"] == tonica)
                    & (df["Modo"] == modo)
                ]
                if sub.empty:
                    continue

                titulo = f"{tipo_acorde} — {tonica} {modo}"
                score = _new_score(titulo)
                part = stream.Part()
                part.partName = titulo
                _init_part(part)
                _add_observacao(part, OBSERVACOES[3])

                sub_sorted = sub.set_index("Grau").reindex(GRAUS_ORDEM).dropna(
                    subset=["Nota do Grau"]
                )
                base_pitches = None
                for grau_label, row in sub_sorted.iterrows():
                    nota_grau = row["Nota do Grau"]
                    notas_ac = row["Notas do Acorde"].split()
                    cifra = _cifra(nota_grau, tipo_acorde)
                    pitches = _ascending_pitches(notas_ac)
                    if base_pitches is None:
                        base_pitches = pitches  # degree I chord as reference
                    _add_pair_measures(part, base_pitches, pitches,
                                       label_above=f"{grau_label}: {cifra}",
                                       lyric_text=row["Notas do Acorde"])

                score.append(part)
                fname = f"{_san(modo)}.musicxml"
                fp = root / _san(tipo_acorde) / _san(tonica) / fname
                _write(score, fp)
                count += 1
    return count


# ===================================================================
# Collection 4: 4_transposicao_cromatica
# ===================================================================
def colecao_4(df, base: Path) -> int:
    """partituras/4_transposicao_cromatica/[Tipo de Acorde]/[Nota do Grau]_[Freq].musicxml"""
    root = base / "4_transposicao_cromatica"
    count = 0

    for tipo_acorde in df["Tipo de Acorde"].unique():
        sub = df[df["Tipo de Acorde"] == tipo_acorde]
        combos = sub.drop_duplicates(subset=["Nota do Grau", "Frequência do Grau (Hz)"])
        combos = combos.sort_values("Frequência do Grau (Hz)")

        for _, row in combos.iterrows():
            nota_grau = row["Nota do Grau"]
            freq = row["Frequência do Grau (Hz)"]
            notas_ac = row["Notas do Acorde"].split()
            cifra = _cifra(nota_grau, tipo_acorde)

            titulo = f"{tipo_acorde} — {nota_grau} ({freq} Hz)"
            score = _new_score(titulo)
            part = stream.Part()
            part.partName = titulo
            _init_part(part)
            _add_observacao(part, OBSERVACOES[4])

            pitches = _ascending_pitches(notas_ac)
            _add_pair_measures(part, pitches, pitches,
                               label_above=cifra,
                               lyric_text=f"{nota_grau} {freq}Hz")

            score.append(part)
            fname = f"{_san(nota_grau)}_{_freq_str(freq)}.musicxml"
            fp = root / _san(tipo_acorde) / fname
            _write(score, fp)
            count += 1
    return count


# ===================================================================
# Collection 5: 5_identidade_modal
# ===================================================================
def colecao_5(df, base: Path) -> int:
    """partituras/5_identidade_modal/[Tônica]/Grau_[Grau]/[Modo]_[Nota do Grau].musicxml"""
    root = base / "5_identidade_modal"
    count = 0

    for tonica in df["Tônica Fundamental"].unique():
        for grau in GRAUS_ORDEM:
            sub = df[(df["Tônica Fundamental"] == tonica) & (df["Grau"] == grau)]
            if sub.empty:
                continue

            modos_presentes = [m for m in MODOS_BRILHO if m in sub["Modo"].values]

            for modo in modos_presentes:
                row_set = sub[sub["Modo"] == modo]
                if row_set.empty:
                    continue
                first = row_set.iloc[0]
                nota_grau = first["Nota do Grau"]
                freq = first["Frequência do Grau (Hz)"]

                titulo = f"{tonica} — Grau {grau} — {modo} ({nota_grau})"
                score = _new_score(titulo)
                part = stream.Part()
                part.partName = titulo
                _init_part(part)
                _add_observacao(part, OBSERVACOES[5])

                pitch = _single_pitch(nota_grau)
                _add_pair_measures(part, pitch, pitch,
                                   label_above=f"{modo}",
                                   lyric_text=f"{nota_grau} ({freq}Hz)")

                base_chord = None
                for _, row in row_set.iterrows():
                    notas_ac = row["Notas do Acorde"].split()
                    cifra = _cifra(nota_grau, row["Tipo de Acorde"])
                    pitches = _ascending_pitches(notas_ac)
                    if base_chord is None:
                        base_chord = pitches
                    _add_pair_measures(part, base_chord, pitches,
                                       label_above=cifra,
                                       lyric_text=row["Notas do Acorde"])

                score.append(part)
                fname = f"{_san(modo)}_{_san(nota_grau)}.musicxml"
                fp = root / _san(tonica) / f"Grau_{grau}" / fname
                _write(score, fp)
                count += 1
    return count


# ===================================================================
# Collection 6: 6_progressoes_com_movimento_interno_suave
# ===================================================================
def colecao_6(df, base: Path) -> int:
    """partituras/6_progressoes_com_movimento_interno_suave/[Modo]/[Tônica]/...musicxml"""
    root = base / "6_progressoes_com_movimento_interno_suave"
    count = 0

    for modo in df["Modo"].unique():
        for tonica in df["Tônica Fundamental"].unique():
            sub = df[(df["Modo"] == modo) & (df["Tônica Fundamental"] == tonica)]
            if sub.empty:
                continue

            for i in range(len(GRAUS_ORDEM) - 1):
                grau_a = GRAUS_ORDEM[i]
                grau_b = GRAUS_ORDEM[i + 1]
                rows_a = sub[sub["Grau"] == grau_a]
                rows_b = sub[sub["Grau"] == grau_b]
                if rows_a.empty or rows_b.empty:
                    continue

                best_dist = 999
                best_pair = None
                for _, ra in rows_a.iterrows():
                    for _, rb in rows_b.iterrows():
                        na = ra["Notas do Acorde"].split()
                        nb = rb["Notas do Acorde"].split()
                        d = _vl_distance(na, nb)
                        if d < best_dist:
                            best_dist = d
                            best_pair = (ra, rb)

                if best_pair is None:
                    continue
                ra, rb = best_pair
                titulo = (f"Condução {modo} {tonica}: "
                          f"{grau_a}→{grau_b} (dist={best_dist}st)")
                score = _new_score(titulo)
                part = stream.Part()
                part.partName = titulo
                _init_part(part)
                _add_observacao(part, OBSERVACOES[6])

                # Chord A (also serves as base)
                na = ra["Notas do Acorde"].split()
                cifra_a = _cifra(ra["Nota do Grau"], ra["Tipo de Acorde"])
                base_pitches = _ascending_pitches(na)
                _add_pair_measures(part, base_pitches, base_pitches,
                                   label_above=f"{grau_a}: {cifra_a}",
                                   lyric_text=ra["Notas do Acorde"])

                # Chord B
                nb = rb["Notas do Acorde"].split()
                cifra_b = _cifra(rb["Nota do Grau"], rb["Tipo de Acorde"])
                _add_pair_measures(part, base_pitches, _ascending_pitches(nb),
                                   label_above=f"{grau_b}: {cifra_b}",
                                   lyric_text=rb["Notas do Acorde"])

                score.append(part)
                fname = f"Minima_Distancia_{grau_a}_{_san(ra['Tipo de Acorde'])}.musicxml"
                fp = root / _san(modo) / _san(tonica) / fname
                _write(score, fp)
                count += 1
    return count


# ===================================================================
# Collection 7: 7_estruturas_iguais
# ===================================================================
def colecao_7(df, base: Path) -> int:
    """partituras/7_estruturas_iguais/[Vetor_Forte]/[Tipo de Acorde]/[Notas do Acorde].musicxml"""
    root = base / "7_estruturas_iguais"
    count = 0
    seen: set[tuple[str, str, str]] = set()

    for _, row in df.iterrows():
        tipo_acorde = row["Tipo de Acorde"]
        notas_str = row["Notas do Acorde"]
        notas_ac = notas_str.split()

        pcs = _pc_set(notas_ac)
        forte = _forte_label(pcs)
        iv = _interval_vector(pcs)
        iv_str = "".join(str(x) for x in iv)

        key = (iv_str, tipo_acorde, notas_str)
        if key in seen:
            continue
        seen.add(key)

        titulo = f"{tipo_acorde} — {notas_str} — Forte {forte} IV<{iv_str}>"
        score = _new_score(titulo)
        part = stream.Part()
        part.partName = titulo
        _init_part(part)
        _add_observacao(part, OBSERVACOES[7])

        pitches = _ascending_pitches(notas_ac)
        _add_pair_measures(part, pitches, pitches,
                           label_above=f"{forte} [{iv_str}]",
                           lyric_text=notas_str)

        score.append(part)
        fname = f"{_san(notas_str)}.musicxml"
        fp = root / iv_str / _san(tipo_acorde) / fname
        _write(score, fp)
        count += 1
    return count


# ===================================================================
# Collection 8: 8_frequencias_musicais
# ===================================================================
def colecao_8(df, base: Path) -> int:
    """partituras/8_frequencias_musicais/[Freq Grau]/[Nota]/[Freq Grau]_[Nota]_[Tônica]_[Modo]_[Freq Fund].musicxml"""
    root = base / "8_frequencias_musicais"
    count = 0
    seen: set[tuple[float, str, str, str, float]] = set()

    df_sorted = df.sort_values("Frequência do Grau (Hz)")

    for _, row in df_sorted.iterrows():
        freq_grau = row["Frequência do Grau (Hz)"]
        nota_grau = row["Nota do Grau"]
        tonica = row["Tônica Fundamental"]
        modo = row["Modo"]
        freq_fund = row["Frequência Fundamental (Hz)"]

        key = (freq_grau, nota_grau, tonica, modo, freq_fund)
        if key in seen:
            continue
        seen.add(key)

        ratio = freq_grau / freq_fund if freq_fund > 0 else 0
        titulo = (f"{nota_grau} ({freq_grau}Hz) — "
                  f"{tonica} {modo} (f₀={freq_fund}Hz, ratio={ratio:.4f})")
        score = _new_score(titulo)
        part = stream.Part()
        part.partName = titulo
        _init_part(part)
        _add_observacao(part, OBSERVACOES[8])

        pitch = _single_pitch(nota_grau)
        _add_pair_measures(part, pitch, pitch,
                           label_above=f"{freq_grau}Hz (ratio {ratio:.4f})",
                           lyric_text=f"{nota_grau} — {tonica} {modo}")

        score.append(part)
        fname = f"{_freq_str(freq_grau)}_{_san(nota_grau)}_{_san(tonica)}_{_san(modo)}_{_freq_str(freq_fund)}.musicxml"
        fp = root / _freq_str(freq_grau) / _san(nota_grau) / fname
        _write(score, fp)
        count += 1
    return count


# ===================================================================
# Main
# ===================================================================
def gerar_todas_colecoes(f_fundamental: float = 440.0,
                         diretorio_saida: Path | str | None = None) -> None:
    """Generate all 8 collections under the target directory."""
    if diretorio_saida is None:
        base = DEFAULT_PARTITURAS_DIR
    else:
        base = Path(diretorio_saida)

    base.mkdir(parents=True, exist_ok=True)
    print(f"Generating harmonic matrix (f₀ = {f_fundamental} Hz) …")
    df = gerar_dataframe_longo(f_fundamental)
    print(f"  {len(df)} rows in relational matrix.\n")

    colecoes = [
        ("1. escalas completas", colecao_1),
        ("2. campos harmônicos das escalas", colecao_2),
        ("3. Acordes", colecao_3),
        ("4. transposição cromática", colecao_4),
        ("5. identidade modal", colecao_5),
        ("6. progressões com movimento interno suave", colecao_6),
        ("7. estruturas iguais", colecao_7),
        ("8. Frequencias musicais", colecao_8),
    ]

    for label, fn in colecoes:
        print(f"▶ {label} …", end=" ", flush=True)
        n = fn(df, base)
        print(f"{n} files ✓")

    print("\nDone — all collections saved under", base)


if __name__ == "__main__":
    gerar_todas_colecoes()
