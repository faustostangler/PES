"""AI Wiki Compiler - Four-Pass LLM Processor for newspaper synthesis, structured extraction, standardization, merging, and scoped grep updates."""

import json
import re
import time
from datetime import UTC, datetime, timezone
from pathlib import Path

import httpx
# pyrefly: ignore [missing-import]
from helper import clean_filename

# ==================== PASS 1 PROMPTS ====================
NEWSPAPER_SYSTEM_PROMPT = """You are a professional technical writer writing for a premium, high-impact technical book.
Your job is to read the raw text and compile it into a highly structured technical book chapter. Include all information from the transcription in a logical structured chapter technical text.

## General Writing Rules
1. Think critically before writing and declare premises explicitly.
2. Write the most concise and impactful text possible.
3. Strictly adhere to the established structure.
4. Avoid redundancy and unnecessary information.
5. Use clear, direct, and unambiguous language.

Your output must be structured in a logical, technical, well-organized manner. Include these sections:

# Metadata & Context: 
## Title: direct and clear title. 
## Learning Objectives: 3-5 bullet points of what the reader will learn from this content. 
## Executive Summary: The Core Thesis in a phrase. And a concise summary of the content. From a single line up to 2 paragraphs. 

# Content/Body Paragraphs: Deep-Dive Analysis & Structural Breakdown
Component/Argument Breakdown: Detailed information provided in logical order. If available, consider Mechanics & Workflows, Comparative Constraints, Strategic Pitfalls & Anti-Patterns

# Conclusion
The broader impact on the landscape or upcoming events. If possible, consider Strategic Takeaways, and Open Threads. 

Language Rule: Write the article in the same language as the original text (e.g. Portuguese for a Portuguese, English for English) to preserve ubiquitous terminology.
Output ONLY the markdown article with the headers specified. Do NOT wrap it in markdown code blocks (no ```markdown or ```) and do not output any conversational introduction.
"""

# ==================== PASS 2 PROMPTS ====================
EXTRACTION_SYSTEM_PROMPT = """You are a highly efficient knowledge compiler implementing the "Karpathy Method" for note-taking in an Obsidian wiki.
Your job is to read a structured document representing a video (a newspaper article or transcript) and extract structured insights in JSON format.

Output ONLY a valid JSON object. Do NOT wrap it in code blocks (no ```json or ```). Do NOT output any conversational text.

Your output JSON must strictly follow this schema:
{
  "summary": "A concise 1-2 sentence summary of the video to be injected into metadata.",
  "takeaways": [
    "Key takeaway/argument/fact 1",
    "Key takeaway/argument/fact 2"
  ],
  "synthesis": "The content logically reorganized, expanded, and rewritten into a well-structured, cohesive article with appropriate markdown headers, bullet points, and paragraphs.",
  "concepts": [
    {"name": "Concept Name", "explanation": "Brief explanation of this concept/topic as mentioned in the video."}
  ],
  "people": [
    {"name": "Person Name", "context": "Who this person is and their role/actions as mentioned in the video."}
  ],
  "organizations": [
    {"name": "Organization Name", "context": "What this organization/group is and their role/actions as mentioned in the video."}
  ],
  "examples": [
    {"name": "Example/Case Name", "description": "Details of the case study, demonstration, or event mentioned."}
  ],
  "skills": [
    {"name": "Skill Name", "description": "Practical skill, tool, method, command, or technique demonstrated or discussed in the video."}
  ],
  "references": [
    {"name": "Resource Name", "context": "Article, book, paper, url, document, or site referenced in the video."}
  ]
}

Language Rule: Identify the language of the document. Write the values of the JSON fields (summary, takeaways, synthesis, explanation, context, description) in the same language as the document (e.g. Portuguese for a Portuguese document, English for English) to preserve ubiquitous terminology. The JSON keys themselves must remain in English as shown in the schema.
"""

