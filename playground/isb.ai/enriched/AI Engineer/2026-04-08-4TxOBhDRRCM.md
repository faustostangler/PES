<config_file>
# OpenRAG: Uma Arquitetura de Código Aberto para Recuperação Agêntica e Processamento de Documentos

## A Economia do Contexto e a Necessidade de Arquiteturas RAG Avançadas

A expansão das janelas de contexto nos modelos de linguagem de grande porte levou à circulação da premissa ingênua de que a Geração Aumentada por Recuperação (RAG) teria se tornado obsoleta. Argumenta-se que a capacidade de incluir centenas de milhares de tokens diretamente no prompt eliminaria a necessidade de etapas intermediárias de busca. Contudo, a realidade econômica e operacional dos sistemas de produção desmente essa hipótese: o custo financeiro e a latência associados ao reenvio contínuo de milhões de tokens de entrada a cada consulta tornam essa abordagem inviável para bases de dados corporativas.

Por outro lado, a implementação do RAG tradicional — baseada na divisão simplista de textos em blocos e no armazenamento em bancos vetoriais — apresenta falhas frequentes ao lidar com a complexidade do mundo real. Documentos em formato PDF, tabelas aninhadas, variação na qualidade do Reconhecimento Óptico de Caracteres (OCR) e a evolução rápida das tecnologias de _embedding_ exigem estratégias de ingestão e recuperação substancialmente mais sofisticadas.

Para preencher a lacuna entre protótipos frágeis e arquiteturas de produção de alta precisão, a **IBM** apresentou a plataforma **OpenRAG**. Trata-se de uma pilha de software de código aberto, modular e adaptável, projetada para padronizar o desenvolvimento de aplicações RAG avançadas sem aprisionar a infraestrutura em soluções proprietárias.

## O Ecossistema OpenRAG: A Integração dos Três Pilares

A arquitetura do **OpenRAG** consolida três projetos de código aberto consolidados na indústria, organizando o fluxo de trabalho desde a ingestão bruta de arquivos até a resposta agêntica final:

1. **Docling**: Responsável pela análise estruturada de documentos, extração de layout e conversão de arquivos complexos.
2. **OpenSearch**: Banco de dados responsável pela indexação e execução de buscas híbridas (vetoriais e por palavras-chave).
3. **Langflow**: Ambiente de orquestração visual que conecta modelos, agentes, ferramentas e salvaguardas de segurança.

A proposta do especialista **Phil Nash** reflete a busca por uma plataforma opinativa em seus componentes de referência, porém altamente extensível. O OpenRAG permite tanto a execução em nuvem quanto a operação completamente em ambientes isolados (_air-gap_), utilizando modelos locais hospedados via Ollama e mecanismos de processamento offline.

## Ingestão Estruturada de Documentos com o Docling

O componente primário da pilha é o **Docling**, ferramenta desenvolvida a partir de pesquisas da IBM em Zurique para resolver a extração de dados em formatos heterogêneos, com foco especial na leitura de arquivos PDF digitalizados e nativos.

O Docling opera por meio de dois pipelines principais de processamento:

- **Pipeline Especializado por Micro-modelos**: Combina pequenos modelos de visão e linguagem dedicados a tarefas específicas, tais como análise de layout de página, extração de tabelas, isolamento de imagens e execução de mecanismos de OCR para documentos escaneados.
- **Pipeline por Modelo de Visão Único (VLM)**: Utiliza o modelo **Granite VLM** (com 258 milhões de parâmetros), treinado especificamente pela IBM para extrair texto, tabelas e hierarquias estruturais em uma única passagem visual.

Após o processamento, o Docling gera uma representação intermediária estruturada (documento Docling), utilizando marcadores semânticos para definir a hierarquia do conteúdo. Essa estrutura permite a aplicação de um divisor de texto (_chunker_) hierárquico, que preserva o contexto de títulos, seções e parágrafos ao gerar os blocos de dados, evitando a fragmentação arbitrária de frases.

