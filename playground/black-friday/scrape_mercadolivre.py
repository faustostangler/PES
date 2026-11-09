#!/usr/bin/env python3
"""Mercado Livre deals scraper prototype for all 27 department categories.

Navigates https://www.mercadolivre.com.br/ofertas across all departments:
- Extracts deals with full pagination per category.
- Outputs individual CSVs per category under playground/mercadolivre/csvs/.
- Produces a compiled CSV of all official stores / manufacturers.
- Includes standard columns plus suggested ML-specific dimensions:
  (vendedor_ou_loja_oficial, tipo_envio, frete_gratis, parcelamento, badge_oferta).
"""

import csv
import json
import re
import select
import sys
import time
import unicodedata
import urllib.parse
from pathlib import Path
from selectolax.lexbor import LexborHTMLParser
from playwright.sync_api import sync_playwright

# --- Configuration ---
BASE_URL = "https://www.mercadolivre.com.br"
EVENT_URL = "https://www.mercadolivre.com.br/ofertas#filter_applied=category&filter_position=0&origin=qcat"
OUTPUT_DIR = Path("playground/black-friday")

# Target categories and exact MLB category IDs on Mercado Livre Brasil
TARGET_CATEGORIES = [
    {"name": "Acessórios para Veículos", "id": "MLB1747", "count_hint": 892},
    {"name": "Agro", "id": "MLB271599", "count_hint": 173},
    {"name": "Alimentos e Bebidas", "id": "MLB1403", "count_hint": 99},
    {"name": "Arte, Papelaria e Armarinho", "id": "MLB1367", "count_hint": 182},
    {"name": "Bebês", "id": "MLB1384", "count_hint": 282},
    {"name": "Beleza e Cuidado Pessoal", "id": "MLB1246", "count_hint": 711},
    {"name": "Brinquedos e Hobbies", "id": "MLB1132", "count_hint": 324},
    {"name": "Calçados, Roupas e Bolsas", "id": "MLB1430", "count_hint": 2256},
    {"name": "Casa, Móveis e Decoração", "id": "MLB1574", "count_hint": 3259},
    {"name": "Celulares e Telefones", "id": "MLB1051", "count_hint": 440},
    {"name": "Construção", "id": "MLB1500", "count_hint": 638},
    {"name": "Câmeras e Acessórios", "id": "MLB1039", "count_hint": 98},
    {"name": "Eletrodomésticos", "id": "MLB5726", "count_hint": 410},
    {"name": "Eletrônicos, Áudio e Vídeo", "id": "MLB1000", "count_hint": 306},
    {"name": "Esportes e Fitness", "id": "MLB1276", "count_hint": 1742},
    {"name": "Ferramentas", "id": "MLB263532", "count_hint": 529},
    {"name": "Festas e Lembrancinhas", "id": "MLB1770", "count_hint": 210},
    {"name": "Games", "id": "MLB1144", "count_hint": 29},
    {"name": "Indústria e Comércio", "id": "MLB1499", "count_hint": 352},
    {"name": "Informática", "id": "MLB1648", "count_hint": 369},
    {"name": "Instrumentos Musicais", "id": "MLB1182", "count_hint": 42},
    {"name": "Joias e Relógios", "id": "MLB3937", "count_hint": 589},
    {"name": "Livros, Revistas e Comics", "id": "MLB3025", "count_hint": 70},
    {"name": "Mais Categorias", "id": "MLB1953", "count_hint": 28},
    {"name": "Música, Filmes e Seriados", "id": "MLB1168", "count_hint": 28},
    {"name": "Pet Shop", "id": "MLB1071", "count_hint": 112},
    {"name": "Saúde", "id": "MLB409431", "count_hint": 741},
]

CSV_FIELDNAMES = [
    "categoria",
    "produto",
    "fabricante",
    "vendedor_ou_loja_oficial",
    "nome anunciado",
    "valor original",
    "valor da oferta",
    "% desconto (calculado)",
    "quantas estrelas",
    "total de avaliações",
    "tipo_envio",
    "frete_gratis",
    "parcelamento",
    "badge_oferta",
    "link",
    "link do site do fabricante",
]


