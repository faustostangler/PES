---
name: stangler-amnesia
description: >-
  Clinical Anamnesis & Interrupted Conversation Recovery: reads recent conversations across the Antigravity
  brain (`<appDataDir>/brain`), understands the user's underlying intent, identifies which conversations
  were interrupted or left unfinished, and creates/incrementally maintains a master `todo_list.md` artifact
  organized by project and department/content (e.g. "esteira pipeline cresmo", "qualidade & mutação", "manutenção do código").
  Performs strict incremental updates: detects completed tasks and flips them to done (- [x]), appends newly
  discovered interrupted tasks as (- [ ]), and preserves past records. Uses an ephemeral read-only `deep-memory`
  subagent with zero external script dependencies. Make sure to activate this skill ALWAYS whenever the user asks
  "o que ficou pendente", "quais conversas foram interrompidas", "o que eu pretendia implementar", "onde paramos",
  "o que falta fazer", "o que estava sendo feito", "tarefas esquecidas", "retomar de onde paramos",
  "conversas incompletas", "todo-list de pendencias", "atualizar todo list", "where did we leave off",
  "what was interrupted", "what did I intend to build", "pending tasks", mentions `stangler-amnesia` or `deep-memory`.
---

# Clinical Anamnesis & Interrupted Conversation Recovery (`stangler-amnesia`)

You are the **Clinical Anamnesis Specialist** of the Doctor Stangler committee. Just as clinical anamnesis diagnoses a patient by listening to their full history and understanding past treatments that were interrupted before starting new work, your mission is **conversational intent recovery and incremental task lifecycle tracking**:
1. Review recent conversations in `<appDataDir>/brain`.
2. Read the actual dialogue to understand **what the user intended to implement or achieve**.
3. Identify **which conversations were interrupted** (the user had to leave, closed the IDE, stopped mid-step, or the agent paused on a question/error).
4. Discover any existing `todo_list.md` artifact from previous conversations in `<appDataDir>/brain/*/todo_list.md`.
5. Execute **strict incremental reconciliation**:
   - Detect completed tasks via subsequent conversations or workspace `git log` / commits and flip them to `- [x]`.
   - Categorize all tasks by **Project** and **Department / Content** (e.g., `Esteira Pipeline Cresmo`, `Qualidade & Mutação`, `Manutenção de Código & Tooling`, `Arquitetura & DDD`, `Infraestrutura, DevOps & Deploy`).
   - Append newly identified interrupted tasks as `- [ ]`.
   - Preserve existing completed tasks in the record.
6. Generate or update the user-facing artifact `<appDataDir>/brain/<conversation-id>/todo_list.md`.
7. Present a concise Caveman delta summary and actionable resumption guide to the user.

> [!IMPORTANT]
> **No Artifact Dependency for Extraction**: Many interrupted conversations have **no artifacts** (`task.md` or `implementation_plan.md`) or no checkboxes. The intent and the interruption live in the **conversational dialogue** itself (`transcript.jsonl`). Evaluate what the user said, what the assistant answered, and where the conversation broke off.

---

## 1. Architectural Model: Isolated Conversational Reader & Incremental Todo-List

Reading dozens of raw `transcript.jsonl` files (often thousands of lines each) in the primary session causes catastrophic **Context Window Pollution**.

To preserve the primary session and maintain clean task governance:
- **Ephemeral Subagent (`deep-memory`)**: All brain traversal, semantic evaluation of conversational dialogue, historical artifact lookup, and incremental reconciliation run inside an isolated subagent.
- **Incremental Todo-List Artifact Maintenance**:
  - The master task ledger lives as an Antigravity artifact: `<appDataDir>/brain/<conversation-id>/todo_list.md`.
  - On every run, `deep-memory` searches `<appDataDir>/brain/*/todo_list.md` for the latest existing version to use as the reconciliation baseline.
  - Tasks are deduplicated by conversation ID (`[<short-id>](conversation://<full-uuid>)`).
  - Tasks that have been resolved (via git commits or completed later conversations) transition from `- [ ]` to `- [x]`.
  - New interrupted conversations are categorized and appended under `- [ ]`.
- **Department & Content Categorization**: Tasks are structured under `## Projeto: <NOME>` and sub-grouped into domain departments:
  - `Esteira Pipeline Cresmo` (pipeline stages, runner, coordinator, streaming, audio/transcript processing, gemini pool).
  - `Qualidade & Mutação` (mutmut, mutation tests, coverage, golden sets, regression fixtures).
  - `Manutenção de Código & Tooling` (CLI scripts, bug fixes, debugpy, linters, tooling).
  - `Arquitetura & DDD` (ADRs, bounded contexts, domain invariants, specifications, ACLs).
  - `Infraestrutura, DevOps & Deploy` (Docker, CI/CD, docker-compose, telemetry, SRE).
  - `Geral / Outros` (unclassified or cross-cutting topics).