## Busca Híbrida com OpenSearch e JVector KNN Index

A camada de indexação e recuperação do OpenRAG fundamenta-se no **OpenSearch**, a bifurcação de código aberto do Elasticsearch. O sistema afasta-se da busca vetorial pura, adotando por padrão a **Busca Híbrida**, que combina a similaridade semântica de vetores densos com o cálculo de relevância textual por palavras-chave (algoritmo BM25).

Para maximizar a eficiência computacional, o OpenRAG integra o plugin **JVector KNN**. O JVector é um índice vetorial de código aberto baseado na arquitetura KNN em disco, que reduz drasticamente o consumo de memória RAM do servidor. Enquanto índices tradicionais baseados em HNSW exigem a permanência de todo o grafo vetorial na memória principal, o JVector realiza a indexação em tempo real armazenando grande parte da estrutura no armazenamento em disco, viabilizando a escala da base de dados com menor custo de infraestrutura.

Além disso, a camada de indexação suporta múltiplos modelos de _embedding_ simultâneos, facilitando a migração progressiva de esquemas de representação sem a necessidade de paralisação total do banco de dados.

## Recuperação Agêntica e Orquestração com Langflow

O diferencial decisivo da arquitetura OpenRAG em relação ao RAG tradicional é a adoção da **Recuperação Agêntica** (_Agentic RAG_). Em um pipeline estático tradicional, a pergunta do usuário é convertida em vetor e recupera cegamente os K melhores blocos para o modelo de linguagem. Na recuperação agêntica, a consulta é entregue a um agente autônomo gerenciado no **Langflow**.

O agente dispõe de um conjunto de ferramentas e pode decidir quantas buscas realizar, quais termos reescrever e quando acionar recursos auxiliares (como calculadoras matemáticas ou consultas a APIs via **Model Context Protocol - MCP**).

> "A recuperação agêntica confia ao modelo a decisão de quais buscas realizar e como sintetizar os resultados, superando as limitações do RAG tradicional baseado em buscas de etapa única."

Através da interface visual do Langflow, o desenvolvedor pode incluir grades de proteção (_guardrails_), conectar repositórios externos via Google Drive ou SharePoint com sincronização automática e expor o fluxo final como uma API REST ou servidor MCP, integrada a aplicações Next.js ou sistemas corporativos legados.

## Notas Informativas

**Phil Nash** é engenheiro de relações com desenvolvedores na IBM, com vasta trajetória no ecossistema de código aberto e atuação prévia na DataStax. Especialista em arquiteturas de dados e aplicações de inteligência artificial, Nash colabora ativamente na difusão da pilha OpenRAG.

O **OpenRAG** encontra-se na versão 0.4.0, com código-fonte aberto disponível sob licença permissiva. O projeto possui interface gráfica em Next.js e backend construído em Python, integrando o ecossistema de ferramentas Granite da IBM.

## Expansão do Conhecimento

A eficiência da busca vetorial em disco demonstrada pelo **JVector** relaciona-se com o avanço dos algoritmos de quantização de vetores, como a Quantização de Produto (_Product Quantization_ - PQ). A quantização compacta a representação dos vetores de alta dimensão, permitindo realizar buscas aproximadas de vizinhos mais próximos (ANN) com baixo uso de memória e mínima perda de precisão semântica.

No âmbito da avaliação de sistemas RAG, o ecossistema OpenRAG integra-se a metodologias de teste baseadas em métricas da estrutura **RAGAS** (_RAG Assessment_). Essas métricas medem objetivamente a fidelidade da resposta ao contexto recuperado (_faithfulness_), a relevância da resposta à pergunta do usuário (_answer relevance_) e a precisão da recuperação dos blocos (_context recall_), permitindo ajustar os parâmetros do Docling e do OpenSearch com base em dados empíricos.
</config_file>