# --- Helpers & Sanitization ---

def slugify(text: str) -> str:
    """Normalize text into a clean file slug.

    >>> slugify('Acessórios para Veículos')
    'acessorios_para_veiculos'
    >>> slugify('Calçados, Roupas e Bolsas')
    'calcados_roupas_e_bolsas'
    >>> slugify('Saúde')
    'saude'
    """
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^\w\s-]", "", ascii_text).strip().lower()
    return re.sub(r"[-\s]+", "_", cleaned)


def parse_price(val: str | float | None) -> float:
    """Parse Brazilian currency price string into float.

    >>> parse_price('R$ 1.299,00')
    1299.0
    >>> parse_price('4.499')
    4499.0
    >>> parse_price('89,90')
    89.9
    >>> parse_price('150')
    150.0
    >>> parse_price(None)
    0.0
    """
    if not val:
        return 0.0
    s = str(val).replace("R$", "").replace(" ", "").strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    elif "." in s:
        parts = s.split(".")
        if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit():
            s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def calculate_discount(original_val: str | float, offer_val: str | float, badge_fallback: str = "") -> str:
    """Calculate discount percentage accurately.

    >>> calculate_discount('100.00', '70.00')
    '30.0%'
    >>> calculate_discount('200', '150')
    '25.0%'
    >>> calculate_discount('0', '50', '15% OFF')
    '15% OFF'
    """
    orig = parse_price(original_val)
    offer = parse_price(offer_val)
    if orig > offer > 0:
        pct = round(((orig - offer) / orig) * 100, 1)
        return f"{pct:.1f}%"
    return badge_fallback if badge_fallback else "0.0%"


def extract_generic_product(title: str, category_name: str) -> str:
    """Extract a concise generic classification from product title.

    >>> extract_generic_product('Smartphone Samsung Galaxy S23 128gb', 'Celulares e Telefones')
    'Smartphone'
    >>> extract_generic_product('Notebook Lenovo IdeaPad 3 Intel Core i5', 'Informática')
    'Notebook'
    """
    if not title:
        return category_name
    words = title.strip().split()
    if not words:
        return category_name
    first = words[0].capitalize()
    return first if len(first) > 2 else category_name


