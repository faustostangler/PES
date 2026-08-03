import json
from pathlib import Path

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 🧠 Antigravity Brain Transcript Navigator\n",
                "\n",
                "Navegador interativo para explorar e analisar todos os logs de conversa (`transcript.jsonl`) em `/home/stangler/.gemini/antigravity-ide/brain`."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Carregamento do DataFrame\n",
                "Carrega todas as conversas do diretório `.gemini/antigravity-ide/brain` em um DataFrame do Pandas."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import json\n",
                "import os\n",
                "from pathlib import Path\n",
                "import pandas as pd\n",
                "\n",
                "BRAIN_DIR = Path('/home/stangler/.gemini/antigravity-ide/brain')\n",
                "\n",
                "def load_brain_transcripts(brain_dir: Path = BRAIN_DIR) -> pd.DataFrame:\n",
                "    \"\"\"Varre todos os transcript.jsonl dentro de brain/ e consolida em um DataFrame.\"\"\"\
                "    records = []\n",
                "    log_files = sorted(brain_dir.glob('*/.system_generated/logs/transcript.jsonl'))\n",
                "    \n",
                "    print(f'🔍 Encontrados {len(log_files)} arquivos transcript.jsonl')\n",
                "    \n",
                "    for log_path in log_files:\n",
                "        conv_id = log_path.parent.parent.parent.name\n",
                "        mtime = os.path.getmtime(log_path)\n",
                "        \n",
                "        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:\n",
                "            for line_idx, line in enumerate(f, 1):\n",
                "                line_str = line.strip()\n",
                "                if not line_str:\n",
                "                    continue\n",
                "                try:\n",
                "                    data = json.loads(line_str)\n",
                "                    # Padronização de colunas essenciais\n",
                "                    rec = {\n",
                "                        'conversation_id': conv_id,\n",
                "                        'line_num': line_idx,\n",
                "                        'source': data.get('source', ''),\n",
                "                        'type': data.get('type', ''),\n",
                "                        'created_at': data.get('created_at', ''),\n",
                "                        'status': data.get('status', ''),\n",
                "                        'content': data.get('content', ''),\n",
                "                        'thinking': data.get('thinking', ''),\n",
                "                        'tool_calls': data.get('tool_calls', []),\n",
                "                        'log_path': str(log_path),\n",
                "                        'file_mtime': mtime\n",
                "                    }\n",
                "                    records.append(rec)\n",
                "                except Exception:\n",
                "                    continue\n",
                "                    \n",
                "    df = pd.DataFrame(records)\n",
                "    print(f'✅ Carregados {len(df):,} registros de {df[\"conversation_id\"].nunique()} conversas.')\n",
                "    return df\n",
                "\n",
                "df = load_brain_transcripts()\n",
                "df.head()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Resumo Geral de Conversas (Overview)\n",
                "Gera uma visão consolidada de cada conversa ID, quantidade de interações, datas e primeiro prompt do usuário."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def summarize_conversations(df: pd.DataFrame) -> pd.DataFrame:\n",
                "    \"\"\"Cria um resumo estruturado por conversa.\"\"\"\
                "    summaries = []\n",
                "    grouped = df.groupby('conversation_id')\n",
                "    \n",
                "    for conv_id, group in grouped:\n",
                "        user_msgs = group[group['source'].str.contains('USER', na=False)]\n",
                "        first_user_prompt = user_msgs.iloc[0]['content'] if not user_msgs.empty else ''\n",
                "        # Limpar tags longas se houver\n",
                "        first_prompt_clean = str(first_user_prompt).replace('\\n', ' ')[:120]\n",
                "        \n",
                "        summaries.append({\n",
                "            'conversation_id': conv_id,\n",
                "            'total_steps': len(group),\n",
                "            'user_steps': len(user_msgs),\n",
                "            'model_steps': len(group[group['source'] == 'MODEL']),\n",
                "            'system_steps': len(group[group['source'] == 'SYSTEM']),\n",
                "            'first_user_prompt': first_prompt_clean,\n",
                "            'last_mtime': pd.to_datetime(group['file_mtime'].iloc[0], unit='s')\n",
                "        })\n",
                "        \n",
                "    summary_df = pd.DataFrame(summaries).sort_values(by='last_mtime', ascending=False)\n",
                "    return summary_df\n",
                "\n",
                "df_summary = summarize_conversations(df)\n",
                "df_summary"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Busca por Palavras-Chave e Filtros\n",
                "Função flexível de pesquisa para localizar termos nos conteúdos, filtrar por conversa ou por fonte (`source`)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def search_brain(df: pd.DataFrame, query: str = None, conversation_id: str = None, source: str = None, type_: str = None) -> pd.DataFrame:\n",
                "    \"\"\"Filtra o dataframe por termo de busca, ID de conversa, fonte ou tipo de evento.\"\"\"\
                "    filtered = df.copy()\n",
                "    \n",
                "    if conversation_id:\n",
                "        filtered = filtered[filtered['conversation_id'].str.contains(conversation_id, case=False, na=False)]\n",
                "    if source:\n",
                "        filtered = filtered[filtered['source'].str.contains(source, case=False, na=False)]\n",
                "    if type_:\n",
                "        filtered = filtered[filtered['type'].str.contains(type_, case=False, na=False)]\n",
                "    if query:\n",
                "        filtered = filtered[filtered['content'].astype(str).str.contains(query, case=False, na=False)]\n",
                "        \n",
                "    print(f'🔍 Resultados encontrados: {len(filtered)}')\n",
                "    return filtered[['conversation_id', 'line_num', 'source', 'type', 'content']]\n",
                "\n",
                "# Exemplo de busca: procurar referências a 'detranscriptor' ou 'agentapi'\n",
                "search_brain(df, query='detranscriptor').head(10)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Visualizador Completo de uma Conversa (Transcript Stream)\n",
                "Exibe a sequência temporal limpa de mensagens de uma conversa específica."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "def print_conversation(df: pd.DataFrame, conversation_id: str, max_chars: int = 500):\n",
                "    \"\"\"Imprime em formato legível todas as interações de uma determinada conversa.\"\"\"\
                "    conv_df = df[df['conversation_id'] == conversation_id].sort_values('line_num')\n",
                "    print(f'=== CONVERSATION: {conversation_id} ({len(conv_df)} eventos) ===\\n')\n",
                "    \n",
                "    for idx, row in conv_df.iterrows():\n",
                "        source = row['source']\n",
                "        type_ = row['type']\n",
                "        content = str(row['content']).strip()\n",
                "        if len(content) > max_chars:\n",
                "            content = content[:max_chars] + f'... [trucado, total: {len(row[\"content\"])} chars]'\n",
                "            \n",
                "        print(f'[{row[\"line_num\"]:03d}] [{source} / {type_}]')\n",
                "        print(f'{content}')\n",
                "        print('-' * 80)\n",
                "\n",
                "# Pegar a conversa mais recente do resumo\n",
                "latest_conv = df_summary.iloc[0]['conversation_id']\n",
                "print_conversation(df, latest_conv, max_chars=300)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Interface Interativa Widgets (Opcional)\n",
                "Tenta renderizar controles interativos (dropdown e caixa de busca) caso `ipywidgets` esteja instalado no ambiente."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "try:\n",
                "    import ipywidgets as widgets\n",
                "    from IPython.display import display, HTML\n",
                "\n",
                "    conv_options = [('Mais Recentes...', '')] + [(f\"{r['conversation_id']} ({r['total_steps']} msgs)\", r['conversation_id']) for _, r in df_summary.iterrows()]\n",
                "    \n",
                "    conv_dropdown = widgets.Dropdown(options=conv_options, description='Conversa:', layout={'width': '500px'})\n",
                "    search_input = widgets.Text(description='Buscar:', placeholder='termo de busca...')\n",
                "    output = widgets.Output()\n",
                "\n",
                "    def on_change(change):\n",
                "        with output:\n",
                "            output.clear_output()\n",
                "            res = search_brain(df, query=search_input.value or None, conversation_id=conv_dropdown.value or None)\n",
                "            display(res.head(20))\n",
                "\n",
                "    conv_dropdown.observe(on_change, names='value')\n",
                "    search_input.observe(on_change, names='value')\n",
                "    \n",
                "    display(widgets.VBox([conv_dropdown, search_input, output]))\n",
                "    on_change(None)\n",
                "except Exception as e:\n",
                "    print(f'Nota: ipywidgets não disponível ou erro de exibição ({e}). Use as funções Python acima (search_brain, print_conversation).')"
            ]
        }
    ],
    "metadata": {
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

output_path = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/playground/isb.ai/brain_browser.ipynb")
output_path.write_text(json.dumps(notebook, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Gerado notebook em: {output_path}")
