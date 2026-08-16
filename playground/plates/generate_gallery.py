#!/usr/bin/env python3
"""Generate an interactive HTML matrix table (Years x States) using original online 15q.net URLs."""

import argparse
import html
import os
import re
from collections import defaultdict
from pathlib import Path

# --- Config ---
DEFAULT_INPUT_DIR = Path("/home/stangler/Documents/Python/PES/downloads")
DEFAULT_OUTPUT_HTML = Path("/home/stangler/Documents/Python/PES/playground/plates/plates_table.html")

ALL_US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WV", "WA", "WI",
    "WY"
]


# Mapping of US states to 15q.net image directory
STATE_TO_DIR = {
    # us1
    "AL": "us1", "AK": "us1", "AZ": "us1", "AR": "us1", "CA": "us1",
    "CO": "us1", "CT": "us1", "DE": "us1", "DC": "us1", "FL": "us1", "GA": "us1",
    # us2
    "HI": "us2", "ID": "us2", "IL": "us2", "IN": "us2", "IA": "us2",
    "KS": "us2", "KY": "us2", "LA": "us2", "ME": "us2", "MD": "us2",
    # us3
    "MA": "us3", "MI": "us3", "MN": "us3", "MS": "us3", "MO": "us3",
    "MT": "us3", "NE": "us3", "NV": "us3", "NH": "us3", "NJ": "us3",
    # us4
    "NM": "us4", "NY": "us4", "NC": "us4", "ND": "us4", "OH": "us4",
    "OK": "us4", "OR": "us4", "PA": "us4", "RI": "us4", "SC": "us4",
    # us5
    "SD": "us5", "TN": "us5", "TX": "us5", "UT": "us5", "VT": "us5",
    "VA": "us5", "WA": "us5", "WV": "us5", "WI": "us5", "WY": "us5",
}


# --- Logic ---
def parse_image_filename(filename: str) -> tuple[str, str, str, int] | None:
    """Extract (year, state, orig_filename, index) from plate image filenames.

    >>> parse_image_filename("1969-al-1.jpg")
    ('1969', 'AL', 'al69.jpg', 1)
    >>> parse_image_filename("1969-al-2.jpg")
    ('1969', 'AL', 'al69a.jpg', 2)
    >>> parse_image_filename("2006-ca-2.jpg")
    ('2006', 'CA', 'ca06a.jpg', 2)
    >>> parse_image_filename("69-al-1.jpg")
    ('1969', 'AL', 'al69.jpg', 1)
    >>> parse_image_filename("al69a.jpg")
    ('1969', 'AL', 'al69a.jpg', 2)
    """
    # Standard format: {year}-{state}-{index}.ext
    m_std = re.match(r"^(\d{2,4})-([a-zA-Z]{2})-(\d+)\.(jpe?g|png|webp)$", filename, re.IGNORECASE)
    if m_std:
        year_raw, state, idx_str, _ = m_std.groups()
        if len(year_raw) == 2:
            yr_int = int(year_raw)
            year = f"19{year_raw}" if yr_int > 30 else f"20{year_raw}"
        else:
            year = year_raw

        idx = int(idx_str)
        year_2digit = year[-2:]
        suffix = "" if idx == 1 else chr(ord("a") + idx - 2)
        orig_fn = f"{state.lower()}{year_2digit}{suffix}.jpg"
        return year, state.upper(), orig_fn, idx

    # Raw legacy format: {state}{year}{suffix}.ext (e.g. al69a.jpg)
    m_raw = re.match(r"^([a-zA-Z]{2})(\d{2})([a-zA-Z]?)\.(jpe?g|png|webp)$", filename, re.IGNORECASE)
    if m_raw:
        state, yr_raw, suffix, _ = m_raw.groups()
        yr_int = int(yr_raw)
        year = f"19{yr_raw}" if yr_int > 30 else f"20{yr_raw}"
        idx = 1 if not suffix else ord(suffix.lower()) - ord("a") + 2
        orig_fn = f"{state.lower()}{yr_raw}{suffix.lower()}.jpg"
        return year, state.upper(), orig_fn, idx

    return None


