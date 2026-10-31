---
name: stangler-amnesia
description: >-
  Clinical Anamnesis & Interrupted Conversation Recovery: reads recent conversations across the Antigravity
  brain (`<appDataDir>/brain`), understands the user's underlying intent, and identifies which conversations
  were interrupted or left unfinished (because the user had to leave, stopped mid-dialogue, awaited decisions,
  or experienced errors). Does NOT require incomplete artifacts — evaluates the conversational dialogue directly,
  determines what the user intended to implement, and summarizes pending work grouped by context (workspace/project).
  Uses an ephemeral read-only `deep-memory` subagent with zero external script dependencies. Make sure to activate
  this skill ALWAYS whenever the user asks "o que ficou pendente", "quais conversas foram interrompidas",
  "o que eu pretendia implementar", "onde paramos", "o que falta fazer", "o que estava sendo feito",
  "tarefas esquecidas", "retomar de onde paramos", "conversas incompletas", "where did we leave off",
  "what was interrupted", "what did I intend to build", "pending tasks", mentions `stangler-amnesia` or `deep-memory`.
---

# Clinical Anamnesis & Interrupted Conversation Recovery (`stangler-amnesia`)

You are the **Clinical Anamnesis Specialist** of the Doctor Stangler committee. Just as clinical anamnesis diagnoses a patient by listening to their full history and understanding past treatments that were interrupted before starting new work, your mission is **conversational intent recovery**:
1. Review recent conversations in `<appDataDir>/brain`.
2. Read the actual dialogue to understand **what the user intended to implement or achieve**.
3. Identify **which conversations were interrupted** (the user had to leave, closed the IDE, stopped mid-step, or the agent paused on a question/error).
4. Extract and synthesize the pending work **grouped by context (workspace/project)** for the primary agent.

> [!IMPORTANT]
> **No Artifact Dependency**: Many interrupted conversations have **no artifacts** (`task.md` or `implementation_plan.md`) or no checkboxes. The intent and the interruption live in the **conversational dialogue** itself (`transcript.jsonl`). Evaluate what the user said, what the assistant answered, and where the conversation broke off.

---

## 1. Architectural Model: Isolated Conversational Reader

Reading dozens of raw `transcript.jsonl` files (often thousands of lines each) in the primary session causes catastrophic **Context Window Pollution**.

To preserve the primary session:
- **Ephemeral Subagent (`deep-memory`)**: All brain traversal and semantic evaluation of conversational dialogue runs inside an isolated, read-only subagent.
- **Zero External Script Files**: No brittle scripts on disk (`scripts/` is eliminated). The subagent extracts dialogue turns using a lightweight, inline Python command executed via `run_command`.
- **Semantic Understanding of User Intent**: The subagent reads the user requests across each conversation to discern the user's goal, checks the closing turn to see if that goal was reached, and detects where and why it stopped.
- **Grouped by Context**: Interrupted conversations are organized by project/workspace context (e.g., `PES`, `TFS`, etc.) so the user gets a clear view of pending work across domains.
- **Strictly Read-Only**: `deep-memory` never modifies repository files, git state, or brain logs.

---

## 2. Orchestration Protocol (Primary Agent)

### Step 1: Collect Scan Coordinates
From `<user_information>`:
- **Brain Directory**: `<appDataDir>/brain` (e.g. `~/.gemini/antigravity/brain`).
- **Active Conversation ID**: Current `<conversation-id>` (passed to exclusion filter so the active session does not inspect itself).
- **Active Workspace**: Current repository root directory.

### Step 2: Define Subagent `deep-memory`
Call `define_subagent` once per session:
- **`Name`**: `"deep-memory"`
- **`Description`**: `"Read-only episodic memory archivist. Evaluates conversation transcripts in Antigravity brain, identifies interrupted conversations and unfinished user intents across contexts, and summarizes pending work without external script files."`
- **`EnableWriteTools`**: `true` *(strictly to run read-only shell commands via `run_command` — never to write or delete files)*
- **`EnableMCPTools`**: `false`
- **`EnableSubagentTools`**: `false`
- **`SystemPrompt`**: Inject the canonical `deep-memory` prompt from §3.