# ==================== PASS 3 PROMPTS ====================
STANDARDIZATION_SYSTEM_PROMPT = """You are an expert knowledge curator standardizing entities in an Obsidian vault (following the Karpathy Method).
Your job is to map newly extracted raw entities to existing note names to prevent duplicates and maintain a clean, standardized graph.

We have the following list of existing notes in our vault:
[{existing_notes_list}]

You will receive a list of newly extracted raw entities. For each entity, decide whether it refers to an existing note in the list.
- If it matches an existing note (e.g. "Trump" matches "Donald Trump", "Moraes" matches "Alexandre de Moraes", or spelling variations/abbreviations), map the sanitized name to the exact existing note name.
- If it is a new entity that doesn't match any existing note, standardize it to a clean, proper name (capitalized, corrected spelling, safe for filenames).

Output ONLY a valid JSON object. Do NOT wrap it in code blocks (no ```json or ```). Do NOT output any conversational text.

Your output JSON must strictly follow this schema:
{{
  "concepts": [
    {{"original_name": "Raw Name", "sanitized_name": "Standardized Name", "explanation": "Brief explanation of this concept."}}
  ],
  "people": [
    {{"original_name": "Raw Name", "sanitized_name": "Standardized Name", "context": "Who this person is."}}
  ],
  "organizations": [
    {{"original_name": "Raw Name", "sanitized_name": "Standardized Name", "context": "What this organization is."}}
  ],
  "examples": [
    {{"original_name": "Raw Name", "sanitized_name": "Standardized Name", "description": "Details of the example."}}
  ]
}}
"""

# ==================== PASS 4 PROMPTS ====================
UPDATE_SYSTEM_PROMPT = """Você é um integrador de conhecimento operando sob o Método Karpathy (LLM Wiki).
Você recebeu uma nota antiga do Obsidian e novas informações sobre o mesmo tema.
Sua missão é mesclar as duas informações em um único arquivo Markdown harmonioso.
Não apague dados históricos, apenas organize os novos pontos nos subtópicos corretos ou crie uma nova seção de 'Atualizações', além de apontar contradições e fortalecer referências cruzadas.

--- DIRETRIZES DE LINKS E CONTEXTO ---
Atualmente, a nossa enciclopédia possui as seguintes notas gravadas:
[{existing_notes_list}]

Regras cruciais de backlinks:
1. Sempre que o texto fizer referência direta ou indireta a qualquer um dos conceitos listados acima, você DEVE envolver a palavra/termo em colchetes duplos (ex: [[Nome Exato do Conceito]]).
2. Se você identificar um novo conceito fundamental, você pode criar backlinks para ele (ex: [[Novo Conceito]]). Seja criterioso.

--- NOTA ANTIGA ---
{existing_content}

--- NOVAS INFORMAÇÕES ---
{new_info_context}

Retorne apenas o Markdown final combinado. Do NOT wrap it in markdown code blocks (no ```markdown or ```) and do not output any conversational introduction.
"""

CREATE_SYSTEM_PROMPT = """Você é um agente organizador de conhecimento focado no método LLM Wiki do Karpathy.
Sua tarefa é ler as informações fornecidas sobre um conceito/entidade e gerar uma nova página estruturada em Markdown.

--- DIRETRIZES DE LINKS E CONTEXTO ---
Atualmente, a nossa enciclopédia possui as seguintes notas gravadas:
[{existing_notes_list}]

Regras cruciais:
1. Organize a página de forma limpa e estruturada usando cabeçalhos markdown.
2. Identifique termos ou conceitos no texto que fazem parte da lista de notas existentes acima e garanta que eles tenham backlinks usando a sintaxe clássica do Obsidian: [[Nome Exato do Conceito]].
3. Se você identificar um novo conceito fundamental, você pode propor um novo link como [[Novo Conceito]]. Seja criterioso.
4. Retorne APENAS o código Markdown limpo, sem introduções, sem explicações e sem blocos de código extras (não use ```markdown).

--- INFORMAÇÕES DO CONCEITO ---
{info_context}
"""

REFERENCE_UPDATE_SYSTEM_PROMPT = """Você é um integrador de conhecimento operando sob o Método Karpathy (LLM Wiki).
Você recebeu uma nota do Obsidian e a descrição de uma entidade de referência.
Sua missão é atualizar o conteúdo da nota para garantir que a entidade esteja corretamente referenciada usando backlinks do Obsidian (ex: [[{entity_name}]]).
Se a nota já menciona a entidade, garanta que ela esteja envolvida em colchetes duplos.
Você também pode enriquecer o parágrafo ou subtópico da nota com detalhes curtos do contexto fornecido, se relevante.

--- CONTEÚDO ATUAL DA NOTA ---
{file_content}

--- ENTIDADE DE REFERÊNCIA ---
Nome: {entity_name}
Contexto da Entidade: {entity_context}

--- CONTEXTO DO NOVO DOCUMENTO (RAW) ---
{raw_context}

Retorne apenas o Markdown final atualizado. Do NOT wrap it in markdown code blocks (no ```markdown or ```) and do not output any conversational introduction.
"""


