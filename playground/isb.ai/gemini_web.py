"""Gemini Web Processor - Playwright-based browser automation to run Gemini as a free API.

Provides absolute temporal anchoring, dynamic prompt routing (News vs Technical),
Obsidian MOC list context injection, and structured file boundary parsing.
"""

import json
import time
from pathlib import Path
from typing import Self

# ==================== SYSTEM PROMPTS ====================

NEWS_SYSTEM_PROMPT = """Você é o motor de processamento do ecossistema RAE-PKM.
A data atual de referência do mundo é {data_yaml}.
Qualquer menção temporal deve ser convertida para uma data absoluta no formato AAAA-MM-DD.
Sua saída deve ser estritamente dividida em arquivos Markdown atômicos independentes, focados em um único fato.

Hierarquia de Diretórios e Links no Cofre:
- As notas de fatos e conceitos são salvas diretamente na raiz do cofre. Portanto, links bilaterais entre elas devem usar o formato direto: [[Nome_da_Nota]].
- Os Mapas de Conteúdo (MOCs) residem na subpasta MOCs/. Se você referenciar algum MOC dentro de uma nota de fato, use o caminho relativo ao cofre: [[MOCs/MOC_Nome]].

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
- As notas de referência (R_) e ação (A_) são salvas diretamente na raiz do cofre. Portanto, links bilaterais entre elas devem usar o formato direto: [[R_Conceito]] ou [[A_Procedimento]].
- Os Mapas de Conteúdo (MOCs) residem na subpasta MOCs/. Se você referenciar algum MOC dentro de uma nota R_ ou A_, use o caminho relativo ao cofre: [[MOCs/MOC_Nome]].

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
    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    def __init__(self, user_data_dir: Path) -> None:
        self.user_data_dir = user_data_dir.expanduser()
        self.playwright = None
        self.context = None
        self.page = None

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

        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

        # print("[GeminiWeb] Navigating to Gemini...")
        self.page.goto(self.GEMINI_URL, timeout=60000)
        self.page.wait_for_timeout(3000)

        prompt_element = self.page.locator(self.PROMPT_SELECTORS).first

        login = False
        alert = False
        while login == False:
            try:
                prompt_element.wait_for(state="visible", timeout=3000)
                print("\n" + "=" * 60)
                # print("👤  [GeminiWeb] SESSION DETECTED")
                # print("Please confirm the Google account in the browser.")
                result = input("PRESS << ENTER >> Here AFTER Login in GEMINI page in BROWSER to continue...")
                if result.lower() == "":
                    login = True
                    print("=" * 60 + "\n")
                else:
                    raise Exception("Please login to your Google Account in the browser window.")
            except Exception:
                if not alert:
                # print("\n" + "=" * 60)
                    print("⚠️  LOGIN REQUIRED")
                    print("Please log in to your Google Account in the browser window.")
                    print("Once logged in and ready, PRESS ENTER to continue...")
                    alert = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()

    def send_prompt(self, prompt_text: str) -> str:
        """Send prompt, wait for stabilization, extract response, delete thread."""
        self.page.goto(self.GEMINI_URL, timeout=60000)

        prompt_element = self.page.locator(self.PROMPT_SELECTORS).first
        prompt_element.wait_for(state="visible", timeout=15000)

        # print("[GeminiWeb] Filling prompt...")
        prompt_element.focus()
        prompt_element.fill(prompt_text)

        send_button = None
        for sel in self.SEND_SELECTORS:
            btn = self.page.locator(sel).first
            if btn.is_visible() and btn.is_enabled():
                send_button = btn
                break

        if send_button:
            send_button.click()
        else:
            self.page.keyboard.press("Enter")

        # print("[GeminiWeb] Waiting for generation...")
        try:
            # Wait reactively for the first response container to appear
            first_response = self.page.locator(self.RESPONSE_SELECTORS).first
            first_response.wait_for(state="visible", timeout=10000)
        except Exception:
            pass

        last_text = ""
        stable_count = 0
        for _ in range(90):  # Allow up to 90 seconds for large processing
            responses = self.page.locator(self.RESPONSE_SELECTORS).all()
            if responses:
                current_text = responses[-1].inner_text()
                if current_text and current_text == last_text:
                    stable_count += 1
                    if stable_count >= 3:
                        break
                else:
                    stable_count = 0
                    last_text = current_text
            self.page.wait_for_timeout(1000)

        if not last_text:
            raise RuntimeError("Failed to capture response from Gemini.")

        # print(f"[GeminiWeb] Response captured ({len(last_text)} characters).")
        self._delete_current_thread()

        return last_text

    def _delete_current_thread(self) -> None:
        """Clean up by deleting the active chat session."""
        # print("[GeminiWeb] Cleaning thread...")
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
                print("[GeminiWeb] Thread deleted successfully.")
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