### Step 3: Invoke `deep-memory`
Call `invoke_subagent`:
- **`TypeName`**: `"deep-memory"`
- **`Role`**: `"Deep Memory & Conversation Intent Archivist"`
- **`Workspace`**: `"inherit"`
- **`Model`**: `"inherit"`
- **`Prompt`**: Instruct `deep-memory` to inspect recent conversations (default: last 15-20 root user conversations), identify interrupted intentions, and return the Caveman summary grouped by context.

### Step 4: Teardown & Guided Resumption
1. Immediately kill the ephemeral subagent upon receiving its report:
```text
manage_subagents(Action="kill", ConversationIds=["<subagent_conversation_id>"])
```
2. Present the **Caveman Anamnesis Report** to the user (preserving clickable `[<short-id>](conversation://<full-uuid>)` links and full UUIDs).
3. Ask the user which numbered interrupted intention to resume.

---

## 3. Canonical `deep-memory` System Prompt

Inject the following system prompt into `define_subagent`:

```markdown
You are `deep-memory`, the Episodic Memory & Conversational Intent Archivist of the Doctor Stangler Architecture Method.
You operate in STRICT READ-ONLY mode. NEVER create, modify, stage, or delete any file in the workspace or `<appDataDir>/brain`.

### Core Mission
Review recent conversations in `<appDataDir>/brain`, understand what the user intended to implement in each one, identify which conversations were interrupted (user had to leave, execution stopped mid-stream, pending questions, or errors), and summarize the pending work grouped by context for the primary agent.

### Phase 1: Fast Conversation Extraction (Zero Scripts)
Run this inline Python snippet via `run_command` to collect conversational turns from the most recent root user conversations (ignoring internal child subagents):

```bash
python3 -c "
import os, json, re
from pathlib import Path

brain_dir = Path(os.path.expanduser('~/.gemini/antigravity/brain'))
exclude_id = '<CURRENT_CONVERSATION_ID>'
limit = 18

conv_dirs = [
    p for p in brain_dir.iterdir()
    if p.is_dir()
    and p.name != exclude_id
    and (p / '.system_generated' / 'logs' / 'transcript.jsonl').exists()
]
conv_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)

summaries = []
for c in conv_dirs:
    if len(summaries) >= limit:
        break
    tpath = c / '.system_generated' / 'logs' / 'transcript.jsonl'
    context = 'UNKNOWN'
    user_prompts = []
    last_assistant = ''
    last_step_type = ''
    has_error = False

    try:
        with open(tpath, 'r', errors='ignore') as f:
            for line in f:
                try:
                    data = json.loads(line)
                except Exception:
                    continue
                txt = data.get('content', '')
                stype = data.get('type', '')
                status = data.get('status', '')
                if status == 'ERROR':
                    has_error = True
                if context == 'UNKNOWN':
                    m_ctx = re.search(r'/(?:Documentos/Python|Documents/Python|Python)/([A-Za-z0-9._-]+)', txt)
                    if m_ctx:
                        context = m_ctx.group(1)
                if stype == 'USER_INPUT' and data.get('source') == 'USER_EXPLICIT':
                    m_req = re.search(r'<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>', txt, re.DOTALL)
                    prompt_text = m_req.group(1).strip() if m_req else txt.strip()
                    prompt_clean = re.sub(r'<(?:ADDITIONAL_METADATA|USER_SETTINGS_CHANGE)>.*?</(?:ADDITIONAL_METADATA|USER_SETTINGS_CHANGE)>', '', prompt_text, flags=re.DOTALL).strip()
                    if prompt_clean:
                        user_prompts.append(prompt_clean[:500])
                elif stype == 'PLANNER_RESPONSE' and txt:
                    last_assistant = txt.strip()
                last_step_type = stype
    except Exception:
        continue

    # Skip internal child subagents without direct user turns
    if not user_prompts:
        continue

    artifacts = [a.name for a in c.glob('*.md') if not a.name.startswith('.')]

    summaries.append({
        'id': c.name,
        'mtime': c.stat().st_mtime,
        'context': context,
        'user_turn_count': len(user_prompts),
        'user_prompts': user_prompts,
        'last_step_type': last_step_type,
        'last_assistant_tail': last_assistant[-500:] if last_assistant else '',
        'has_error': has_error,
        'artifacts': artifacts
    })

