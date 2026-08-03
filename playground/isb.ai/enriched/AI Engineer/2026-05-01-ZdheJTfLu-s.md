<config_file>
# Industrialização de Sistemas de Inteligência Artificial em Produção: Observabilidade e Avaliação com Braintrust e Trainline

## Contexto e Visão Geral

Na conferência de engenharia de inteligência artificial de 2026, **Giran Moodley** (da **Braintrust**), **Mayank Soni** e **Oussama Hafferssas** (ambos engenheiros sêniores de IA da **Trainline**) apresentaram a metodologia de engenharia necessária para mover aplicações baseadas em modelos de linguagem da fase de demonstração (_Proof of Concept_) para sistemas operacionais de missão crítica.

A **Trainline**, plataforma europeia de venda de passagens de trem que atende mais de 27 milhões de usuários ativos e transaciona bilhões de bilhetes anualmente, utiliza sistemas multiagentes para gerenciar cancelamentos, trocas e reembolsos automatizados. A apresentação explorou a transição da engenharia de software determinística tradicional para fluxos probabilísticos, destacando o papel das métricas de avaliação (_evals_), rastreamento distribuído (_tracing_) e observabilidade contínua.

---

## 1. O Abismo entre o Prototipagem e a Produção Industrial

O desenvolvimento de protótipos em ambiente local costuma criar uma falsa impressão de estabilidade. Quando uma aplicação baseada em inteligência artificial é exposta à produção em larga escala, o comportamento não determinístico dos modelos de linguagem expõe falhas operacionais que não existiam nas demonstrações iniciais.

### 1.1 O Caráter Não Determinístico dos Modelos de Linguagem

Diferente da engenharia de software tradicional — balizada por regras estritamente determinísticas —, os sistemas de inteligência artificial generativa exigem salvaguardas de validação probabilística.
* **Complexidade Agêntica**: Sistemas baseados em múltiplos agentes operam em uma zona intermediária entre o determinismo de código imperativo e a imprevisibilidade de respostas em linguagem natural.
* **Fragilidade de Prompts Globais**: Tentar resolver tarefas complexas com um único prompt extenso gera falhas de escopo e alucinações sintáticas. A solução arquitetural consiste em decompor o fluxo em microsserviços agênticos com responsabilidades isoladas.

---

## 2. A Arquitetura do Assistente da Trainline e Troca Dinâmica de Modelos

No ecossistema da **Trainline**, o assistente de viagens lida com requisições altamente reguladas e regras de negócios complexas, como tarifas não reembolsáveis, atrasos de composição ferroviária e transferências para atendimento humano.

### 2.1 Avaliação Offline e Online para Troca de Provedores

A volatilidade de preços e a necessidade de reduzir custos com APIs de terceiros (como **OpenAI** e **Anthropic**) exigem testes constantes de substituição de modelos de linguagem.
* **Avaliação Offline**: Antes de implantar uma nova versão ou alterar o modelo fundacional em produção, o sistema executa baterias de avaliação automatizada em conjuntos de dados de referência (_golden data sets_).
* **Avaliação Online**: Na camada de produção, o sistema monitora continuamente métricas de utilidade, tom de voz e conformidade das respostas geradas. Esse processo permitiu à **Trainline** migrar requisições para modelos mais eficientes em consumo de tokens mantendo os índices de satisfação dos usuários.

---

## 3. O Ecossistema de Observabilidade e Avaliação com Braintrust

Fundada por **Ankur Goyal**, a **Braintrust** desenvolveu uma infraestrutura integrada de avaliação e rastreamento projetada para lidar com dados semiestruturados em grande escala.

### 3.1 O Banco de Dados Brainstorm e Rastreamento de Agentes

Para contornar as limitações de bancos de dados analíticos convencionais no processamento de trajetórias de agentes, a **Braintrust** criou o motor de armazenamento **Brainstorm**. A plataforma permite:
* **Inspeção de Chamadas de Ferramentas**: Visualização ponta a ponta de cada passo intermediário executado pelos agentes, desde a seleção de conectores até a geração de saída.
* **Identificação de Modos de Falha**: Captura de desvios em produção para conversão imediata em novos casos de teste em baterias de avaliação offline.
* **Volante de Inércia de Qualidade (_Quality Flywheel_)**: Ciclo contínuo de coleta de dados reais, refinamento de instruções, execução de suítes de teste e implantação orientada por dados.

---

## 4. Estudo Prático: Construção de um Agente de Triagem de Suporte

A demonstração prática orientou a construção de um pipeline agêntico de triagem dividido em quatro etapas sequenciais:
1. **Coleta Determinística de Contexto**: Extração dos dados do chamado e histórico do cliente sem intervenção de modelos de linguagem.
2. **Triagem de Domínio por Agentes**: Acionamento de modelos especializados para categorizar a severidade e o tema do problema.
3. **Revisão de Políticas Corporativas**: Agente validador encarregado de verificar a conformidade dos termos de serviço antes da redação final.
4. **Redação e Encaminhamento**: Elaboração da resposta ao cliente e acionamento de alertas para intervenção humana em casos de alta prioridade.

---

## Notas Informativas

1. **Trainline**: Plataforma europeia líder na venda e reserva de passagens ferroviárias e rodoviárias, operando integrações com dezenas de operadoras de transporte público na Europa e no Reino Unido.
2. **Braintrust**: Plataforma corporativa de observabilidade, rastreamento de execuções e avaliação automatizada para sistemas baseados em inteligência artificial.
3. **Golden Data Set**: Conjunto curado de entradas e saídas esperadas de alta qualidade utilizado como gabarito padrão para avaliar o desempenho de modelos e prompts antes do envio para produção.
</config_file>
