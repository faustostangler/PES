#!/usr/bin/env python3
"""Extract workout group and exercises from Bend screenshot into a Pandas DataFrame."""

import re
from pathlib import Path
import pandas as pd
import pytesseract
from PIL import Image

# --- Config ---
IMAGE_DIR = Path(__file__).resolve().parent

# --- Logic ---
def extract_all_workouts(img_dir: Path) -> pd.DataFrame:
    """Process all screenshots in loop, tracking routine groups, descriptions, and extracting exercises."""
    records = []
    current_group = "Unknown"
    current_description = ""

    img_files = sorted(img_dir.glob("*.jpg"))
    print(f"Processing {len(img_files)} images...")

    for i, img_path in enumerate(img_files, 1):
        image = Image.open(img_path)
        raw_text = pytesseract.image_to_string(image)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        # Check for new Group title header (e.g., '> 4 Lower Back 4 =', 'x Lower Back 1 =')
        group_idx = -1
        for line_i, line in enumerate(lines[:8]):
            # Skip exercise lines containing time patterns (e.g. 1:00)
            if re.search(r'\d+:\d+', line):
                continue
            # Strip OCR noise prefix symbols like '> 4 ', '4 ', 'xX ', 'b) *'
            clean_line = re.sub(r'^(?:[>\d×xX\*\)\(]|b\))*\s*', '', line).strip()
            match = re.search(r'^([A-Za-z0-9\s\'&]+?)(?:\s+[=—–\-]\s*|\s+\d+\s+MINUTES|\s*$)', clean_line)
            if match:
                title = match.group(1).strip()
                # Clean leading digit/symbol noise (e.g. '4 Chest 3' -> 'Chest 3')
                title = re.sub(r'^[0-9>\s]+', '', title).strip()
                # Validate if extracted title is a valid routine name
                is_valid_group = (
                    any(w in title.lower() for w in [
                        'back', 'hips', 'core', 'chest', 'neck', 'body', 'shoulder', 
                        'hamstring', 'posture', 'tilt', 'hybrid', 'sleep', 'wake', 
                        'reset', 'desk', 'leg', 'spine', 'stretch'
                    ]) or bool(re.search(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+\d+$', title))
                )
                if is_valid_group and title.upper() not in ["POS", "MINUTES", "SHARE", "FULL", "THE LOWER BACK", "THE HIPS"]:
                    current_group = title
                    group_idx = line_i
                    break

        print(f"[{i}/{len(img_files)}] Group: {current_group} | File: {img_path.name}")

        # Extract Description if a new title header is present in current image
        if group_idx != -1:
            desc_parts = []
            for line in lines[group_idx + 1:]:
                # Stop if line is an exercise line
                if re.search(r'\d+:\d+', line):
                    break
                # Skip duration badge (e.g. 5 MINUTES)
                if re.search(r'\d+\s*MINUTES', line, re.IGNORECASE):
                    continue
                if line.upper() not in ["POS", "SHARE", "FULL"] and len(line) > 3:
                    desc_parts.append(line)
            if desc_parts:
                current_description = " ".join(desc_parts).strip()

        # Extract exercises
        for line in lines:
            ex_match = re.search(r'^\s*(?:[^\w\s]|[0-9oQdá©ø])*\s*([A-Za-z\s\'\(\)/]+?)\s*[-–—=+]+\s*\d+:\d+', line)
            if ex_match:
                ex_name = ex_match.group(1).strip()
                # Clean up OCR icon artifacts before exercise name
                ex_name = re.sub(r'^(?:[^\w\s]|[0-9©øQoASdÁ]|Dre|ay|me|OY|za|dá)+\s+(?=[A-Z])', '', ex_name, flags=re.IGNORECASE).strip()
                if ex_name == 'uad Stretch':
                    ex_name = 'Quad Stretch'
                if ex_name and ex_name.upper() not in ["MINUTES", "SHARE"]:
                    records.append({
                        "Group": current_group,
                        "Description": current_description,
                        "Exercise": ex_name,
                        "Source_File": img_path.name
                    })

    df = pd.DataFrame(records)
    # Deduplicate (Group, Exercise) while preserving order and description
    df_clean = df.drop_duplicates(subset=["Group", "Exercise"]).reset_index(drop=True)
    return df_clean

# --- Main ---
if __name__ == "__main__":
    df = extract_all_workouts(IMAGE_DIR)

    # Sanity checks
    assert not df.empty, "DataFrame should not be empty"
    assert all(col in df.columns for col in ["Group", "Description", "Exercise"])

    # Save output to CSV
    output_csv = IMAGE_DIR / "stretch_groups_exercises.csv"
    df[["Group", "Description", "Exercise"]].to_csv(output_csv, index=False)

    print(f"\n=== Total Extracted Rows (Deduplicated): {len(df)} ===")
    print(f"=== Total Groups Found: {df['Group'].nunique()} ===")
    print(f"Saved results to {output_csv}\n")
    print(df[["Group", "Description", "Exercise"]].head(20).to_string(index=False))