def parse_mercadolivre_card(card, category_name: str) -> dict | None:
    """Parse single Mercado Livre product card (supports both promotion-item and poly-card layouts)."""
    # 1. Title & Link
    title_el = (
        card.css_first(".poly-component__title")
        or card.css_first(".promotion-item__title")
        or card.css_first("a.ui-search-item__group__element")
        or card.css_first("h2")
    )
    if not title_el:
        return None

    title = title_el.text().strip()
    link_el = card.css_first("a")
    raw_link = link_el.attributes.get("href", "") if link_el else ""
    canonical_link = raw_link.split("?")[0] if raw_link else ""
    if canonical_link and canonical_link.startswith("/"):
        canonical_link = f"{BASE_URL}{canonical_link}"

    # 2. Prices
    # Original price
    prev_price_el = (
        card.css_first(".andes-money-amount--previous .andes-money-amount__fraction")
        or card.css_first(".promotion-item__old-price span")
        or card.css_first("s .andes-money-amount__fraction")
    )
    orig_str = prev_price_el.text().strip() if prev_price_el else ""

    # Current offer price
    current_price_el = (
        card.css_first(".poly-price__current .andes-money-amount__fraction")
        or card.css_first(".andes-money-amount:not(.andes-money-amount--previous) .andes-money-amount__fraction")
        or card.css_first(".promotion-item__price span")
    )
    cents_el = card.css_first(".poly-price__current .andes-money-amount__cents")
    cents_str = cents_el.text().strip() if cents_el else "00"

    offer_raw = current_price_el.text().strip() if current_price_el else ""
    offer_str = f"{offer_raw},{cents_str}" if offer_raw else ""

    if not orig_str:
        orig_str = offer_str

    # 3. Discount badge
    discount_el = (
        card.css_first(".andes-money-amount__discount")
        or card.css_first(".promotion-item__discount-text")
        or card.css_first(".poly-price__discount")
    )
    badge_fallback = discount_el.text().strip() if discount_el else ""
    discount = calculate_discount(orig_str, offer_str, badge_fallback)

    # 4. Seller / Brand / Official Store
    seller_el = (
        card.css_first(".poly-component__seller")
        or card.css_first(".promotion-item__seller")
        or card.css_first(".ui-search-official-store-label")
    )
    seller_name = seller_el.text().strip() if seller_el else ""
    seller_name = re.sub(r"^por\s+", "", seller_name, flags=re.I).strip()

    # Brand inference
    brand = seller_name if seller_name else (title.split()[0] if title else "")

    # Brand store link inside ML
    brand_store_url = ""
    if brand:
        encoded_brand = urllib.parse.quote_plus(brand)
        brand_store_url = f"https://loja.mercadolivre.com.br/{encoded_brand}"

    # 5. Reviews and Stars
    rating_el = card.css_first(".poly-reviews__rating") or card.css_first(".ui-search-reviews__rating-number")
    stars = rating_el.text().strip() if rating_el else "N/A"

    reviews_el = card.css_first(".poly-reviews__total") or card.css_first(".ui-search-reviews__amount")
    total_reviews = reviews_el.text().strip().replace("(", "").replace(")", "") if reviews_el else "0"

    # 6. ML specific signals: Shipping, Free Shipping, Installments, Badge
    shipping_el = card.css_first(".poly-component__shipping") or card.css_first(".promotion-item__shipping")
    shipping_text = shipping_el.text().strip() if shipping_el else ""
    is_full = "FULL" in card.text() or bool(card.css_first("[class*='full']"))
    tipo_envio = "Full" if is_full else ("Normal" if shipping_text else "Padrão")
    frete_gratis = "Sim" if ("grátis" in shipping_text.lower() or "gratis" in shipping_text.lower()) else "Não"

    installments_el = card.css_first(".poly-price__installments") or card.css_first(".promotion-item__installments")
    parcelamento = installments_el.text().strip() if installments_el else ""

    badge_el = card.css_first(".poly-component__highlight") or card.css_first(".promotion-item__pill")
    badge_oferta = badge_el.text().strip() if badge_el else ""

    return {
        "categoria": category_name,
        "produto": extract_generic_product(title, category_name),
        "fabricante": brand,
        "vendedor_ou_loja_oficial": seller_name,
        "nome anunciado": title,
        "valor original": orig_str,
        "valor da oferta": offer_str,
        "% desconto (calculado)": discount,
        "quantas estrelas": stars,
        "total de avaliações": total_reviews,
        "tipo_envio": tipo_envio,
        "frete_gratis": frete_gratis,
        "parcelamento": parcelamento,
        "badge_oferta": badge_oferta,
        "link": canonical_link,
        "link do site do fabricante": brand_store_url,
    }


def is_security_challenge(url: str, html: str = "") -> bool:
    """Check if page is currently stuck on a security challenge or login wall.

    >>> is_security_challenge("https://www.mercadolivre.com.br/gz/account-verification?status=pending")
    True
    >>> is_security_challenge("https://www.mercadolivre.com.br/captcha/wall")
    True
    >>> is_security_challenge("https://www.mercadolivre.com.br/ofertas")
    False
    >>> is_security_challenge("https://www.mercadolivre.com.br/ofertas?redirect_url=login", html="<div class='poly-card'>Deal</div>")
    False
    """
    if html and any(m in html for m in ["poly-card", "promotion-item", "ui-search-result", "andes-pagination"]):
        return False
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lower()
    if any(k in path for k in ["gz/account-verification", "captcha/wall", "negative_traffic"]):
        return True
    if path == "/login" or path.startswith("/login/"):
        return True
    return False