def scan_images(input_dir: Path) -> dict[str, dict[str, list[dict]]]:
    """Scan folder to discover present plate images and group by year and state."""
    matrix = defaultdict(lambda: defaultdict(list))

    for root, _, files in os.walk(input_dir):
        for f in sorted(files):
            parsed = parse_image_filename(f)
            if not parsed:
                continue

            year, state, orig_fn, idx = parsed
            folder = STATE_TO_DIR.get(state, "us1")
            online_img_url = f"http://15q.net/{folder}/{orig_fn}"
            online_state_url = f"http://15q.net/{state.lower()}.html"

            matrix[year][state].append({
                "orig_filename": orig_fn,
                "online_url": online_img_url,
                "online_state_url": online_state_url,
                "index": idx
            })

    # Sort images inside each cell by index
    for year in matrix:
        for state in matrix[year]:
            matrix[year][state].sort(key=lambda x: x["index"])

    return matrix


def generate_html_table(matrix: dict[str, dict[str, list[dict]]], title: str = "US License Plates Matrix") -> str:
    """Construct full responsive HTML page using original online 15q.net URLs and state page links."""
    # Years from older to newer (ascending order)
    all_years = sorted(matrix.keys(), key=lambda y: int(y) if y.isdigit() else y)

    # Total stats
    total_images = sum(len(imgs) for yr in matrix.values() for imgs in yr.values())
    present_states = sorted(list({st for yr in matrix.values() for st in yr.keys()}))
    rows_states = [st for st in ALL_US_STATES if st in present_states] or present_states or ALL_US_STATES

    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-cell: #1a202c;
            --bg-cell-empty: #0f141c;
            --border-color: #30363d;
            --border-focus: #58a6ff;
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
            --accent-color: #38bdf8;
            --accent-badge: #0284c7;
            --year-color: #fbbf24;
            --thumb-width: 140px;
            --thumb-height: 70px;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-main);
            min-height: 100vh;
            padding: 24px;
        }}

        /* Header & Control Bar */
        .top-bar {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(13, 17, 23, 0.92);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 24px;
            margin: -24px -24px 20px -24px;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 16px;
        }}

        .title-area h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .stats-badge {{
            display: inline-block;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            padding: 4px 10px;
            border-radius: 9999px;
            color: var(--text-muted);
            margin-top: 4px;
        }}

        .stats-badge strong {{
            color: var(--accent-color);
        }}

        .controls {{
            display: flex;
            align-items: center;
            gap: 16px;
            flex-wrap: wrap;
        }}

        .control-group {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        input[type="text"], input[type="number"] {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 7px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
            outline: none;
            transition: border-color 0.2s;
        }}

        input[type="text"]:focus, input[type="number"]:focus {{
            border-color: var(--border-focus);
        }}

        input[type="range"] {{
            cursor: pointer;
            accent-color: var(--accent-color);
        }}

        button.btn {{
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 7px 14px;
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }}

        button.btn:hover {{
            background: #21262d;
            border-color: var(--border-focus);
        }}

        /* Table Container */
        .table-wrap {{
            overflow: auto;
            max-height: calc(100vh - 120px);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background: var(--bg-secondary);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }}

        table.matrix-table {{
            border-collapse: separate;
            border-spacing: 0;
            width: max-content;
        }}

        /* Sticky Columns & Rows */
        th, td {{
            border-right: 1px solid var(--border-color);
            border-bottom: 1px solid var(--border-color);
            padding: 8px;
            text-align: center;
            vertical-align: middle;
        }}

        th.year-col-header {{
            position: sticky;
            top: 0;
            z-index: 30;
            background: #1f2937;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 0.9rem;
            color: var(--year-color);
            padding: 12px 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            min-width: calc(var(--thumb-width) + 16px);
        }}

        th.corner-cell {{
            position: sticky;
            top: 0;
            left: 0;
            z-index: 50;
            background: #111827;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            min-width: 90px;
            box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
        }}

        td.state-row-header {{
            position: sticky;
            left: 0;
            z-index: 20;
            background: #111827;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 2px 0 4px rgba(0, 0, 0, 0.4);
            padding: 4px;
        }}

        a.state-link {{
            color: var(--accent-color);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 6px 10px;
            border-radius: 4px;
            transition: all 0.15s ease;
        }}

        a.state-link:hover {{
            background: rgba(56, 189, 248, 0.15);
            color: #7dd3fc;
            text-decoration: underline;
        }}

        /* Plate Image Cells */
        td.cell-empty {{
            background: var(--bg-cell-empty);
            color: #374151;
            font-size: 0.75rem;
            user-select: none;
        }}

        td.cell-has-plates {{
            background: var(--bg-cell);
            padding: 6px;
        }}

        .plates-container {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            align-items: center;
            justify-content: center;
        }}

        a.plate-card {{
            position: relative;
            display: inline-block;
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: #000;
            text-decoration: none;
            cursor: pointer;
            transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        }}

        a.plate-card:hover {{
            transform: scale(1.06);
            z-index: 10;
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.8);
            border-color: var(--accent-color);
        }}

        a.plate-card img {{
            display: block;
            width: var(--thumb-width);
            height: var(--thumb-height);
            object-fit: cover;
            border-radius: 3px;
        }}

        a.plate-card .badge {{
            position: absolute;
            bottom: 2px;
            right: 2px;
            background: rgba(0, 0, 0, 0.75);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            color: #cbd5e1;
            padding: 1px 4px;
            border-radius: 3px;
            pointer-events: none;
        }}
    </style>
