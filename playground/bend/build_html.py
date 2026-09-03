#!/usr/bin/env python3
"""Build an interactive, beautiful HTML page for the Bend stretching routine.

Features:
- Glassmorphic modern dark design with vibrant accents.
- Responsive layout (mobile & desktop).
- Built-in exercise player with Web Audio API chime sound effects.
- Bilateral support with automatic side switching ('Lado Esquerdo' / 'Lado Direito').
- Dynamic variation switcher for exercises with alternatives (e.g., Rag Doll vs Toe Touch vs Forward Fold).
- Real high-resolution images from bend.com dataset.
- Complete, uncapped original Instructions, Tips, Modifications, and Benefits displayed on every card.
- Global expand/collapse toggle for all details.
- Keyboard shortcuts (Space: Play/Pause, Arrows: Prev/Next, M: Mute).
"""

from __future__ import annotations

import json
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
EXERCISES_JSON_PATH = BASE_DIR / "exercises.json"
OUTPUT_HTML_PATH = BASE_DIR / "index.html"

# Load database
with open(EXERCISES_JSON_PATH, "r", encoding="utf-8") as f:
    all_exercises_raw = json.load(f)
    exercises_map = {e["name"]: e for e in all_exercises_raw}

# Sequence specification from user
ROUTINE_SPEC = [
    {
        "id": 1,
        "title": "Upward Salute",
        "user_note": "Abre a frente do corpo e prepara a coluna",
        "default_duration": 30,
        "is_bilateral": False,
        "side_duration": 0,
        "variants": ["Upward Salute"],
        "default_variant": "Upward Salute",
        "warning": "",
    },
    {
        "id": 2,
        "title": "Rag Doll / Toe Touch / Forward Fold",
        "user_note": "Cadeia completa em pé",
        "default_duration": 60,
        "is_bilateral": False,
        "side_duration": 0,
        "variants": ["Rag Doll", "Toe Touch", "Forward Fold"],
        "default_variant": "Rag Doll",
        "warning": "",
    },
    {
        "id": 3,
        "title": "Wide Leg Bend",
        "user_note": "Isquiotibiais + adutores + lombar",
        "default_duration": 60,
        "is_bilateral": False,
        "side_duration": 0,
        "variants": ["Wide Leg Bend"],
        "default_variant": "Wide Leg Bend",
        "warning": "",
    },
    {
        "id": 4,
        "title": "Downward Dog",
        "user_note": "Panturrilhas + isquiotibiais + ombros",
        "default_duration": 60,
        "is_bilateral": False,
        "side_duration": 0,
        "variants": ["Downward Dog"],
        "default_variant": "Downward Dog",
        "warning": "",
    },
    {
        "id": 5,
        "title": "Lizard Pose / Pigeon",
        "user_note": "Glúteos + isquiotibiais + flexores (60 s cada lado)",
        "default_duration": 120,
        "is_bilateral": True,
        "side_duration": 60,
        "variants": ["Lizard Pose", "Pigeon"],
        "default_variant": "Lizard Pose",
        "warning": "",
    },
    {
        "id": 6,
        "title": "Seated Fold",
        "user_note": "Isquiotibiais + lombar sentado",
        "default_duration": 60,
        "is_bilateral": False,
        "side_duration": 0,
        "variants": ["Seated Fold"],
        "default_variant": "Seated Fold",
        "warning": "",
    },
    {
        "id": 7,
        "title": "Seated Straddle / Hurdler",
        "user_note": "45–60 s (ou 30 s cada lado no Hurdler)",
        "default_duration": 60,
        "is_bilateral": False,  # Hurdler switches to bilateral dynamically in UI
        "side_duration": 30,
        "variants": ["Seated Straddle", "Hurdler"],
        "default_variant": "Seated Straddle",
        "warning": "",
    },
    {
        "id": 8,
        "title": "Lying Hamstring",
        "user_note": "Isquiotibiais isolados com apoio lombar protegido (45 s cada lado)",
        "default_duration": 90,
        "is_bilateral": True,
        "side_duration": 45,
        "variants": ["Lying Hamstring"],
        "default_variant": "Lying Hamstring",
        "warning": "",
    },
    {
        "id": 9,
        "title": "Plow",
        "user_note": "Descompressão e alongamento da coluna posterior (30–45 s)",
        "default_duration": 45,
        "is_bilateral": False,
        "side_duration": 0,
        "variants": ["Plow"],
        "default_variant": "Plow",
        "warning": "Atenção ao pescoço: mantenha o olhar voltado para o teto, não gire a cabeça de lado e saia suavemente da postura se sentir qualquer pressão ou desconforto cervical.",
    },
    {
        "id": 10,
        "title": "Knees-to-chest / Happy Baby",
        "user_note": "Alívio sacrolombar e relaxamento dos flexores",
        "default_duration": 45,
        "is_bilateral": False,
        "side_duration": 0,
        "variants": ["Knees-to-chest", "Happy Baby"],
        "default_variant": "Knees-to-chest",
        "warning": "",
    },
    {
        "id": 11,
        "title": "Legs-up-wall / Child’s Pose",
        "user_note": "Recuperação e descarga da coluna (60–90 s)",
        "default_duration": 90,
        "is_bilateral": False,
        "side_duration": 0,
        "variants": ["Legs-up-wall", "Child's Pose"],
        "default_variant": "Legs-up-wall",
        "warning": "",
    },
]

# Build compact data structure of all referenced variants
referenced_variants = set()
for step in ROUTINE_SPEC:
    for v in step["variants"]:
        referenced_variants.add(v)

variants_db = {}
for v_name in referenced_variants:
    if v_name in exercises_map:
        ex = exercises_map[v_name]
        variants_db[v_name] = {
            "name": ex["name"],
            "image_url": ex["image_url"],
            "alt_text": ex.get("alt_text", f"{ex['name']} exercise demonstration"),
            "benefits": ex["benefits"],
            "instructions": ex["instructions"],
            "tips": ex["tips"],
            "modifications": ex["modifications"],
        }
    else:
        print(f"Warning: Exercise '{v_name}' not found in exercises_map")

data_payload = {
    "steps": ROUTINE_SPEC,
    "variants": variants_db,
}


