#!/usr/bin/env python3
"""Stage 2 - Enrichment Pipeline.

Uses custom Gemini Gems to clean, expand, and downgrade raw transcripts.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from gemini_web import GeminiWebProcessor

# Add current dir to path to ensure flat imports work
sys.path.insert(0, str(Path(__file__).parent.resolve()))

# --- Path Configurations ---
STAGE2_ROOT = Path(__file__).parent.resolve()
DEFAULT_RAW_DIR = STAGE2_ROOT / "raw"
DEFAULT_ENRICHED_DIR = STAGE2_ROOT / "enriched"
DEFAULT_CHROME_PROFILE = Path.home() / ".isb-ai-chrome-profile"

def clean_gemini_response(text: str) -> str:
    """Clean and unwrap markdown code blocks from response, and extract only the XML content."""
    text = text.strip()
    if text.startswith("```"):
        # Split into lines
        lines = text.splitlines()
        if len(lines) >= 2:
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            
    # Extract only the XML portion (from first '<' to last '>')
    first_lt = text.find("<")
    last_gt = text.rfind(">")
    if first_lt != -1 and last_gt != -1 and last_gt > first_lt:
        text = text[first_lt:last_gt + 1].strip()
        
    return text

def validate_response(text: str) -> str:
    """Validate that response is valid XML, contains no API errors,
    and returns ONLY the extracted inner text content (not the XML tags).
    Returns empty string if invalid.
    """
    if not text:
        return ""
        
    cleaned_text = text.strip()
    if len(cleaned_text) < 50:
        return ""
    
    # 1. Standard API error check
    error_phrases = [
        "something went wrong",
        "please try again",
        "quota exceeded",
        "internal error",
        "error code"
    ]
    text_lower = cleaned_text.lower()
    for phrase in error_phrases:
        if phrase in text_lower:
            return ""

    # 2. XML check: Must start with '<' (or '<?xml') and end with '>'
    if not (cleaned_text.startswith("<") and cleaned_text.endswith(">")):
        return ""

    # 3. XML comment checks: Avoid comments at the start or end of the text
    if cleaned_text.startswith("<!--") or cleaned_text.endswith("-->"):
        return ""

    # 4. Syntactic XML parsing check and content extraction
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(cleaned_text)
        extracted_text = "".join(root.itertext()).strip()
    except ET.ParseError:
        # Fallback 1: Repair unescaped '&' (e.g., P&D, Q&A, AT&T) which cause XML ParseError
        try:
            fixed_xml = re.sub(r'&(?!(?:amp|lt|gt|apos|quot);)', '&amp;', cleaned_text)
            if not fixed_xml.startswith("<?xml"):
                root = ET.fromstring(f"<root>{fixed_xml}</root>")
            else:
                root = ET.fromstring(fixed_xml)
            extracted_text = "".join(root.itertext()).strip()
        except ET.ParseError:
            # Fallback 2: Extract text by stripping XML tags if strict parser fails
            extracted_text = re.sub(r'</?[a-zA-Z0-9_-]+(?:\s+[^>]*)?>', '', cleaned_text).strip()

    # Check that extracted text is not too short
    if len(extracted_text) < 50:
        return ""

    # 5. Check for deepening offers: "Não se ofereça para aprofundar e não ofereça aprofundamentos"
    extracted_lower = extracted_text.lower()
    deepening_phrases = [
        "se quiser saber mais",
        "caso queira saber mais",
        "posso detalhar",
        "posso explicar",
        "gostaria de saber",
        "para se aprofundar",
        "oferecer aprofundamento",
        "quer saber mais",
        "deseja saber mais",
        "se você quiser",
    ]
    for phrase in deepening_phrases:
        if phrase in extracted_lower:
            return ""

    # 6. Check for external links/videos: "não mostre links externos e não apresente vídeos sobre o assunto"
    if "http://" in extracted_lower or "https://" in extracted_lower or "www." in extracted_lower:
        return ""

    video_phrases = [
        "assista ao vídeo",
        "assista no youtube",
        "vídeo sobre o assunto",
        "vídeos sobre o assunto",
        "link do vídeo",
        "link externo",
    ]
    for phrase in video_phrases:
        if phrase in extracted_lower:
            return ""
            
    return extracted_text

def discover_unprocessed_files(raw_dir: Path, enriched_dir: Path) -> list[Path]:
    """Find all .txt files in raw_dir that have not been enriched yet."""
    if not raw_dir.exists():
        return []
    
    unprocessed = []
    for raw_file in sorted(raw_dir.rglob("*.txt")):
        # Calculate relative path
        rel_path = raw_file.relative_to(raw_dir)
        enriched_file = enriched_dir / rel_path
        if not enriched_file.exists():
            unprocessed.append(raw_file)
            
    return unprocessed

def parse_raw_file(file_path: Path) -> tuple[dict, str]:
    """Parse raw file to separate YAML header block and transcription text."""
    from helper import parse_merged_transcriptions
    blocks = parse_merged_transcriptions(file_path)
    if not blocks:
        return {}, ""
    # Assume first block is the main block in the raw file
    return blocks[0].get("metadata", {}), blocks[0].get("text", "")

def call_detranscriptor(processor: GeminiWebProcessor, text: str) -> str:
    """Call Detranscriptor Gem to clean transcription text."""
    gem_id = "cc00c0110bf0"
    prompt = (
        "Por favor, limpe e estruture a seguinte transcrição de áudio. "
        "Corrija erros de sintaxe, gramática e pontuação, remova redundâncias de fala, "
        "mas mantenha todas as ideias, fatos e terminologia técnica intactas. "
        "Sua resposta deve ser estritamente em formato XML. "
        "IMPORTANTE: Encapsule toda a resposta em um bloco de código markdown (usando ```xml no início e ``` no final):\n\n" + text
    )
    
    for attempt in range(1, 4):
        try:
            is_subsequent = attempt > 1
            response = processor.send_prompt_to_gem(gem_id, prompt, keep_thread=True, is_subsequent_turn=is_subsequent)
            response = clean_gemini_response(response)
            validated = validate_response(response)
            if validated:
                processor.delete_current_thread()
                return validated
            prompt = (
                "A resposta anterior foi inválida, curta ou incompleta. Por favor, limpe e estruture "
                "toda a transcrição de forma completa em formato XML (usando tags apropriadas):\n\n" + text
            )
        except Exception as e:
            if attempt == 3:
                processor.delete_current_thread()
                raise e
    processor.delete_current_thread()
    raise ValueError("Failed to obtain a valid response from Detranscriptor.")

def call_expander(processor: GeminiWebProcessor, text: str) -> str:
    """Call Expander Gap Filler Gem 5 times in the same chat thread."""
    gem_id = "2dd102b966de"
    last_response = text
    
    try:
        for i in range(1, 6):
            if i == 1:
                prompt = (
                    "Aqui está o texto estruturado. Por favor, inicie a expansão de lacunas teóricas "
                    "e aprofundamento técnico. Retorne a resposta em formato XML. "
                    "IMPORTANTE: Encapsule toda a resposta em um bloco de código markdown (usando ```xml no início e ``` no final):\n\n" + last_response
                )
                is_subsequent = False
            else:
                prompt = (
                    f"Esta é a iteração {i}/5 de expansão técnica extrema. Aprofunde ainda mais as explicações, "
                    "adicione mais detalhes sobre os mecanismos e teorias subjacentes. "
                    "IMPORTANTE: Retorne o compêndio completo em formato XML encapsulado em um bloco de código markdown (```xml ... ```)."
                )
                is_subsequent = True
                
            response = processor.send_prompt_to_gem(
                gem_id, prompt, keep_thread=True, is_subsequent_turn=is_subsequent
            )
            response = clean_gemini_response(response)
            
            validated = validate_response(response)
            attempt = 1
            while not validated and attempt <= 3:
                prompt_reinforce = (
                    "A resposta anterior foi inválida ou incompleta. Por favor, forneça o compêndio completo "
                    "atualizado e expandido até este ponto em formato XML."
                )
                response = processor.send_prompt_to_gem(
                    gem_id, prompt_reinforce, keep_thread=True, is_subsequent_turn=True
                )
                response = clean_gemini_response(response)
                validated = validate_response(response)
                attempt += 1
                
            if not validated:
                raise ValueError(f"Expander failed on iteration {i} to return a valid response.")
            
            last_response = validated
    finally:
        processor.delete_current_thread()
        
    return last_response

def call_downgrader(processor: GeminiWebProcessor, text: str) -> str:
    """Call Downgrader Gem to trim and refine the expanded compendium."""
    gem_id = "86ba1b4ce534"
    prompt = (
        "Aqui está o compêndio expandido. Remova redundâncias, apare explicações tangenciais irrelevantes "
        "ou fora do contexto do assunto principal, organize em subtópicos lógicos, e forneça o compêndio final em formato XML. "
        "IMPORTANTE: Encapsule toda a resposta em um bloco de código markdown (usando ```xml no início e ``` no final):\n\n" + text
    )
    
    for attempt in range(1, 4):
        try:
            is_subsequent = attempt > 1
            response = processor.send_prompt_to_gem(gem_id, prompt, keep_thread=True, is_subsequent_turn=is_subsequent)
            response = clean_gemini_response(response)
            validated = validate_response(response)
            if validated:
                processor.delete_current_thread()
                return validated
            prompt = (
                "A resposta anterior foi inválida ou incompleta. Por favor, forneça a compilação "
                "final organizada e limpa em formato XML:\n\n" + text
            )
        except Exception as e:
            if attempt == 3:
                processor.delete_current_thread()
                raise e
    processor.delete_current_thread()
    raise ValueError("Failed to obtain a valid response from Downgrader.")

def process_file(raw_file: Path, enriched_dir: Path, processor: GeminiWebProcessor, raw_dir: Path | None = None) -> None:
    """Run full Stage 2 pipeline on a raw file and save the output to enriched_dir."""
    yaml_header, transcription = parse_raw_file(raw_file)
    if not transcription.strip():
        # print(f"  ⚠️ Empty transcription in {raw_file.name}. Skipping.")
        return
        
    # print(f"  [1/3] Calling Detranscriptor Gem...")
    detranscribed = call_detranscriptor(processor, transcription)
    
    # print(f"  [2/3] Calling Expander Gem (5 iterations)...")
    expanded = call_expander(processor, detranscribed)
    
    # print(f"  [3/3] Calling Downgrader Gem...")
    # downgraded = call_downgrader(processor, expanded)
    
    # Format original YAML metadata header
    yaml_lines = ["---"]
    for k, v in yaml_header.items():
        if k == "video_description":
            v_indented = "\n".join("  " + l for l in v.splitlines())
            yaml_lines.append(f"{k}: |\n{v_indented}")
        else:
            # Escape strings if needed
            if isinstance(v, str) and ("\n" in v or ":" in v or '"' in v):
                escaped = v.replace('"', '\\"')
                yaml_lines.append(f'{k}: "{escaped}"')
            else:
                yaml_lines.append(f"{k}: {v}")
    yaml_lines.append("---")
    yaml_header_str = "\n".join(yaml_lines)
    
    # Assemble the final enriched file
    enriched_content = yaml_header_str + "\n" + expanded
    
    # Determine the target path
    if raw_dir is None:
        raw_dir = raw_file.parent.parent
    rel_path = raw_file.relative_to(raw_dir)
    target_file = enriched_dir / rel_path
    target_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(enriched_content)


def main() -> None:
    parser = argparse.ArgumentParser(description="ISB.AI Stage 2 - Pre-process & Enrichment Gems")
    parser.add_argument("--raw-dir", type=str, default=str(DEFAULT_RAW_DIR), help="Raw transcripts directory")
    parser.add_argument("--enriched-dir", type=str, default=str(DEFAULT_ENRICHED_DIR), help="Enriched output directory")
    parser.add_argument(
        "--chrome-profile",
        type=str,
        default=str(DEFAULT_CHROME_PROFILE),
        help="Chrome profile directory"
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of files to process")
    parser.add_argument("--dry-run", action="store_true", help="List files to be processed without executing")
    
    args = parser.parse_args()
    
    # Convert paths to Path objects relative to current directory if not absolute
    raw_path = Path(args.raw_dir).resolve()
    enriched_path = Path(args.enriched_dir).resolve()
    chrome_profile = Path(args.chrome_profile).resolve()
    
    unprocessed = discover_unprocessed_files(raw_path, enriched_path)
    print(f"Discovered {len(unprocessed)} unprocessed raw files.")
    
    if args.limit:
        unprocessed = unprocessed[:args.limit]
        print(f"Limiting execution to first {args.limit} files.")
        
    if not unprocessed:
        print("Nothing to process.")
        return
        
    if args.dry_run:
        print("--- Dry Run: Pending Files ---")
        for idx, f in enumerate(unprocessed, 1):
            print(f"  {idx}. {f.relative_to(raw_path)}")
        return
        
    print(f"Initializing Playwright context using profile: {chrome_profile}")
    with GeminiWebProcessor(user_data_dir=chrome_profile) as processor:
        for idx, raw_file in enumerate(unprocessed, 1):
            print(f"[{idx}/{len(unprocessed)}] Processing: {raw_file.relative_to(raw_path)}")
            try:
                process_file(raw_file, enriched_path, processor, raw_dir=raw_path)
                print(f"  ✓ Successfully enriched and saved.")
            except Exception as e:
                print(f"  ✗ Error processing {raw_file.name}: {e}")

if __name__ == "__main__":
    main()
print('done!') # debug purpose