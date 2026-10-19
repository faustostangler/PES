# Comprehensive Disk Space Diagnosis Report
Generated on: Mon Oct 19 12:46:47 PM -03 2026
Target: System `/` and `/home/stangler` (Excluding: `/home/stangler/gamer_d`)

## 1. Partition Disk Usage
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  116G  103G  7.7G  94% /
/dev/nvme0n1p2  116G  103G  7.7G  94% /
```

## 2. Swapfile Memory Allocation
- `/swap.img` file size: **32.00 GB**
```text
NAME      TYPE SIZE USED PRIO
/swap.img file  32G  12G   -1
```
> [!WARNING]
> `/swap.img` is currently allocating **32.00 GB** on the root SSD.
> For a 116 GB root drive, this consumes ~28% of total storage. Reducing or moving swap can free 16-24 GB.


## 3. Temporary Media Artifacts in `/tmp`
**Total space trapped in `/tmp`:** **0.00 B**

_No large temporary media files found in `/tmp`._

## 4. Inactive Snap Package Revisions (`/var/lib/snapd/snaps`)
**Reclaimable space from disabled snap revisions:** **1.49 GB**

- `core26_462.snap` (disabled): **60.05 MB**
- `cups_1262.snap` (disabled): **50.74 MB**
- `firefox_8995.snap` (disabled): **262.22 MB**
- `firmware-updater_258.snap` (disabled): **12.70 MB**
- `google-cloud-cli_509.snap` (disabled): **348.46 MB**
- `musescore_255.snap` (disabled): **617.34 MB**
- `obsidian_68.snap` (disabled): **110.64 MB**
- `snap-store_1427.snap` (disabled): **11.83 MB**
- `snapd_27738.snap` (disabled): **50.27 MB**

## 5. System Level Caches
- **Systemd Journal (`/var/log/journal`)**: **2.91 GB**
- **APT Package Cache (`/var/cache/apt/archives`)**: **498.74 MB**
- **Flatpak Runtimes (`/var/lib/flatpak`)**: **7.37 GB**

## 6. User Profile & Development Caches
- **Google Chrome Cache** (`/home/stangler/.cache/google-chrome`): **1.51 GB**
- **Antigravity IDE Conversations** (`/home/stangler/.gemini/antigravity-ide/conversations`): **3.14 GB**
- **Antigravity IDE Browser Recordings** (`/home/stangler/.gemini/antigravity-ide/browser_recordings`): **0.00 B**
- **Antigravity Browser Profile** (`/home/stangler/.gemini/antigravity-browser-profile`): **1.35 GB**
- **NPM Cache** (`/home/stangler/.npm`): **655.63 MB**
- **UV Cache** (`/home/stangler/.local/share/uv`): **563.18 MB**
- **Hugging Face Cache** (`/home/stangler/.cache/huggingface`): **132.62 MB**
- **Whisper Cache** (`/home/stangler/.cache/whisper`): **138.53 MB**
- **Steam Data & Shaders** (`/home/stangler/.local/share/Steam`): **8.14 GB**
- **Standard ~/.cache Folder** (`/home/stangler/.cache`): **2.62 GB**

## 7. Top 12 Largest Home Subdirectories (excluding gamer_d)
- `.config`: **12.95 GB**
- `.local`: **10.35 GB**
- `.gemini`: **5.84 GB**
- `.cache`: **2.62 GB**
- `photoprism`: **1.92 GB**
- `.hermes`: **1.89 GB**
- `.antigravity-ide`: **1.05 GB**
- `.antigravity`: **1.01 GB**
- `.vscode`: **819.89 MB**
- `.npm`: **655.63 MB**
- `.isb-ai-chrome-profile`: **420.72 MB**
- `.nvm`: **368.09 MB**
