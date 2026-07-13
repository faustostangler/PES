import csv
import time
import sys
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set headless backend
import matplotlib.pyplot as plt

TIME_LOG_PATH = Path(__file__).parent / "time_log.csv"
TIME_LOG_CHART_PATH = Path(__file__).parent / "time_log_chart.png"


def log_time_data(set_name: str, block_idx: int, total_blocks: int, percent: float, elapsed: float, remaining: float | None):
    """Logs progress tracking data to a CSV file for performance and trend analysis."""
    file_exists = TIME_LOG_PATH.exists()
    
    # Calculate estimated total time
    estimated_total = elapsed + remaining if remaining is not None else None
    
    row = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "set_name": set_name,
        "block_idx": block_idx,
        "total_blocks": total_blocks,
        "percent": round(percent, 2),
        "elapsed_seconds": round(elapsed, 2),
        "estimated_remaining_seconds": round(remaining, 2) if remaining is not None else "",
        "estimated_total_seconds": round(estimated_total, 2) if estimated_total is not None else ""
    }
    
    headers = [
        "timestamp", "set_name", "block_idx", "total_blocks", "percent", 
        "elapsed_seconds", "estimated_remaining_seconds", "estimated_total_seconds"
    ]
    
    try:
        with open(TIME_LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"Warning: Failed to write time log: {e}", file=sys.stderr)


def plot_time_log():
    """Generates a beautiful multi-panel stacked area chart (one panel per set)."""
    if not TIME_LOG_PATH.exists():
        return
        
    try:
        df = pd.read_csv(TIME_LOG_PATH)
    except Exception:
        return
        
    if df.empty:
        return

    # Convert fields to numeric
    df['block_idx'] = pd.to_numeric(df['block_idx'], errors='coerce')
    df['percent'] = pd.to_numeric(df['percent'], errors='coerce')
    df['elapsed_seconds'] = pd.to_numeric(df['elapsed_seconds'], errors='coerce')
    df['estimated_remaining_seconds'] = pd.to_numeric(df['estimated_remaining_seconds'], errors='coerce')
    df['estimated_total_seconds'] = pd.to_numeric(df['estimated_total_seconds'], errors='coerce')
    
    # Drop rows without block_idx or elapsed_seconds
    df = df.dropna(subset=['block_idx', 'elapsed_seconds', 'set_name']).reset_index(drop=True)
    
    if df.empty:
        return
        
    df['estimated_remaining_seconds'] = df['estimated_remaining_seconds'].fillna(0)
    df['estimated_total_seconds'] = df['estimated_total_seconds'].fillna(df['elapsed_seconds'])

    # Clean and sanitize data per set to prevent overlapping blocks and time regression bugs in subplots
    cleaned_dfs = []
    for s_name in df['set_name'].unique():
        df_set = df[df['set_name'] == s_name].copy()
        
        # Discard any "future" orphan blocks from previous aborted runs that went further
        if not df_set.empty:
            last_recorded_block = df_set['block_idx'].iloc[-1]
            df_set = df_set[df_set['block_idx'] <= last_recorded_block]
            
        # Drop duplicates of block_idx keeping the last (most recent) run record
        df_set = df_set.drop_duplicates(subset=['block_idx'], keep='last')
        # Sort by block index to ensure monotonic progress on the X-axis
        df_set = df_set.sort_values(by='block_idx').reset_index(drop=True)
        # Prevent elapsed time regressions (due to session restarts or clock drifts)
        df_set['elapsed_seconds'] = df_set['elapsed_seconds'].cummax()
        # Re-align estimated remaining seconds based on the raw estimated total
        df_set['estimated_remaining_seconds'] = (df_set['estimated_total_seconds'] - df_set['elapsed_seconds']).clip(lower=0)
        
        # Ensure the plot starts at 0% progress to avoid whitespace cuts at the beginning of the chart
        if not df_set.empty and df_set['percent'].iloc[0] > 0:
            first_row = df_set.iloc[0].copy()
            first_row['percent'] = 0.0
            first_row['block_idx'] = 0
            first_row['elapsed_seconds'] = 0.0
            first_row['estimated_total_seconds'] = df_set['estimated_total_seconds'].iloc[0]
            first_row['estimated_remaining_seconds'] = first_row['estimated_total_seconds']
            df_set = pd.concat([pd.DataFrame([first_row]), df_set], ignore_index=True)
            
        cleaned_dfs.append(df_set)
        
    if cleaned_dfs:
        df = pd.concat(cleaned_dfs, ignore_index=True)

    # Get unique sets in reverse chronological order (most recent on top, oldest on bottom)
    unique_sets = list(df['set_name'].unique())[::-1]
    # Limit to the 5 most recent runs to keep the chart clean and readable
    unique_sets = unique_sets[:5]
    num_sets = len(unique_sets)
    
    if num_sets == 0:
        return
        
    # Style configuration for Premium Look
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # Adjust figure height dynamically depending on the number of sets
    fig, axes = plt.subplots(nrows=num_sets, ncols=1, figsize=(10, 3.5 * num_sets), dpi=150, sharex=True)
    
    # Handle single subplot case where axes is not a list
    if num_sets == 1:
        axes = [axes]
        
    color_elapsed = '#4f46e5'  # indigo
    color_remaining = '#06b6d4'  # cyan
    
    for idx, (set_name, ax) in enumerate(zip(unique_sets, axes)):
        df_set = df[df['set_name'] == set_name].reset_index(drop=True)
        
        x = df_set['percent']
        y_elapsed = df_set['elapsed_seconds'] / 60
        y_remaining = df_set['estimated_remaining_seconds'] / 60
        y_total = df_set['estimated_total_seconds'] / 60
        
        ax.stackplot(x, y_elapsed, y_remaining, 
                     labels=['Elapsed (m)', 'Est. Remaining (m)'],
                     colors=[color_elapsed, color_remaining], 
                     alpha=0.85,
                     edgecolor='none')
        
        ax.plot(x, y_total, color='#0f172a', linestyle='--', linewidth=1.5, label='Est. Total (m)')
        
        ax.set_title(f"Timing Convergence: {set_name}", fontsize=11, fontweight='bold', pad=8, color='#1e293b')
        ax.set_ylabel("Minutes", fontsize=9, labelpad=8, color='#475569')
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 20, 40, 60, 80, 100])
        ax.tick_params(labelbottom=True)
        
        ax.grid(True, linestyle=':', alpha=0.6, color='#cbd5e1')
        for spine in ax.spines.values():
            spine.set_edgecolor('#e2e8f0')
            
        # Place legend only on the first subplot to save space
        if idx == 0:
            ax.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', framealpha=0.9, fontsize=8)
            
        pass

    # Set common X label on the bottom-most subplot
    axes[-1].set_xlabel("Progress (%)", fontsize=10, labelpad=10, color='#475569')
    
    plt.suptitle("Processing Timing Vibe: Dynamic ETA Convergence", fontsize=13, fontweight='bold', y=0.98, color='#1e293b')
    plt.tight_layout()
    try:
        plt.savefig(TIME_LOG_CHART_PATH, dpi=300)
    finally:
        plt.close(fig)  # prevent memory leaks in loop
