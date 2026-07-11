#!/usr/bin/env python3
"""Script to process, rename, and move reference markdown files grouped by set name from backup directories."""

import re
import shutil
from collections import defaultdict
from pathlib import Path

# --- Config ---
REFERENCES_DIR = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/PES/.agents/skills/stangler-doctor/references")
SEPARATOR = "--------------------------------------------------------------------------------"

def main():
    print(f"Scanning references directory: {REFERENCES_DIR}")
    
    if not REFERENCES_DIR.exists():
        print(f"Error: References directory {REFERENCES_DIR} does not exist!")
        return

    # Find all backup directories matching *-backup-YYYY-MM-DD
    backup_dirs = [
        d for d in REFERENCES_DIR.iterdir()
        if d.is_dir() and re.search(r"-backup-\d{4}-\d{2}-\d{2}$", d.name)
    ]

    if not backup_dirs:
        print("No backup directories matching '-backup-YYYY-MM-DD' found!")
        return

    print(f"Found {len(backup_dirs)} backup directories to process:")
    for d in backup_dirs:
        print(f"  - {d.name}")

    # Process each backup directory independently
    for backup_dir in backup_dirs:
        # Determine the target set name
        set_name = re.sub(r"-backup-\d{4}-\d{2}-\d{2}$", "", backup_dir.name)
        
        # Apply the XX-YY-rest_of_name mask
        match_pattern = re.match(r"^(\d+)\.(\d+)\.\s*(.*)$", set_name)
        if match_pattern:
            xx = f"{int(match_pattern.group(1)):02d}"
            yy = f"{int(match_pattern.group(2)):02d}"
            rest_of_name = match_pattern.group(3).lower()
            formatted_set_name = f"{xx}-{yy} {rest_of_name}"
        else:
            formatted_set_name = set_name

        print(f"\n==========================================")
        print(f"Processing Set: '{formatted_set_name}' (Original: '{set_name}')")
        print(f"Source: {backup_dir.name}")
        print(f"==========================================")

        # Find all markdown files in this backup directory
        files_in_dir = list(backup_dir.glob("*.md"))
        if not files_in_dir:
            print(f"  No markdown files found in {backup_dir.name}!")
            continue

        # Parse and group files
        grouped_files = []
        for p in files_in_dir:
            match = re.match(r"^(\d+)-", p.name)
            if match:
                num = int(match.group(1))
                
                # Extract the final number from the end of the filename (before .md)
                num_match = re.search(r"(\d+)\.md$", p.name)
                if num_match:
                    final_num = num_match.group(1)
                else:
                    final_num = str(num)
                
                # Construct renamed filename directly under the references root
                renamed_filename = f"{formatted_set_name} {final_num}.md"
                
                grouped_files.append({
                    "num": num,
                    "path": p,
                    "renamed_filename": renamed_filename,
                    "set_name": formatted_set_name
                })
            else:
                # If a file doesn't start with a number, just copy it to target
                dest = REFERENCES_DIR / p.name
                shutil.copy2(p, dest)
                p.unlink()
                print(f"  Moved non-sequenced file directly: {p.name} -> {dest.name}")

        if not grouped_files:
            print("  No sequenced files found to process in this directory.")
            # Clean up empty backup dir
            if not list(backup_dir.iterdir()):
                backup_dir.rmdir()
            continue

        # Sort files in group by their sequence number
        grouped_files.sort(key=lambda x: x["num"])

        # Load files and split by separator
        files_articles = []
        original_total_articles = 0
        for item in grouped_files:
            p = item["path"]
            content = p.read_text(encoding="utf-8")
            articles = content.split(SEPARATOR)
            original_total_articles += len(articles)
            print(f"  File {p.name}: {len(articles)} articles found.")
            files_articles.append({
                "item": item,
                "articles": articles
            })

        # Re-organize (shift last article of file i to the start of file i+1 if there's more than one article)
        shifts_performed = 0
        for i in range(len(files_articles) - 1):
            if len(files_articles[i]["articles"]) > 1:
                last_article = files_articles[i]["articles"].pop()
                files_articles[i+1]["articles"][0] = last_article + files_articles[i+1]["articles"][0]
                shifts_performed += 1
            else:
                print(f"  Warning: File {files_articles[i]['item']['path'].name} has only 1 article. Skipping shift to avoid empty file.")

        # Verify article counts
        new_total_articles = sum(len(f["articles"]) for f in files_articles)
        expected_articles = original_total_articles - shifts_performed
        assert new_total_articles == expected_articles, (
            f"Set '{set_name}': Expected {expected_articles} articles, but got {new_total_articles}"
        )

        # Write new files
        original_paths_to_delete = []
        for f_art in files_articles:
            item = f_art["item"]
            old_path = item["path"]

            # Save directly under REFERENCES_DIR
            new_path = REFERENCES_DIR / item["renamed_filename"]

            # Join articles and write
            new_content = SEPARATOR.join(f_art["articles"])
            new_path.write_text(new_content, encoding="utf-8")
            print(f"    Saved: {new_path.relative_to(REFERENCES_DIR.parent)}")

            assert new_path.exists(), f"Target file {new_path} does not exist after writing!"
            original_paths_to_delete.append(old_path)

        # Clean up original files for this set
        print("  Cleaning up original files in backup directory...")
        for old_path in original_paths_to_delete:
            old_path.unlink()
            print(f"    Deleted original: {old_path.name}")

        # Remove the backup directory if it's now empty
        if not list(backup_dir.iterdir()):
            backup_dir.rmdir()
            print(f"  Removed empty backup directory: {backup_dir.name}")
        else:
            print(f"  Warning: Backup directory {backup_dir.name} not empty, did not remove.")

    print("\nAll sets processed successfully!")

if __name__ == "__main__":
    main()
