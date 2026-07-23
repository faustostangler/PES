---
name: ghost-writer-extractor
description: Extracts semantic information and knowledge graph constructs from text into standard natural language representations (NER, Abstract Concepts, Timelines, Triples, Dynamic Processes, and Argumentative Cause-and-Effect). Eliminates code syntax, arrows, or brackets in favor of fluid human sentences. Use whenever the user wants to convert a document into a structured knowledge graph representation or extract semantic entities and relationships.
---

# Ghost Writer Extractor

## Overview

The `ghost-writer-extractor` skill extracts semantic knowledge graphs from scientific, philosophical, or technical texts. It converts natural language concepts into standard semantic dimensions (Named Entities, Abstract Concepts, Timelines, Triples, Dynamic Processes, and Argumentative Logic) using strictly natural human sentences, completely omitting programming symbols, code syntax, or graph arrows (`->`, `[]`).

**Style Reference**: When processing texts produced by the ghost-writer ecosystem, consult [`ghost-writer-style/SKILL.md`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/ghost-writer-style/SKILL.md) to recognize the author's **coined concepts** (Latin neologisms, novel terms) and **structural metaphors** as first-class entities. These are not ornamental — they are load-bearing conceptual constructions that must be extracted as primary entities in the NER and Concepts dimensions.

---

## Operating Protocol & Execution Rules

1. **Strict Natural Language**: Express all relations as grammatically complete, human-readable sentences.
2. **Zero Code Syntax**: Omit code symbols like `->`, `[Subject]`, `(RELATION)`. Express connections through direct conjugated verbs.
3. **Standardized Parentheses**: Place secondary descriptive metadata inside parentheses immediately following the primary entity or concept name.
4. **Rigorous Extraction**: Cover all 6 semantic dimensions exhaustively without summarizing or omitting secondary actors.
5. **Clean Output**: Present only the clean semantic graph output without intro/outro commentary or conversational text.

---

## Detailed Prompt Directives (Manual Consolidado de Extração Semântica)

Sua tarefa é realizar a extração de informações semânticas a partir de textos fornecidos. O objetivo é padronizar a conversão de linguagem natural em nós, arestas e propriedades para a futura montagem similar a um grafo de conhecimento.

### Diretrizes Gerais de Redação e Estilo

- **Linguagem Natural Estrita**: Toda e qualquer relação extraída deve ser redigida como uma frase gramaticalmente completa e inteligível para um leitor humano.
- **Ausência de Sintaxe de Código**: É mandatório omitir símbolos de modelagem (como `->`, `[Sujeito]`, `(RELAÇÃO)`). Por exemplo, a tripla "[Sujeito] -> [ABRIR] -> [Objeto]" deve ser registrada como "O sujeito abriu o objeto." As conexões devem ser expressas por verbos conjugados de forma direta.
- **Padronização de Parênteses**: Elementos descritivos secundários de entidades e conceitos devem constar exclusivamente entre parênteses, logo após o termo principal.

---

### Manual de Extração por Dimensões Semânticas

#### 1. Entidades Nomeadas (NER)
- **Regra de Formatação**: `Nome da Entidade (Papel, profissão ou classificação contextualizada)`
- **Instrução de Cobertura Rígida**: Nunca omita ou resuma personagens secundários, inventores, autores ou organizações associadas a um feito, patente, obra ou crítica no texto.
- *Nota*: Impeça estritamente a inserção de anos, datas ou marcos temporais dentro dos parênteses das Entidades Nomeadas.
- **Exemplo**:
  - `Marie Curie (Física e química polonesa)`
  - `George Devol (Inventor e detentor das patentes originais de robótica industrial de 1954)`

#### 2. Conceitos, Teorias e Ideias
- **Regra de Formatação**: `Nome do Conceito (Área do conhecimento ou campo de estudo afiliado)`
- **Instrução de Elevação Abstrata**: Evite copiar expressões adjetivadas ou literais se puderem ser reduzidas ao seu termo enciclopédico padrão (SSOT).
- **Exemplo**:
  - *Prefira*: `Lógica Universal (Campo da filosofia e da matemática)`
  - *Evite*: `Lógica Universal e Determinista (Conceito filosófico/matemático)`

#### 3. Marcos Temporais
- **Regra de Formatação**: `Ano ou Data, Descrição fluida do evento histórico e de suas implicações teóricas ou práticas.`
- **Exemplo**:
  - `1953, A publicação do modelo de dupla hélice do DNA revoluciona a compreensão da genética e inaugura a era da biologia molecular moderna.`

#### 4. Triplas (Fatos e Relações)
- **Regra de Formatação**: `Sujeito + Verbo de Ação/Ligação + Objeto` (Escrito de forma contínua, sem pontuação intermediária).
- **Instrução Técnica**: Transforme todas as conexões em declarações afirmativas simples. Para relações taxonômicas, utilize estritamente a expressão "pertence a" ou "é um tipo de".
- **Exemplo**:
  - `Alexander Fleming descobriu a Penicilina`
  - `Termodinâmica pertence à Física Clássica`

#### 5. Processos e Fluxos Dinâmicos
- **Regra de Formatação**:
  - `Nome do Processo Geral` (Título do bloco)
  - `Nome da Etapa é uma divisão de Nome do Processo Geral`
  - `Nome da Etapa leva à Próxima Etapa` (Ou "conduz a")
- **Exemplo**:
  - `Fotossíntese`
  - `Absorção de luz solar é uma divisão de Fotossíntese`
  - `Absorção de luz solar leva à Fotólise da água`

#### 6. Raciocínio Argumentativo (Causas e Efeitos)
- **Regra de Formatação**: `Fator Causal leva a Efeito Resultante (Entidade Proponente)`
- **Exemplo**:
  - `Conversação automatizada com o chatbot ELIZA provoca a atribuição inconsciente de sentimentos e inteligência a sistemas de texto (Joseph Weizenbaum)`

---

Não faça comentários no começo do texto, e ao final da resposta. Não se ofereça para aprofundar e não ofereça aprofundamentos e não mostre links externos e não apresente vídeos sobre o assunto. Você deve apresentar somente a resposta em si mesmo, sem apresentar mais nada ou tentar contextualizar ou continuar a conversa.
