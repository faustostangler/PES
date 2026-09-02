#!/usr/bin/env python3
"""
Brazilian Constitutions Parser: Downloads and transforms Brazilian Constitutions into hierarchical XML and plain-text files.

Removes revoked/struck-through text (<strike>, <s>, <del>, line-through styles) and builds:
1. Structured XML documents containing Parte, Livro, Título, Capítulo, Seção, Subseção,
   Artigo, Caput, Parágrafo, Inciso, Alínea, and Item nodes with inline references.
2. Clean, human-readable plain-text files (.txt) preserving the complete indented hierarchy
   without any XML tags and with 100% correct UTF-8 character encoding.
"""

from __future__ import annotations

import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TypedDict
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

# --- Configuration ---
OUTPUT_DIR = Path("/home/stangler/Documents/Python/PES/playground/legis")
CACHE_DIR = Path("/home/stangler/Documents/Python/PES/playground/legis/cache_html")


class ConstitutionMeta(TypedDict):
    id: str
    name: str
    year: int
    url: str


class LinkData(TypedDict):
    text: str
    href: str


class BlockData(TypedDict):
    text: str
    links: list[LinkData]


CONSTITUTIONS: list[ConstitutionMeta] = [
    {
        "id": "constituicao_1988",
        "name": "Constituição da República Federativa do Brasil de 1988",
        "year": 1988,
        "url": "http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao.htm",
    },
    {
        "id": "constituicao_1969",
        "name": "Constituição da República Federativa do Brasil de 1967 com Emenda Constitucional nº 1 de 1969",
        "year": 1969,
        "url": "http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao67EMC69.htm",
    },
    {
        "id": "constituicao_1967",
        "name": "Constituição da República Federativa do Brasil de 1967",
        "year": 1967,
        "url": "http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao67.htm",
    },
    {
        "id": "constituicao_1946",
        "name": "Constituição dos Estados Unidos do Brasil de 1946",
        "year": 1946,
        "url": "http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao46.htm",
    },
    {
        "id": "constituicao_1937",
        "name": "Constituição dos Estados Unidos do Brasil de 1937",
        "year": 1937,
        "url": "http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao37.htm",
    },
    {
        "id": "constituicao_1934",
        "name": "Constituição da República dos Estados Unidos do Brasil de 1934",
        "year": 1934,
        "url": "http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao34.htm",
    },
    {
        "id": "constituicao_1891",
        "name": "Constituição da República dos Estados Unidos do Brasil de 1891",
        "year": 1891,
        "url": "http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao91.htm",
    },
    {
        "id": "constituicao_1824",
        "name": "Constituição Política do Império do Brasil de 1824",
        "year": 1824,
        "url": "http://www.planalto.gov.br/ccivil_03/Constituicao/Constituicao24.htm",
    },
]

