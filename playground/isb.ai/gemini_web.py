"""Gemini Web Processor - Playwright-based browser automation to run Gemini as a free API.

Provides absolute temporal anchoring, dynamic prompt routing (News vs Technical),
Obsidian MOC list context injection, and structured file boundary parsing.
"""

import json
import time
from pathlib import Path
from typing import Self, TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Playwright, BrowserContext, Page

# ==================== SYSTEM PROMPTS ====================

NEWS_SYSTEM_PROMPT = """Você é o motor de processamento do ecossistema RAE-PKM.
A data atual de referência do mundo é {data_yaml}.
Qualquer menção temporal deve ser convertida para uma data absoluta no formato AAAA-MM-DD.
Sua saída deve ser estritamente dividida em arquivos Markdown atômicos independentes, focados em um único fato.

Hierarquia de Diretórios e Links no Cofre:
- As notas de referência (R_) residem em concepts/, as de ação (A_) em procedures/, e as de fatos em chronicles/. O cofre usa links diretos para referências bilaterais: [[Nome_da_Nota]] ou [[R_Conceito]].
- Os Mapas de Conteúdo (MOCs) residem na subpasta MOCs/. Ao referenciar MOCs, use o caminho relativo ao cofre: [[MOCs/MOC_Nome]].

IMPORTANTE: Você deve encapsular toda a sua resposta (contendo os arquivos e as associações MOC) dentro de um único bloco de código markdown (usando ```markdown no início e ``` no final). Isso garante que a nossa automação capture perfeitamente os caracteres especiais como # e ---.

Analise a transcrição de notícia fornecida. Extraia os dados formatando-os como notas atômicas independentes de fatos.
Cada nota de fato deve ser gerada separadamente.

Dentro do bloco de código markdown, para cada nota de fato encontrada, gere um bloco de arquivo seguindo exatamente esta sintaxe:
<<<< FILE: {{Nome_do_Fato_Simplificado}}.md >>>>
---
data: {{Data_Absoluta_do_Fato_no_formato_AAAA-MM-DD}}
entidades:
  - {{Nome da Entidade 1}}
  - {{Nome da Entidade 2}}
---
# {{Título: Sentença nominal clara descrevendo o fato}}

## Contexto e Resumo
{{Resumo objetivo do contexto do fato}}

## Conexões
{{Conexões diretas para termos adjacentes ou conceitos usando a sintaxe de links bilaterais [[Link]]{{Se houver}}}}
<<<< END FILE >>>>

Além disso, também dentro do bloco de código markdown, ao final da resposta, informe a quais MOCs do Obsidian (a partir da lista fornecida abaixo) essas novas notas pertencem, ou sugira novos MOCs se não houver correspondência, no seguinte formato de bloco:
<<<< MOC_ASSOCIATIONS >>>>
{{Nome_do_Fato_Simplificado}}.md -> {{Nome_do_MOC}}
<<<< END MOC_ASSOCIATIONS >>>>

Lista de MOCs ativos:
{mocs_list}

Transcrição da notícia:
{transcription}
"""