# ==================== HELPERS ====================
def extract_json_from_response(response_text: str) -> dict:
    """Clean and parse JSON from the LLM response, stripping code blocks if present."""
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r'^```(?:json)?\n', '', text)
        text = re.sub(r'\n```$', '', text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        raise ValueError("Could not parse valid JSON from LLM response.")


def get_ollama_generate(prompt: str, system: str, model: str, ollama_url: str, response_format: str | None = None) -> str:
    """Send generation request to Ollama and return the text response."""
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {
            "temperature": 0.2,
        }
    }
    if response_format:
        payload["format"] = response_format

    headers = {"Content-Type": "application/json"}
    api_url = f"{ollama_url.rstrip('/')}/api/generate"

    start_time = time.time()
    with httpx.Client(timeout=None) as client:
        response = client.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        duration = time.time() - start_time
        res = response.json()

        # Token and performance stats extraction
        eval_count = res.get("eval_count", 0)
        eval_duration_ns = res.get("eval_duration", 0)
        prompt_eval_count = res.get("prompt_eval_count", 0)
        prompt_eval_duration_ns = res.get("prompt_eval_duration", 0)
        total_duration_ns = res.get("total_duration", 0)
        load_duration_ns = res.get("load_duration", 0)

        # Convert ns to seconds
        eval_dur = eval_duration_ns / 1e9 if eval_duration_ns else 0
        prompt_dur = prompt_eval_duration_ns / 1e9 if prompt_eval_duration_ns else 0
        total_dur = total_duration_ns / 1e9 if total_duration_ns else 0
        load_dur = load_duration_ns / 1e9 if load_duration_ns else 0

        eval_tps = eval_count / eval_dur if eval_dur > 0 else 0
        prompt_tps = prompt_eval_count / prompt_dur if prompt_dur > 0 else 0

        print(f"      [Ollama API Stats]")
        print(f"        - Model: {model}")
        print(f"        - Total Duration: {total_dur:.2f}s (Load: {load_dur:.2f}s, Process Wall Time: {duration:.2f}s)")
        print(f"        - Prompt: {prompt_eval_count} tokens | Duration: {prompt_dur:.2f}s | Speed: {prompt_tps:.2f} t/s")
        print(f"        - Generation: {eval_count} tokens | Duration: {eval_dur:.2f}s | Speed: {eval_tps:.2f} t/s")

        return res.get("response", "").strip()


def get_existing_notes(wiki_dir: Path) -> list:
    """Scan all subdirectories of wiki_dir and collect the stems of all markdown notes (excluding index and log)."""
    if not wiki_dir.exists():
        return []
    notes = []
    for file_path in wiki_dir.rglob("*.md"):
        stem = file_path.stem
        if stem.lower() not in ["index", "log"]:
            notes.append(stem)
    return sorted(set(notes))


def regenerate_global_index(wiki_dir: Path) -> None:
    """Scan the wiki subdirectories and programmatically regenerate index.md."""
    index_path = wiki_dir / "index.md"
    print(f"Regenerating global index: {index_path.name}")

    categories = {
        "sources": "Sources (Transcripts & Summaries)",
        "concepts": "Concepts & Topics",
        "people": "People & Citations",
        "organizations": "Organizations & Groups",
        "examples": "Examples & Case Studies"
    }

    content = "# Wiki Index\n\nWelcome to your Intelligent Second Brain. Below is the automated map of all ingested knowledge.\n\n"

    for folder_name, title in categories.items():
        folder_path = wiki_dir / folder_name
        content += f"## {title}\n"
        if folder_path.exists():
            files = sorted(folder_path.glob("*.md"))
            if files:
                for file in files:
                    basename = file.stem
                    content += f"- [[{folder_name}/{basename}|{basename}]]\n"
            else:
                content += "_No entries yet._\n"
        else:
            content += "_No entries yet._\n"
        content += "\n"

    try:
        with index_path.open("w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Warning: Failed to regenerate index: {e}")