# --- Hierarchy Regular Expressions ---
RE_ADCT = re.compile(
    r"^(?:ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSIT[OÓ]RIAS|DISPOSIÇÕES CONSTITUCIONAIS TRANSIT[OÓ]RIAS|DISPOSIÇÕES TRANSIT[OÓ]RIAS(?:\s+E\s+FINAIS)?)\b",
    re.I,
)
RE_PARTE = re.compile(
    r"^(?:PARTE\s+(?:PRIMEIRA|SEGUNDA|TERCEIRA|GERAL|ESPECIAL|[IVXLCDM]+|\d+))\b",
    re.I,
)
RE_LIVRO = re.compile(
    r"^(?:LIVRO\s+([IVXLCDM]+|\d+|ÚNICO|UNICO|PRIMEIRO|SEGUNDO))\b",
    re.I,
)
RE_TITULO = re.compile(
    r"^(?:T[ÍI]T[ÍI]?ULO)\s+([IVXLCDM]+|\d+º?|\d+|ÚNICO|UNICO|PRELIMINAR)(?:\b|[\.\:\s\-–—]|$)",
    re.I,
)
RE_CAPITULO = re.compile(
    r"^(?:CAP[ÍI]TULO)\s+([IVXLCDM]+|\d+º?|\d+|ÚNICO|UNICO)(?:\b|[\.\:\s\-–—]|$)",
    re.I,
)
RE_SECAO = re.compile(
    r"^(?:SE[ÇC][ÇC]?[ÃA]O)\s+([IVXLCDM]+[A-Za-z\-]*|\d+º?|\d+[A-Za-z\-]*|ÚNICA|UNICA)(?:\b|[\.\:\s\-–—]|$)",
    re.I,
)
RE_SUBSECAO = re.compile(
    r"^(?:SUBSE[ÇC][ÇC]?[ÃA]O)\s+([IVXLCDM]+[A-Za-z\-]*|\d+º?|\d+[A-Za-z\-]*|ÚNICA|UNICA)(?:\b|[\.\:\s\-–—]|$)",
    re.I,
)
RE_ARTIGO = re.compile(
    r"^(?:Artigo|Art\.|Art)\s*(\d+[A-Za-z0-9\-\.]*|\b[IVXLCDM]+\b|primeiro|segundo|único)?\s*[\-\.\º\°\:]?\s*(.*)$",
    re.I,
)
RE_PARAGRAFO = re.compile(
    r"^(?:§\s*(\d+[A-Za-z0-9\-\.]*º?|\búnico\b|\bunico\b)?|Par[áa]gra(?:f|ph)o\s+([uú]nico|\d+[A-Za-z0-9\-\.]*º?)|Par[áa]gra(?:f|ph)o|§\.\s*(\d+[A-Za-z0-9\-\.]*º?))\s*[\-\.\º\°\:]?\s*(.*)$",
    re.I,
)
RE_INCISO = re.compile(
    r"^([IVXLCDM]+|\d+º\s*\))\s*[\-\–\—\.\)\,\:]\s*(.*)$",
    re.I,
)
RE_ALINEA = re.compile(
    r"^([a-z])\s*[\)\-\–\—\.]\s*(.*)$",
)
RE_ITEM = re.compile(
    r"^(\d+)\s*[\.\-\)\–\—]\s*(.*)$",
)


def fetch_html(url: str, cache_file: Path) -> bytes:
    """Fetch HTML content from URL with caching."""
    if cache_file.exists() and cache_file.stat().st_size > 0:
        return cache_file.read_bytes()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_bytes(response.content)
    return response.content