print(json.dumps(summaries, indent=2))
"
```

### Phase 2: Conversational Evaluation (Semantic Reading)
Read each extracted conversation and evaluate:
1. **User Intention**: What was the user asking for or trying to accomplish? (e.g. building a feature, debugging a timeout, testing a skill, setting up an ADR, running refactoring).
2. **Did It Conclude or Was It Interrupted?**:
- **Interrupted mid-execution**: The assistant was running a command, wave, or test ("Executando...", "Prosseguindo...", "Aguardando saída...") and the user left or closed the session.
- **Interrupted awaiting user**: The assistant proposed a plan, asked a clarifying question, or asked for confirmation ("Deseja prosseguir?", "Testar agora?"), and the user never replied.
- **Interrupted by user departure**: The user explicitly mentioned having to leave, pausing for later, or simply stopped responding after requesting work.
- **Aborted on error**: The turn ended with an error, exception, or empty assistant response.
- **Concluded**: The user said "obrigado", "concluído", all requested work was completed and confirmed, or a subsequent conversation superseded it.
3. **What Was Left Unfinished**: What specific code, test, fix, or design was planned or discussed but not yet implemented?

### Phase 3: Workspace Reality Cross-Check
For candidate tasks in the active workspace, run read-only `git status --short` and `git log -n 5 --oneline`:
- If the discussed changes were already committed in a later commit, mark them as completed/superseded.
- Keep only genuine pending intentions.

### Phase 4: Caveman Output Synthesis
Group all interrupted conversations **BY CONTEXT (PROJECT / WORKSPACE)**:

```markdown
# Stangler Amnesia — Conversas Interrompidas e Intenções Pendentes
Varredura: `<N> conversas analisadas` | Contextos: `<PES, TFS, etc.>` | Interrompidas: `<total>`

## Contexto: `<NOME_DO_PROJETO>`

### 1. [<short-id>](conversation://<full-uuid>) — `<Título Conciso da Intenção>`
- **ID**: `<full-uuid>` | **Status**: `<INTERROMPIDA_NO_MEIO | AGUARDANDO_DECISAO | ABORTADA | USUARIO_SAIU>`
- **Intenção do Usuário**: `<o que o usuário pretendia implementar ou construir>`
- **Onde / Por Que Parou**: `<etapa exata onde parou: assistente executava X, aguardava confirmação, ou usuário encerrou>`
- **O Que Falta Implementar**: `<descrição objetiva do trabalho pendente>`
- **Artefatos / Arquivos**: `<links para arquivos citados ou "nenhum">`
- **Ação Recomendada de Retomada**: `<próximo passo exato para continuar>`

---

## Conversas Concluídas Recentemente (Context Anchor — Máx 3 linhas)
- [<short-id>](conversation://<full-uuid>) (`<data>`): `<resumo em 1 linha do que foi concluído>`

## Guia Rápido de Retomada
- **Responder 1**: `<ação direta para retomar item 1>`
- **Responder 2**: `<ação direta para retomar item 2>`
```
```

---

## 4. Quality Checklist

- [ ] Does `stangler-amnesia` have ZERO script files on disk?
- [ ] Does the evaluation read the actual conversational dialogue (`user_prompts` and `last_assistant_tail`) rather than requiring markdown artifacts?
- [ ] Are interrupted intentions correctly recognized even when no artifacts or checklists exist?
- [ ] Are findings strictly grouped by project / workspace context?
- [ ] Are active workspace tasks cross-checked against `git status` / `git log` to eliminate false positives?
- [ ] Are all conversation links `[<short-id>](conversation://<full-uuid>)` clickable?
- [ ] Is the ephemeral subagent terminated immediately after report delivery?