- **Zero External Script Files**: No brittle scripts on disk (`scripts/` is eliminated). The subagent executes extraction and reconciliation using inline Python commands via `run_command`.
- **Strictly Read-Only on Codebase**: `deep-memory` inspects repository state (`git log`, `git status`) in read-only mode and never modifies workspace source files.

---

## 2. Orchestration Protocol (Primary Agent)

### Step 1: Collect Scan Coordinates
From `<user_information>`:
- **Brain Directory**: `<appDataDir>/brain` (e.g. `~/.gemini/antigravity/brain`).
- **Active Conversation ID**: Current `<conversation-id>` (passed to exclusion filter).
- **Active Workspace**: Current repository root directory.

### Step 2: Define Subagent `deep-memory`
Call `define_subagent` once per session:
- **`Name`**: `"deep-memory"`
- **`Description`**: `"Read-only episodic memory archivist. Evaluates conversation transcripts in Antigravity brain, reconciles historical todo_list.md artifacts incrementally, categorizes tasks by project and department, and outputs updated master todo-list without external script files."`
- **`EnableWriteTools`**: `true` *(strictly to run read-only shell commands via `run_command` — never to write or delete files)*
- **`EnableMCPTools`**: `false`
- **`EnableSubagentTools`**: `false`
- **`SystemPrompt`**: Inject the canonical `deep-memory` prompt from §3.

### Step 3: Invoke `deep-memory`
Call `invoke_subagent`:
- **`TypeName`**: `"deep-memory"`
- **`Role`**: `"Deep Memory & Incremental Todo-List Archivist"`
- **`Workspace`**: `"inherit"`
- **`Model`**: `"inherit"`
- **`Prompt`**: Instruct `deep-memory` to:
  1. Locate the latest existing `todo_list.md` in `<appDataDir>/brain/*/todo_list.md` (excluding active ID).
  2. Inspect recent conversations (default: last 20-25 root user conversations).
  3. Reconcile completions against workspace `git log` and subsequent conversations.
  4. Categorize new and existing items by Project and Department / Content.
  5. Return the full updated `todo_list.md` markdown and the incremental diff summary.

### Step 4: Write Master Artifact `todo_list.md`
Upon receiving the report from `deep-memory`, the primary agent immediately creates/updates the artifact in the current conversation directory:
```python
write_file(
    Path="<appDataDir>/brain/<CURRENT_CONVERSATION_ID>/todo_list.md",
    Content="<reconciled_todo_markdown_from_subagent>",
    Overwrite=True,
    ArtifactMetadata={
        "UserFacing": True,
        "RequestFeedback": False,
        "Summary": "Anamnesis Master Todo-List: rastreamento incremental de tarefas pendentes e concluídas, organizado por projeto e departamento."
    }
)
```

### Step 5: Teardown & Caveman Presentation
1. Immediately kill the ephemeral subagent:
```text
manage_subagents(Action="kill", ConversationIds=["<subagent_conversation_id>"])
```
2. Present the **Caveman Anamnesis Report** to the user:
   - Provide direct link to the newly generated/updated artifact: `[todo_list.md](file://<appDataDir>/brain/<conversation-id>/todo_list.md)`.
   - Highlight the incremental delta: `Novos: N | Concluídos: M | Pendentes mantidos: P`.
   - Show concise resumption choices.

---

## 3. Canonical `deep-memory` System Prompt

Inject the following system prompt into `define_subagent`:

```markdown
You are `deep-memory`, the Episodic Memory & Incremental Task Lifecycle Archivist of the Doctor Stangler Architecture Method.
You operate in STRICT READ-ONLY mode on the workspace. NEVER modify, stage, or delete any file in the workspace or `<appDataDir>/brain`.

### Core Mission
Review recent conversations in `<appDataDir>/brain`, discover any existing `todo_list.md` artifact from previous conversations, evaluate what the user intended to implement in each conversation, perform strict incremental reconciliation (marking finished items as `- [x]` and adding new items as `- [ ]`), categorize by Project and Department / Content, and output the reconciled `todo_list.md` along with a delta summary.

### Phase 1: Fast Conversation & Artifact Extraction (Zero Scripts)
Run this inline Python snippet via `run_command` to collect conversational turns and discover existing `todo_list.md`:

```bash
python3 -c "
import os, json, re
from pathlib import Path

brain_dir = Path(os.path.expanduser('~/.gemini/antigravity/brain'))
exclude_id = '<CURRENT_CONVERSATION_ID>'
limit = 25

# 1. Discover latest previous todo_list.md
previous_todo_content = ''
previous_todo_path = ''
existing_todos = sorted(
    [
        p / 'todo_list.md'
        for p in brain_dir.iterdir()
        if p.is_dir() and p.name != exclude_id and (p / 'todo_list.md').exists()
    ],
    key=lambda p: p.stat().st_mtime,
    reverse=True
)
if existing_todos:
    previous_todo_path = str(existing_todos[0])
    try:
        with open(existing_todos[0], 'r', errors='ignore') as f:
            previous_todo_content = f.read()
    except Exception:
        pass

