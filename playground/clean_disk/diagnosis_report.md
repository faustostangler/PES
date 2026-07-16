# Disk Space Diagnosis Report
Generated on: Thu Jul 16 05:12:02 PM -03 2026
Target: `/home/stangler` (Excluding: `/home/stangler/gamer_d`)

## Partition Disk Usage (`df -h /home`)
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  116G  112G     0 100% /
```

## Known Cache Directory Sizes
- **UV Cache** (`/home/stangler/.uv_cache`): _Not Found_
- **NPM Cache** (`/home/stangler/.npm`): **1.05 GB**
- **Pip Cache** (`/home/stangler/.cache/pip`): _Not Found_
- **Hugging Face Cache** (`/home/stangler/.cache/huggingface`): _Not Found_
- **Ollama Models (default local path)** (`/home/stangler/.ollama`): **20.28 KB**
- **Cargo/Rust Registry** (`/home/stangler/.cargo`): _Not Found_
- **Antigravity IDE app data (Antigravity logs/caches)** (`/home/stangler/.gemini`): **7.44 GB**
- **Standard user cache folder (~/.cache)** (`/home/stangler/.cache`): **2.29 GB**

## Top 15 Largest Home Subdirectories (excluding gamer_d)
- `.config`: **26.91 GB**
- `.local`: **7.71 GB**
- `.gemini`: **7.44 GB**
- `.cache`: **2.29 GB**
- `.hermes`: **1.81 GB**
- `.vscode`: **1.24 GB**
- `.npm`: **1.05 GB**
- `.antigravity`: **1.01 GB**
- `.antigravity-ide`: **1.00 GB**
- `.nvm`: **368.09 MB**
- `.isb-ai-chrome-profile`: **366.94 MB**
- `snap`: **216.41 MB**
- `Pictures`: **108.17 MB**
- `.cua-driver`: **19.14 MB**
- `Documents`: **10.89 MB**

## Top 20 Largest Files (excluding gamer_d)
- `.config/google-chrome/OptGuideOnDeviceModel/2025.8.21.1028/weights.bin`: **2.67 GB**
- `.gemini/antigravity-browser-profile/OptGuideOnDeviceModel/2025.8.21.1028/weights.bin`: **2.67 GB**
- `.config/google-chrome/OptGuideOnDeviceModel/2025.8.21.1028/cache.bin`: **1.31 GB**
- `.gemini/antigravity-browser-profile/OptGuideOnDeviceModel/2025.8.21.1028/cache.bin`: **1.31 GB**
- `.local/share/Steam/ubuntu12_64/libcef.so`: **209.28 MB**
- `.hermes/hermes-agent/apps/desktop/node_modules/electron/dist/electron`: **193.58 MB**
- `.vscode/extensions/google.geminicodeassist-2.72.0/cloudcode_cli.zip`: **189.32 MB**
- `.local/share/AnkiProgramFiles/.venv/lib/python3.13/site-packages/PyQt6/Qt6/lib/libQt6WebEngineCore.so.6`: **177.27 MB**
- `.local/share/AnkiProgramFiles/cache/archive-v0/q3A4AtDuMgZskQ2NPVqLJ/PyQt6/Qt6/lib/libQt6WebEngineCore.so.6`: **177.27 MB**
- `.cache/whisper/base.pt`: **138.53 MB**
- `.config/google-chrome/OptGuideOnDeviceClassifierModel/2026.2.12.1554/weights.bin`: **120.19 MB**
- `.config/google-chrome/component_crx_cache/fd3d52862a925cd5166f8b976949ed41c4aba299b0d1daf465cc3a8f2c5d5d95`: **119.14 MB**
- `.vscode/cli/servers/Stable-ce099c1ed25d9eb3076c11e4a280f3eb52b4fbeb/server/node`: **117.69 MB**
- `.nvm/versions/node/v24.14.1/bin/node`: **116.83 MB**
- `.cache/ms-playwright-go/1.57.0/node`: **115.51 MB**
- `.cache/ms-playwright-go/1.50.1/node`: **114.52 MB**
- `.cache/electron/3978a3c4a2965533dc07f99112894e7e7f80c9ea0f13e2a48cd5a29593568fb2/electron-v40.10.2-linux-x64.zip`: **109.71 MB**
- `.cache/evolution/calendar/852304363bcea5a92529459db585ff580d4b846b/cache.db`: **87.92 MB**
- `.local/share/Steam/package/webkit_ubuntu12.zip.vz.d96a6cf40707276b58972e67fcdfa1eca50893fc_89711046`: **85.56 MB**
- `.local/share/Steam/package/runtime_steamrt_ubuntu12.zip.vz.dde7d029d01806ad08a1fe7b7d544e1312782fad_78132074`: **74.51 MB**

## Docker Disk Usage (`docker system df`)
```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          4         1         1.633GB   1.528GB (93%)
Containers      1         0         135.6MB   135.6MB (100%)
Local Volumes   0         0         0B        0B
Build Cache     0         0         0B        0B
```
