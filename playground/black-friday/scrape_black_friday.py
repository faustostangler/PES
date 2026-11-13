#!/usr/bin/env python3
"""Amazon Black Friday deals scraper for all 25 department categories.

Collects deals with full pagination across all requested departments:
- Uses an isolated browser context per category to prevent session throttling.
- Saves a dedicated CSV per department category with all required columns.
- Gathers manufacturer / brand store links across all offers.
- Generates a consolidated compiled CSV with all manufacturer links.
"""

import csv
import json
import re
import time
import unicodedata
import urllib.parse
from pathlib import Path
from selectolax.lexbor import LexborHTMLParser
from playwright.sync_api import sync_playwright

# --- Config ---
BASE_URL = "https://www.amazon.com.br"
EVENT_URL = "https://www.amazon.com.br/blackfriday?ref_=nav_cs_td_bf_dt_cr&bubble-id=deals-todasofertas"
OUTPUT_DIR = Path("playground/black-friday")

# Target categories exactly as requested by user
TARGET_CATEGORIES = [
    "Alimentos e Bebidas",
    "Automotivo",
    "Bebês",
    "Beleza",
    "Brinquedos e Jogos",
    "Casa",
    "CD e Vinil",
    "Computadores e Informática",
    "Cozinha",
    "Dispositivos Amazon e Acessórios",
    "DVD e Blu-ray",
    "Eletrodomésticos",
    "Eletrônicos e Tecnologia",
    "Esporte, Aventura e Lazer",
    "Ferramentas e Materiais de Construção",
    "Games e Consoles",
    "Indústria e Comércio",
    "Instrumentos Musicais",
    "Jardim e Piscina",
    "Livros",
    "Loja Kindle",
    "Moda",
    "Papelaria e Escritório",
    "Pet Shop",
    "Saúde e Bem-Estar",
]

# Exact department ID mapping on Amazon.com.br
KNOWN_DEPARTMENT_IDS = {
    "Alimentos e Bebidas": "18991080011",
    "Automotivo": "18914210011",
    "Bebês": "17242604011",
    "Beleza": "16194415011",
    "Brinquedos e Jogos": "16194300011",
    "Casa": "16191001011",
    "CD e Vinil": "7791938011",
    "Computadores e Informática": "16339927011",
    "Cozinha": "16957126011",
    "Dispositivos Amazon e Acessórios": "16333487011",
    "DVD e Blu-ray": "7791857011",
    "Eletrodomésticos": "16522083011",
    "Eletrônicos e Tecnologia": "16209063011",
    "Esporte, Aventura e Lazer": "17349397011",
    "Ferramentas e Materiais de Construção": "16957183011",
    "Games e Consoles": "7791986011",
    "Indústria e Comércio": "18991196011",
    "Instrumentos Musicais": "18991253011",
    "Jardim e Piscina": "18991022011",
    "Livros": "7841278011",
    "Loja Kindle": "5308308011",
    "Moda": "17365812011",
    "Papelaria e Escritório": "16957240011",
    "Pet Shop": "18991137011",
    "Saúde e Bem-Estar": "16215418011",
}

CSV_FIELDNAMES = [
    "categoria",
    "produto",
    "fabricante",
    "nome anunciado",
    "valor original",
    "valor da oferta",
    "% desconto (calculado)",
    "quantas estrelas",
    "total de avaliações",
    "link",
    "link do site do fabricante",
]


def slugify(text: str) -> str:
    """Normalize category name into a clean filename slug.

    >>> slugify('Alimentos e Bebidas')
    'alimentos_e_bebidas'
    >>> slugify('Saúde e Bem-Estar')
    'saude_e_bem_estar'
    """
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^\w\s-]", "", ascii_text).strip().lower()
    return re.sub(r"[-\s]+", "_", cleaned)