# ==================== PASS 1: NEWSPAPER ARTICLE GENERATION ====================
def run_pass1_chunked_newspaper(title: str, transcript_text: str, model: str, ollama_url: str, chunk_size: int, overlap: int) -> str:
    """Generate a newspaper article from a long transcript by processing it in overlapping chunks and merging them."""
    print(f"  [Phase 1: Article Generator] Generating newspaper article in overlapping chunks of {chunk_size} characters for tiny model '{model}'...")

    chunks = []
    start = 0
    step = chunk_size - overlap
    while start < len(transcript_text):
        end = start + chunk_size
        chunks.append(transcript_text[start:end])
        if end >= len(transcript_text):
            break
        start += step

    chunk_drafts = []
    for idx, chunk in enumerate(chunks):
        print(f"    Drafting chunk {idx + 1}/{len(chunks)} ({len(chunk)} chars)...")
        user_prompt = f"Transcript for Video '{title}' (Part {idx + 1}/{len(chunks)}):\n\n{chunk}"
        try:
            draft = get_ollama_generate(user_prompt, NEWSPAPER_SYSTEM_PROMPT, model, ollama_url)
            if draft.strip():
                chunk_drafts.append(draft.strip())
        except Exception as e:
            print(f"    Warning: Failed to draft chunk {idx + 1}: {e}")
            continue

    if not chunk_drafts:
        return "No newspaper article draft generated."

    print("    Merging chunk drafts into final newspaper article...")
    combined_drafts = "\n\n=== NEXT CHUNK DRAFT ===\n\n".join(chunk_drafts)
    merge_prompt = f"Here are the draft newspaper articles for different parts of the video '{title}'. Merge them into a single, cohesive, professional newspaper article following the inverted pyramid style.\n\nDrafts:\n{combined_drafts}"
    return get_ollama_generate(merge_prompt, NEWSPAPER_SYSTEM_PROMPT, model, ollama_url)


def run_pass1_newspaper(title: str, transcript_text: str, model: str, ollama_url: str) -> str:
    """Pass 1: Generate a newspaper article, inverted-pyramid-style structured document from the original transcript."""
    is_tiny = "270m" in model or "gemma3" in model
    chunk_size = 3500
    overlap = 500

    if is_tiny and len(transcript_text) > chunk_size:
        return run_pass1_chunked_newspaper(title, transcript_text, model, ollama_url, chunk_size, overlap)
    else:
        print("  [Phase 1: Article Generator] Generating newspaper article using NEWSPAPER_SYSTEM_PROMPT...")
        user_prompt = f"Transcript for Video '{title}':\n\n{transcript_text}"
        return get_ollama_generate(user_prompt, NEWSPAPER_SYSTEM_PROMPT, model, ollama_url)


