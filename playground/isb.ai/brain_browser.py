#!/usr/bin/env python3
"""Antigravity Brain Transcript DataFrame Navigator & CLI Helper.

Reads all `.system_generated/logs/transcript.jsonl` files in
`/home/stangler/.gemini/antigravity-ide/brain` and loads them into a pandas DataFrame.
"""

import json
import os
import sys
from pathlib import Path
import pandas as pd

BRAIN_DIR = Path('/home/stangler/.gemini/antigravity-ide/brain')


def load_brain_df(brain_dir: Path = BRAIN_DIR) -> pd.DataFrame:
    """Recursively search and parse all transcript.jsonl files into a pandas DataFrame."""
    records = []
    log_files = sorted(brain_dir.glob('*/.system_generated/logs/transcript.jsonl'))

    print(f"🔍 Discovered {len(log_files)} transcript.jsonl log files in {brain_dir}")

    for log_path in log_files:
        conv_id = log_path.parent.parent.parent.name
        mtime = os.path.getmtime(log_path)

        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            for line_idx, line in enumerate(f, 1):
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    rec = {
                        'conversation_id': conv_id,
                        'line_num': line_idx,
                        'source': data.get('source', ''),
                        'type': data.get('type', ''),
                        'created_at': data.get('created_at', ''),
                        'status': data.get('status', ''),
                        'content': data.get('content', ''),
                        'thinking': data.get('thinking', ''),
                        'tool_calls': data.get('tool_calls', []),
                        'log_path': str(log_path),
                        'file_mtime': mtime,
                    }
                    records.append(rec)
                except Exception:
                    continue

    df = pd.DataFrame(records)
    print(f"✅ Successfully loaded {len(df):,} log entries across {df['conversation_id'].nunique()} conversations.")
    return df


def summarize_conversations(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize log DataFrame by conversation_id."""
    summaries = []
    for conv_id, group in df.groupby('conversation_id'):
        user_msgs = group[group['source'].astype(str).str.contains('USER', na=False)]
        first_prompt = user_msgs.iloc[0]['content'] if not user_msgs.empty else ''
        first_prompt_clean = str(first_prompt).replace('\n', ' ')[:100]

        summaries.append({
            'conversation_id': conv_id,
            'total_entries': len(group),
            'user_entries': len(user_msgs),
            'model_entries': len(group[group['source'] == 'MODEL']),
            'first_user_prompt': first_prompt_clean,
            'last_modified': pd.to_datetime(group['file_mtime'].iloc[0], unit='s'),
        })

    return pd.DataFrame(summaries).sort_values(by='last_modified', ascending=False).reset_index(drop=True)


def search_transcripts(df: pd.DataFrame, query: str = None, conv_id: str = None, source: str = None) -> pd.DataFrame:
    """Search and filter the transcripts DataFrame."""
    res = df.copy()
    if conv_id:
        res = res[res['conversation_id'].str.contains(conv_id, case=False, na=False)]
    if source:
        res = res[res['source'].str.contains(source, case=False, na=False)]
    if query:
        res = res[res['content'].astype(str).str.contains(query, case=False, na=False)]

    return res[['conversation_id', 'line_num', 'source', 'type', 'content']]


if __name__ == '__main__':
    df = load_brain_df()
    summary = summarize_conversations(df)
    print("\n--- Recent Conversations ---")
    print(summary.head(10).to_string())
