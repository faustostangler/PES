#!/usr/bin/env python3
"""Master Black Friday Scraper and Consolidator.

Executes both Amazon and Mercado Livre scraping pipelines and merges all
individual category deals into a unified master CSV.

Usage:
    # Run full end-to-end pipeline (Amazon + ML + Compile)
    uv run python -u playground/black-friday/master_scraper.py

    # Only compile existing CSVs into master without re-scraping
    uv run python -u playground/black-friday/master_scraper.py --only-compile

    # Skip one specific platform
    uv run python -u playground/black-friday/master_scraper.py --skip-amazon
    uv run python -u playground/black-friday/master_scraper.py --skip-ml
"""

import csv
import sys
import time
from pathlib import Path

# Base paths
BASE_DIR = Path("playground/black-friday")
CSV_DIR = BASE_DIR / "csv"

MASTER_DEALS_CSV = CSV_DIR / "master_ofertas_black_friday.csv"
MASTER_MFRS_CSV = CSV_DIR / "master_compilado_fabricantes.csv"

# Unified Master CSV Columns
MASTER_FIELDNAMES = [
    "plataforma",
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


def detect_platform(filename: str) -> str:
    """Identify platform from CSV filename prefix.

    >>> detect_platform('am_computadores_e_informatica.csv')
    'Amazon'
    >>> detect_platform('ml_celulares_e_telefones.csv')
    'Mercado Livre'
    >>> detect_platform('other_file.csv')
    'Outros'
    """
    fname = filename.lower()
    if fname.startswith("am_"):
        return "Amazon"
    if fname.startswith("ml_"):
        return "Mercado Livre"
    return "Outros"


def normalize_master_row(raw_row: dict, platform: str) -> dict:
    """Normalize row fields across Amazon and Mercado Livre schemas into unified master schema.

    >>> r = {'categoria': 'Livros', 'nome anunciado': 'Clean Code', 'valor da oferta': '89.9'}
    >>> res = normalize_master_row(r, 'Amazon')
    >>> res['plataforma']
    'Amazon'
    >>> res['vendedor_ou_loja_oficial']
    'Amazon'
    """
    row = {col: raw_row.get(col, "") for col in MASTER_FIELDNAMES}
    row["plataforma"] = platform

    # Platform-specific defaults
    if platform == "Amazon":
        if not row.get("vendedor_ou_loja_oficial"):
            row["vendedor_ou_loja_oficial"] = "Amazon"
        if not row.get("tipo_envio"):
            row["tipo_envio"] = "Prime / Padrão"
        if not row.get("frete_gratis"):
            row["frete_gratis"] = "Sim (Prime)"

    return row


def compile_master_csvs() -> tuple[int, int]:
    """Merge all individual am_*.csv and ml_*.csv into unified master CSVs.

    Returns:
        (total_master_deals, total_unique_brands)
    """
    CSV_DIR.mkdir(parents=True, exist_ok=True)

    category_files = sorted(
        [
            p
            for p in CSV_DIR.glob("*.csv")
            if (p.name.startswith("am_") or p.name.startswith("ml_"))
            and "compilado" not in p.name
            and "master" not in p.name
        ]
    )

    print("\n" + "=" * 80)
    print("📦 COMPILING UNIFIED MASTER BLACK FRIDAY CSV...")
    print(f"Source folder: {CSV_DIR.resolve()}")
    print(f"Category CSV files found: {len(category_files)}")
    print("=" * 80)

    all_deals: list[dict] = []
    seen_links: set[str] = set()

    brands_summary: dict[str, dict] = {}
    platform_counts: dict[str, int] = {"Amazon": 0, "Mercado Livre": 0}

    for file_path in category_files:
        platform = detect_platform(file_path.name)
        file_deals_count = 0

        try:
            with open(file_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for raw in reader:
                    row = normalize_master_row(raw, platform)
                    link = row.get("link", "").strip()

                    # Deduplicate deals by canonical link
                    if link and link in seen_links:
                        continue
                    if link:
                        seen_links.add(link)

                    all_deals.append(row)
                    file_deals_count += 1
                    platform_counts[platform] = platform_counts.get(platform, 0) + 1

                    # Track master brands
                    brand = row.get("fabricante", "").strip()
                    if brand:
                        if brand not in brands_summary:
                            brands_summary[brand] = {
                                "fabricante": brand,
                                "plataformas": set(),
                                "categorias": set(),
                                "total_ofertas": 0,
                                "links_lojas": set(),
                            }
                        brands_summary[brand]["plataformas"].add(platform)
                        if row.get("categoria"):
                            brands_summary[brand]["categorias"].add(row["categoria"])
                        brands_summary[brand]["total_ofertas"] += 1
                        store_url = row.get("link do site do fabricante", "").strip()
                        if store_url:
                            brands_summary[brand]["links_lojas"].add(store_url)

        except Exception as e:
            print(f"⚠️ Error reading {file_path.name}: {e}")

    # 1. Write Unified Master Deals CSV
    with open(MASTER_DEALS_CSV, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=MASTER_FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_deals)

    print(f"💾 Saved {len(all_deals)} unified deals to {MASTER_DEALS_CSV.name}")

    # 2. Write Unified Master Manufacturers CSV
    mfr_fieldnames = [
        "fabricante",
        "plataformas",
        "total_ofertas",
        "categorias",
        "links_lojas",
    ]
    sorted_brands = sorted(
        brands_summary.values(),
        key=lambda x: x["total_ofertas"],
        reverse=True,
    )

    with open(MASTER_MFRS_CSV, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=mfr_fieldnames)
        writer.writeheader()
        for b in sorted_brands:
            writer.writerow({
                "fabricante": b["fabricante"],
                "plataformas": ", ".join(sorted(b["plataformas"])),
                "total_ofertas": b["total_ofertas"],
                "categorias": ", ".join(sorted(b["categorias"])),
                "links_lojas": " | ".join(sorted(b["links_lojas"])),
            })

    print(f"💾 Saved {len(sorted_brands)} unique manufacturers to {MASTER_MFRS_CSV.name}")

    # 3. Output Summary Report
    print("\n" + "=" * 80)
    print("📊 MASTER CONSOLIDATION REPORT")
    print("-" * 80)
    print(f"Amazon Deals:        {platform_counts.get('Amazon', 0):>6d}")
    print(f"Mercado Livre Deals: {platform_counts.get('Mercado Livre', 0):>6d}")
    print("-" * 80)
    print(f"TOTAL MASTER DEALS:  {len(all_deals):>6d} -> {MASTER_DEALS_CSV.resolve()}")
    print(f"TOTAL UNIQUE BRANDS: {len(sorted_brands):>6d} -> {MASTER_MFRS_CSV.resolve()}")
    print("=" * 80)

    return len(all_deals), len(sorted_brands)


def main() -> None:
    """Execute scraping pipelines according to CLI arguments and compile outputs."""
    args = sys.argv[1:]

    only_compile = "--only-compile" in args
    skip_amazon = "--skip-amazon" in args
    skip_ml = "--skip-ml" in args

    print("=" * 80)
    print("🚀 MASTER BLACK FRIDAY AUTOMATION")
    print("=" * 80)

    if not only_compile:
        # 1. Run Amazon Scraper
        if not skip_amazon:
            print("\n▶️ [1/2] Executing Amazon Scraper...")
            try:
                import scrape_black_friday
                scrape_black_friday.run()
            except ImportError:
                # Dynamic import fallback
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "scrape_black_friday",
                    BASE_DIR / "scrape_black_friday.py",
                )
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    mod.run()
            except Exception as e:
                print(f"⚠️ Error in Amazon Scraper: {e}")
        else:
            print("⏭️ Skipping Amazon Scraper (--skip-amazon)")

        # 2. Run Mercado Livre Scraper
        if not skip_ml:
            print("\n▶️ [2/2] Executing Mercado Livre Scraper...")
            try:
                import scrape_mercadolivre
                scrape_mercadolivre.run_scraper()
            except ImportError:
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "scrape_mercadolivre",
                    BASE_DIR / "scrape_mercadolivre.py",
                )
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    mod.run_scraper()
            except Exception as e:
                print(f"⚠️ Error in Mercado Livre Scraper: {e}")
        else:
            print("⏭️ Skipping Mercado Livre Scraper (--skip-ml)")

    # 3. Always compile all CSVs into Master CSVs at the end
    compile_master_csvs()


if __name__ == "__main__":
    import doctest

    fails, _ = doctest.testmod()
    if fails > 0:
        sys.exit(1)
    main()

