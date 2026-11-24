# Comprehensive Disk Space Diagnosis Report
Generated on: Tue Nov 24 10:44:32 AM -03 2026
Target: System `/` and `/home/stangler` (Excluding: `/home/stangler/gamer_d`)

## 1. Partition Disk Usage
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  116G   89G   22G  81% /
/dev/nvme0n1p2  116G   89G   22G  81% /
```

## 2. Swapfile Memory Allocation
- `/swap.img` file size: **32.00 GB**
```text
NAME      TYPE SIZE USED PRIO
/swap.img file  32G 5.5G   -1
```
> [!WARNING]
> `/swap.img` is currently allocating **32.00 GB** on the root SSD.
> For a 116 GB root drive, this consumes ~28% of total storage. Reducing or moving swap can free 16-24 GB.


## 3. Temporary Media Artifacts in `/tmp`
**Total space trapped in `/tmp`:** **0.00 B**

_No large temporary media files found in `/tmp`._

## 4. Inactive Snap Package Revisions (`/var/lib/snapd/snaps`)
**Reclaimable space from disabled snap revisions:** **0.00 B**

_No disabled snap revisions found._

## 5. System Level Caches
- **Systemd Journal (`/var/log/journal`)**: **88.00 MB**
- **APT Package Cache (`/var/cache/apt/archives`)**: **307.59 MB**
- **Flatpak Runtimes (`/var/lib/flatpak`)**: **1.05 GB**

## 6. User Profile & Development Caches
- **Google Chrome Cache** (`/home/stangler/.cache/google-chrome`): **437.67 MB**
- **Antigravity IDE Conversations** (`/home/stangler/.gemini/antigravity-ide/conversations`): **3.20 GB**
- **Antigravity IDE Browser Recordings** (`/home/stangler/.gemini/antigravity-ide/browser_recordings`): **0.00 B**
- **Antigravity Browser Profile** (`/home/stangler/.gemini/antigravity-browser-profile`): **1.15 GB**
- **NPM Cache** (`/home/stangler/.npm`): _Not Found_
- **UV Cache** (`/home/stangler/.local/share/uv`): **200.50 MB**
- **Hugging Face Cache** (`/home/stangler/.cache/huggingface`): _Not Found_
- **Whisper Cache** (`/home/stangler/.cache/whisper`): _Not Found_
- **Steam Data & Shaders** (`/home/stangler/.local/share/Steam`): **8.84 GB**
- **Standard ~/.cache Folder** (`/home/stangler/.cache`): **607.42 MB**

## 7. Top 12 Largest Home Subdirectories (excluding gamer_d)
- `.local`: **11.21 GB**
- `.gemini`: **10.24 GB**
- `.config`: **6.77 GB**
- `.vscode`: **1.60 GB**
- `.antigravity`: **1.01 GB**
- `.antigravity-ide`: **975.44 MB**
- `.hermes`: **792.88 MB**
- `.cache`: **607.42 MB**
- `.isb-ai-chrome-profile`: **420.72 MB**
- `.nvm`: **368.09 MB**
- `snap`: **328.07 MB**
- `Pictures`: **154.01 MB**