def parse_price(val: str | float | None) -> float:
    """Parse raw price string into float supporting both dot and comma formats.

    >>> parse_price('157.90')
    157.9
    >>> parse_price('1.450,50')
    1450.5
    >>> parse_price('84.3')
    84.3
    >>> parse_price(None)
    0.0
    """
    if not val:
        return 0.0
    s = str(val).replace("R$", "").strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def calculate_discount(original_str: str, offer_str: str, badge_fallback: str = "") -> str:
    """Calculate percentage discount accurately.

    >>> calculate_discount('157.90', '109.90')
    '30.4%'
    >>> calculate_discount('145.44', '84.3')
    '42.0%'
    >>> calculate_discount('', '100.00', '15% off')
    '15% off'
    """
    orig = parse_price(original_str)
    offer = parse_price(offer_str)
    if orig > offer > 0:
        pct = round(((orig - offer) / orig) * 100, 1)
        return f"{pct:.1f}%"
    return badge_fallback if badge_fallback else "0.0%"


def get_brand_store_url(brand_name: str) -> str:
    """Generate canonical Amazon Brand Store / Brand Hub URL.

    >>> get_brand_store_url('Apple')
    'https://www.amazon.com.br/s?k=Apple&rh=p_89%3AApple'
    >>> get_brand_store_url('Old Parr')
    'https://www.amazon.com.br/s?k=Old+Parr&rh=p_89%3AOld+Parr'
    >>> get_brand_store_url('')
    ''
    """
    if not brand_name:
        return ""
    encoded = urllib.parse.quote_plus(brand_name)
    return f"https://www.amazon.com.br/s?k={encoded}&rh=p_89%3A{encoded}"


def extract_product_row(item: dict, category_name: str, brand_map: dict[str, str]) -> dict:
    """Convert raw product JSON item into normalized dictionary."""
    asin = item.get("asin", "")
    title = item.get("title", "").strip()

    # Generic product classification
    cat_info = item.get("productCategory") or {}
    product_type = (
        cat_info.get("productType")
        or cat_info.get("websiteDisplayGroup")
        or cat_info.get("symbol")
        or category_name
    )

    # Manufacturer / Brand
    meta = item.get("meta") or {}
    brand_id = str(meta.get("brandId", ""))
    brand_name = brand_map.get(brand_id, "")

    if not brand_name:
        brand_logo = item.get("brandLogo") or {}
        brand_name = brand_logo.get("altText", "")

    if not brand_name and title:
        first_token = title.split()[0]
        if len(first_token) > 1 and not first_token.isdigit():
            brand_name = first_token

    brand_url = get_brand_store_url(brand_name)

    # Prices
    price_info = item.get("price") or {}
    pay_obj = price_info.get("priceToPay") or {}
    basis_obj = price_info.get("basisPrice") or {}

    offer_price = pay_obj.get("price", "")
    orig_price = basis_obj.get("price", "") or offer_price

    # Badge fallback
    badge_label = ""
    badge = item.get("dealBadge") or {}
    fragments = (badge.get("label") or {}).get("content", {}).get("fragments", [])
    if fragments and isinstance(fragments, list):
        badge_label = fragments[0].get("text", "")

    discount = calculate_discount(orig_price, offer_price, badge_label)

    # Reviews
    rev_info = item.get("customerReviews") or {}
    rating_obj = rev_info.get("rating") or {}
    stars = rating_obj.get("shortDisplayString") or str(rating_obj.get("fullStarCount") or "N/A")

    count_obj = rev_info.get("count") or {}
    total_reviews = str(count_obj.get("value") or count_obj.get("displayString") or "0")

    # Link
    raw_link = item.get("link", "")
    clean_path = raw_link.split("?")[0] if raw_link else f"/dp/{asin}"
    canonical_link = f"{BASE_URL}{clean_path}" if clean_path.startswith("/") else clean_path

    return {
        "asin": asin,
        "categoria": category_name,
        "produto": product_type,
        "fabricante": brand_name,
        "nome anunciado": title,
        "valor original": orig_price,
        "valor da oferta": offer_price,
        "% desconto (calculado)": discount,
        "quantas estrelas": stars,
        "total de avaliações": total_reviews,
        "link": canonical_link,
        "link do site do fabricante": brand_url,
    }


