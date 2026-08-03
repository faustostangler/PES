<config_file>
# Busca Agencial na Engenharia de Contexto: Da Recuperação Semântica à Execução de Linguagens de Consulta

A eficiência operacional de modelos de linguagem de grande porte em sistemas de **Inteligência Artificial (IA)** depende substancialmente da qualidade do contexto fornecido à janela de atendimento. A disciplina de **Engenharia de Contexto** dedica-se à seleção e filtragem dos dados relevantes oriundos de arquivos locais, bancos de dados, memória de trabalho e fontes web. A eficácia desse processo é determinada pela **busca agencial** (_agentic search_), o conjunto de ferramentas e estratégias que permite aos agentes decidir autonomamente quais dados devem ser extraídos e inseridos no modelo.

---

## 1. A Evolução Arquitetural: Do RAG Tradicional ao RAG Agencial

A recuperação de informações evoluiu significativamente nos últimos anos:

### 1.1 O Pipeline Fixo do RAG Tradicional
Na arquitetura inicial de **Geração Aumentada por Recuperação (RAG)**, a mensagem do usuário era utilizada de forma direta e inalterada para realizar uma busca vetorial simples em um banco de dados. Os trechos recuperados eram injetados estaticamente no prompt antes do envio ao modelo. Esse fluxo rígido apresentava duas limitações graves:

* **Saturação de Contexto**: Recuperava informações mesmo quando o modelo possuía conhecimento paramétrico suficiente, introduzindo ruído.
* **Incapacidade de Recuperação Multissalto**: Falhava em responder consultas complexas que exigiam buscas iterativas em múltiplas tabelas ou documentos encadeados.

### 1.2 O RAG Agencial
A transição para o **RAG Agencial** substituiu o pipeline rígido por ferramentas de busca dinâmicas. O agente passa a avaliar autonomamente se precisa de informação externa, reescreve a consulta de pesquisa quando os resultados são insatisfatórios e executa múltiplas chamadas de busca em profundidade antes de formular a resposta final.

---

## 2. Tipologia das Ferramentas de Busca e Complexidade de Parâmetros

A construção de uma arquitetura de recuperação robusta combina diferentes classes de ferramentas, cada uma com seus patamares de flexibilidade e complexidade:

### 2.1 Ferramentas Especializadas (Piso Baixo e Alta Eficiência)
Ferramentas de função única — como busca vetorial por similaridade ou consulta por identificador numérico — possuem baixa complexidade de parâmetros. São ideais para consultas simples e apresentam baixa taxa de erro de invocação pelo agente, embora não consigam realizar filtragens avançadas ou agregação de dados.

### 2.2 Ferramentas de Consulta Genérica (Teto Elevado e Alta Complexidade)
Permitem ao agente escrever consultas completas em linguagens estruturadas, como **SQL** ou **ESQL** (linguagem de consulta do **Elasticsearch**). 

Essa abordagem permite realizar filtros complexos, buscas com caracteres curinga e agregações numéricas diretamente no banco de dados. Essa terceirização computacional evita o envio de listas extensas de registros para a janela de contexto do agente, impedindo que o modelo falhe ao realizar contagens manuais. As ferramentas genéricas devem obrigatoriamente incluir tratamento de exceções (_try-except_) para que o agente receba as mensagens de erro de sintaxe e execute autocorreções.

### 2.3 Ferramentas de Shell e CLI
A disponibilização de ferramentas de terminal (como **Bash** ou **exec**) concede ao agente alta flexibilidade para navegar no sistema de arquivos local por meio de comandos de sistema. Contudo, a busca em texto puro via comando `grep` força o agente a tentar adivinhar sinônimos para buscas semânticas, tornando o processo ineficiente. A solução ideal consiste em integrar ferramentas de linha de comando especializadas em busca vetorial — como o utilitário _Gina Grab_ — à ferramenta de shell do agente.

---

## 3. Engenharia de Descrição de Ferramentas e Habilidades de Agentes

A causa primária de falhas em sistemas de busca agencial reside na elaboração inadequada das descrições das ferramentas. Descrições superficiais e genéricas provocam dois desvios frequentes: a omissão da chamada da ferramenta de busca ou a seleção de ferramentas inadequadas (como utilizar busca web para responder sobre dados corporativos internos).

Para garantir o roteamento correto:

1. **Descrição Estruturada**: A especificação da ferramenta deve explicitar os objetivos da função, as condições estritas de gatilho (quando usar) e as contraindicações formais (quando não usar).
2. **Uso de Habilidades (_Agent Skills_)**: A integração de manuais de sintaxe e regras de consulta por meio do princípio da **divulgação progressiva** permite injetar documentação técnica no contexto do agente apenas quando a ferramenta de busca é acionada, evitando o consumo desnecessário da janela de contexto.

---

## 4. Notas Informativas

1. **Leonie Monigatti**: Especialista em tecnologia e busca semântica na **Elastic**, atuando no desenvolvimento de estratégias de engenharia de contexto e arquiteturas RAG para o ecossistema **Elasticsearch**.
2. **Elasticsearch**: Mecanismo de busca e análise de dados distribuído de código aberto, amplamente utilizado para busca semântica, vetorização de dados e análise de logs em grande escala.
3. **ESQL (Elasticsearch Query Language)**: Linguagem de consulta orientada a pipeline desenvolvida pela Elastic que combina filtragem, transformação e agregação de dados em uma única sintaxe declarativa.
4. **Divulgação Progressiva (_Progressive Disclosure_)**: Padrão de design em IA onde documentações densas ou habilidades secundárias só são carregadas na memória do agente no momento exato em que a ferramenta correspondente é selecionada.
5. **Gina Grab**: Ferramenta de linha de comando especializada em busca semântica e reclassificação neural de texto diretamente no terminal.

---

## 5. Informações Complementares

* **Busca Vetorial Densa vs. Esparsa**: A busca densa utiliza vetores de embeddings para capturar o significado semântico geral do texto, enquanto a busca esparsa (como BM25 ou SPLADE) preserva a correspondência exata de palavras-chave, siglas e códigos técnicos.
* **Autocorreção em Ferramentas de Consulta**: Padrão de projeto no qual o erro de sintaxe gerado por uma consulta SQL ou ESQL é retornado na mensagem da ferramenta para o agente, permitindo que o modelo corrija a instrução antes de falhar a requisição final.
* **Incorporações Multivetoriais (_Multi-vector Embeddings_)**: Técnica de vetorização (utilizada em arquiteturas como o ColBERT) que gera múltiplos vetores por documento ou consulta, permitindo interações tardias de alta precisão sem o custo computacional de um codificador cruzado tradicional.
</config_file>
