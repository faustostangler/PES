# Disk Space Diagnosis Report
Generated on: Sun Jul 19 11:58:42 AM -03 2026
Target: `/home/stangler` (Excluding: `/home/stangler/gamer_d`)

## Partition Disk Usage (`df -h /home`)
```text
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  116G   93G   18G  85% /
```

## Known Cache Directory Sizes
- **UV Cache** (`/home/stangler/.uv_cache`): _Not Found_
- **NPM Cache** (`/home/stangler/.npm`): _Not Found_
- **Pip Cache** (`/home/stangler/.cache/pip`): _Not Found_
- **Hugging Face Cache** (`/home/stangler/.cache/huggingface`): _Not Found_
- **Ollama Models (default local path)** (`/home/stangler/.ollama`): **20.28 KB**
- **Cargo/Rust Registry** (`/home/stangler/.cargo`): _Not Found_
- **Antigravity IDE app data (Antigravity logs/caches)** (`/home/stangler/.gemini`): **3.57 GB**
- **Standard user cache folder (~/.cache)** (`/home/stangler/.cache`): **2.06 GB**

## Top 15 Largest Home Subdirectories (excluding gamer_d)
- `.local`: **7.68 GB**
- `.config`: **4.76 GB**
- `.gemini`: **3.57 GB**
- `.cache`: **2.06 GB**
- `.hermes`: **1.79 GB**
- `.vscode`: **1.24 GB**
- `.antigravity`: **1.01 GB**
- `.antigravity-ide`: **1.00 GB**
- `.isb-ai-chrome-profile`: **373.46 MB**
- `.nvm`: **368.09 MB**
- `snap`: **237.34 MB**
- `Pictures`: **108.23 MB**
- `.cua-driver`: **19.14 MB**
- `Documents`: **10.89 MB**
- `.playwright-mcp`: **9.75 MB**

## Top 20 Largest Files (excluding gamer_d)
- `.local/share/Steam/ubuntu12_64/libcef.so`: **209.28 MB**
- `.hermes/hermes-agent/apps/desktop/node_modules/electron/dist/electron`: **193.58 MB**
- `.vscode/extensions/google.geminicodeassist-2.72.0/cloudcode_cli.zip`: **189.32 MB**
- `.local/share/AnkiProgramFiles/.venv/lib/python3.13/site-packages/PyQt6/Qt6/lib/libQt6WebEngineCore.so.6`: **177.27 MB**
- `.local/share/AnkiProgramFiles/cache/archive-v0/q3A4AtDuMgZskQ2NPVqLJ/PyQt6/Qt6/lib/libQt6WebEngineCore.so.6`: **177.27 MB**
- `.config/google-chrome/component_crx_cache/fd3d52862a925cd5166f8b976949ed41c4aba299b0d1daf465cc3a8f2c5d5d95`: **119.14 MB**
- `.vscode/cli/servers/Stable-ce099c1ed25d9eb3076c11e4a280f3eb52b4fbeb/server/node`: **117.69 MB**
- `.nvm/versions/node/v24.14.1/bin/node`: **116.83 MB**
- `.cache/evolution/calendar/852304363bcea5a92529459db585ff580d4b846b/cache.db`: **87.96 MB**
- `.local/share/Steam/package/webkit_ubuntu12.zip.vz.d96a6cf40707276b58972e67fcdfa1eca50893fc_89711046`: **85.56 MB**
- `.local/share/Steam/package/runtime_steamrt_ubuntu12.zip.vz.dde7d029d01806ad08a1fe7b7d544e1312782fad_78132074`: **74.51 MB**
- `.antigravity/extensions/devsense.intelli-php-vscode-0.12.17700-linux-x64/out/server/models/intelliphp_v3/model.onnx`: **73.47 MB**
- `.antigravity-ide/extensions/devsense.intelli-php-vscode-0.12.17700-linux-x64/out/server/models/intelliphp_v3/model.onnx`: **73.47 MB**
- `.config/google-chrome/optimization_guide_model_store/40/E6DC4029A1E4B4C1/0B2C0A75B37A3A9E/ts.bin`: **71.39 MB**
- `.local/share/Steam/steamapps/common/Proton - Experimental/files/share/wine/gecko/wine-gecko-2.47.4-x86/xul.dll`: **68.44 MB**
- `.local/share/Steam/steamapps/common/Proton - Experimental/files/share/wine/gecko/wine-gecko-2.47.4-x86_64/xul.dll`: **67.23 MB**
- `.hermes/bin/uv`: **61.34 MB**
- `.local/share/Steam/package/runtime_scout_ubuntu12.zip.3375cf3a02dffc8405f3ef5411a36ed6b9bf1b16`: **60.49 MB**
- `.local/share/Steam/ubuntu12_32/steam-runtime.tar.xz`: **60.48 MB**
- `.hermes/hermes-agent/.git/objects/pack/pack-18b290d261a8ad750595207fb2fea6f9bfdc1ff4.pack`: **53.83 MB**

## Docker Disk Usage (`docker system df`)
```text
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          0         0         0B        0B
Containers      0         0         0B        0B
Local Volumes   0         0         0B        0B
Build Cache     0         0         0B        0B
```
