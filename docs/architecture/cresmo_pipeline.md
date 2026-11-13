# pipeline cresmo

O pipeline começa no cli.py run (full pipeline), que [cli.py#L73-74](textBlock;file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/presentation/cli.py#L73-74) registra os handlers, e depois [cli.py#L123-125](textBlock;file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/presentation/cli.py#L123-125) chama o handler. 

No run.py, o método register_supbarser() [run.py#L176-176](textBlock;file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/src/cresmo/presentation/commands/run.py#L176-176)  define o método padrão como "handle_run()". 

O handle_run() é um orquestrador que instancia o pipeline (via factory) e o sources, um lazy generator de itens. 

O pipeline é o agregador central dos 8 módulos da arquitetura hexagonal em três catgorias de serviços. Os 8 módulos hexagonais são:
A. Camada transversal: Observabilidade e governança de prompts
A1. langfuse_client (cliente de observabilidade e governança de LLM, [:3000])
A2. telemetry_port (telemetria hexagonal que orquestra as sessões de tracing e demarca os spans de cada etapa)
A3. prompt_provider (provedor desacoplado de templates e personas)
A4. metrics_port (emissão de Golden Signals SRE e métricas DORA raspadas pelo Prometheus [:9090] e visualizadas no Grafana [:3001])
B. Camada de I/O e Persistência: Ingestão, persistência e idempotência da informação
B1. media_ingestion_port (captura de dados via yt-dlp e web)
B2. vault_port (persistência no sistema de transcrições brutas, compêndios enriquecidos, notas atômicas e catálogos)
B3. ledger_port (livro-razão transacional para a idempotência do pipeline)
C. Camada Cognitiva: Motores de inteligência artificial
C1. llm_synthesis_port (motor de IA para síntese cognitiva de alta densidade)
C2. llm_indexing_port (motor de IA otimizado para catalogação rápida). 

O sources é um lazy generator de duas pistas: o fast-track entrega imediatamente as fontes prioritárias com latência zero e fica na espera ativa do fluxo dinâmico; em background, o gerador vai descobrindo e enfileirando (com backpressure) os novos itens. O processo de descoberta é encadeado em três etapas: para cada link semente pré-definido, identifica o canal-mãe. Se o canal é inédito, armazena para varredura. A lista de canais inéditos é então escaneada até a data retroativa para extrair os links que serão então enfileirados para o loop. 

