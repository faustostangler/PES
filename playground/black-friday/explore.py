from playwright.sync_api import sync_playwright
import time

URL = "https://www.amazon.com.br/blackfriday?ref_=nav_cs_td_bf_dt_cr&bubble-id=deals-todasofertas"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        viewport={"width": 1400, "height": 900}
    )
    page = context.new_page()
    print("Navigating to URL...")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    
    # Save page title and URL
    print("Title:", page.title())
    print("Current URL:", page.url)
    
    # Check for department filters on left or anywhere
    # Look for department elements or text
    departments = page.eval_on_selector_all(
        "text=Departamento, [aria-label*='Departamento'], [data-csa-c-element-id*='department']",
        "els => els.map(e => e.outerHTML)"
    )
    print("Found potential department headers:", len(departments))
    
    # Let's search all elements containing department names or filter checkboxes/links
    html = page.content()
    with open("playground/black-friday/page_dump.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Dumped HTML to playground/black-friday/page_dump.html (length:", len(html), ")")

    browser.close()