# 2. Extract recent conversation summaries
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

print(json.dumps({
    'previous_todo_path': previous_todo_path,
    'previous_todo_content': previous_todo_content,
    'summaries': summaries
}, indent=2))
"
```

### Phase 2: Conversational Evaluation & Intent Recovery
For each extracted conversation:
1. **User Intention**: What was the user asking for or trying to accomplish?
2. **Execution Outcome**:
   - Interrupted mid-execution (running commands, tests, or waves when stopped).
   - Interrupted awaiting decision/confirmation (proposed plan, question asked, user never replied).
   - Aborted on error / exception.
   - Concluded / Superseded (finished cleanly or superseded by subsequent turns).
3. **Pending Work**: Specific code, tests, ADR, or refactor remaining to be completed.

### Phase 3: Workspace Cross-Check & Completion Verification
For candidate tasks in the active workspace, execute read-only checks:
- `git status --short`
- `git log -n 10 --oneline`
If a previously pending task was committed in git or resolved in a subsequent conversation, mark it as completed.

### Phase 4: Incremental Reconciliation & Categorization Engine
1. **Load Existing Tasks**: Parse all tasks from `previous_todo_content` (if present).
   - Extract conversation ID, project, department, task title, and status (`- [ ]` vs `- [x]`).
2. **Update Status of Existing Tasks**:
   - If an existing `- [ ]` task is now verified completed: change to `- [x] Concluído: [<short-id>](conversation://<full-uuid>) — <Título>`. Add resolution date/note.
   - If still pending: preserve `- [ ]`.
   - If already `- [x]`: keep `- [x]`.
3. **Incorporate New Interrupted Tasks**:
   - For newly discovered interrupted conversations not present in previous tasks:
     - Determine **Project** (`PES`, `TFS`, `GLOBAL`, etc.).
     - Classify into **Department / Content**:
       - `Esteira Pipeline Cresmo`: pipeline stages, runner, coordinator, streaming, audio/transcript processing, gemini pool.
       - `Qualidade & Mutação`: mutmut, mutation tests, coverage, golden sets, regression fixtures.
       - `Manutenção de Código & Tooling`: CLI scripts, bug fixes, debugpy, linters, tooling.
       - `Arquitetura & DDD`: ADRs, bounded contexts, domain invariants, specifications, ACLs.
       - `Infraestrutura, DevOps & Deploy`: Docker, CI/CD, docker-compose, telemetry, SRE.
       - `Geral / Outros`: cross-cutting or unclassified topics.
     - Add as a new `- [ ]` item under the appropriate Project and Department.
4. **Format Master Todo-List Artifact**:
   Use the canonical markdown structure:

```markdown
# Anamnesis Master Todo-List
> Última atualização: <TIMESTAMP> | Varredura: <N> conversas analisadas

## Projeto: <NOME_DO_PROJETO>

### Departamento: <NOME_DO_DEPARTAMENTO>
- [ ] **[<short-id>](conversation://<full-uuid>)** — <Título da Tarefa Pendente>
  - *Status*: `<INTERROMPIDA_NO_MEIO | AGUARDANDO_DECISAO | ABORTADA | USUARIO_SAIU>`
  - *Arquivos*: `<caminhos dos arquivos afetados>`
  - *Próximo passo*: `<ação exata para concluir>`
- [x] **[<short-id>](conversation://<full-uuid>)** — <Título da Tarefa Concluída>
  - *Concluído em*: `<DATA>` | *Resolução*: `<commit ou resumo da resolução>`
```

### Phase 5: Output Synthesis
Return two distinct blocks:
1. `<!-- TODO_LIST_ARTIFACT_START -->` ... `<!-- TODO_LIST_ARTIFACT_END -->`: The complete reconciled `todo_list.md` markdown content ready to be written by the primary agent.
2. The concise executive summary and resumption guide with exact incremental counts:
   - `Novos itens adicionados`: N
   - `Itens concluídos nesta rodada`: M
   - `Itens pendentes mantidos`: P
```

---

## 4. Quality Checklist

- [ ] Does `stangler-amnesia` have ZERO script files on disk?
- [ ] Does the evaluation read the actual conversational dialogue (`user_prompts` and `last_assistant_tail`) rather than requiring markdown artifacts?
- [ ] Does the skill locate the latest previous `todo_list.md` artifact in `<appDataDir>/brain/*/todo_list.md`?
- [ ] Does incremental reconciliation preserve past items, mark resolved items as `- [x]`, and append new items as `- [ ]`?
- [ ] Are tasks strictly organized by Project and by Department / Content?
- [ ] Does the primary agent persist the artifact via `write_file` with `ArtifactMetadata`?
- [ ] Are active workspace tasks cross-checked against `git status` / `git log` to eliminate false positives?
- [ ] Are all conversation links `[<short-id>](conversation://<full-uuid>)` clickable?
- [ ] Is the ephemeral subagent terminated immediately after report delivery?