# ==================== PASS 2: EXTRACTION ====================
def run_pass2_chunked_extraction(title: str, text_to_process: str, model: str, ollama_url: str, chunk_size: int, overlap: int) -> dict:
    """Extract and merge insights from a long document by processing it in overlapping chunks."""
    print(f"  [Pass 2] Processing document in overlapping chunks of {chunk_size} characters for tiny model '{model}'...")

    chunks = []
    start = 0
    step = chunk_size - overlap
    while start < len(text_to_process):
        end = start + chunk_size
        chunks.append(text_to_process[start:end])
        if end >= len(text_to_process):
            break
        start += step

    merged_results = {
        "summary": "",
        "takeaways": [],
        "synthesis": "",
        "concepts": [],
        "people": [],
        "organizations": [],
        "examples": [],
        "skills": [],
        "references": []
    }

    summaries = []
    syntheses = []
    seen_takeaways = set()
    seen_concepts = {}
    seen_people = {}
    seen_organizations = {}
    seen_examples = {}
    seen_skills = {}
    seen_references = {}

    for idx, chunk in enumerate(chunks):
        print(f"    Processing chunk {idx + 1}/{len(chunks)} ({len(chunk)} chars)...")
        user_prompt = f"Document for Video '{title}' (Part {idx + 1}/{len(chunks)}):\n\n{chunk}"
        try:
            raw_response = get_ollama_generate(user_prompt, EXTRACTION_SYSTEM_PROMPT, model, ollama_url, response_format="json")
            res = extract_json_from_response(raw_response)
        except Exception as e:
            print(f"    Warning: Failed to extract from chunk {idx + 1}: {e}")
            continue

        # Merge fields
        summary = res.get("summary", "").strip()
        if summary:
            summaries.append(summary)

        synth_chunk = res.get("synthesis", "").strip()
        if synth_chunk:
            syntheses.append(synth_chunk)

        for t in res.get("takeaways", []):
            t_clean = t.strip()
            if not t_clean:
                continue
            if t_clean in seen_takeaways:
                continue
            seen_takeaways.add(t_clean)
            merged_results["takeaways"].append(t_clean)

        for item in res.get("concepts", []):
            name = item.get("name", "").strip()
            explanation = item.get("explanation", "").strip()
            if not name:
                continue
            if not explanation:
                continue
            name_lower = name.lower()
            if name_lower in seen_concepts:
                continue
            seen_concepts[name_lower] = item
            merged_results["concepts"].append(item)

        for item in res.get("people", []):
            name = item.get("name", "").strip()
            context = item.get("context", "").strip()
            if not name:
                continue
            if not context:
                continue
            name_lower = name.lower()
            if name_lower in seen_people:
                continue
            seen_people[name_lower] = item
            merged_results["people"].append(item)

        for item in res.get("organizations", []):
            name = item.get("name", "").strip()
            context = item.get("context", "").strip()
            if not name:
                continue
            if not context:
                continue
            name_lower = name.lower()
            if name_lower in seen_organizations:
                continue
            seen_organizations[name_lower] = item
            merged_results["organizations"].append(item)

        for item in res.get("examples", []):
            name = item.get("name", "").strip()
            description = item.get("description", "").strip()
            if not name:
                continue
            if not description:
                continue
            name_lower = name.lower()
            if name_lower in seen_examples:
                continue
            seen_examples[name_lower] = item
            merged_results["examples"].append(item)

        for item in res.get("skills", []):
            name = item.get("name", "").strip()
            description = item.get("description", "").strip()
            if not name:
                continue
            if not description:
                continue
            name_lower = name.lower()
            if name_lower in seen_skills:
                continue
            seen_skills[name_lower] = item
            merged_results["skills"].append(item)

        for item in res.get("references", []):
            name = item.get("name", "").strip()
            context = item.get("context", "").strip()
            if not name:
                continue
            if not context:
                continue
            name_lower = name.lower()
            if name_lower in seen_references:
                continue
            seen_references[name_lower] = item
            merged_results["references"].append(item)

    merged_results["summary"] = " ".join(summaries)
    merged_results["synthesis"] = "\n\n".join(syntheses)
    return merged_results


def run_pass2_extraction(title: str, text_to_process: str, model: str, ollama_url: str) -> dict:
    """Pass 2: Extract core raw concepts, takeaways, entities, and summary from document text."""
    is_tiny = "270m" in model or "gemma3" in model
    chunk_size = 3500
    overlap = 500

    if is_tiny and len(text_to_process) > chunk_size:
        return run_pass2_chunked_extraction(title, text_to_process, model, ollama_url, chunk_size, overlap)
    else:
        print("  [Pass 2] Extracting raw entities from document...")
        user_prompt = f"Document for Video '{title}':\n\n{text_to_process}"
        raw_response = get_ollama_generate(user_prompt, EXTRACTION_SYSTEM_PROMPT, model, ollama_url, response_format="json")
        return extract_json_from_response(raw_response)


