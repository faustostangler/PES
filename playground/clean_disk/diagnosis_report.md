# Comprehensive Disk Space Diagnosis Report
Generated on: Mon Oct 19 08:47:27 PM -03 2026
Target: System `/` and `/home/stangler` (Excluding: `/home/stangler/gamer_d`)

## 1. Partition Disk Usage
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  116G   93G   18G  85% /
/dev/nvme0n1p2  116G   93G   18G  85% /
```

## 2. Swapfile Memory Allocation
- `/swap.img` file size: **32.00 GB**
```text
NAME      TYPE SIZE USED PRIO
/swap.img file  32G 8.9G   -1
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
- **Systemd Journal (`/var/log/journal`)**: **112.00 MB**
- **APT Package Cache (`/var/cache/apt/archives`)**: **0.00 B**
- **Flatpak Runtimes (`/var/lib/flatpak`)**: **1.05 GB**

## 6. User Profile & Development Caches
- **Google Chrome Cache** (`/home/stangler/.cache/google-chrome`): **8.87 MB**
- **Antigravity IDE Conversations** (`/home/stangler/.gemini/antigravity-ide/conversations`): **3.16 GB**
- **Antigravity IDE Browser Recordings** (`/home/stangler/.gemini/antigravity-ide/browser_recordings`): **0.00 B**
- **Antigravity Browser Profile** (`/home/stangler/.gemini/antigravity-browser-profile`): **1.35 GB**
- **NPM Cache** (`/home/stangler/.npm`): _Not Found_
- **UV Cache** (`/home/stangler/.local/share/uv`): **563.18 MB**
- **Hugging Face Cache** (`/home/stangler/.cache/huggingface`): **132.62 MB**
- **Whisper Cache** (`/home/stangler/.cache/whisper`): _Not Found_
- **Steam Data & Shaders** (`/home/stangler/.local/share/Steam`): **8.14 GB**
- **Standard ~/.cache Folder** (`/home/stangler/.cache`): **1001.18 MB**

## 7. Top 12 Largest Home Subdirectories (excluding gamer_d)
- `.config`: **13.00 GB**
- `.local`: **10.35 GB**
- `.gemini`: **5.87 GB**
- `.hermes`: **1.89 GB**
- `.antigravity`: **1.01 GB**
- `.cache`: **1001.18 MB**
- `.antigravity-ide`: **943.30 MB**
- `.vscode`: **819.89 MB**
- `.isb-ai-chrome-profile`: **420.72 MB**
- `.nvm`: **368.09 MB**
- `snap`: **279.83 MB**
- `Downloads`: **229.90 MB**