def check_and_resolve_verification(page, target_url: str, auth_file: Path | None = None) -> None:
    """Detect security block and assist user with interactive + auto-polling resolution."""
    try:
        html = page.content()
    except Exception:
        html = ""

    if not is_security_challenge(page.url, html):
        return

    print("\n" + "!" * 80)
    print("🚨 MERCADO LIVRE SECURITY / LOGIN CHECK DETECTED!")
    print(f"URL: {page.url}")
    print("👉 Uma janela do Google Chrome está aberta na sua tela (Display :1).")
    print("👉 Resolva o captcha/login diretamente na janela do Chrome.")
    print("👉 Após resolver, pressione ENTER aqui no terminal ou aguarde a auto-detecção.")
    print("⏳ Auto-verificando a cada 5 segundos...")
    print("!" * 80 + "\n")

    last_nav = time.time()
    while True:
        # 1. Non-blocking check for ENTER press from terminal
        if sys.stdin.isatty():
            rlist, _, _ = select.select([sys.stdin], [], [], 2.0)
            if rlist:
                sys.stdin.readline()
                print("⌨️ ENTER recebido! Forçando navegação para validar sessão...")
                try:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                    time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️ Erro ao recarregar: {e}")
        else:
            time.sleep(2.0)

        # 2. Inspect current page content and URL
        try:
            curr_html = page.content()
            curr_url = page.url
        except Exception:
            curr_html = ""
            curr_url = page.url

        if any(m in curr_html for m in ["poly-card", "promotion-item", "ui-search-result"]):
            print("✅ Ofertas detectadas no DOM! Verificação concluída com sucesso.")
            break

        # 3. Check if URL is no longer blocked
        if not is_security_challenge(curr_url, curr_html):
            print("🔄 URL liberada. Confirmando carregamento da página de ofertas...")
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(2)
                test_html = page.content()
                if any(m in test_html for m in ["poly-card", "promotion-item", "ui-search-result"]):
                    print("✅ Acesso ao Mercado Livre validado com sucesso!")
                    break
            except Exception:
                pass

        # 4. Periodically (every 8s) test navigation to target_url in case challenge finished
        if time.time() - last_nav > 8:
            last_nav = time.time()
            try:
                page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                time.sleep(2)
                test_html = page.content()
                if not is_security_challenge(page.url, test_html) and (
                    any(m in test_html for m in ["poly-card", "promotion-item", "ui-search-result"])
                    or "ofertas" in page.url
                ):
                    print("✅ Verificação superada! Acesso liberado.")
                    break
            except Exception:
                pass

    if auth_file:
        try:
            page.context.storage_state(path=str(auth_file))
            print(f"💾 Sessão salva em {auth_file.name}\n")
        except Exception:
            pass


# --- Main Pipeline ---

