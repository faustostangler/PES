"""Unit tests for SelectolaxHtmlParser ensuring high-speed HTML text and link extraction."""

from __future__ import annotations

from cresmo.infrastructure.adapters.scrapers import SelectolaxHtmlParser


def test_extract_clean_text() -> None:
    """Verify that script, style, and navigation tags are stripped and clean text returned."""
    html = """
    <html>
        <head>
            <title>Test Page Title</title>
            <style>body { color: red; }</style>
            <script>console.log("secret tracker");</script>
        </head>
        <body>
            <header><nav><a href="/home">Home</a></nav></header>
            <main>
                <h1>Main Heading</h1>
                <p>First paragraph with <strong>bold</strong> words.</p>
                <p>Second paragraph explaining historical palimpsest.</p>
            </main>
            <footer><p>Copyright 2026</p></footer>
        </body>
    </html>
    """

    text = SelectolaxHtmlParser.extract_clean_text(html)
    assert "Main Heading" in text
    assert "First paragraph with bold words." in text
    assert "Second paragraph explaining historical palimpsest." in text
    assert "secret tracker" not in text
    assert "body { color: red; }" not in text
    assert "Copyright" not in text


def test_extract_metadata_and_links() -> None:
    """Verify title, meta description, and anchor link resolution."""
    html = """
    <html>
        <head>
            <title>Cresmo Knowledge Portal</title>
            <meta name="description" content="Deep structural historiography and knowledge synthesis." />
        </head>
        <body>
            <a href="/episodes/1">Episode 1</a>
            <a href="https://externalsite.org/ref">External Reference</a>
        </body>
    </html>
    """

    meta = SelectolaxHtmlParser.extract_metadata_and_links(html, base_url="https://cresmo.ai")
    assert meta["title"] == "Cresmo Knowledge Portal"
    assert meta["description"] == "Deep structural historiography and knowledge synthesis."
    assert "https://cresmo.ai/episodes/1" in meta["links"]
    assert "https://externalsite.org/ref" in meta["links"]


def test_empty_html_handling() -> None:
    """Verify graceful empty handling."""
    assert SelectolaxHtmlParser.extract_clean_text("") == ""
    assert SelectolaxHtmlParser.extract_clean_text("   ") == ""
    res = SelectolaxHtmlParser.extract_metadata_and_links("")
    assert res["title"] == ""
    assert res["links"] == []
