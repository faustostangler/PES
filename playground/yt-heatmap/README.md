# YouTube Heatmap Harvester & Autonomous Graph Crawler

Pipeline automatizado de raspagem, curadoria semântica e corte cirúrgico de micropedaços virais do YouTube baseado no sinal do **Heatmap** (*most replayed*).

---

## 🏗️ Topologia do Grafo e Fluxo de Execução

```
[Vídeo-Semente]
      │
      ▼
[video_pool] ◄────────────────────────────────────────────────────────┐
      │                                                               │
      ▼ (retira próximo vídeo para analisar)                          │
[Análise de Heatmap & Picos Virais] ──> [Download dos Clips MP4/JSON] │
      │                                                               │
      ▼                                                               │
[Vídeos Recomendados na Barra Lateral] (/youtubei/v1/next)            │
      │                                                               │
      ▼                                                               │
[Canais dos Vídeos Recomendados] (extração e desduplicação)           │
      │                                                               │
      ▼                                                               │
[Top-Vídeos Populares de Cada Canal] (/videos)                        │
      │                                                               │
      ▼                                                               │
[Análise Temática do Canal] (Cosine Similarity com Ollama/Embeddings) │
      ├── [REJEITADO] ──> Registra no SQLite e descarta               │
      └── [APROVADO]  ──> Cada Top-N Vídeo + Vídeo Recomendado ───────┘
```

---

## 🚀 Como Executar

### 1. Execução Padrão (com Seed Video ou Pool de Seeds)
```bash
python harvest_heatmaps.py \
  --seed "https://www.youtube.com/watch?v=plExzNxH1Po" \
  --max-channels 10 \
  --max-videos 30 \
  --top-n 50 \
  --min-video-score 0.80 \
  --target-clips 10 \
  --backend ollama

# Exemplo com Pool de Seeds (múltiplos vídeos separados por vírgula):
# python harvest_heatmaps.py --seed "url1,url2,url3"
```

### 2. Parâmetros Disponíveis
| Flag | Padrão | Descrição |
| --- | --- | --- |
| `--seed` | `https://www.youtube.com/watch?v=plExzNxH1Po` | URL única ou lista de URLs/IDs separadas por vírgula para calcular o centróide de seeds |
| `--output-dir` | `clips_harvested` | Pasta onde os cortes e metadados serão salvos |
| `--db-path` | `heatmap_pipeline.sqlite` | Banco SQLite para controle de estado e desduplicação |
| `--max-channels` | `10` | Número máximo de canais aprovados a auditar e minerar |
| `--max-videos` | `0` | Número máximo de vídeos a analisar do pool (`0` para esvaziar todo o pool) |
| `--top-n` | `50` | Quantidade de top-vídeos de cada canal aprovado a inspecionar para o pool |
| `--min-video-score` | `0.80` | Similaridade cosseno mínima do título para o vídeo entrar no pool |
| `--target-clips` | `0` | Meta de cortes a coletar antes de parar (`0` para desativar a meta e esvaziar o pool) |
| `--max-clips` | `0` | Número máximo de picos cortados por vídeo com heatmap (`0` para ilimitado) |
| `--padding-start` | `0.0` | Margem de segurança em segundos adicionada antes do pico |
| `--padding-end` | `0.0` | Margem de segurança em segundos adicionada após o pico |
| `--cutoff-ratio` | `0.0` | Fração inicial do vídeo a descartar (drop-off inicial; 0.0 desativa) |
| `--cutoff-sec` | `0.0` | Segundos iniciais a descartar (drop-off inicial; 0.0 desativa) |
| `--format` | `bestvideo[vcodec^=avc1][height<=720]+bestaudio[acodec^=mp4a]/best[ext=mp4]/18/best` | Formato otimizado de stream para corte sem recodificação pesada |
| `--backend` | `ollama` | Backend de embeddings (`ollama` com `nomic-embed-text` ou `sentence-transformers`) |

---

## 📂 Estrutura de Saída e Persistência Unificada

Toda a persistência de metadados, controle de fila e histórico de auditoria ocorre **estritamente em SQLite**, eliminando arquivos `.json` soltos:

### 1. Arquivos de Vídeo (`clips_harvested/`)
* **Vídeo MP4:** `{canal_id}_{video_id}_peak_{indice}.mp4` (baixado em tempo real via HTTP range requests no trecho exato do pico).

### 2. Banco de Dados SQLite (`heatmap_pipeline.sqlite`)
Tabelas relacionais com suporte a sistemas de arquivos FUSE/NTFS (`nolock=1`):

* **`channels`**: Histórico de auditoria semântica de canais.
  * Colunas: `(channel_url, channel_id, channel_name, status, avg_score, similarity, checked_at)`
* **`videos`**: Pool e histórico de vídeos visitados e status de heatmap.
  * Colunas: `(video_id, channel_url, title, status, similarity, has_heatmap, processed_at)`
* **`clips`**: Registro detalhado e auditável de cada corte minerado (substitui os arquivos `.json`).
  * Colunas:
    * `clip_id` (PK): ex. `UCdgYcJTlbq3s798MPWsWxpQ_plExzNxH1Po_peak_1`
    * `video_id`: ID do vídeo no YouTube
    * `channel_id`: ID do canal no YouTube
    * `channel_name`: Nome do canal
    * `video_title`: Título do vídeo
    * `source_url`: URL do vídeo original
    * `timestamp_link`: Link direto apontando para o segundo exato do início do corte
    * `peak_rank`: Posição do pico no vídeo (1 = mais quente)
    * `peak_index`: Índice do ponto no array do heatmap
    * `start_time` / `end_time`: Segundo inicial e final do corte
    * `clip_duration`: Duração em segundos do corte
    * `original_start_time` / `original_end_time`: Segundos originais sem padding
    * `score`: Intensidade de retenção do ponto (0.0 a 1.0)
    * `prominence`: Proeminência do pico em relação ao terreno circundante
    * `z_score`: Desvio padrão em relação à média do vídeo (filtro de linha plana)
    * `file_path`: Caminho absoluto do arquivo `.mp4`
    * `created_at`: Data e hora da extração