def run_scraper() -> None:
    """Run Mercado Livre deals scraper across all 27 categories."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_dir = OUTPUT_DIR / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)
    auth_file = OUTPUT_DIR / "ml_auth.json"
    profile_dir = OUTPUT_DIR / ".ml_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    # Default to visible browser (headless=False) so user can log in / solve CAPTCHA
    is_headless = "--headless" in sys.argv

    print("=" * 80)
    print("🚀 MERCADO LIVRE DEALS SCRAPER — FAST PROTOTYPE")
    print(f"Categories to scrape: {len(TARGET_CATEGORIES)}")
    print(f"Output directory: {OUTPUT_DIR.resolve()}")
    print(f"Mode: {'Headless' if is_headless else 'Visible UI (Headful)'}")
    print("=" * 80)

    summary_report: list[dict] = []
    compilado_lojas: dict[str, dict] = {}

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            executable_path="/usr/bin/google-chrome",
            headless=is_headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ],
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900},
        )
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # Step 1: Initial verification / login check on deals landing page
        print("\n🔍 Checking Mercado Livre access permissions...")
        page.goto(EVENT_URL, wait_until="domcontentloaded", timeout=45000)
        time.sleep(2)

        check_and_resolve_verification(page, EVENT_URL, auth_file)

        # Step 2: Iterate over all 27 categories
        for idx, cat in enumerate(TARGET_CATEGORIES, 1):
            category_name = cat["name"]
            cat_id = cat["id"]
            slug = slugify(category_name)
            csv_path = csv_dir / f"ml_{slug}.csv"

            print(f"\n[{idx:02d}/{len(TARGET_CATEGORIES)}] 📂 Category: {category_name} (ID: {cat_id})")

            cat_deals: list[dict] = []
            seen_links: set[str] = set()
            page_num = 1
            max_pages = 20  # Safeguard limit per category

            while page_num <= max_pages:
                cat_url = f"{BASE_URL}/ofertas?category={cat_id}&page={page_num}"
                try:
                    page.goto(cat_url, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    print(f"   ⚠️ Navigation error on page {page_num}: {e}")
                    break

                # Handle in-flight CAPTCHA during pagination
                check_and_resolve_verification(page, cat_url, auth_file)

                # Parse page cards
                html = page.content()
                tree = LexborHTMLParser(html)
                cards = tree.css(".poly-card, .promotion-item, .ui-search-result__wrapper, .andes-card")

                if not cards:
                    if page_num > 1:
                        print(f"   ✓ Last page reached (no cards found on page {page_num}).")
                    else:
                        print(f"   ℹ️ No cards rendered on page 1 for {category_name}.")
                    break

                page_new_count = 0
                for c in cards:
                    row = parse_mercadolivre_card(c, category_name)
                    if row and row["link"] and row["link"] not in seen_links:
                        seen_links.add(row["link"])
                        cat_deals.append(row)
                        page_new_count += 1

                        # Track manufacturer / store
                        bname = row["fabricante"]
                        if bname:
                            if bname not in compilado_lojas:
                                compilado_lojas[bname] = {
                                    "fabricante_ou_loja_oficial": bname,
                                    "link_loja_oficial": row["link do site do fabricante"],
                                    "categorias": set(),
                                    "total_ofertas": 0,
                                }
                            compilado_lojas[bname]["categorias"].add(category_name)
                            compilado_lojas[bname]["total_ofertas"] += 1

                print(f"   Page {page_num:2d} → +{page_new_count:2d} deals (Total: {len(cat_deals):4d})")

                if page_new_count == 0:
                    break

                page_num += 1
                time.sleep(1.0)

            # Write Category CSV
            with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
                writer.writeheader()
                writer.writerows(cat_deals)

            print(f"   💾 Saved {len(cat_deals)} deals to {csv_path.name}")
            summary_report.append({
                "categoria": category_name,
                "total_ofertas": len(cat_deals),
                "arquivo": csv_path.name,
            })

            time.sleep(0.5)

        ctx.close()

    # Write Master Compiled Stores / Manufacturers CSV
    compilado_path = csv_dir / "ml_compilado_fabricantes.csv"
    store_fieldnames = ["fabricante_ou_loja_oficial", "link_loja_oficial", "categorias", "total_ofertas"]
    sorted_stores = sorted(compilado_lojas.values(), key=lambda x: x["total_ofertas"], reverse=True)

    with open(compilado_path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=store_fieldnames)
        writer.writeheader()
        for item in sorted_stores:
            writer.writerow({
                "fabricante_ou_loja_oficial": item["fabricante_ou_loja_oficial"],
                "link_loja_oficial": item["link_loja_oficial"],
                "categorias": ", ".join(sorted(item["categorias"])),
                "total_ofertas": item["total_ofertas"],
            })

    print("\n" + "=" * 80)
    print(f"💾 Saved {len(sorted_stores)} unique brands/stores to {compilado_path}")
    print("=" * 80)

    # Summary table
    print("\n" + "=" * 80)
    print(f"{'#':<3} | {'CATEGORIA':<38} | {'OFERTAS':<8} | ARQUIVO")
    print("-" * 80)
    total_all = sum(s["total_ofertas"] for s in summary_report)
    for i, s in enumerate(summary_report, 1):
        print(f"{i:<3} | {s['categoria']:<38} | {s['total_ofertas']:<8} | {s['arquivo']}")
    print("-" * 80)
    print(f"{'TOTAL GERAL':<44} | {total_all:<8} | {len(summary_report)} CSVs + 1 compilado")
    print("=" * 80)


if __name__ == "__main__":
    import doctest

    fails, _ = doctest.testmod()
    if fails > 0:
        sys.exit(1)
    run_scraper()