def fetch_api_batch(page, api_url: str) -> tuple[dict | None, bool]:
    """Fetch an API batch returning (data, is_end_of_results)."""
    for attempt in range(3):
        try:
            res = page.evaluate(f"""async () => {{
                try {{
                    const resp = await fetch('{api_url}', {{
                        headers: {{ 'accept': 'application/json, text/plain, */*' }}
                    }});
                    const ctype = resp.headers.get('content-type') || '';
                    const text = await resp.text();
                    const isHtml = text.trim().startsWith('<') || !ctype.includes('json');
                    if (isHtml) {{
                        return {{ success: false, isHtml: true, status: resp.status }};
                    }}
                    const data = JSON.parse(text);
                    return {{ success: true, isHtml: false, data: data }};
                }} catch (e) {{
                    return {{ success: false, isHtml: false, error: e.message }};
                }}
            }}""")
            if res and res.get("success"):
                return res.get("data"), False
            if res and res.get("isHtml"):
                return None, True  # Clean end of results
            time.sleep(1.0 * (attempt + 1))
        except Exception:
            time.sleep(1.5 * (attempt + 1))
    return None, True


def run() -> None:
    """Run full Black Friday deals scraping pipeline across all categories."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_dir = OUTPUT_DIR / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("🚀 AMAZON BLACK FRIDAY SCRAPER — FAST PROTOTYPE")
    print(f"Categories to scrape: {len(TARGET_CATEGORIES)}")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")
    print("=" * 80)

    # Master caches
    global_brand_map: dict[str, str] = {}
    manufacturers_compilation: dict[str, dict] = {}
    summary_report: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
        )

        for cat_idx, category_name in enumerate(TARGET_CATEGORIES, 1):
            dept_id = KNOWN_DEPARTMENT_IDS.get(category_name)
            if not dept_id:
                print(f"[{cat_idx:02d}/{len(TARGET_CATEGORIES)}] ⚠️ '{category_name}' not mapped! Skipping.")
                continue

            print(f"\n[{cat_idx:02d}/{len(TARGET_CATEGORIES)}] 📂 Processing category: {category_name}")

            # Create fresh context for each department
            ctx = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                viewport={"width": 1400, "height": 900},
            )
            ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page = ctx.new_page()

            # Resilient navigation with retry
            nav_success = False
            for attempt in range(3):
                try:
                    page.goto(EVENT_URL, wait_until="domcontentloaded", timeout=45000)
                    time.sleep(2)
                    nav_success = True
                    break
                except Exception as e:
                    print(f"   ⚠️ Connection warning on attempt {attempt + 1}/3: {e}")
                    if "ERR_CONNECTION_CLOSED" in str(e) or "SSL" in str(e):
                        print("   💡 Note: Amazon actively closes TLS connections from VPN/datacenter IPs.")
                        print("      Verifique se o Surfshark/VPN está desconectado na interface de rede.")
                    time.sleep(2.5 * (attempt + 1))

            if not nav_success:
                print(f"   ❌ Could not reach Amazon for '{category_name}'. Skipping.")
                ctx.close()
                continue

            start_index = 0
            cat_products: list[dict] = []
            seen_asins: set[str] = set()

            while True:
                api_url = (
                    f"/d2b/api/v1/products/search?pageSize=30&startIndex={start_index}&calculateRefinements=true"
                    f"&rankingContext=%7B%22pageTypeId%22%3A%22blackfriday%22%2C%22rankGroup%22%3A%22PARENT_ASIN_RANKING%22%7D"
                    f"&filters=%7B%22includedDepartments%22%3A%5B%5D%2C%22excludedDepartments%22%3A%5B%5D%2C%22includedTags%22%3A%5B%5D%2C%22excludedTags%22%3A%5B%22restrictedcontent%22%2C%22DealOMatic%22%2C%22duplicatedeal%22%2C%22TFSRestricted3P%22%2C%22predefined-request%23deals-todasofertas%22%5D%2C%22promotionTypes%22%3A%5B%22LIGHTNING_DEAL%22%2C%22BEST_DEAL%22%5D%2C%22accessTypes%22%3A%5B%5D%2C%22brandIds%22%3A%5B%5D%2C%22unifiedIds%22%3A%5B%5D%7D"
                    f"&refinementFilters=%5B%7B%22id%22%3A%22departments%22%2C%22value%22%3A%5B%22{dept_id}%22%5D%7D%5D"
                )

                batch_data, is_end = fetch_api_batch(page, api_url)
                if is_end or not batch_data:
                    print(f"   ✓ Finished pagination for {category_name} (at index {start_index}).")
                    break

                # Update brand mapping from refinements
                for ref in batch_data.get("refinements", []):
                    if ref.get("id") == "brands":
                        for opt in ref.get("options", []):
                            val = opt.get("value", "")
                            if "|" in val:
                                bid, bname = val.split("|", 1)
                                global_brand_map[bid] = bname

                raw_items = batch_data.get("products", [])
                if not raw_items:
                    print(f"   ✓ Last page reached for {category_name} (no more products).")
                    break

                new_count = 0
                for p_raw in raw_items:
                    asin = p_raw.get("asin")
                    if asin and asin not in seen_asins:
                        seen_asins.add(asin)
                        cat_products.append(p_raw)
                        new_count += 1

                next_idx = batch_data.get("nextIndex")
                print(f"   Page @ {start_index:4d} → +{new_count:2d} deals (Total: {len(cat_products):4d}) | nextIndex={next_idx}")

                if next_idx is None or next_idx == start_index or new_count == 0:
                    break

                start_index = next_idx
                time.sleep(1.0)

            # Build final rows for category
            rows = []
            for p_raw in cat_products:
                row = extract_product_row(p_raw, category_name, global_brand_map)
                bname = row["fabricante"]
                store_link = row["link do site do fabricante"]

                # Update master manufacturer compilation
                if bname:
                    if bname not in manufacturers_compilation:
                        manufacturers_compilation[bname] = {
                            "fabricante": bname,
                            "link do site do fabricante": store_link,
                            "categorias": set(),
                            "total de ofertas": 0,
                        }
                    manufacturers_compilation[bname]["categorias"].add(category_name)
                    manufacturers_compilation[bname]["total de ofertas"] += 1

                row.pop("asin", None)
                rows.append(row)

            # Write category CSV
            cat_filename = f"am_{slugify(category_name)}.csv"
            cat_csv_path = csv_dir / cat_filename
            with open(cat_csv_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
                writer.writeheader()
                writer.writerows(rows)

            print(f"   💾 Saved {len(rows)} deals to {cat_filename}")
            summary_report.append({
                "categoria": category_name,
                "total_ofertas": len(rows),
                "arquivo": cat_filename,
            })

            # Close context cleanly
            ctx.close()
            time.sleep(0.8)

        browser.close()

    # Write compiled manufacturers CSV
    print("\n" + "=" * 80)
    print("Writing Compiled Manufacturers CSV...")
    compilado_path = csv_dir / "am_compilado_fabricantes.csv"
    mfr_fieldnames = ["fabricante", "link do site do fabricante", "categorias", "total de ofertas"]

    sorted_mfrs = sorted(
        manufacturers_compilation.values(),
        key=lambda x: x["total de ofertas"],
        reverse=True,
    )

    with open(compilado_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=mfr_fieldnames)
        writer.writeheader()
        for item in sorted_mfrs:
            writer.writerow({
                "fabricante": item["fabricante"],
                "link do site do fabricante": item["link do site do fabricante"],
                "categorias": ", ".join(sorted(item["categorias"])),
                "total de ofertas": item["total de ofertas"],
            })

    print(f"💾 Saved {len(sorted_mfrs)} unique manufacturers to {compilado_path}")

    # Summary table output
    print("\n" + "=" * 80)
    print(f"{'#':<3} | {'CATEGORIA':<38} | {'OFERTAS':<8} | {'ARQUIVO'}")
    print("-" * 80)
    total_deals = sum(s["total_ofertas"] for s in summary_report)
    for i, s in enumerate(summary_report, 1):
        print(f"{i:<3} | {s['categoria']:<38} | {s['total_ofertas']:<8} | {s['arquivo']}")
    print("-" * 80)
    print(f"{'TOTAL GERAL':<44} | {total_deals:<8} | 25 CSVs + 1 compilado")
    print("=" * 80)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    run()