# ==================== PASS 3: STANDARDIZATION ====================
def run_pass3_standardization(raw_entities: dict, existing_notes: list, model: str, ollama_url: str) -> dict:
    """Pass 3: Map newly extracted raw entity names to existing vault note names to enforce consistency."""
    print(f"  [Pass 3] Standardizing raw entities against {len(existing_notes)} existing vault notes...")

    # Prepare list for prompt
    existing_notes_str = ", ".join([f'"{n}"' for n in existing_notes])

    # Structure the raw entities into a simple format for Pass 3 prompt
    payload_entities = {
        "concepts": [{"name": c.get("name"), "explanation": c.get("explanation")} for c in raw_entities.get("concepts", []) if c.get("name")],
        "people": [{"name": p.get("name"), "context": p.get("context")} for p in raw_entities.get("people", []) if p.get("name")],
        "organizations": [{"name": o.get("name"), "context": o.get("context")} for o in raw_entities.get("organizations", []) if o.get("name")],
        "examples": [{"name": e.get("name"), "description": e.get("description")} for e in raw_entities.get("examples", []) if e.get("name")]
    }

    prompt = f"Raw Entities to Standardize:\n{json.dumps(payload_entities, indent=2)}"
    system_prompt = STANDARDIZATION_SYSTEM_PROMPT.format(existing_notes_list=existing_notes_str)

    raw_response = get_ollama_generate(prompt, system_prompt, model, ollama_url, response_format="json")
    standardized_data = extract_json_from_response(raw_response)

    # Filter and clean the standardized data to prevent nulls and empty strings
    sanitized = {"concepts": [], "people": [], "organizations": [], "examples": []}

    for category in ["concepts", "people", "organizations", "examples"]:
        seen = set()
        raw_list = standardized_data.get(category, [])
        if not isinstance(raw_list, list):
            continue
        for item in raw_list:
            if not isinstance(item, dict):
                continue
            orig = item.get("original_name")
            san = item.get("sanitized_name")

            # Use appropriate context key depending on the category
            ctx_key = "explanation" if category == "concepts" else ("description" if category == "examples" else "context")
            ctx_val = item.get(ctx_key)

            if not isinstance(san, str) or not san.strip():
                continue
            if not isinstance(ctx_val, str) or not ctx_val.strip():
                continue
            san_clean = clean_filename(san.strip())
            norm = san_clean.lower()
            if norm in seen:
                continue
            if san_clean.lower() in ["index", "log"]:
                continue
            seen.add(norm)
            sanitized[category].append({
                "original_name": orig.strip() if isinstance(orig, str) else san_clean,
                "sanitized_name": san_clean,
                ctx_key: ctx_val.strip()
            })

    return sanitized