TECHNICAL_SYSTEM_PROMPT = """Você é o motor de processamento do ecossistema RAE-PKM.
A data atual de referência do mundo é {data_yaml}.
Qualquer menção temporal deve ser convertida para uma data absoluta no formato AAAA-MM-DD.
Sua saída deve ser estritamente dividida em arquivos Markdown atômicos independentes, focados em um único conceito ou procedimento.

Hierarquia de Diretórios e Links no Cofre:
- As notas de referência (R_) residem em concepts/, as de ação (A_) em procedures/, e as de fatos em chronicles/. O cofre usa links diretos para referências bilaterais: [[R_Conceito]] ou [[A_Procedimento]].
- Os Mapas de Conteúdo (MOCs) residem na subpasta MOCs/. Ao referenciar MOCs, use o caminho relativo ao cofre: [[MOCs/MOC_Nome]].

IMPORTANTE: Você deve encapsular toda a sua resposta (contendo os arquivos e as associações MOC) dentro de um único bloco de código markdown (usando ```markdown no início e ``` no final). Isso garante que a nossa automação capture perfeitamente os caracteres especiais como # e ---.

Analise a transcrição técnica fornecida. Separe o conhecimento em duas categorias de arquivos:
1. Referência (Invariante): O núcleo teórico duradouro, mecânica biológica, lógica jurídica ou fundamento financeiro. Prefixação: R_{{Nome_do_Conceito}}.md
2. Ação (Variante): O protocolo prático, passos de execução, comandos, ferramentas temporárias ou regras conjunturais. Prefixação: A_{{Nome_do_Procedimento}}.md

Gere arquivos separados para cada conceito atômico descoberto, ligando-os de forma recíproca.

Dentro do bloco de código markdown, para cada arquivo de Referência gerado, use exatamente esta sintaxe:
<<<< FILE: R_{{Nome_do_Conceito}}.md >>>>
---
tags: [referencia]
---
# R_{{Nome_do_Conceito}}

## Núcleo Teórico / Fundamento Invariante
{{Descrição detalhada do núcleo teórico duradouro, mecânica, leis, ou fundamentos}}

## Conexões
{{Conexões para outros conceitos usando links [[R_Conceito]] ou [[A_Procedimento]]{{Se houver}}}}
<<<< END FILE >>>>

Dentro do bloco de código markdown, para cada arquivo de Ação gerado, use exatamente esta sintaxe:
<<<< FILE: A_{{Nome_do_Procedimento}}.md >>>>
---
tags: [acao]
---
# A_{{Nome_do_Procedimento}}

## Protocolo Prático / Roteiro de Execução
{{Roteiro prático, comandos, guias passo a passo, sintaxes de código específicas, dosagens ou ritos processuais}}

## Conexões
{{Conexões para outros conceitos usando links [[R_Conceito]] ou [[A_OutroProcedimento]]{{Se houver}}}}
<<<< END FILE >>>>

Além disso, também dentro do bloco de código markdown, ao final da resposta, informe a quais MOCs do Obsidian (a partir da lista fornecida abaixo) essas novas notas pertencem, ou sugira novos MOCs se não houver correspondência, no seguinte formato de bloco:
<<<< MOC_ASSOCIATIONS >>>>
R_{{Nome_do_Conceito}}.md -> {{Nome_do_MOC}}
A_{{Nome_do_Procedimento}}.md -> {{Nome_do_MOC}}
<<<< END MOC_ASSOCIATIONS >>>>

Lista de MOCs ativos:
{mocs_list}

Transcrição técnica:
{transcription}
"""