def generate_static_cards(routine_spec: list[dict], variants_db: dict) -> str:
    cards = []
    for idx, step in enumerate(routine_spec):
        current_variant_name = step["default_variant"]
        v_data = variants_db.get(current_variant_name, {})

        duration_str = f"{step['default_duration']} s"
        if step["is_bilateral"]:
            duration_str = f"{step['default_duration']} s ({step['side_duration']} s / lado)"
        elif current_variant_name == "Hurdler":
            duration_str = "60 s (30 s / lado)"

        variant_buttons_html = ""
        if len(step["variants"]) > 1:
            btns = []
            for v in step["variants"]:
                sel = "selected" if v == current_variant_name else ""
                btns.append(f'<button type="button" class="variant-btn {sel}" onclick="selectVariant({step["id"]}, \\\'{v}\\\', event)">{v}</button>')
            variant_buttons_html = f'''
              <div class="variant-selector">
                <span class="variant-label">Variação:</span>
                {''.join(btns)}
              </div>
            '''

        warning_html = ""
        if step["warning"]:
            warning_html = f'''
              <div class="warning-box">
                <svg class="icon-svg" style="flex-shrink: 0; margin-top: 2px;" viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
                <div>{step["warning"]}</div>
              </div>
            '''

        all_benefits = v_data.get("benefits", [])
        if all_benefits:
            benefits_html = "".join(f'<span class="benefit-tag">{b}</span>' for b in all_benefits)
        else:
            benefits_html = '<span class="empty-note">Nenhum benefício listado</span>'

        all_instructions = v_data.get("instructions", [])
        if all_instructions:
            instructions_html = "".join(f'<li>{inst}</li>' for inst in all_instructions)
        else:
            instructions_html = '<li class="empty-note">Instruções não disponíveis</li>'

        all_tips = v_data.get("tips", [])
        if all_tips:
            tips_html = "".join(f'<li>{tip}</li>' for tip in all_tips)
        else:
            tips_html = '<li class="empty-note">Mantenha respiração ritmada e postura firme sem forçar articulações.</li>'

        all_mods = v_data.get("modifications", [])
        if all_mods:
            mods_html = "".join(f'<li>{mod}</li>' for mod in all_mods)
        else:
            mods_html = '<li class="empty-note">Sem modificações adicionais necessárias para esta postura (ajuste a amplitude de acordo com o seu conforto).</li>'

        active_cls = "is-active" if idx == 0 else ""

        cards.append(f'''
          <article class="exercise-card {active_cls}" id="card-step-{step["id"]}">
            <div class="card-top">
              <div class="card-thumb-wrap">
                <img id="img-{step["id"]}" src="{v_data.get("image_url", "")}" alt="{v_data.get("alt_text", "")}" loading="lazy" />
              </div>

              <div class="card-body">
                <div class="card-header-row">
                  <span class="step-number">#{step["id"]}</span>
                  <h3 class="card-title" id="title-{step["id"]}">{v_data.get("name", step["title"])}</h3>
                  <span class="duration-badge">
                    <svg class="icon-svg" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
                    {duration_str}
                  </span>
                </div>

                <div class="user-purpose">{step["user_note"]}</div>

                {variant_buttons_html}

                {warning_html}
              </div>

              <div class="card-actions">
                <button type="button" class="btn-jump" onclick="jumpToStep({idx})" aria-label="Iniciar a partir deste exercício">
                  <svg class="icon-svg" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                  Começar
                </button>

                <button type="button" class="btn-details" onclick="toggleDetails({step["id"]})" aria-label="Alternar visualização das instruções">
                  <span id="btn-text-{step["id"]}">Ocultar detalhes</span>
                  <svg class="icon-svg" id="chevron-{step["id"]}" style="transform: rotate(180deg);" viewBox="0 0 24 24"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>
                </button>
              </div>
            </div>

            <!-- All 4 Sections: Benefits, Instructions, Tips, Modifications -->
            <div class="card-details" id="details-{step["id"]}">
              
              <!-- Section 1: Benefits -->
              <div class="benefits-section">
                <h4 class="section-label label-benefits">
                  <svg class="icon-svg" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                  <span>Benefits</span>
                  <span class="section-count">({len(all_benefits)} regiões beneficiadas)</span>
                </h4>
                <div class="benefits-chips-wrap" id="benefits-{step["id"]}">
                  {benefits_html}
                </div>
              </div>

              <!-- Grid for Instructions, Tips, Modifications -->
              <div class="details-grid">
                
                <!-- Section 2: Instructions -->
                <div class="detail-col instructions-col">
                  <h4 class="section-label label-instructions">
                    <svg class="icon-svg" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
                    <span>Instructions</span>
                    <span class="section-count">({len(all_instructions)} passos)</span>
                  </h4>
                  <ol class="instructions-list" id="instructions-{step["id"]}">
                    {instructions_html}
                  </ol>
                </div>
                
                <!-- Section 3: Tips -->
                <div class="detail-col tips-col">
                  <h4 class="section-label label-tips">
                    <svg class="icon-svg" viewBox="0 0 24 24"><path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z"/></svg>
                    <span>Tips</span>
                    <span class="section-count">({len(all_tips)} dicas)</span>
                  </h4>
                  <ul class="tips-list" id="tips-{step["id"]}">
                    {tips_html}
                  </ul>
                </div>

                <!-- Section 4: Modifications -->
                <div class="detail-col mods-col">
                  <h4 class="section-label label-mods">
                    <svg class="icon-svg" viewBox="0 0 24 24"><path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/></svg>
                    <span>Modifications</span>
                    <span class="section-count">({len(all_mods)} ajustes)</span>
                  </h4>
                  <ul class="mods-list" id="mods-{step["id"]}">
                    {mods_html}
                  </ul>
                </div>

              </div>
            </div>
          </article>
        ''')
    return "\\n".join(cards)


