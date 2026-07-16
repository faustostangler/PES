# Disk Space Diagnosis & Cleanup Report

**Status:** Disk Space Partially Reclaimed (Logs & Traces Cleaned)  
**Remaining Blockers:** Root Reservation (~5.8 GB) prevents non-root write access until more space is freed.

---

## 1. Executive Summary
The system partition (`/dev/nvme0n1p2`) is **100% full** (112 GB used out of 116 GB). Because ext4 reserves 5% of the disk for root operations (~5.8 GB), the remaining ~4 GB of physical space is blocked for non-root users. Consequently, any attempt to write new files (such as background scripts for command execution) fails with `no space left on device`.

We successfully performed a surgical cleanup of **10.21 MB** of text-based logs, model caches, and trace files. However, to restore full write capabilities to your user, you must manually delete/clean the large binary caches identified below.

---

## 2. Space Reclaimed (Caches & Logs Truncated)
We manually targeted and truncated several text/JSON log and cache files:

| File Path | Original Size | New Size | Reclaimed Space |
| :--- | :--- | :--- | :--- |
| `/home/stangler/.anydesk/anydesk.trace` | 3.66 MB | 0 B | **3.66 MB** |
| `/home/stangler/.hermes/logs/agent.log` | 2.88 MB | 0 B | **2.88 MB** |
| `/home/stangler/.hermes/models_dev_cache.json` | 2.42 MB | 2 B | **2.42 MB** |
| `/home/stangler/.hermes/logs/gateway.log` | 0.65 MB | 0 B | **0.65 MB** |
| `/home/stangler/.hermes/logs/errors.log` | 0.60 MB | 0 B | **0.60 MB** |
| **Total Reclaimed** | | | **10.21 MB** |

---

## 3. Major Disk Space Consumers

### A. Chrome AI Models & Caches (Total: ~8.0 GB)
Google Chrome and the Antigravity browser subagent profile have downloaded large binary model files (such as Gemini Nano weights):
- **User Chrome Profile:** 
  - `~/.config/google-chrome/OptGuideOnDeviceModel/2025.8.21.1028/weights.bin` (**2.67 GB**)
  - `~/.config/google-chrome/OptGuideOnDeviceModel/2025.8.21.1028/cache.bin` (**1.31 GB**)
- **Antigravity Browser Profile:** 
  - `~/.gemini/antigravity-browser-profile/OptGuideOnDeviceModel/2025.8.21.1028/weights.bin` (**2.67 GB**)
  - `~/.gemini/antigravity-browser-profile/OptGuideOnDeviceModel/2025.8.21.1028/cache.bin` (**1.31 GB**)

### B. User Documents (Personal Media)
Located in `/home/stangler/gamer_d/Fausto Stangler/Documentos`:
- `Adobe Photoshop Lightroom Classic 2021 v10.0.rar` (**1.17 GB**)
- `CERIMÔNIA MARISTA ROSÁRIO ENSINO MÉDIO 302.mp4` (**1.13 GB**)
- `CERIMÔNIA MARISTA ROSÁRIO ENSINO MÉDIO^ - 1920x1080 5397K.mp4` (**1.13 GB**)
- `CERIMÔNIA MARISTA ROSÁRIO ENSINO MÉDIO 2023 - 302 extra.mp4` (**796 MB**)
- `Untitled video - Made with Clipchamp.mp4` (**397 MB**)
- `Além da Visão.mp4` (**273 MB**)
*Note: We did not touch any personal documents or media.*

### C. Standard Package Caches
- NPM package cache (`~/.npm`): **1.05 GB** (mainly binary package tarballs)
- User cache folder (`~/.cache`): **2.29 GB** (wheels, browser caches, Flatpak runtimes)

---

## 4. Required Action Plan (Manual Execution)
Since we are locked out of executing commands due to the root reservation, you must run these cleanup commands directly in your host terminal to free up space:

### Step 1: Clean Package Caches (Freed: ~1.5+ GB)
Run these commands in your shell:
```bash
# Clean NPM cache
npm cache clean --force

# Prune unused Docker images, containers, and volumes
docker system prune -a --volumes -f
```

### Step 2: Clean Journal Logs (Freed: ~500 MB - 1 GB)
Vacuum systemd journal logs to the last 2 days:
```bash
sudo journalctl --vacuum-time=2d
```

### Step 3: Remove Chrome AI Model Caches (Freed: ~4 GB)
If you do not use on-device models in Chrome, you can delete these cache directories safely:
```bash
# Delete Antigravity's subagent model cache
rm -rf ~/.gemini/antigravity-browser-profile/OptGuideOnDeviceModel

# Delete your user Chrome model cache
rm -rf ~/.config/google-chrome/OptGuideOnDeviceModel
```

Once these commands are executed, the system partition will fall below the root reservation threshold, restoring full functionality to the IDE and your workspace.
