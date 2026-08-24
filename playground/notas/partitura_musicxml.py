"""Generate MusicXML scores organized by Modo → Tônica → Grau.

Output structure:
    partituras/{modo}/{tonica}_grau_{grau}.musicxml

Each file contains 9 measures (one per tipo de acorde), with:
  - Title showing modo, tônica, and grau
  - Each measure labeled with the chord type + note names
  - Chord symbol (cifra) above each beat

Total: 12 tônicas × 9 modos × 7 graus = 756 files, 9 compassos each.
"""

from pathlib import Path

from music21 import (
    chord as m21chord,
    clef,
    expressions,
    metadata,
    meter,
    note,
    stream,
    tempo,
)

from notas import gerar_dataframe_longo


# ---------------------------------------------------------------------------
# Mappings
# ---------------------------------------------------------------------------
NOTA_PARA_PITCH: dict[str, str] = {
    "Dó": "C4", "Réb": "D-4", "Ré": "D4", "Mib": "E-4", "Mi": "E4",
    "Fá": "F4", "Fa#": "F#4", "Sol": "G4", "Láb": "A-4", "Lá": "A4",
    "Sib": "B-4", "Si": "B4",
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


def _cifra(nota_grau: str, tipo_acorde: str) -> str:
    base = CIFRAS.get(nota_grau, nota_grau)
    sufixo = SUFIXOS_ACORDE.get(tipo_acorde, "")
    return f"{base}{sufixo}"


def _pitches(nomes: list[str]) -> list[str]:
    return [NOTA_PARA_PITCH.get(n, "C4") for n in nomes]


def _sanitizar(nome: str) -> str:
    """Filesystem-safe name: remove accents and special chars."""
    import unicodedata
    # Normalize → strip combining chars → replace problematic chars
    nfkd = unicodedata.normalize("NFKD", nome)
    ascii_safe = "".join(c for c in nfkd if not unicodedata.combining(c))
    return (
        ascii_safe
        .replace("#", "sharp")
        .replace("/", "-")
        .replace(" ", "_")
    )


def _criar_compasso(
    acordes_por_tempo: list[tuple[list[str], str]],
    tipo_acorde: str,
    notas_nomes: list[str],
    numero: int,
) -> stream.Measure:
    """Create a single 4/4 measure from a sequence of (pitches, cifra) per beat.

    *acordes_por_tempo* is a list of 4 tuples: (pitches, cifra_label)
    — one per quarter-note beat.
    """
    m = stream.Measure(number=numero)

    for beat_idx, (pits, cifra_lbl) in enumerate(acordes_por_tempo):
        if len(pits) == 1:
            n = note.Note(pits[0], quarterLength=1.0)
        else:
            n = m21chord.Chord(pits, quarterLength=1.0)

        # First beat: add header labels and lyric
        if beat_idx == 0:
            cifra_te = expressions.TextExpression(cifra_lbl)
            cifra_te.placement = "above"
            cifra_te.style.fontWeight = "bold"
            cifra_te.style.fontSize = 14
            m.insert(0, cifra_te)

            tipo_te = expressions.TextExpression(tipo_acorde)
            tipo_te.placement = "above"
            tipo_te.style.fontSize = 10
            m.insert(0, tipo_te)

            n.lyric = " ".join(notas_nomes)

        m.append(n)

    return m


def _criar_par_compassos(
    pitches_maior: list[str],
    cifra_maior: str,
    pitches_acorde: list[str],
    cifra_acorde: str,
    tipo_acorde: str,
    notas_nomes: list[str],
    numero_base: int,
) -> tuple[stream.Measure, stream.Measure]:
    """Create the 2-measure pattern for a chord type.

    Measure 1 (intercalated):  Maior | acorde | Maior | acorde
    Measure 2 (pure):          acorde | acorde | acorde | acorde

    Returns (measure1, measure2).
    """
    # Measure 1: alternating Maior / chord
    acordes_m1 = [
        (pitches_maior, cifra_maior),   # 1º tempo — Acorde Maior
        (pitches_acorde, cifra_acorde), # 2º tempo — acorde da vez
        (pitches_maior, cifra_maior),   # 3º tempo — Acorde Maior
        (pitches_acorde, cifra_acorde), # 4º tempo — acorde da vez
    ]
    m1 = _criar_compasso(acordes_m1, tipo_acorde, notas_nomes, numero_base)

    # Measure 2: pure chord
    acordes_m2 = [(pitches_acorde, cifra_acorde)] * 4
    m2 = _criar_compasso(acordes_m2, tipo_acorde, notas_nomes, numero_base + 1)

    return m1, m2


def gerar_musicxml_por_modo_tonica_grau(
    f_fundamental: float = 440.0,
    diretorio_saida: str = "partituras",
) -> None:
    """Generate one .musicxml per (modo, tônica, grau) combination.

    Each file has 18 measures (9 chord types × 2 measures each).
    """
    saida = Path(diretorio_saida)

    print(f"Generating harmonic catalog (f₀ = {f_fundamental} Hz) …")
    df = gerar_dataframe_longo(f_fundamental)

    # Group by (Tônica Fundamental, Modo, Grau)
    grupos = df.groupby(
        ["Tônica Fundamental", "Modo", "Grau", "Nota do Grau"],
        sort=False,
    )
    total_arquivos = len(grupos)
    print(f"  {len(df)} chords → {total_arquivos} files (18 measures each).\n")

    contador = 0
    for (tonica, modo, grau, nota_grau), df_grupo in grupos:
        # Directory per modo
        modo_dir = saida / _sanitizar(modo)
        modo_dir.mkdir(parents=True, exist_ok=True)

        nome_arquivo = modo_dir / f"grau_{grau}_{_sanitizar(tonica)}.musicxml"

        # Build score
        titulo = f"{tonica} — {modo} — Grau {grau} ({nota_grau})"
        score = stream.Score()
        score.metadata = metadata.Metadata()
        score.metadata.title = titulo
        score.metadata.composer = "Sistema Harmônico Pitagórico"

        part = stream.Part()
        part.partName = titulo

        # Extract the "Acorde Maior" row to use as reference for intercalation
        row_maior = df_grupo[df_grupo["Tipo de Acorde"] == "Acorde Maior"].iloc[0]
        pitches_maior = _pitches(row_maior["Notas do Acorde"].split())
        cifra_maior = _cifra(nota_grau, "Acorde Maior")

        numero_compasso = 1
        primeiro = True
        for _, row in df_grupo.iterrows():
            tipo_acorde = row["Tipo de Acorde"]
            notas_nomes = row["Notas do Acorde"].split()
            cifra_acorde = _cifra(nota_grau, tipo_acorde)
            pitches_acorde = _pitches(notas_nomes)

            m1, m2 = _criar_par_compassos(
                pitches_maior, cifra_maior,
                pitches_acorde, cifra_acorde,
                tipo_acorde, notas_nomes,
                numero_compasso,
            )

            # First measure of the file: clef, time signature, tempo
            if primeiro:
                m1.insert(0, clef.TrebleClef())
                m1.insert(0, meter.TimeSignature("4/4"))
                m1.insert(0, tempo.MetronomeMark(text="Moderato", number=108))
                primeiro = False

            part.append(m1)
            part.append(m2)
            numero_compasso += 2

        score.append(part)
        score.write("musicxml", fp=str(nome_arquivo))

        contador += 1
        if contador % 50 == 0 or contador == total_arquivos:
            print(f"  {contador}/{total_arquivos} files written …")

    print(f"\nDone — {total_arquivos} MusicXML files saved to '{diretorio_saida}/'.")


if __name__ == "__main__":
    gerar_musicxml_por_modo_tonica_grau()