</head>
<body>

<div class="top-bar">
    <div class="title-area">
        <h1>US License Plates Matrix</h1>
        <div class="stats-badge">
            Total: <strong>{total_images}</strong> plates | <strong>{len(rows_states)}</strong> states | <strong>{len(all_years)}</strong> years (older &rarr; newer)
        </div>
    </div>

    <div class="controls">
        <div class="control-group">
            <label for="searchState">State:</label>
            <input type="text" id="searchState" placeholder="e.g. CA" style="width: 75px;" oninput="filterMatrix()">
        </div>
        <div class="control-group">
            <label>Years:</label>
            <input type="number" id="yearFrom" placeholder="{all_years[0] if all_years else ''}" style="width: 80px;" oninput="filterMatrix()" title="From Year">
            <span>to</span>
            <input type="number" id="yearTo" placeholder="{all_years[-1] if all_years else ''}" style="width: 80px;" oninput="filterMatrix()" title="To Year">
        </div>
        <div class="control-group">
            <label for="sizeRange">Zoom:</label>
            <input type="range" id="sizeRange" min="80" max="260" value="140" oninput="changeThumbSize(this.value)">
        </div>
        <button class="btn" onclick="toggleYearSortOrder()">Reverse Years</button>
    </div>
</div>

<div class="table-wrap">
    <table class="matrix-table" id="matrixTable">
        <thead>
            <tr id="headerRow">
                <th class="corner-cell">State / Year</th>""")

    # Column headers (Years: Older to Newer)
    for yr in all_years:
        html_parts.append(f"""                <th class="year-col-header" data-year="{yr}">{yr}</th>""")

    html_parts.append("""            </tr>
        </thead>
        <tbody id="matrixBody">""")

    # Rows (States)
    for st in rows_states:
        state_url = f"http://15q.net/{st.lower()}.html"
        html_parts.append(f"""            <tr data-state="{st}">
                <td class="state-row-header">
                    <a href="{state_url}" target="15q_page" rel="noopener noreferrer" class="state-link" title="Open {st} page on 15q.net">{st} &nearr;</a>
                </td>""")
        for yr in all_years:
            plates = matrix.get(yr, {}).get(st, [])
            if not plates:
                html_parts.append(f"""                <td class="cell-empty" data-year="{yr}">—</td>""")
            else:
                html_parts.append(f"""                <td class="cell-has-plates" data-year="{yr}">
                    <div class="plates-container">""")
                for item in plates:
                    orig_fn = html.escape(item["orig_filename"])
                    online_url = html.escape(item["online_url"])
                    html_parts.append(f"""                        <a href="{state_url}" target="15q_page" rel="noopener noreferrer" class="plate-card" title="{orig_fn} - Open {st} on 15q.net">
                            <img src="{online_url}" alt="{orig_fn}" loading="lazy">
                            <span class="badge">{orig_fn}</span>
                        </a>""")
                html_parts.append("""                    </div>
                </td>""")
        html_parts.append("""            </tr>""")

    html_parts.append("""        </tbody>
    </table>
