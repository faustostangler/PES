# Disk Space Diagnosis Report
Generated on: Tue Jun 23 09:08:43 AM -03 2026
Target: `/home/stangler` (Excluding: `/home/stangler/gamer_d`)

## Partition Disk Usage (`df -h /home`)
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  116G   85G   25G  78% /
```

## Known Cache Directory Sizes
- **UV Cache** (`/home/stangler/.uv_cache`): _Not Found_
- **NPM Cache** (`/home/stangler/.npm`): **402.86 MB**
- **Pip Cache** (`/home/stangler/.cache/pip`): _Not Found_
- **Hugging Face Cache** (`/home/stangler/.cache/huggingface`): _Not Found_
- **Ollama Models (default local path)** (`/home/stangler/.ollama`): **35.76 KB**
- **Cargo/Rust Registry** (`/home/stangler/.cargo`): _Not Found_
- **Antigravity IDE app data (Antigravity logs/caches)** (`/home/stangler/.gemini`): **8.31 GB**
- **Standard user cache folder (~/.cache)** (`/home/stangler/.cache`): **1.74 GB**

## Top 15 Largest Home Subdirectories (excluding gamer_d)
- `.gemini`: **8.31 GB**
- `.local`: **7.63 GB**
- `.config`: **5.66 GB**
- `.cache`: **1.74 GB**
- `.vscode`: **1.24 GB**
- `.antigravity`: **1.01 GB**
- `.antigravity-ide`: **1.01 GB**
- `.npm`: **402.86 MB**
- `.nvm`: **368.09 MB**
- `snap`: **197.00 MB**
- `Pictures`: **94.17 MB**
- `Downloads`: **50.89 MB**
- `Documents`: **11.13 MB**
- `.playwright-mcp`: **9.75 MB**
- `Videos`: **7.91 MB**

## Top 20 Largest Files (excluding gamer_d)
- `.local/share/Steam/ubuntu12_64/libcef.so`: **209.28 MB**
- `.vscode/extensions/google.geminicodeassist-2.72.0/cloudcode_cli.zip`: **189.32 MB**
- `.local/share/AnkiProgramFiles/.venv/lib/python3.13/site-packages/PyQt6/Qt6/lib/libQt6WebEngineCore.so.6`: **177.27 MB**
- `.local/share/AnkiProgramFiles/cache/archive-v0/q3A4AtDuMgZskQ2NPVqLJ/PyQt6/Qt6/lib/libQt6WebEngineCore.so.6`: **177.27 MB**
- `.cache/whisper/base.pt`: **138.53 MB**
- `.config/google-chrome/component_crx_cache/ab113f11fb73276481842322f8aaaac36824ddb0f1cccb69c6be721ffdd32415`: **120.41 MB**
- `.vscode/cli/servers/Stable-ce099c1ed25d9eb3076c11e4a280f3eb52b4fbeb/server/node`: **117.69 MB**
- `.nvm/versions/node/v24.14.1/bin/node`: **116.83 MB**
- `.cache/ms-playwright-go/1.57.0/node`: **115.51 MB**
- `.cache/ms-playwright-go/1.50.1/node`: **114.52 MB**
- `.cache/evolution/calendar/852304363bcea5a92529459db585ff580d4b846b/cache.db`: **87.85 MB**
- `.local/share/Steam/package/webkit_ubuntu12.zip.vz.d96a6cf40707276b58972e67fcdfa1eca50893fc_89711046`: **85.56 MB**
- `.local/share/Steam/package/runtime_steamrt_ubuntu12.zip.vz.dde7d029d01806ad08a1fe7b7d544e1312782fad_78132074`: **74.51 MB**
- `.antigravity/extensions/devsense.intelli-php-vscode-0.12.17700-linux-x64/out/server/models/intelliphp_v3/model.onnx`: **73.47 MB**
- `.antigravity-ide/extensions/devsense.intelli-php-vscode-0.12.17700-linux-x64/out/server/models/intelliphp_v3/model.onnx`: **73.47 MB**
- `.cache/whisper/tiny.pt`: **72.07 MB**
- `.local/share/Steam/steamapps/common/Proton - Experimental/files/share/wine/gecko/wine-gecko-2.47.4-x86/xul.dll`: **68.44 MB**
- `.local/share/Steam/steamapps/common/Proton - Experimental/files/share/wine/gecko/wine-gecko-2.47.4-x86_64/xul.dll`: **67.23 MB**
- `.local/share/Steam/package/runtime_scout_ubuntu12.zip.3375cf3a02dffc8405f3ef5411a36ed6b9bf1b16`: **60.49 MB**
- `.local/share/Steam/ubuntu12_32/steam-runtime.tar.xz`: **60.48 MB**

## Docker Disk Usage (`docker system df`)
```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          2         0         104.3MB   0B (0%)
Containers      0         0         0B        0B
Local Volumes   17        0         12.87GB   12.87GB (100%)
Build Cache     0         0         0B        0B
```