# ==================== PASS 4: INTEGRATION ====================
def create_or_update_entity_note(
    name: str,
    context: str,
    category_folder: Path,
    model: str,
    ollama_url: str,
    wiki_dir: Path
) -> None:
    """Helper to write or merge content into the entity's own note file."""
    category_folder.mkdir(parents=True, exist_ok=True)
    filename = clean_filename(name)
    file_path = category_folder / f"{filename}.md"

    existing_notes = get_existing_notes(wiki_dir)
    existing_notes_str = ", ".join([f'"{c}"' for c in existing_notes])

    if file_path.exists():
        try:
            with file_path.open("r", encoding="utf-8") as f:
                existing_content = f.read().strip()

            print(f"  [Pass 4] Merging new context into existing note: [[{filename}]]")
            new_info = f"Entity Name: {name}\nNew Context: {context}"
            prompt = UPDATE_SYSTEM_PROMPT.format(
                existing_content=existing_content,
                new_info_context=new_info,
                existing_notes_list=existing_notes_str
            )
            updated_content = get_ollama_generate(prompt, "", model, ollama_url)

            with file_path.open("w", encoding="utf-8") as f:
                f.write(updated_content)
        except Exception as e:
            print(f"  Warning: Failed to update note [[{filename}]]: {e}")
    else:
        try:
            print(f"  [Pass 4] Creating new note: [[{filename}]]")
            new_info = f"Entity Name: {name}\nContext: {context}"
            prompt = CREATE_SYSTEM_PROMPT.format(
                info_context=new_info,
                existing_notes_list=existing_notes_str
            )
            content = get_ollama_generate(prompt, "", model, ollama_url)

            with file_path.open("w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"  Warning: Failed to create note [[{filename}]]: {e}")


def save_source_note(
    video_id: str,
    title: str,
    channel: str,
    channel_id: str,
    upload_date: str,
    summary: str,
    takeaways: list,
    synthesis: str,
    skills: list,
    references: list,
    sanitized_entities: dict,
    wiki_dir: Path
) -> bool:
    """Save the structured video source note under the sources/ directory."""
    sources_dir = wiki_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    source_note_path = sources_dir / f"{video_id}.md"

    frontmatter = f"""---
video_id: {video_id}
title: "{title.replace('"', '\\"')}"
channel: "{channel.replace('"', '\\"')}"
channel_id: {channel_id}
upload_date: {upload_date}
synced_at: {datetime.now(timezone.utc).isoformat()}
summary: "{summary.replace('"', '\\"')}"
tags: [youtube-sync, transcript]
---

# [[sources/{video_id}|{title}]]

## Metadata
- **Source URL**: https://www.youtube.com/watch?v={video_id}
- **Channel**: [[{channel}]]
- **Upload Date**: {upload_date}

## Synthesis
### Summary
{summary}

### Key Takeaways
"""
    for takeaway in takeaways:
        frontmatter += f"- {takeaway}\n"

    frontmatter += f"\n### Detailed Synthesis\n{synthesis}\n"

    frontmatter += "\n## Entities\n"
    for cat in ["concepts", "people", "organizations", "examples"]:
        for item in sanitized_entities.get(cat, []):
            s_name = item.get("sanitized_name")
            frontmatter += f"- [[{cat}/{s_name}|{s_name}]]\n"

    frontmatter += "\n## Skills\n"
    if skills:
        for skill in skills:
            name = skill.get("name", "Unknown Skill")
            desc = skill.get("description", "")
            frontmatter += f"- **{name}**: {desc}\n"
    else:
        frontmatter += "_No specific skills extracted._\n"

    frontmatter += "\n## References\n"
    if references:
        for ref in references:
            name = ref.get("name", "Unknown Reference")
            ctx = ref.get("context", "")
            frontmatter += f"- *{name}*: {ctx}\n"
    else:
        frontmatter += "_No specific references cited._\n"

    try:
        with source_note_path.open("w", encoding="utf-8") as f:
            f.write(frontmatter)
        return True
    except Exception as e:
        print(f"  Error: Failed to save source note: {e}")
        return False


def update_entity_notes(
    sanitized_entities: dict,
    model: str,
    ollama_url: str,
    wiki_dir: Path
) -> None:
    """Create or update notes for each individual extracted entity."""
    categories_mapping = [
        ("concepts", "concepts", "explanation"),
        ("people", "people", "context"),
        ("organizations", "organizations", "context"),
        ("examples", "examples", "description")
    ]
    for key, folder, context_key in categories_mapping:
        for item in sanitized_entities.get(key, []):
            create_or_update_entity_note(
                item.get("sanitized_name"),
                item.get(context_key),
                wiki_dir / folder,
                model,
                ollama_url,
                wiki_dir
            )


def update_grep_references(
    sanitized_entities: dict,
    summary: str,
    model: str,
    ollama_url: str,
    wiki_dir: Path
) -> None:
    """Scan existing wiki notes to link references to new entities (Scoped Grep & Update)."""
    # Prepare a list of all entity names to look for
    all_target_entities = []
    categories_mapping = [
        ("concepts", "explanation"),
        ("people", "context"),
        ("organizations", "context"),
        ("examples", "description")
    ]
    for key, context_key in categories_mapping:
        for item in sanitized_entities.get(key, []):
            all_target_entities.append({
                "sanitized_name": item.get("sanitized_name"),
                "original_name": item.get("original_name"),
                "context": item.get(context_key)
            })

    # Iterate through all markdown notes in the wiki to find mentions and inject links
    for file_path in wiki_dir.rglob("*.md"):
        # Skip log, index, sources and the entity's own directories when looking to link
        if file_path.name in ["index.md", "log.md"] or "sources" in file_path.parts:
            continue

        try:
            with file_path.open("r", encoding="utf-8") as f:
                content = f.read()

            updated = False
            for entity in all_target_entities:
                san_name = entity["sanitized_name"]
                orig_name = entity["original_name"]

                # Skip if we are looking at the entity's own note file to avoid self-reference updates
                if file_path.stem == san_name:
                    continue

                # Check if the note contains the name (case-insensitive) but is not already linked
                has_plain_ref = False
                for term in [san_name, orig_name]:
                    if term.lower() in content.lower():
                        has_plain_ref = True
                        break

                if has_plain_ref:
                    print(f"  [Pass 4][Grep] Found reference to [[{san_name}]] in note: {file_path.relative_to(wiki_dir)}")
                    prompt = REFERENCE_UPDATE_SYSTEM_PROMPT.format(
                        file_content=content,
                        entity_name=san_name,
                        entity_context=entity["context"],
                        raw_context=summary
                    )
                    content = get_ollama_generate(prompt, "", model, ollama_url)
                    updated = True

            if updated:
                with file_path.open("w", encoding="utf-8") as f:
                    f.write(content)
        except Exception as e:
            print(f"  Warning: Grep reference update failed for {file_path.name}: {e}")


def run_pass4_integration(
    video_id: str,
    title: str,
    channel: str,
    channel_id: str,
    upload_date: str,
    summary: str,
    takeaways: list,
    synthesis: str,
    skills: list,
    references: list,
    sanitized_entities: dict,
    model: str,
    ollama_url: str,
    wiki_dir: Path
) -> bool:
    """Pass 4: Create source summary note, update/create entity notes, and run grep update sweep across the vault."""
    print("  [Pass 4] Committing source note and updating vault references...")

    # 1. Save structured source note under sources/
    success = save_source_note(
        video_id=video_id,
        title=title,
        channel=channel,
        channel_id=channel_id,
        upload_date=upload_date,
        summary=summary,
        takeaways=takeaways,
        synthesis=synthesis,
        skills=skills,
        references=references,
        sanitized_entities=sanitized_entities,
        wiki_dir=wiki_dir
    )
    if not success:
        return False

    # 2. Update or create the entity's own notes
    update_entity_notes(
        sanitized_entities=sanitized_entities,
        model=model,
        ollama_url=ollama_url,
        wiki_dir=wiki_dir
    )

    # 3. Scoped Grep & Update Sweep across other vault notes
    update_grep_references(
        sanitized_entities=sanitized_entities,
        summary=summary,
        model=model,
        ollama_url=ollama_url,
        wiki_dir=wiki_dir
    )

    # 4. Regenerate Global Index
    regenerate_global_index(wiki_dir)
    return True


# ==================== MAIN COMPILER ENTRYPOINT ====================
def process_transcript_to_obsidian(
    res: dict,
    model: str = "gemma4:e2b",
    ollama_url: str = "http://localhost:11434",
    output_dir: Path = Path(__file__).parent / "wiki"
) -> bool:
    """Run the complete four-pass LLM compilation loop to structure the transcript into the Wiki."""
    video_id = res["video_id"]
    title = res["video_title"]
    channel = res["channel_name"]
    channel_id = res.get("channel_id", "unknown_channel")
    upload_date = res["upload_date"]
    transcript_text = res["text"]

    # Ensure vault directories exist
    output_dir.mkdir(parents=True, exist_ok=True)
    for cat in ["sources", "concepts", "people", "organizations", "examples"]:
        (output_dir / cat).mkdir(parents=True, exist_ok=True)

    try:
        # Pass 1: Newspaper Article Generation
        newspaper_article = run_pass1_newspaper(title, transcript_text, model, ollama_url)

        # Pass 2: Extraction
        raw_extraction = run_pass2_extraction(title, newspaper_article, model, ollama_url)
        summary = raw_extraction.get("summary", "No summary generated.")

        # Pass 3: Standardization & Sanitization
        existing_notes = get_existing_notes(output_dir)
        sanitized_entities = run_pass3_standardization(raw_extraction, existing_notes, model, ollama_url)

        # Pass 4: Integration (Grep & Update)
        success = run_pass4_integration(
            video_id=video_id,
            title=title,
            channel=channel,
            channel_id=channel_id,
            upload_date=upload_date,
            summary=summary,
            takeaways=raw_extraction.get("takeaways", []),
            synthesis=newspaper_article,
            skills=raw_extraction.get("skills", []),
            references=raw_extraction.get("references", []),
            sanitized_entities=sanitized_entities,
            model=model,
            ollama_url=ollama_url,
            wiki_dir=output_dir
        )
        return success

    except Exception as e:
        print(f"  Error: Processing transcript to Obsidian failed: {e}")
        return False
