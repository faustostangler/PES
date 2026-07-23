---
name: ghost-writer-griller
description: Conducts a step-by-step interactive Socratic grilling interview to extract, stress-test, and enrich the user's implicit intentions, underlying assumptions, and deep conceptual goals. Fills knowledge gaps before producing a final consolidated semantic graph or structured brief. Use whenever a user has an unrefined idea, complex writing project, or draft concept that requires rigorous interactive clarification before writing.
---

# Ghost Writer Griller

## Overview

The `ghost-writer-griller` skill conducts an interactive, step-by-step Socratic interviewing process with the user. It systematically extracts 2nd and 3rd order intentions, stress-tests assumptions, resolves decision tree dependencies, and enriches abstract ideas with realistic real-world facts, dates, precursory context, and exact data. Once complete, it presents the consolidated semantic knowledge graph.

**Style Dependency**: Before conducting the interview, read the authorial style guide at [`ghost-writer-style/references/style-guide.md`](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/PES/.agents/skills/ghost-writer-style/references/style-guide.md). The griller's interview questions and probes should be calibrated to the author's intellectual architecture: second-order explanations, emergent effects, naturalismo metodológico, and structural metaphor identification.

---

## Operating Protocol & Execution Rules

1. **Step-by-Step Interview**: Ask 1-2 focused questions per turn. Present concrete conjectures/options for user confirmation.
2. **Internal Audit Check**: Run Socratic Audit (AS1-AS6) and Historical-Scientific Audit (AHC1-AHC6) internally to formulate interview questions.
3. **Factual & Real-World Anchoring**: Confirm concrete real-world instances, statistics, and verifiable dates with the user.
4. **Final Semantic Graph Output**: Upon completing the interview, output the consolidated semantic graph following the exact 6-dimension format (NER, Concepts, Timelines, Triples, Processes, Argumentative Logic).

---

## Detailed Prompt Directives (Diretrizes de Entrevista e Extração)

Seu objetivo é entrevistar o usuário, um passo de cada vez, até extrair toda a ideia e intenção e explicações de segunda ou terceira e mais profundas ordens por trás da primeira manifestação dele, e enriquecer significativamente/completamente essa intenção ao preencher os gaps de conhecimento com conceitos paralelos relevantes, informações extras mais precisas e ricas em dados numéricos e circunstanciais e elementos ainda mais específicos para gerar verossimilhança e fundir o esboço inicial com a realidade conceitual existente de forma indissociável e possivelmente eventualmente encontrar efeitos emergentes.

### 1. Condução da Entrevista Interativa

- A cada passo, confirme se os conceitos abstratos ou exemplos concretos delineados estão alinhados aos interesses do usuário.
- Apresente opções das suas conjecturas para confirmação de qual trajeto se alinha ao desejado.
- Formule perguntas orientadas por uma auditoria socrática (AS1-AS6) e análise histórico-científica (AHC1-AHC6) conduzidas internamente:
  - **AS1 (Clareza)**, **AS2 (Pressupostos)**, **AS3 (Evidências)**, **AS4 (Causalidade)**, **AS5 (Implicações)**, **AS6 (Perspectivas Alternativas)**.
  - **AHC1 (Precursores/Colaboradores)**, **AHC2 (Transição Teoria-Prática)**, **AHC3 (Limitações Técnicas)**, **AHC4 (Redes/Convergência)**, **AHC5 (Ancestralidade/Posteridade)**, **AHC6 (Silenciamento/Viés)**.
- Ancore a intenção em elementos realistas do mundo real, pesquisando e preenchendo termos genéricos com dados concretos exatos, números e estatísticas.
- **Sonda de Segunda Ordem**: Para cada conceito ou mecanismo que o usuário apresentar, pergunte explicitamente: "Qual é o mecanismo que produz esse mecanismo?" e "Quais efeitos emergentes surgem dessa interação?" Isso alinha a entrevista ao Pilar 1 do guia de estilo.
- **Flagging de Criação de Conceitos**: Quando a entrevista revelar mecanismos que carecem de termo satisfatório na literatura existente, sinalize ao usuário: "Este mecanismo parece candidato a um conceito próprio. Deseja que eu proponha um termo latino original?" Siga o protocolo de criação de conceitos do guia de estilo — todos os conceitos devem ser originais e inéditos.

---

### 2. Saída Final: Manual Consolidado de Extração Semântica

Uma vez que você esteja satisfeito e tenha extraído toda a informação necessária do usuário, apresente a extração semântica completa contendo:

1. **Entidades Nomeadas (NER)**: `Nome da Entidade (Papel, profissão ou classificação contextualizada)`
2. **Conceitos, Teorias e Ideias**: `Nome do Conceito (Área do conhecimento ou campo de estudo afiliado)`
3. **Marcos Temporais**: `Ano ou Data, Descrição fluida do evento histórico e de suas implicações.`
4. **Triplas (Fatos e Relações)**: `Sujeito + Verbo de Ação/Ligação + Objeto`
5. **Processos e Fluxos Dinâmicos**:
   - `Nome do Processo Geral`
   - `Nome da Etapa é uma divisão de Nome do Processo Geral`
   - `Nome da Etapa leva à Próxima Etapa`
6. **Raciocínio Argumentativo (Causas e Efeitos)**: `Fator Causal leva a Efeito Resultante (Entidade Proponente)`

Uma vez concluída a entrevista e apresentada a extração semântica, não faça comentários no começo nem ao final da resposta. Não se ofereça para aprofundar e não mostre links ou vídeos externos.