def clean_html_blocks(html_bytes: bytes, base_url: str) -> list[BlockData]:
    """Parse HTML, eliminate struck-through/deleted text, and return clean block lines with related links."""
    # Planalto documents are natively encoded in Windows-1252 / ISO-8859-1
    try:
        html_text = html_bytes.decode("windows-1252")
    except UnicodeDecodeError:
        try:
            html_text = html_bytes.decode("iso-8859-1")
        except UnicodeDecodeError:
            html_text = html_bytes.decode("utf-8", errors="replace")

    soup = BeautifulSoup(html_text, "lxml")

    # 1. Decompose unwanted metadata / script / style tags
    for tag in soup.find_all(["script", "style", "head", "noscript"]):
        tag.decompose()

    # 2. Decompose struck-through and deleted tags (<strike>, <s>, <del>)
    for tag in soup.find_all(["strike", "s", "del"]):
        tag.decompose()

    # 3. Decompose inline styles with text-decoration: line-through
    for tag in soup.find_all(lambda t: t.has_attr("style") and "line-through" in t.get("style", "").lower()):
        tag.decompose()

    # 4. Extract distinct block-level elements in document sequence
    blocks: list[BlockData] = []
    block_tags = ["p", "center", "blockquote", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr"]
    for elem in soup.find_all(block_tags):
        if elem.find(block_tags):
            continue
        text = " ".join(elem.get_text().split())
        if not text:
            continue

        links: list[LinkData] = []
        for a in elem.find_all("a", href=True):
            href = str(a["href"]).strip()
            if href and not href.startswith("#") and not href.startswith("javascript:") and not href.startswith("mailto:"):
                full_url = urljoin(base_url, href)
                a_text = " ".join(a.get_text().split()).strip("() ")
                if a_text:
                    links.append({"text": a_text, "href": full_url})

        blocks.append({"text": text, "links": links})

    return blocks


def sanitize_id(val: str) -> str:
    """Generate safe XML attribute IDs with unicode normalization."""
    nfkd = unicodedata.normalize("NFKD", val).encode("ASCII", "ignore").decode("ASCII")
    cleaned = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", nfkd.lower()).strip("_")
    return cleaned or "node"


def is_heading(text: str) -> bool:
    """Check if text is a structural container heading."""
    return bool(
        RE_ADCT.match(text)
        or RE_PARTE.match(text)
        or RE_LIVRO.match(text)
        or RE_TITULO.match(text)
        or RE_CAPITULO.match(text)
        or RE_SECAO.match(text)
        or RE_SUBSECAO.match(text)
    )


def is_normative(text: str) -> bool:
    """Check if text begins a normative unit."""
    return bool(
        RE_ARTIGO.match(text)
        or RE_PARAGRAFO.match(text)
        or RE_INCISO.match(text)
        or RE_ALINEA.match(text)
        or RE_ITEM.match(text)
    )


def add_references(elem: ET.Element, links: list[LinkData]) -> None:
    """Attach related legislation reference elements directly to the given node."""
    for lk in links:
        ET.SubElement(elem, "referencia", {"texto": lk["text"], "link": lk["href"]})


def build_constitution_tree(name: str, year: int, url: str, blocks: list[BlockData]) -> ET.Element:
    """Build a complete hierarchical XML tree with inline legislation references attached directly to each node."""
    root = ET.Element("constituicao", {"nome": name, "ano": str(year), "url": url})
    preambulo: ET.Element | None = None
    corpo = ET.SubElement(root, "corpo")
    adct: ET.Element | None = None
    fecho: ET.Element | None = None

    current_container: ET.Element = corpo
    current_artigo: ET.Element | None = None
    current_paragrafo: ET.Element | None = None
    current_inciso: ET.Element | None = None
    current_alinea: ET.Element | None = None

    containers: dict[str, ET.Element | None] = {
        "corpo": corpo,
        "parte": None,
        "livro": None,
        "titulo": None,
        "capitulo": None,
        "secao": None,
        "subsecao": None,
    }

    def get_parent_container(level: int) -> ET.Element:
        hierarchy = ["subsecao", "secao", "capitulo", "titulo", "livro", "parte", "corpo"]
        is_in_adct = (adct is not None) and (
            current_container == adct
            or any(
                adct == containers[c]
                for c in ["subsecao", "secao", "capitulo", "titulo", "parte"]
                if containers[c] is not None
            )
        )
        if is_in_adct and adct is not None:
            for key in hierarchy:
                elem = containers[key]
                if elem is not None:
                    key_level = {
                        "corpo": 0,
                        "parte": 1,
                        "livro": 2,
                        "titulo": 3,
                        "capitulo": 4,
                        "secao": 5,
                        "subsecao": 6,
                    }[key]
                    if key_level < level:
                        return elem
            return adct

        for key in hierarchy:
            elem = containers[key]
            if elem is not None:
                key_level = {
                    "corpo": 0,
                    "parte": 1,
                    "livro": 2,
                    "titulo": 3,
                    "capitulo": 4,
                    "secao": 5,
                    "subsecao": 6,
                }[key]
                if key_level < level:
                    return elem
        return corpo

    i = 0
    in_preamble = True
    in_fecho = False

    while i < len(blocks):
        b_data = blocks[i]
        b = b_data["text"]
        b_links = b_data["links"]

        # Check for ADCT (must not be a preamble header link)
        if RE_ADCT.match(b) and not in_preamble:
            adct_id = "adct"
            adct = ET.SubElement(root, "adct", {"id": adct_id, "rotulo": b})
            add_references(adct, b_links)
            current_container = adct
            for k in containers:
                if k != "corpo":
                    containers[k] = None
            current_artigo = None
            current_paragrafo = None
            current_inciso = None
            current_alinea = None
            i += 1
            continue

        # Check for Parte
        m_parte = RE_PARTE.match(b)
        if m_parte:
            in_preamble = False
            denominacao = ""
            if i + 1 < len(blocks) and not is_heading(blocks[i + 1]["text"]) and not is_normative(blocks[i + 1]["text"]):
                denominacao = blocks[i + 1]["text"]
                b_links.extend(blocks[i + 1]["links"])
                i += 1
            parent = adct if (adct is not None and current_container == adct) else corpo
            parte_id = sanitize_id(b)
            parte_elem = ET.SubElement(
                parent,
                "parte",
                {"id": parte_id, "rotulo": b, "denominacao": denominacao},
            )
            add_references(parte_elem, b_links)
            containers["parte"] = parte_elem
            containers["livro"] = None
            containers["titulo"] = None
            containers["capitulo"] = None
            containers["secao"] = None
            containers["subsecao"] = None
            current_container = parte_elem
            current_artigo = None
            i += 1
            continue

        # Check for Livro
        m_livro = RE_LIVRO.match(b)
        if m_livro:
            in_preamble = False
            denominacao = ""
            if i + 1 < len(blocks) and not is_heading(blocks[i + 1]["text"]) and not is_normative(blocks[i + 1]["text"]):
                denominacao = blocks[i + 1]["text"]
                b_links.extend(blocks[i + 1]["links"])
                i += 1
            parent = get_parent_container(2)
            livro_id = sanitize_id(b)
            livro_elem = ET.SubElement(
                parent,
                "livro",
                {"id": livro_id, "rotulo": b, "denominacao": denominacao},
            )
            add_references(livro_elem, b_links)
            containers["livro"] = livro_elem
            containers["titulo"] = None
            containers["capitulo"] = None
            containers["secao"] = None
            containers["subsecao"] = None
            current_container = livro_elem
            current_artigo = None
            i += 1
            continue

        # Check for Titulo
        m_tit = RE_TITULO.match(b)
        if m_tit:
            in_preamble = False
            denominacao = ""
            if i + 1 < len(blocks) and not is_heading(blocks[i + 1]["text"]) and not is_normative(blocks[i + 1]["text"]):
                denominacao = blocks[i + 1]["text"]
                b_links.extend(blocks[i + 1]["links"])
                i += 1
            parent = get_parent_container(3)
            titulo_id = sanitize_id(b)
            tit_elem = ET.SubElement(
                parent,
                "titulo",
                {"id": titulo_id, "rotulo": b, "denominacao": denominacao},
            )
            add_references(tit_elem, b_links)
            containers["titulo"] = tit_elem
            containers["capitulo"] = None
            containers["secao"] = None
            containers["subsecao"] = None
            current_container = tit_elem
            current_artigo = None
            i += 1
            continue

        # Check for Capitulo
        m_cap = RE_CAPITULO.match(b)
        if m_cap:
            in_preamble = False
            denominacao = ""
            if i + 1 < len(blocks) and not is_heading(blocks[i + 1]["text"]) and not is_normative(blocks[i + 1]["text"]):
                denominacao = blocks[i + 1]["text"]
                b_links.extend(blocks[i + 1]["links"])
                i += 1
            parent = get_parent_container(4)
            capitulo_id = sanitize_id(b)
            cap_elem = ET.SubElement(
                parent,
                "capitulo",
                {"id": capitulo_id, "rotulo": b, "denominacao": denominacao},
            )
            add_references(cap_elem, b_links)
            containers["capitulo"] = cap_elem
            containers["secao"] = None
            containers["subsecao"] = None
            current_container = cap_elem
            current_artigo = None
            i += 1
            continue

        # Check for Secao
        m_sec = RE_SECAO.match(b)
        if m_sec:
            in_preamble = False
            denominacao = ""
            if i + 1 < len(blocks) and not is_heading(blocks[i + 1]["text"]) and not is_normative(blocks[i + 1]["text"]):
                denominacao = blocks[i + 1]["text"]
                b_links.extend(blocks[i + 1]["links"])
                i += 1
            parent = get_parent_container(5)
            secao_id = sanitize_id(b)
            sec_elem = ET.SubElement(
                parent,
                "secao",
                {"id": secao_id, "rotulo": b, "denominacao": denominacao},
            )
            add_references(sec_elem, b_links)
            containers["secao"] = sec_elem
            containers["subsecao"] = None
            current_container = sec_elem
            current_artigo = None
            i += 1
            continue

        # Check for Subsecao
        m_subsec = RE_SUBSECAO.match(b)
        if m_subsec:
            in_preamble = False
            denominacao = ""
            if i + 1 < len(blocks) and not is_heading(blocks[i + 1]["text"]) and not is_normative(blocks[i + 1]["text"]):
                denominacao = blocks[i + 1]["text"]
                b_links.extend(blocks[i + 1]["links"])
                i += 1
            parent = get_parent_container(6)
            subsecao_id = sanitize_id(b)
            subsec_elem = ET.SubElement(
                parent,
                "subsecao",
                {"id": subsecao_id, "rotulo": b, "denominacao": denominacao},
            )
            add_references(subsec_elem, b_links)
            containers["subsecao"] = subsec_elem
            current_container = subsec_elem
            current_artigo = None
            i += 1
            continue

        # Check for Artigo
        m_art = RE_ARTIGO.match(b)
        if m_art:
            in_preamble = False
            raw_num = m_art.group(1) or ""
            text = (m_art.group(2) or "").lstrip(" -–—.:").strip()
            num = raw_num.rstrip(".-º°")
            parent = get_parent_container(7)
            art_id = f"art_{sanitize_id(num)}" if num else f"art_{i}"
            if adct is not None and (
                current_container == adct
                or any(
                    adct == containers[c]
                    for c in ["subsecao", "secao", "capitulo", "titulo", "parte"]
                    if containers[c] is not None
                )
            ):
                art_id = f"adct_{art_id}"
            art_elem = ET.SubElement(
                parent,
                "artigo",
                {"id": art_id, "rotulo": f"Art. {raw_num}" if raw_num else "Artigo", "numero": num},
            )
            if text:
                caput = ET.SubElement(art_elem, "caput")
                caput.text = text
            add_references(art_elem, b_links)
            current_artigo = art_elem
            current_paragrafo = None
            current_inciso = None
            current_alinea = None
            i += 1
            continue

        # Check for Paragrafo
        m_par = RE_PARAGRAFO.match(b)
        if m_par and current_artigo is not None:
            text = (m_par.groups()[-1] or "").lstrip(" -–—.:").strip()
            rot_match = m_par.group(1) or m_par.group(2) or m_par.group(3) or "unico"
            rotulo = f"§ {rot_match}" if not rot_match.lower().startswith("único") and not rot_match.lower().startswith("unico") else "Parágrafo único"
            if "paragrapho" in b.lower():
                rotulo = f"Paragrapho {rot_match}"
            elif "parágrafo" in b.lower() or "paragrafo" in b.lower():
                rotulo = f"Parágrafo {rot_match}"

            par_id = f"{current_artigo.get('id', 'art')}-par_{sanitize_id(rot_match)}"
            par_elem = ET.SubElement(current_artigo, "paragrafo", {"id": par_id, "rotulo": rotulo})
            if text:
                t_elem = ET.SubElement(par_elem, "texto")
                t_elem.text = text
            add_references(par_elem, b_links)
            current_paragrafo = par_elem
            current_inciso = None
            current_alinea = None
            i += 1
            continue

        # Check for Inciso
        m_inc = RE_INCISO.match(b)
        if m_inc and current_artigo is not None:
            num = m_inc.group(1).rstrip(")")
            text = (m_inc.group(2) or "").lstrip(" -–—.:").strip()
            parent = current_paragrafo if current_paragrafo is not None else current_artigo
            inc_id = f"{parent.get('id', 'item')}-inc_{sanitize_id(num)}"
            inc_elem = ET.SubElement(parent, "inciso", {"id": inc_id, "rotulo": num})
            if text:
                t_elem = ET.SubElement(inc_elem, "texto")
                t_elem.text = text
            add_references(inc_elem, b_links)
            current_inciso = inc_elem
            current_alinea = None
            i += 1
            continue

        # Check for Alinea
        m_ali = RE_ALINEA.match(b)
        if m_ali and (
            current_inciso is not None or current_paragrafo is not None or current_artigo is not None
        ):
            letra = m_ali.group(1)
            text = (m_ali.group(2) or "").lstrip(" -–—.:)").strip()
            parent = (
                current_inciso
                if current_inciso is not None
                else (current_paragrafo if current_paragrafo is not None else current_artigo)
            )
            if parent is not None:
                ali_id = f"{parent.get('id', 'item')}-ali_{sanitize_id(letra)}"
                ali_elem = ET.SubElement(parent, "alinea", {"id": ali_id, "rotulo": letra})
                if text:
                    t_elem = ET.SubElement(ali_elem, "texto")
                    t_elem.text = text
                add_references(ali_elem, b_links)
                current_alinea = ali_elem
            i += 1
            continue

        # Check for Item
        m_itm = RE_ITEM.match(b)
        if m_itm and current_alinea is not None:
            num = m_itm.group(1)
            text = (m_itm.group(2) or "").lstrip(" -–—.:)").strip()
            itm_id = f"{current_alinea.get('id', 'item')}-itm_{sanitize_id(num)}"
            itm_elem = ET.SubElement(current_alinea, "item", {"id": itm_id, "rotulo": num})
            if text:
                t_elem = ET.SubElement(itm_elem, "texto")
                t_elem.text = text
            add_references(itm_elem, b_links)
            i += 1
            continue

        # Handle Preamble vs Body continuation vs Enactment/Fecho
        if in_preamble:
            if preambulo is None:
                preambulo = ET.Element("preambulo", {"id": "preambulo"})
                root.insert(0, preambulo)
            p_elem = ET.SubElement(preambulo, "texto")
            p_elem.text = b
            add_references(p_elem, b_links)
        else:
            if any(
                k in b.lower()
                for k in [
                    "brasília,",
                    "rio de janeiro,",
                    "palácio do governo",
                    "este texto não substitui",
                    "mesa da assembléia",
                    "sala das sessões",
                ]
            ):
                in_fecho = True
                if fecho is None:
                    fecho = ET.SubElement(root, "fecho", {"id": "fecho"})
            if in_fecho and fecho is not None:
                p_elem = ET.SubElement(fecho, "texto")
                p_elem.text = b
                add_references(p_elem, b_links)
            else:
                if current_artigo is not None:
                    target = (
                        current_alinea
                        if current_alinea is not None
                        else (
                            current_inciso
                            if current_inciso is not None
                            else (current_paragrafo if current_paragrafo is not None else current_artigo)
                        )
                    )
                    t_child = target.find("texto")
                    if t_child is not None and t_child.text:
                        t_child.text += " " + b
                    else:
                        t_elem = ET.SubElement(target, "texto")
                        t_elem.text = b
                    add_references(target, b_links)
                else:
                    target_container = get_parent_container(7)
                    t_elem = ET.SubElement(target_container, "texto")
                    t_elem.text = b
                    add_references(target_container, b_links)
        i += 1

    return root


def tree_to_indented_text(elem: ET.Element, indent_level: int = 0) -> list[str]:
    """Convert XML ElementTree into a clean, human-readable indented plain-text document."""
    lines: list[str] = []
    indent = "  " * indent_level
    tag = elem.tag

    if tag == "constituicao":
        nome = (elem.get("nome") or "").upper()
        ano = elem.get("ano") or ""
        url = elem.get("url") or ""
        lines.append("=" * 80)
        lines.append(f"{nome} ({ano})")
        lines.append(f"URL Oficial: {url}")
        lines.append("=" * 80)
        lines.append("")
        for child in elem:
            lines.extend(tree_to_indented_text(child, 0))

    elif tag == "preambulo":
        lines.append("[PREÂMBULO]")
        for child in elem:
            if child.tag == "texto" and child.text:
                lines.append(f"  {child.text}")
            elif child.tag == "referencia":
                lines.append(f"  [Ref: {child.get('texto')} -> {child.get('link')}]")
        lines.append("")

    elif tag == "corpo":
        for child in elem:
            lines.extend(tree_to_indented_text(child, 0))

    elif tag == "adct":
        rotulo = elem.get("rotulo") or "ATO DAS DISPOSIÇÕES CONSTITUCIONAIS TRANSITÓRIAS"
        lines.append(f"\n{rotulo}")
        lines.append("-" * len(rotulo) + "\n")
        for child in elem:
            lines.extend(tree_to_indented_text(child, 1))

    elif tag in ("parte", "livro", "titulo", "capitulo", "secao", "subsecao"):
        rotulo = elem.get("rotulo") or ""
        denominacao = elem.get("denominacao") or ""
        header = rotulo
        if denominacao:
            header += f" - {denominacao}"
        lines.append(f"\n{indent}{header}")
        for child in elem:
            lines.extend(tree_to_indented_text(child, indent_level + 1))

    elif tag == "artigo":
        rotulo = elem.get("rotulo") or "Artigo"
        caput_elem = elem.find("caput")
        caput_text = caput_elem.text if caput_elem is not None and caput_elem.text else ""
        if caput_text:
            lines.append(f"{indent}{rotulo} {caput_text}")
        else:
            lines.append(f"{indent}{rotulo}")
        for child in elem:
            if child.tag != "caput":
                lines.extend(tree_to_indented_text(child, indent_level + 1))
        lines.append("")

    elif tag == "paragrafo":
        rotulo = elem.get("rotulo") or "§"
        t_elem = elem.find("texto")
        t_text = t_elem.text if t_elem is not None and t_elem.text else ""
        lines.append(f"{indent}{rotulo} {t_text}".rstrip())
        for child in elem:
            if child.tag != "texto":
                lines.extend(tree_to_indented_text(child, indent_level + 1))

    elif tag == "inciso":
        rotulo = elem.get("rotulo") or ""
        t_elem = elem.find("texto")
        t_text = t_elem.text if t_elem is not None and t_elem.text else ""
        lines.append(f"{indent}{rotulo} - {t_text}".rstrip())
        for child in elem:
            if child.tag != "texto":
                lines.extend(tree_to_indented_text(child, indent_level + 1))

    elif tag == "alinea":
        rotulo = elem.get("rotulo") or ""
        t_elem = elem.find("texto")
        t_text = t_elem.text if t_elem is not None and t_elem.text else ""
        lines.append(f"{indent}{rotulo}) {t_text}".rstrip())
        for child in elem:
            if child.tag != "texto":
                lines.extend(tree_to_indented_text(child, indent_level + 1))

    elif tag == "item":
        rotulo = elem.get("rotulo") or ""
        t_elem = elem.find("texto")
        t_text = t_elem.text if t_elem is not None and t_elem.text else ""
        lines.append(f"{indent}{rotulo}. {t_text}".rstrip())
        for child in elem:
            if child.tag != "texto":
                lines.extend(tree_to_indented_text(child, indent_level + 1))

    elif tag == "referencia":
        texto = elem.get("texto") or ""
        link = elem.get("link") or ""
        lines.append(f"{indent}[Ref: {texto} -> {link}]")

    elif tag == "fecho":
        lines.append("\n[FECHO / ENCERRAMENTO]")
        for child in elem:
            if child.tag == "texto" and child.text:
                lines.append(f"  {child.text}")
            elif child.tag == "referencia":
                lines.append(f"  [Ref: {child.get('texto')} -> {child.get('link')}]")

    elif tag == "texto":
        if elem.text:
            lines.append(f"{indent}{elem.text}")

    return lines


def main():
    """Main execution function to process all constitutions into XML and clean indented TXT."""
    print("=" * 70)
    print("BRAZILIAN CONSTITUTIONS TO XML & INDENTED TXT PARSER (YOLO MODE)")
    print("=" * 70)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    summary_stats: list[dict[str, object]] = []

    for item in CONSTITUTIONS:
        cid = str(item["id"])
        cname = str(item["name"])
        cyear = int(item["year"])
        curl = str(item["url"])
        cache_file = CACHE_DIR / f"{cid}.html"

        print(f"\n[+] Processing {cname} ({cyear})...")
        print(f"    Fetching: {curl}")
        html_bytes = fetch_html(curl, cache_file)
        print(f"    Raw HTML Size: {len(html_bytes):,} bytes")

        blocks = clean_html_blocks(html_bytes, curl)
        print(f"    Clean blocks (no strikes): {len(blocks)}")

        tree = build_constitution_tree(cname, cyear, curl, blocks)
        ET.indent(tree, space="  ")
        xml_bytes = ET.tostring(tree, encoding="utf-8", xml_declaration=True)

        # 1. Save structured XML
        xml_file = OUTPUT_DIR / f"{cid}.xml"
        xml_file.write_bytes(xml_bytes)

        # 2. Render and save clean hierarchical plain text (no XML tags)
        txt_lines = tree_to_indented_text(tree)
        txt_content = "\n".join(txt_lines) + "\n"
        txt_file = OUTPUT_DIR / f"{cid}.txt"
        txt_file.write_text(txt_content, encoding="utf-8")

        # Sanity validation
        reparsed = ET.fromstring(xml_bytes)
        artigos = list(reparsed.iter("artigo"))
        titulos = list(reparsed.iter("titulo"))
        capitulos = list(reparsed.iter("capitulo"))
        secoes = list(reparsed.iter("secao"))
        paragrafos = list(reparsed.iter("paragrafo"))
        incisos = list(reparsed.iter("inciso"))
        alineas = list(reparsed.iter("alinea"))
        referencias = list(reparsed.iter("referencia"))

        assert len(artigos) > 0, f"Constitution {cid} must contain articles"
        assert xml_file.exists() and xml_file.stat().st_size > 0
        assert txt_file.exists() and txt_file.stat().st_size > 0

        print(f"    ✓ Saved XML: {xml_file.name} ({len(xml_bytes):,} bytes)")
        print(f"    ✓ Saved TXT: {txt_file.name} ({len(txt_content):,} chars, {len(txt_lines):,} lines)")
        print(
            f"    Structure: {len(titulos)} Títulos | {len(capitulos)} Capítulos | "
            f"{len(secoes)} Seções | {len(artigos)} Artigos | "
            f"{len(paragrafos)} Parágrafos | {len(incisos)} Incisos | {len(alineas)} Alíneas | "
            f"{len(referencias)} Referências Inline"
        )

        summary_stats.append(
            {
                "id": cid,
                "year": cyear,
                "xml_kb": len(xml_bytes) / 1024,
                "txt_kb": len(txt_content.encode("utf-8")) / 1024,
                "articles": len(artigos),
                "titles": len(titulos),
                "chapters": len(capitulos),
                "sections": len(secoes),
                "paragraphs": len(paragrafos),
                "incisos": len(incisos),
                "refs": len(referencias),
            }
        )

    print("\n" + "=" * 70)
    print("SUMMARY OF PROCESSED CONSTITUTIONS (XML & INDENTED TXT)")
    print("=" * 70)
    print(f"{'Constitution':<20} | {'Year':<4} | {'XML (KB)':<8} | {'TXT (KB)':<8} | {'Arts':<5} | {'Tits':<4} | {'Caps':<4} | {'Pars':<5} | {'Incs':<5} | {'Refs':<5}")
    print("-" * 88)
    for s in summary_stats:
        print(
            f"{str(s['id']):<20} | {s['year']!s:<4} | {float(s['xml_kb']):<8.1f} | {float(s['txt_kb']):<8.1f} | {s['articles']!s:<5} | "
            f"{s['titles']!s:<4} | {s['chapters']!s:<4} | {s['paragraphs']!s:<5} | {s['incisos']!s:<5} | {s['refs']!s:<5}"
        )
    print("=" * 70)
    print(f"All XML & TXT files successfully created in: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