class GeminiWebProcessor:
    """Automates Gemini web interface using Playwright."""

    PROMPT_SELECTORS = "div[contenteditable='true'], textarea#prompt-textarea, [role='combobox']"
    SEND_SELECTORS = [
        "button[aria-label*='Send']",
        "button[aria-label*='Enviar']",
        "button.send-button",
        "button[type='submit']",
        "div.send-button-container button",
    ]
    RESPONSE_SELECTORS = (
        "message-content, .message-content, .model-response, "
        "div[class*='message-content']"
    )
    MENU_SELECTORS = "button[aria-label*='Menu'], button[aria-label*='Expand']"
    ACTION_SELECTORS = (
        "button[aria-label*='actions'], button[aria-label*='opções'], "
        "button[aria-label*='Options']"
    )
    DELETE_SELECTORS = (
        "span:has-text('Delete'), span:has-text('Excluir'), "
        "[role='menuitem']:has-text('Delete'), [role='menuitem']:has-text('Excluir'), "
        "[class*='delete']"
    )
    CONFIRM_DELETE_SELECTORS = "button:has-text('Delete'), button:has-text('Excluir')"
    DIALOG_SELECTORS = "[role='dialog'], mat-dialog-container, [class*='dialog']"

    GEMINI_URL = "https://gemini.google.com/"
    # GEMINI_URL = "https://gemini.google.com/gem/bae17c2375e7"

    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    def __init__(self, user_data_dir: Path) -> None:
        self.user_data_dir = user_data_dir.expanduser()
        self.playwright: "Playwright | None" = None
        self.context: "BrowserContext | None" = None
        self.page: "Page | None" = None

    def __enter__(self) -> Self:
        from playwright.sync_api import sync_playwright

        self.playwright = sync_playwright().start()
        args = ["--disable-blink-features=AutomationControlled"]

        try:
            # print("[GeminiWeb] Launching Chrome persistent context...")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir.resolve()),
                headless=False,
                channel="chrome",
                slow_mo=100,
                user_agent=self.USER_AGENT,
                args=args,
                ignore_default_args=["--enable-automation"],
            )
        except Exception as e:
            print(f"[GeminiWeb] Chrome failed ({e}). Launching Chromium fallback...")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir.resolve()),
                headless=False,
                slow_mo=100,
                user_agent=self.USER_AGENT,
                args=args,
                ignore_default_args=["--enable-automation"],
            )

        if not self.context:
            raise RuntimeError("Browser context failed to initialize.")
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

        # print("[GeminiWeb] Navigating to Gemini...")
        self.page.goto(self.GEMINI_URL, timeout=60000)
        self.page.wait_for_timeout(3000)

        # Check if Google Account login is active
        if not self._is_logged_in():
            print("\n" + "=" * 60)
            print("⚠️  LOGIN REQUIRED")
            print("Google Account session not detected in Gemini Web.")
            print("Please log in to your Google Account in the browser window.")
            print("=" * 60 + "\n")
            
            while True:
                input("PRESS << ENTER >> here AFTER completing Google Login in the browser window to continue...")
                self.page.wait_for_timeout(2000)
                if self._is_logged_in():
                    print("✓ Google Account login verified! Proceeding...\n")
                    break
                else:
                    print("⚠️ Login not detected yet. Please sign in to Google in the browser and try again.")

        return self

    def _is_logged_in(self) -> bool:
        """Check if the user is logged into a Google Account on Gemini Web."""
        if not self.page:
            return False
        
        # Check for Sign In / Fazer Login buttons or links
        sign_in_selectors = [
            "a[href*='ServiceLogin']",
            "a:has-text('Sign in')",
            "a:has-text('Fazer login')",
            "button:has-text('Sign in')",
            "button:has-text('Fazer login')",
            "[aria-label*='Sign in']",
            "[aria-label*='Fazer login']",
        ]
        for sel in sign_in_selectors:
            try:
                elem = self.page.locator(sel).first
                if elem.is_visible(timeout=500):
                    return False
            except Exception:
                pass
                
        # Check for logged-in user indicators (avatar, account button)
        logged_in_selectors = [
            "a[href*='myaccount.google.com']",
            "a[aria-label*='Google Account']",
            "a[aria-label*='Conta do Google']",
            "img[src*='googleusercontent.com']",
            "button[aria-label*='Google Account']",
            "button[aria-label*='Conta do Google']",
        ]
        for sel in logged_in_selectors:
            try:
                elem = self.page.locator(sel).first
                if elem.is_visible(timeout=500):
                    return True
            except Exception:
                pass

        if "accounts.google.com" in self.page.url:
            return False

        # If sign-in buttons were not visible, assume logged in
        return True

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

    def send_prompt(self, prompt_text: str, keep_thread: bool = False) -> str:
        """Send prompt, wait for stabilization, extract response, delete thread if keep_thread is False."""
        if not self.page:
            raise RuntimeError("GeminiWebProcessor is not initialized. Use as a context manager.")
        self.page.goto(self.GEMINI_URL, timeout=60000)

        prompt_element = self.page.locator(self.PROMPT_SELECTORS).first
        prompt_element.wait_for(state="visible", timeout=15000)

        # print("[GeminiWeb] Filling prompt...")
        prompt_element.focus()
        prompt_element.fill(prompt_text)

        # Submission loop with silent-failure retry fallback
        success = False
        current_timeout = 1000
        while not success:
            # Check if prompt has already been cleared or response is already visible
            # to prevent double submission (which clicks the "Stop response" button on Gemini)
            tag_name = prompt_element.evaluate("el => el.tagName.toLowerCase()")
            val = prompt_element.input_value().strip() if tag_name in ["input", "textarea"] else prompt_element.inner_text().strip()
            
            if not val or self.page.locator(self.RESPONSE_SELECTORS).first.is_visible():
                success = True
                break

            send_button = None
            for sel in self.SEND_SELECTORS:
                btn = self.page.locator(sel).first
                if btn.is_visible() and btn.is_enabled():
                    send_button = btn
                    break

            if send_button:
                send_button.click()
            else:
                prompt_element.focus()
                self.page.keyboard.press("Enter")

            # Wait deterministically for the response container to appear (indicating successful submission)
            try:
                first_response = self.page.locator(self.RESPONSE_SELECTORS).first
                first_response.wait_for(state="visible", timeout=current_timeout)
                success = True
            except Exception:
                # Double the timeout for the next attempt, capping at 16 seconds
                current_timeout = min(current_timeout * 2, 300000)

        last_text = ""
        stable_count = 0
        for _ in range(90):  # Allow up to 90 seconds for large processing
            responses = [r for r in self.page.locator(self.RESPONSE_SELECTORS).all() if r.inner_text().strip()]
            if responses:
                current_text = responses[-1].inner_text().strip()
                if current_text == last_text:
                    stable_count += 1
                    if stable_count >= 3:
                        break
                else:
                    stable_count = 0
                    last_text = current_text
            self.page.wait_for_timeout(1000)

        if not last_text:
            raise RuntimeError("Failed to capture response from Gemini.")

        # Extract raw unrendered response text (preserving Markdown markup like #, **, code blocks)
        responses = [r for r in self.page.locator(self.RESPONSE_SELECTORS).all() if r.inner_text().strip()]
        if responses:
            last_text = self._extract_raw_response(responses[-1])

        if not keep_thread:
            self._delete_current_thread()

        return last_text

    def _extract_raw_response(self, response_element) -> str:
        """Extract raw unrendered Markdown text using code-block locator or clipboard copy button fallback."""
        if not self.page or not self.context:
            return response_element.inner_text().strip()

        # 1. Check for code blocks (pre, code, code-block)
        try:
            code_elem = response_element.locator("code-block, pre, code").first
            if code_elem.is_visible(timeout=500):
                code_text = code_elem.inner_text().strip()
                if code_text and len(code_text) > 10:
                    return code_text
        except Exception:
            pass

        # 2. Try clicking Gemini's copy button to read raw Markdown from clipboard
        copy_button_selectors = [
            "button[aria-label*='Copy']",
            "button[aria-label*='Copiar']",
            "button[data-test-id='copy-button']",
            "mat-icon[fonticon='content_copy']",
            "button:has(mat-icon[fonticon='content_copy'])",
        ]
        try:
            self.context.grant_permissions(["clipboard-read", "clipboard-write"])
            copy_btn = None
            for sel in copy_button_selectors:
                btn = response_element.locator(sel).first
                if btn.is_visible(timeout=500):
                    copy_btn = btn
                    break
            if not copy_btn:
                for sel in copy_button_selectors:
                    btns = self.page.locator(sel).all()
                    if btns:
                        copy_btn = btns[-1]
                        break
            
            if copy_btn:
                copy_btn.click()
                self.page.wait_for_timeout(500)
                clipboard_text = self.page.evaluate("navigator.clipboard.readText()")
                if clipboard_text and len(clipboard_text.strip()) > 10:
                    return clipboard_text.strip()
        except Exception:
            pass

        # 3. Fallback to standard inner_text()
        return response_element.inner_text().strip()

    def delete_current_thread(self) -> None:
        """Expose thread deletion publicly."""
        self._delete_current_thread()

    def send_prompt_to_gem(self, gem_id_or_url: str, prompt_text: str, keep_thread: bool = False, is_subsequent_turn: bool = False) -> str:
        """Send prompt to a custom Gem, wait for stabilization, and return the response."""
        if not self.page:
            raise RuntimeError("GeminiWebProcessor is not initialized. Use as a context manager.")
        
        # Determine the Gem URL
        if gem_id_or_url.startswith("http://") or gem_id_or_url.startswith("https://"):
            url = gem_id_or_url
        else:
            url = f"https://gemini.google.com/gem/{gem_id_or_url}"

        # Navigate to the Gem URL if it's the first turn or if we are not reusing the thread
        if not is_subsequent_turn:
            # print(f"[GeminiWeb] Navigating to Gem: {url}")
            self.page.goto(url, timeout=60000)
            self.page.wait_for_timeout(2000)
        
        prompt_element = self.page.locator(self.PROMPT_SELECTORS).first
        prompt_element.wait_for(state="visible", timeout=15000)

        # Get response count before sending prompt
        prev_responses = [r for r in self.page.locator(self.RESPONSE_SELECTORS).all() if r.inner_text().strip()]
        prev_count = len(prev_responses)

        # Fill prompt
        prompt_element.focus()
        prompt_element.fill(prompt_text)

        # Send
        success = False
        current_timeout = 1000
        while not success:
            tag_name = prompt_element.evaluate("el => el.tagName.toLowerCase()")
            val = prompt_element.input_value().strip() if tag_name in ["input", "textarea"] else prompt_element.inner_text().strip()
            
            # Check if prompt was sent
            responses = [r for r in self.page.locator(self.RESPONSE_SELECTORS).all() if r.inner_text().strip()]
            if not val or len(responses) > prev_count:
                success = True
                break

            send_button = None
            for sel in self.SEND_SELECTORS:
                btn = self.page.locator(sel).first
                if btn.is_visible() and btn.is_enabled():
                    send_button = btn
                    break

            if send_button:
                send_button.click()
            else:
                prompt_element.focus()
                self.page.keyboard.press("Enter")

            # Wait for response count to increase
            try:
                self.page.wait_for_function(
                    f"() => document.querySelectorAll(\"{self.RESPONSE_SELECTORS}\").length > {prev_count}",
                    timeout=current_timeout
                )
                success = True
            except Exception:
                current_timeout = min(current_timeout * 2, 30000)

        # Wait for the response to stabilize
        last_text = ""
        stable_count = 0
        for _ in range(1200):  # Allow up to 1200 seconds for large processing
            responses = [r for r in self.page.locator(self.RESPONSE_SELECTORS).all() if r.inner_text().strip()]
            if len(responses) > prev_count:
                current_text = responses[-1].inner_text().strip()
                if current_text == last_text:
                    stable_count += 1
                    if stable_count >= 3:
                        break
                else:
                    stable_count = 0
                    last_text = current_text
            self.page.wait_for_timeout(1000)

        if not last_text:
            raise RuntimeError("Failed to capture response from Gemini.")

        # Extract raw unrendered response text (preserving Markdown markup like #, **, code blocks)
        responses = [r for r in self.page.locator(self.RESPONSE_SELECTORS).all() if r.inner_text().strip()]
        if responses:
            last_text = self._extract_raw_response(responses[-1])

        if not keep_thread:
            self._delete_current_thread()

        return last_text


    def _delete_current_thread(self) -> None:
        """Clean up by deleting the active chat session."""
        # print("[GeminiWeb] Cleaning thread...")
        if not self.page:
            return
        try:
            menu_btn = self.page.locator(self.MENU_SELECTORS).first
            if menu_btn.is_visible():
                menu_btn.click()

            action_btn = self.page.locator(self.ACTION_SELECTORS).first
            action_btn.wait_for(state="visible", timeout=3000)

            if action_btn.is_visible():
                action_btn.click()

                delete_opt = self.page.locator(self.DELETE_SELECTORS).first
                delete_opt.wait_for(state="visible", timeout=3000)
                delete_opt.click()

                confirm_btn = (
                    self.page.locator(self.DIALOG_SELECTORS)
                    .locator(self.CONFIRM_DELETE_SELECTORS)
                    .first
                )
                confirm_btn.wait_for(state="visible", timeout=3000)
                confirm_btn.click()
                
                # Wait until the delete confirmation dialog is hidden before proceeding
                confirm_btn.wait_for(state="hidden", timeout=5000)
                # print("[GeminiWeb] Thread deleted successfully.")
        except Exception as e:
            print(f"[GeminiWeb] Warning: failed to delete thread ({e})")


# ==================== TRACKING LOGS ====================

def load_processed_log(log_path: Path) -> dict:
    if log_path.exists():
        try:
            with open(log_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_processed_log(log_path: Path, log_data: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
