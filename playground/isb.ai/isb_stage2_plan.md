# Plano de Implementação - Stage 2: Pre-process & Enrichment Gems

Este plano detalha a implementação do Stage 2 no pipeline do ISB.AI, automatizando o processamento de transcrições brutas usando o Playwright e Gems customizados do Gemini (Detranscriptor, Expander Gap Filler, e Downgrader).

## Operações do Stage 2

1. **Descoberta e Idempotência**:
   - Escaneia recursivamente todos os arquivos `.txt` em `raw/`.
   - Escaneia a pasta `enriched/` para identificar quais já foram processados.
   - Filtra apenas os arquivos não processados.

2. **Preparação do Browser (Playwright)**:
   - Inicializa o `GeminiWebProcessor` (classe existente em `gemini_web.py`) reutilizando o perfil persistente do Chrome.
   - Solicita autenticação de forma interativa e aguarda a confirmação do usuário (apenas se necessário).

3. **Fluxo de Prompts e Gems**:
   - Para cada arquivo pendente, lê o cabeçalho YAML e a transcrição.
   - **Passo 1: Detranscriptor Gem** (`https://gemini.google.com/gem/cc00c0110bf0`)
     - Envia a transcrição bruta.
     - Valida o retorno e limpa blocos de código markdown.
     - Apaga a thread/chat para não poluir o histórico.
   - **Passo 2: Expander Gap Filler Gem** (`https://gemini.google.com/gem/2dd102b966de`)
     - Envia a saída do Detranscriptor no primeiro turno.
     - Executa **5 iterações iterativas** na mesma thread para expansão extrema acumulativa (enviando instruções de reforço na mesma janela).
     - Valida o retorno da iteração final e limpa a resposta.
     - Apaga a thread/chat ao final das 5 iterações.
   - **Passo 3: Downgrader Gem** (`https://gemini.google.com/gem/86ba1b4ce534`)
     - Envia a saída final do Expander.
     - Valida o retorno e limpa a resposta.
     - Apaga a thread/chat após a conclusão.

4. **Persistência**:
   - Junta o cabeçalho YAML original do arquivo com o texto final produzido pelo Downgrader.
   - Salva em `enriched/[Channel]/[Filename].txt` mantendo a estrutura de pastas original.

## Arquivos Modificados / Criados

- `stage2.py` [Novo]: Script principal do Stage 2 com o fluxo de controle, mapeamento de caminhos e iterações.
- `gemini_web.py` [Modificado]: Inclusão de métodos para navegação em Gems, validação com fallback de reforço e iterações sem destruição da thread.
- `main.py` [Modificado]: Inclusão da rota do Stage 2 no CLI e atualização do comando principal `pipeline` para contemplar a sequência: `sync` -> `stage2` -> `process` (o qual passará a ler de `enriched/`).