static_cards_html = generate_static_cards(ROUTINE_SPEC, variants_db)

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rotina de Alongamento e Mobilidade • Bend Flow</title>
  <meta name="description" content="Sequência guiada de 11 exercícios de mobilidade e alongamento com timer integrado, troca de lados bilateral e instruções originais completas: Instructions, Tips, Modifications e Benefits.">
  
  <!-- Modern Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">

  <style>
    /* Design Tokens & Theme Variables */
    :root {{
      --bg-dark: #090d16;
      --bg-surface: #0f172a;
      --bg-card: rgba(18, 26, 44, 0.82);
      --bg-card-hover: rgba(26, 38, 64, 0.92);
      --bg-glass: rgba(15, 23, 42, 0.88);
      
      --accent-primary: #38bdf8;
      --accent-gradient: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-purple: #c084fc;
      --accent-rose: #f43f5e;
      
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(56, 189, 248, 0.5);
      --border-card: rgba(255, 255, 255, 0.12);
      
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
      --radius-full: 9999px;
      
      --shadow-glow: 0 0 25px rgba(56, 189, 248, 0.15);
      --shadow-card: 0 12px 36px -10px rgba(0, 0, 0, 0.55);
      
      --font-display: 'Outfit', sans-serif;
      --font-body: 'Inter', sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background: var(--bg-dark);
      background-image: 
        radial-gradient(circle at 15% 10%, rgba(56, 189, 248, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 60%, rgba(129, 140, 248, 0.10) 0%, transparent 45%),
        radial-gradient(circle at 50% 90%, rgba(16, 185, 129, 0.08) 0%, transparent 50%);
      background-attachment: fixed;
      color: var(--text-main);
      font-family: var(--font-body);
      line-height: 1.6;
      min-height: 100vh;
      padding-bottom: 120px;
      -webkit-font-smoothing: antialiased;
    }}

    /* Container */
    .container {{
      max-width: 1140px;
      margin: 0 auto;
      padding: 0 20px;
    }}

    /* Header Section */
    header.hero {{
      padding: 48px 0 32px;
      text-align: center;
    }}

    .badge-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(56, 189, 248, 0.12);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: var(--accent-primary);
      padding: 6px 14px;
      border-radius: var(--radius-full);
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 16px;
    }}

    .hero h1 {{
      font-family: var(--font-display);
      font-size: clamp(2.2rem, 4vw, 3.4rem);
      font-weight: 800;
      line-height: 1.15;
      background: var(--accent-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 12px;
    }}

    .hero p.subtitle {{
      color: var(--text-muted);
      font-size: 1.1rem;
      max-width: 720px;
      margin: 0 auto 24px;
    }}

    /* Routine Metrics Bar */
    .metrics-bar {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 20px;
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 16px 28px;
      margin-bottom: 36px;
      box-shadow: var(--shadow-card);
    }}

    .metric-item {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .metric-icon {{
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.06);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--accent-primary);
    }}

    .metric-info {{
      text-align: left;
    }}

    .metric-val {{
      font-family: var(--font-display);
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--text-main);
    }}

    .metric-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
    }}

    /* Sticky Player Dock */
    .player-dock {{
      position: sticky;
      top: 16px;
      z-index: 100;
      background: var(--bg-glass);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(56, 189, 248, 0.28);
      box-shadow: 0 16px 40px -10px rgba(0, 0, 0, 0.75), var(--shadow-glow);
      border-radius: var(--radius-lg);
      padding: 18px 24px;
      margin-bottom: 40px;
      transition: all 0.3s ease;
    }}

    .player-grid {{
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 20px;
      align-items: center;
    }}

    @media (max-width: 768px) {{
      .player-grid {{
        grid-template-columns: 1fr;
        text-align: center;
        gap: 14px;
      }}
    }}

    /* Circular Timer Widget */
    .timer-widget {{
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      width: 86px;
      height: 86px;
    }}

    .timer-svg {{
      transform: rotate(-90deg);
      width: 86px;
      height: 86px;
    }}

    .timer-circle-bg {{
      fill: none;
      stroke: rgba(255, 255, 255, 0.08);
      stroke-width: 6;
    }}

    .timer-circle-fg {{
      fill: none;
      stroke: url(#timerGrad);
      stroke-width: 6;
      stroke-linecap: round;
      stroke-dasharray: 226;
      stroke-dashoffset: 0;
      transition: stroke-dashoffset 0.2s linear;
    }}

    .timer-display-text {{
      position: absolute;
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 1.35rem;
      color: var(--text-main);
    }}

    /* Active Info */
    .active-info {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}

    .active-meta {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .step-counter-tag {{
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent-primary);
    }}

    .side-badge {{
      display: inline-flex;
      align-items: center;
      padding: 2px 10px;
      border-radius: var(--radius-full);
      font-size: 0.75rem;
      font-weight: 700;
      background: rgba(16, 185, 129, 0.15);
      color: var(--accent-emerald);
      border: 1px solid rgba(16, 185, 129, 0.4);
      transition: all 0.3s ease;
    }}

    .side-badge.side-right {{
      background: rgba(245, 158, 11, 0.15);
      color: var(--accent-amber);
      border-color: rgba(245, 158, 11, 0.4);
    }}

    .active-title {{
      font-family: var(--font-display);
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--text-main);
    }}

    .active-focus {{
      font-size: 0.88rem;
      color: var(--text-muted);
    }}

    /* Controls */
    .player-controls {{
      display: flex;
      align-items: center;
      gap: 10px;
      justify-content: center;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      border: none;
      outline: none;
      cursor: pointer;
      font-family: var(--font-body);
      font-weight: 600;
      border-radius: var(--radius-md);
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    .btn-icon {{
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-main);
      border: 1px solid var(--border-subtle);
    }}

    .btn-icon:hover {{
      background: rgba(255, 255, 255, 0.16);
      transform: translateY(-2px);
    }}

    .btn-primary {{
      width: 54px;
      height: 54px;
      border-radius: 50%;
      background: var(--accent-gradient);
      color: #090d16;
      font-size: 1.25rem;
      box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);
    }}

    .btn-primary:hover {{
      transform: scale(1.06);
      box-shadow: 0 6px 22px rgba(56, 189, 248, 0.6);
    }}

    .btn-tool {{
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: transparent;
      color: var(--text-dim);
    }}

    .btn-tool:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.06);
    }}

    /* Global Progress Bar */
    .global-progress {{
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.06);
      border-radius: 3px;
      margin-top: 14px;
      overflow: hidden;
      position: relative;
    }}

    .global-progress-bar {{
      height: 100%;
      width: 0%;
      background: var(--accent-gradient);
      border-radius: 3px;
      transition: width 0.3s ease;
    }}

    /* Section Header Toolbar */
    .section-header-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }}

    .section-heading {{
      font-family: var(--font-display);
      font-size: 1.6rem;
      font-weight: 700;
      color: var(--text-main);
    }}

    .section-subtext {{
      font-size: 0.88rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .btn-toggle-all {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      padding: 8px 16px;
      border-radius: var(--radius-full);
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}

    .btn-toggle-all:hover {{
      background: rgba(255, 255, 255, 0.12);
      border-color: rgba(255, 255, 255, 0.25);
    }}

    /* Exercise List / Cards */
    .card-list {{
      display: flex;
      flex-direction: column;
      gap: 28px;
    }}

    .exercise-card {{
      background: var(--bg-card);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border-card);
      border-radius: var(--radius-lg);
      padding: 26px;
      box-shadow: var(--shadow-card);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: hidden;
    }}

    .exercise-card:hover {{
      background: var(--bg-card-hover);
      border-color: rgba(56, 189, 248, 0.35);
      transform: translateY(-2px);
    }}

    .exercise-card.is-active {{
      border-color: var(--accent-primary);
      box-shadow: 0 0 35px rgba(56, 189, 248, 0.28);
    }}

    .exercise-card.is-active::before {{
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 5px;
      background: var(--accent-gradient);
    }}

    .card-top {{
      display: grid;
      grid-template-columns: 140px 1fr auto;
      gap: 24px;
      align-items: center;
    }}

    @media (max-width: 720px) {{
      .card-top {{
        grid-template-columns: 1fr;
        text-align: left;
      }}
    }}

    .card-thumb-wrap {{
      width: 140px;
      height: 140px;
      border-radius: var(--radius-md);
      overflow: hidden;
      background: #0f172a;
      border: 1px solid var(--border-subtle);
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .card-thumb-wrap img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      padding: 4px;
      transition: transform 0.4s ease;
    }}

    .exercise-card:hover .card-thumb-wrap img {{
      transform: scale(1.05);
    }}

    .card-body {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .card-header-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .step-number {{
      font-family: var(--font-display);
      font-size: 0.85rem;
      font-weight: 800;
      color: var(--accent-primary);
      background: rgba(56, 189, 248, 0.12);
      padding: 3px 10px;
      border-radius: var(--radius-sm);
    }}

    .card-title {{
      font-family: var(--font-display);
      font-size: 1.45rem;
      font-weight: 700;
      color: var(--text-main);
    }}

    .duration-badge {{
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-main);
      font-size: 0.82rem;
      font-weight: 600;
      padding: 3px 10px;
      border-radius: var(--radius-full);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .user-purpose {{
      color: #93c5fd;
      font-size: 0.95rem;
      font-weight: 500;
    }}

    /* Variation Selector Pills */
    .variant-selector {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 4px;
    }}

    .variant-label {{
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
    }}

    .variant-btn {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
      padding: 5px 12px;
      border-radius: var(--radius-full);
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .variant-btn:hover {{
      background: rgba(255, 255, 255, 0.12);
      color: var(--text-main);
    }}

    .variant-btn.selected {{
      background: rgba(56, 189, 248, 0.2);
      border-color: var(--accent-primary);
      color: var(--text-main);
      font-weight: 600;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.25);
    }}

    /* Card Top Actions */
    .card-actions {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      align-items: flex-end;
    }}

    @media (max-width: 720px) {{
      .card-actions {{
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        margin-top: 10px;
      }}
    }}

    .btn-jump {{
      background: rgba(56, 189, 248, 0.14);
      border: 1px solid rgba(56, 189, 248, 0.35);
      color: var(--accent-primary);
      padding: 8px 18px;
      border-radius: var(--radius-md);
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s ease;
    }}

    .btn-jump:hover {{
      background: var(--accent-primary);
      color: #090d16;
      box-shadow: 0 4px 14px rgba(56, 189, 248, 0.4);
    }}

    .btn-details {{
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-size: 0.82rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }}

    .btn-details:hover {{
      color: var(--text-main);
    }}

    /* Warning alert */
    .warning-box {{
      margin-top: 14px;
      background: rgba(244, 63, 94, 0.12);
      border: 1px solid rgba(244, 63, 94, 0.35);
      border-radius: var(--radius-md);
      padding: 10px 14px;
      display: flex;
      align-items: flex-start;
      gap: 10px;
      font-size: 0.85rem;
      color: #fda4af;
    }}

    /* --- Detailed Sections: Instructions, Tips, Modifications, Benefits --- */
    .card-details {{
      display: block; /* Visible by default */
      margin-top: 22px;
      padding-top: 22px;
      border-top: 1px solid var(--border-subtle);
      animation: fadeIn 0.3s ease;
    }}

    .card-details.collapsed {{
      display: none;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(-6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* 1. Benefits Section Bar */
    .benefits-section {{
      background: rgba(16, 185, 129, 0.05);
      border: 1px solid rgba(16, 185, 129, 0.22);
      border-radius: var(--radius-md);
      padding: 14px 18px;
      margin-bottom: 18px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .section-label {{
      font-family: var(--font-display);
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 700;
    }}

    .section-label.label-benefits {{
      color: var(--accent-emerald);
    }}

    .section-label.label-instructions {{
      color: var(--accent-primary);
    }}

    .section-label.label-tips {{
      color: var(--accent-amber);
    }}

    .section-label.label-mods {{
      color: var(--accent-purple);
    }}

    .section-count {{
      font-size: 0.72rem;
      font-weight: 500;
      opacity: 0.8;
      text-transform: none;
      letter-spacing: 0;
    }}

    .benefits-chips-wrap {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .benefit-tag {{
      background: rgba(16, 185, 129, 0.12);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.3);
      font-size: 0.78rem;
      font-weight: 600;
      padding: 3px 10px;
      border-radius: var(--radius-sm);
    }}

    /* 2. Grid for Instructions, Tips, Modifications */
    .details-grid {{
      display: grid;
      grid-template-columns: 1.2fr 1fr 1fr;
      gap: 16px;
    }}

    @media (max-width: 960px) {{
      .details-grid {{
        grid-template-columns: 1fr;
        gap: 14px;
      }}
    }}

    .detail-col {{
      border-radius: var(--radius-md);
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    /* Instructions Column */
    .instructions-col {{
      background: rgba(56, 189, 248, 0.04);
      border: 1px solid rgba(56, 189, 248, 0.18);
    }}

    .instructions-list {{
      list-style: none;
      counter-reset: step-count;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .instructions-list li {{
      counter-increment: step-count;
      position: relative;
      padding-left: 32px;
      font-size: 0.88rem;
      color: #e2e8f0;
      line-height: 1.5;
    }}

    .instructions-list li::before {{
      content: counter(step-count);
      position: absolute;
      left: 0;
      top: 1px;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: rgba(56, 189, 248, 0.16);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: var(--accent-primary);
      font-size: 0.75rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    /* Tips Column */
    .tips-col {{
      background: rgba(245, 158, 11, 0.04);
      border: 1px solid rgba(245, 158, 11, 0.2);
    }}

    .tips-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .tips-list li {{
      position: relative;
      padding-left: 24px;
      font-size: 0.88rem;
      color: #fde68a;
      line-height: 1.5;
    }}

    .tips-list li::before {{
      content: '💡';
      position: absolute;
      left: 0;
      top: 1px;
      font-size: 0.8rem;
    }}

    /* Modifications Column */
    .mods-col {{
      background: rgba(192, 132, 252, 0.04);
      border: 1px solid rgba(192, 132, 252, 0.2);
    }}

    .mods-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .mods-list li {{
      position: relative;
      padding-left: 24px;
      font-size: 0.88rem;
      color: #e9d5ff;
      line-height: 1.5;
    }}

    .mods-list li::before {{
      content: '⚡';
      position: absolute;
      left: 0;
      top: 1px;
      font-size: 0.8rem;
    }}

    .empty-note {{
      font-style: italic;
      color: var(--text-dim);
      font-size: 0.84rem;
    }}

    /* Footer */
    footer.app-footer {{
      margin-top: 60px;
      text-align: center;
      color: var(--text-dim);
      font-size: 0.85rem;
      border-top: 1px solid var(--border-subtle);
      padding-top: 24px;
    }}

    footer.app-footer a {{
      color: var(--accent-primary);
      text-decoration: none;
    }}

    /* SVG Icon Helpers */
    .icon-svg {{
      width: 18px;
      height: 18px;
      fill: currentColor;
    }}
  </style>
</head>
<body>

  <!-- Definition of SVG Gradients -->
  <svg style="position: absolute; width: 0; height: 0; overflow: hidden;" aria-hidden="true">
    <defs>
      <linearGradient id="timerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#38bdf8" />
        <stop offset="50%" stop-color="#818cf8" />
        <stop offset="100%" stop-color="#c084fc" />
      </linearGradient>
    </defs>
  </svg>

  <div class="container">

    <!-- Header Section -->
    <header class="hero">
      <div class="badge-pill">
        <svg class="icon-svg" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
        Rotina Guiada de Mobilidade
      </div>
      <h1>Sequência Completa de Alongamento</h1>
      <p class="subtitle">
        11 posturas estratégicas para descompressão vertebral, abertura de quadril e relaxamento miofascial profundo da cadeia posterior — com todas as instruções, dicas, modificações e benefícios originais.
      </p>

      <!-- Routine Metrics Overview -->
      <div class="metrics-bar" id="metricsBar">
        <div class="metric-item">
          <div class="metric-icon">
            <svg class="icon-svg" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
          </div>
          <div class="metric-info">
            <div class="metric-val" id="totalDurationDisplay">11 min 55 s</div>
            <div class="metric-label">Duração Estimada</div>
          </div>
        </div>

        <div class="metric-item">
          <div class="metric-icon">
            <svg class="icon-svg" viewBox="0 0 24 24"><path d="M4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm16-4H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H8V4h12v12z"/></svg>
          </div>
          <div class="metric-info">
            <div class="metric-val">11 Exercícios</div>
            <div class="metric-label">Passos da Rotina</div>
          </div>
        </div>

        <div class="metric-item">
          <div class="metric-icon">
            <svg class="icon-svg" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
          </div>
          <div class="metric-info">
            <div class="metric-val">Cadeia Posterior</div>
            <div class="metric-label">Foco Principal</div>
          </div>
        </div>
      </div>
    </header>

    <!-- Sticky Active Player Dock -->
    <section class="player-dock" id="playerDock" aria-label="Player de Exercícios">
      <div class="player-grid">
        
        <!-- Circular Timer -->
        <div class="timer-widget">
          <svg class="timer-svg" viewBox="0 0 86 86">
            <circle class="timer-circle-bg" cx="43" cy="43" r="36" />
            <circle class="timer-circle-fg" id="timerCircle" cx="43" cy="43" r="36" />
          </svg>
          <div class="timer-display-text" id="timerDisplay">00:30</div>
        </div>

        <!-- Active Exercise Info -->
        <div class="active-info">
          <div class="active-meta">
            <span class="step-counter-tag" id="activeStepTag">Passo 1 de 11</span>
            <span class="side-badge" id="activeSideBadge" style="display: none;">Lado Esquerdo</span>
          </div>
          <h2 class="active-title" id="activeTitle">Upward Salute</h2>
          <p class="active-focus" id="activeFocus">Abre a frente do corpo e prepara a coluna</p>
        </div>

        <!-- Controls -->
        <div class="player-controls">
          <button class="btn btn-icon" id="btnPrev" title="Exercício Anterior (Seta Esquerda)" aria-label="Exercício Anterior">
            <svg class="icon-svg" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
          </button>
          
          <button class="btn btn-primary" id="btnPlayPause" title="Iniciar / Pausar (Espaço)" aria-label="Iniciar ou Pausar">
            <svg class="icon-svg" id="iconPlayPause" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          </button>

          <button class="btn btn-icon" id="btnNext" title="Próximo Exercício (Seta Direita)" aria-label="Próximo Exercício">
            <svg class="icon-svg" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
          </button>

          <button class="btn btn-tool" id="btnReset" title="Reiniciar Exercício" aria-label="Reiniciar">
            <svg class="icon-svg" viewBox="0 0 24 24"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
          </button>

          <button class="btn btn-tool" id="btnMute" title="Ativar/Desativar Som de Sino (M)" aria-label="Mutar ou Desmutar">
            <svg class="icon-svg" id="iconSound" viewBox="0 0 24 24"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>
          </button>
        </div>

      </div>

      <!-- Global Routine Timeline Progress -->
      <div class="global-progress">
        <div class="global-progress-bar" id="globalProgressBar"></div>
      </div>
    </section>

    <!-- Exercise Steps List -->
    <main>
      <div class="section-header-bar">
        <div>
          <h2 class="section-heading">Sequência Completa de Exercícios</h2>
          <p class="section-subtext">Todas as seções originais: <strong>Instructions</strong>, <strong>Tips</strong>, <strong>Modifications</strong> e <strong>Benefits</strong></p>
        </div>
        <button type="button" class="btn btn-toggle-all" id="btnToggleAll" onclick="toggleAllDetails()">
          <span id="toggleAllIcon">▲</span>
          <span id="toggleAllText">Recolher Todos</span>
        </button>
      </div>

      <div class="card-list" id="cardListContainer">
        {static_cards_html}
      </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p>Base de dados enriquecida via bend.com • Desenvolvido com carinho para bem-estar e mobilidade funcional.</p>
    </footer>

  </div>

  <!-- Raw Data JSON Script -->
  <script id="routineData" type="application/json">
{json.dumps(data_payload, ensure_ascii=False, indent=2)}
  </script>

  <script>
    // --- Parse Data ---
    const RAW_DATA = JSON.parse(document.getElementById('routineData').textContent);
    const steps = RAW_DATA.steps;
    const variants = RAW_DATA.variants;

    // --- State Variables ---
    let currentStepIndex = 0;
    let areAllExpanded = true;
    let selectedVariants = {{}}; // stepId -> variantName
    steps.forEach(s => {{
      selectedVariants[s.id] = s.default_variant;
    }});

    let timerInterval = null;
    let isPlaying = false;
    let timeRemaining = 0;
    let currentTotalTime = 0;
    let isSideTwo = false; // false = Lado 1 (Esquerdo), true = Lado 2 (Direito)
    let isMuted = false;

    // --- Web Audio Synthesizer (Zero External Dependencies) ---
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    let audioCtx = null;

    function getAudioContext() {{
      if (!audioCtx) {{
        audioCtx = new AudioContextClass();
      }}
      if (audioCtx.state === 'suspended') {{
        audioCtx.resume();
      }}
      return audioCtx;
    }}

    // Play singing bowl / harmonic chime
    function playChime(freqs = [528, 792, 1056], duration = 1.2, volume = 0.25) {{
      if (isMuted) return;
      try {{
        const ctx = getAudioContext();
        const now = ctx.currentTime;
        
        freqs.forEach(f => {{
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          
          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, now);
          
          gain.gain.setValueAtTime(volume / freqs.length, now);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
          
          osc.connect(gain);
          gain.connect(ctx.destination);
          
          osc.start(now);
          osc.stop(now + duration);
        }});
      }} catch (e) {{
        console.warn("Audio chime prevented by browser autoplay policy", e);
      }}
    }}

    // Double chime for side switch
    function playSideSwitchSound() {{
      playChime([660, 880], 0.8, 0.3);
      setTimeout(() => {{
        playChime([880, 1320], 1.2, 0.35);
      }}, 150);
    }}

    // Triple celebratory chime on completion
    function playCompletionSound() {{
      playChime([528, 660, 792], 0.9, 0.3);
      setTimeout(() => playChime([660, 792, 990], 1.1, 0.3), 200);
      setTimeout(() => playChime([792, 990, 1320], 1.8, 0.4), 450);
    }}

    // --- Format Seconds into MM:SS ---
    function formatTime(sec) {{
      const m = Math.floor(sec / 60);
      const s = sec % 60;
      return `${{m.toString().padStart(2, '0')}}:${{s.toString().padStart(2, '0')}}`;
    }}

    // --- Render Exercise Cards ---
    const container = document.getElementById('cardListContainer');

    function renderCards() {{
      container.innerHTML = '';
      steps.forEach((step, idx) => {{
        const currentVariantName = selectedVariants[step.id];
        const vData = variants[currentVariantName] || {{}};

        const card = document.createElement('article');
        card.className = `exercise-card ${{idx === currentStepIndex ? 'is-active' : ''}}`;
        card.id = `card-step-${{step.id}}`;

        // Calculate card duration string
        let durationStr = `${{step.default_duration}} s`;
        if (step.is_bilateral) {{
          durationStr = `${{step.default_duration}} s (${{step.side_duration}} s / lado)`;
        }} else if (currentVariantName === 'Hurdler') {{
          durationStr = '60 s (30 s / lado)';
        }}

        // Variant selector buttons if multiple variants
        let variantButtonsHtml = '';
        if (step.variants.length > 1) {{
          variantButtonsHtml = `
            <div class="variant-selector">
              <span class="variant-label">Variação:</span>
              ${{step.variants.map(v => `
                <button type="button" class="variant-btn ${{v === currentVariantName ? 'selected' : ''}}" 
                  onclick="selectVariant(${{step.id}}, '${{v}}', event)">
                  ${{v}}
                </button>
              `).join('')}}
            </div>
          `;
        }}

        // Warning Box
        const warningHtml = step.warning ? `
          <div class="warning-box">
            <svg class="icon-svg" style="flex-shrink: 0; margin-top: 2px;" viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>
            <div>${{step.warning}}</div>
          </div>
        ` : '';

        // 1. Benefits (ALL benefits - unconstrained)
        const allBenefits = vData.benefits || [];
        const benefitsHtml = allBenefits.length > 0 
          ? allBenefits.map(b => `<span class="benefit-tag">${{b}}</span>`).join('')
          : '<span class="empty-note">Nenhum benefício listado</span>';

        // 2. Instructions (ALL instructions)
        const allInstructions = vData.instructions || [];
        const instructionsHtml = allInstructions.length > 0
          ? allInstructions.map(inst => `<li>${{inst}}</li>`).join('')
          : '<li class="empty-note">Instruções não disponíveis</li>';

        // 3. Tips (ALL tips)
        const allTips = vData.tips || [];
        const tipsHtml = allTips.length > 0
          ? allTips.map(tip => `<li>${{tip}}</li>`).join('')
          : '<li class="empty-note">Mantenha respiração ritmada e postura firme sem forçar articulações.</li>';

        // 4. Modifications (ALL modifications)
        const allMods = vData.modifications || [];
        const modsHtml = allMods.length > 0
          ? allMods.map(mod => `<li>${{mod}}</li>`).join('')
          : '<li class="empty-note">Sem modificações adicionais necessárias para esta postura (ajuste a amplitude de acordo com o seu conforto).</li>';

        card.innerHTML = `
          <div class="card-top">
            <div class="card-thumb-wrap">
              <img id="img-${{step.id}}" src="${{vData.image_url}}" alt="${{vData.alt_text}}" loading="lazy" />
            </div>

            <div class="card-body">
              <div class="card-header-row">
                <span class="step-number">#${{step.id}}</span>
                <h3 class="card-title" id="title-${{step.id}}">${{vData.name}}</h3>
                <span class="duration-badge">
                  <svg class="icon-svg" viewBox="0 0 24 24"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
                  ${{durationStr}}
                </span>
              </div>

              <div class="user-purpose">${{step.user_note}}</div>

              ${{variantButtonsHtml}}

              ${{warningHtml}}
            </div>

            <div class="card-actions">
              <button type="button" class="btn-jump" onclick="jumpToStep(${{idx}})" aria-label="Iniciar a partir deste exercício">
                <svg class="icon-svg" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                Começar
              </button>

              <button type="button" class="btn-details" onclick="toggleDetails(${{step.id}})" aria-label="Alternar visualização das instruções">
                <span id="btn-text-${{step.id}}">${{areAllExpanded ? 'Ocultar detalhes' : 'Ver detalhes'}}</span>
                <svg class="icon-svg" id="chevron-${{step.id}}" style="transform: ${{areAllExpanded ? 'rotate(180deg)' : 'rotate(0deg)'}};" viewBox="0 0 24 24"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>
              </button>
            </div>
          </div>

          <!-- All 4 Sections: Benefits, Instructions, Tips, Modifications -->
          <div class="card-details ${{areAllExpanded ? '' : 'collapsed'}}" id="details-${{step.id}}">
            
            <!-- Section 1: Benefits -->
            <div class="benefits-section">
              <h4 class="section-label label-benefits">
                <svg class="icon-svg" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
                <span>Benefits</span>
                <span class="section-count">(${{allBenefits.length}} regiões beneficiadas)</span>
              </h4>
              <div class="benefits-chips-wrap" id="benefits-${{step.id}}">
                ${{benefitsHtml}}
              </div>
            </div>

            <!-- Grid for Instructions, Tips, Modifications -->
            <div class="details-grid">
              
              <!-- Section 2: Instructions -->
              <div class="detail-col instructions-col">
                <h4 class="section-label label-instructions">
                  <svg class="icon-svg" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
                  <span>Instructions</span>
                  <span class="section-count">(${{allInstructions.length}} passos)</span>
                </h4>
                <ol class="instructions-list" id="instructions-${{step.id}}">
                  ${{instructionsHtml}}
                </ol>
              </div>
              
              <!-- Section 3: Tips -->
              <div class="detail-col tips-col">
                <h4 class="section-label label-tips">
                  <svg class="icon-svg" viewBox="0 0 24 24"><path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z"/></svg>
                  <span>Tips</span>
                  <span class="section-count">(${{allTips.length}} dicas)</span>
                </h4>
                <ul class="tips-list" id="tips-${{step.id}}">
                  ${{tipsHtml}}
                </ul>
              </div>

              <!-- Section 4: Modifications -->
              <div class="detail-col mods-col">
                <h4 class="section-label label-mods">
                  <svg class="icon-svg" viewBox="0 0 24 24"><path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/></svg>
                  <span>Modifications</span>
                  <span class="section-count">(${{allMods.length}} ajustes)</span>
                </h4>
                <ul class="mods-list" id="mods-${{step.id}}">
                  ${{modsHtml}}
                </ul>
              </div>

            </div>
          </div>
        `;

        container.appendChild(card);
      }});
    }}

    // Toggle Details Accordion on individual card
    window.toggleDetails = function(stepId) {{
      const el = document.getElementById(`details-${{stepId}}`);
      const chevron = document.getElementById(`chevron-${{stepId}}`);
      const btnText = document.getElementById(`btn-text-${{stepId}}`);
      if (el) {{
        el.classList.toggle('collapsed');
        const isNowCollapsed = el.classList.contains('collapsed');
        if (chevron) {{
          chevron.style.transform = isNowCollapsed ? 'rotate(0deg)' : 'rotate(180deg)';
        }}
        if (btnText) {{
          btnText.textContent = isNowCollapsed ? 'Ver detalhes' : 'Ocultar detalhes';
        }}
      }}
    }};

    // Global Toggle All Cards
    window.toggleAllDetails = function() {{
      areAllExpanded = !areAllExpanded;
      const detailsList = document.querySelectorAll('.card-details');
      const toggleText = document.getElementById('toggleAllText');
      const toggleIcon = document.getElementById('toggleAllIcon');

      detailsList.forEach(el => {{
        if (areAllExpanded) {{
          el.classList.remove('collapsed');
        }} else {{
          el.classList.add('collapsed');
        }}
      }});

      document.querySelectorAll('[id^="chevron-"]').forEach(ch => {{
        ch.style.transform = areAllExpanded ? 'rotate(180deg)' : 'rotate(0deg)';
      }});

      document.querySelectorAll('[id^="btn-text-"]').forEach(bt => {{
        bt.textContent = areAllExpanded ? 'Ocultar detalhes' : 'Ver detalhes';
      }});

      if (toggleText && toggleIcon) {{
        toggleText.textContent = areAllExpanded ? 'Recolher Todos' : 'Expandir Todos';
        toggleIcon.textContent = areAllExpanded ? '▲' : '▼';
      }}
    }};

    // Switch Variation
    window.selectVariant = function(stepId, variantName, event) {{
      if (event) event.stopPropagation();
      selectedVariants[stepId] = variantName;
      
      const stepIndex = steps.findIndex(s => s.id === stepId);
      renderCards();

      if (stepIndex === currentStepIndex) {{
        initStep(currentStepIndex, false);
      }}
    }};

    // --- Player Logic ---
    function isStepBilateral(step) {{
      const variantName = selectedVariants[step.id];
      if (variantName === 'Hurdler') return true;
      return step.is_bilateral;
    }}

    function getStepDuration(step) {{
      const variantName = selectedVariants[step.id];
      if (variantName === 'Hurdler') return 60;
      return step.default_duration;
    }}

    function getSideDuration(step) {{
      const variantName = selectedVariants[step.id];
      if (variantName === 'Hurdler') return 30;
      return step.side_duration;
    }}

    function initStep(stepIdx, autoPlay = false) {{
      currentStepIndex = stepIdx;
      const step = steps[currentStepIndex];
      const variantName = selectedVariants[step.id];
      const vData = variants[variantName] || {{}};

      const bilateral = isStepBilateral(step);
      isSideTwo = false;

      if (bilateral) {{
        const sDur = getSideDuration(step);
        currentTotalTime = sDur;
        timeRemaining = sDur;
      }} else {{
        const totalDur = getStepDuration(step);
        currentTotalTime = totalDur;
        timeRemaining = totalDur;
      }}

      updatePlayerUI();
      highlightActiveCard();

      if (autoPlay) {{
        startTimer();
      }} else {{
        pauseTimer();
      }}
    }}

    function highlightActiveCard() {{
      document.querySelectorAll('.exercise-card').forEach((c, idx) => {{
        if (idx === currentStepIndex) {{
          c.classList.add('is-active');
        }} else {{
          c.classList.remove('is-active');
        }}
      }});
      
      // Smooth scroll into view gently if needed
      const activeCard = document.getElementById(`card-step-${{steps[currentStepIndex].id}}`);
      if (activeCard) {{
        activeCard.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}
    }}

    function updatePlayerUI() {{
      const step = steps[currentStepIndex];
      const variantName = selectedVariants[step.id];
      const vData = variants[variantName] || {{}};
      const bilateral = isStepBilateral(step);

      // Titles and Tags
      document.getElementById('activeStepTag').textContent = `Passo ${{step.id}} de ${{steps.length}}`;
      document.getElementById('activeTitle').textContent = vData.name || step.title;
      document.getElementById('activeFocus').textContent = step.user_note;

      // Side badge
      const sideBadge = document.getElementById('activeSideBadge');
      if (bilateral) {{
        sideBadge.style.display = 'inline-flex';
        if (!isSideTwo) {{
          sideBadge.textContent = 'Lado Esquerdo';
          sideBadge.className = 'side-badge';
        }} else {{
          sideBadge.textContent = 'Lado Direito';
          sideBadge.className = 'side-badge side-right';
        }}
      }} else {{
        sideBadge.style.display = 'none';
      }}

      // Timer Text
      document.getElementById('timerDisplay').textContent = formatTime(timeRemaining);

      // Circular Ring Progress
      const circle = document.getElementById('timerCircle');
      const circumference = 2 * Math.PI * 36; // ~226.19
      const fraction = currentTotalTime > 0 ? (timeRemaining / currentTotalTime) : 0;
      const offset = circumference * (1 - fraction);
      circle.style.strokeDashoffset = offset;

      // Global Routine Timeline Progress
      const globalBar = document.getElementById('globalProgressBar');
      const pct = ((currentStepIndex + (1 - fraction)) / steps.length) * 100;
      globalBar.style.width = `${{Math.min(100, Math.max(0, pct))}}%`;
    }}

    function startTimer() {{
      if (timerInterval) clearInterval(timerInterval);
      isPlaying = true;
      getAudioContext(); // user gesture unlock
      playChime([528, 792], 0.4, 0.2);

      updatePlayPauseButton();

      timerInterval = setInterval(() => {{
        if (timeRemaining > 0) {{
          timeRemaining--;
          updatePlayerUI();
        }} else {{
          // Time expired for this segment!
          const step = steps[currentStepIndex];
          const bilateral = isStepBilateral(step);

          if (bilateral && !isSideTwo) {{
            // Switch to Right Side
            isSideTwo = true;
            const sDur = getSideDuration(step);
            currentTotalTime = sDur;
            timeRemaining = sDur;
            playSideSwitchSound();
            updatePlayerUI();
          }} else {{
            // Exercise complete! Advance to next step
            if (currentStepIndex < steps.length - 1) {{
              playChime([660, 880, 1100], 0.8, 0.3);
              initStep(currentStepIndex + 1, true);
            }} else {{
              // Routine finished!
              pauseTimer();
              playCompletionSound();
              alert("🎉 Parabéns! Você concluiu a rotina completa de alongamento e mobilidade!");
            }}
          }}
        }}
      }}, 1000);
    }}

    function pauseTimer() {{
      if (timerInterval) clearInterval(timerInterval);
      timerInterval = null;
      isPlaying = false;
      updatePlayPauseButton();
    }}

    function togglePlayPause() {{
      if (isPlaying) {{
        pauseTimer();
      }} else {{
        startTimer();
      }}
    }}

    function updatePlayPauseButton() {{
      const icon = document.getElementById('iconPlayPause');
      if (isPlaying) {{
        // Pause icon
        icon.innerHTML = '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>';
      }} else {{
        // Play icon
        icon.innerHTML = '<path d="M8 5v14l11-7z"/>';
      }}
    }}

    window.jumpToStep = function(stepIdx) {{
      initStep(stepIdx, true);
    }};

    // Next / Prev handlers
    document.getElementById('btnPrev').addEventListener('click', () => {{
      if (currentStepIndex > 0) {{
        initStep(currentStepIndex - 1, isPlaying);
      }}
    }});

    document.getElementById('btnNext').addEventListener('click', () => {{
      if (currentStepIndex < steps.length - 1) {{
        initStep(currentStepIndex + 1, isPlaying);
      }}
    }});

    document.getElementById('btnPlayPause').addEventListener('click', togglePlayPause);

    document.getElementById('btnReset').addEventListener('click', () => {{
      initStep(currentStepIndex, false);
    }});

    // Mute toggle
    document.getElementById('btnMute').addEventListener('click', () => {{
      isMuted = !isMuted;
      const icon = document.getElementById('iconSound');
      if (isMuted) {{
        icon.innerHTML = '<path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>';
      }} else {{
        icon.innerHTML = '<path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>';
      }}
    }});

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {{
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.code === 'Space') {{
        e.preventDefault();
        togglePlayPause();
      }} else if (e.code === 'ArrowRight') {{
        e.preventDefault();
        if (currentStepIndex < steps.length - 1) initStep(currentStepIndex + 1, isPlaying);
      }} else if (e.code === 'ArrowLeft') {{
        e.preventDefault();
        if (currentStepIndex > 0) initStep(currentStepIndex - 1, isPlaying);
      }} else if (e.key === 'm' || e.key === 'M') {{
        document.getElementById('btnMute').click();
      }}
    }});

    // Initial render and step setup
    renderCards();
    initStep(0, false);
  </script>
</body>
</html>
"""

with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✓ Successfully regenerated {OUTPUT_HTML_PATH} ({len(html_content)} bytes)")