</div>

<script>
    let yearsReversed = false;

    function changeThumbSize(val) {
        document.documentElement.style.setProperty('--thumb-width', val + 'px');
        document.documentElement.style.setProperty('--thumb-height', (val / 2) + 'px');
    }

    function toggleYearSortOrder() {
        const headerRow = document.getElementById('headerRow');
        const yearThs = Array.from(headerRow.querySelectorAll('th.year-col-header'));
        yearThs.reverse();
        yearThs.forEach(th => headerRow.appendChild(th));

        const rows = document.querySelectorAll('#matrixBody tr');
        rows.forEach(row => {
            const cells = Array.from(row.querySelectorAll('td[data-year]'));
            cells.reverse();
            cells.forEach(td => row.appendChild(td));
        });
        yearsReversed = !yearsReversed;
    }

    function filterMatrix() {
        const stateQuery = document.getElementById('searchState').value.trim().toUpperCase();
        const yearFromVal = parseInt(document.getElementById('yearFrom').value, 10);
        const yearToVal = parseInt(document.getElementById('yearTo').value, 10);

        const hasYearFrom = !isNaN(yearFromVal);
        const hasYearTo = !isNaN(yearToVal);

        function matchYear(yrStr) {
            const yr = parseInt(yrStr, 10);
            if (isNaN(yr)) return true;
            if (hasYearFrom && yr < yearFromVal) return false;
            if (hasYearTo && yr > yearToVal) return false;
            return true;
        }

        // Filter Rows (States)
        const rows = document.querySelectorAll('#matrixBody tr');
        rows.forEach(row => {
            const st = row.getAttribute('data-state') || '';
            const matchState = !stateQuery || st.includes(stateQuery);
            row.style.display = matchState ? '' : 'none';
        });

        // Filter Columns (Years)
        const yearHeaders = document.querySelectorAll('.year-col-header');
        yearHeaders.forEach(th => {
            const yr = th.getAttribute('data-year') || '';
            th.style.display = matchYear(yr) ? '' : 'none';
        });

        const cells = document.querySelectorAll('#matrixBody td[data-year]');
        cells.forEach(td => {
            const yr = td.getAttribute('data-year') || '';
            td.style.display = matchYear(yr) ? '' : 'none';
        });
    }
</script>

</body>
</html>
""")

    return "\n".join(html_parts)


def run_generator(input_dir: Path, output_file: Path, title: str = "US License Plates Matrix"):
    """Scan folder and write HTML table."""
    print(f"Scanning images in: {input_dir.resolve()}")
    if not input_dir.exists():
        print(f"[!] Warning: Directory '{input_dir}' does not exist yet. Creating empty HTML shell.")
        input_dir.mkdir(parents=True, exist_ok=True)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    matrix = scan_images(input_dir)

    total_images = sum(len(imgs) for yr in matrix.values() for imgs in yr.values())
    print(f"[+] Found {total_images} plates across {len(matrix)} year(s).")

    html_content = generate_html_table(matrix, title=title)
    output_file.write_text(html_content, encoding="utf-8")
    print(f"[✓] Successfully generated HTML matrix table at: {output_file.resolve()}")


# --- Main ---
if __name__ == "__main__":
    import doctest

    doctest_result = doctest.testmod()
    assert doctest_result.failed == 0, f"Doctests failed: {doctest_result}"
    assert parse_image_filename("1969-al-1.jpg") == ("1969", "AL", "al69.jpg", 1)
    assert parse_image_filename("1969-al-2.jpg") == ("1969", "AL", "al69a.jpg", 2)
    assert parse_image_filename("2006-ca-2.jpg") == ("2006", "CA", "ca06a.jpg", 2)

    parser = argparse.ArgumentParser(description="Generate an HTML matrix table for US license plates.")
    parser.add_argument("--input", "-i", type=Path, default=DEFAULT_INPUT_DIR, help="Path to the directory containing downloaded plate images.")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_HTML, help="Path for the output HTML file.")
    parser.add_argument("--title", "-t", type=str, default="US License Plates Matrix", help="Title for the HTML page.")
    args = parser.parse_args()

    run_generator(args.input, args.output, title=args.title)
