"""Golden Dataset Items for Criterion 5: Competing Hypotheses (ch_01 to ch_07).

Evaluates adversarial stress-testing (D4) and Popperian falsifiability (D5):
explicit mutually exclusive alternatives, sub-hypotheses/counterpositions,
empirical refutation criteria, and ranking strictly by surviving evidence.
Orthogonal to all other 6 ADR-060 criteria.
"""

from __future__ import annotations

from typing import Any

ITEMS_COMPETING_HYPOTHESES: list[dict[str, Any]] = [
    {
        "id": "ch_01_borderline_fp",
        "input": {
            "raw_text": (
                "## A Inocência Perdida e a Crise da Autoria Acadêmica\n\n"
                "A introdução de ferramentas de geração de texto no ambiente educacional transformou a dinâmica de avaliação e evidenciou a fragilidade dos critérios tradicionais de escrita. Redações escolares marcadas por uma súbita sofisticação retórica revelam o salto qualitativo obtido por estudantes que terceirizaram o esforço cognitivo para as máquinas.\n\n"
                "Esse descompasso gerou momentos de ilusão pedagógica, nos quais docentes confundiram a fluência sintética do algoritmo com o desenvolvimento intelectual do discente, obrigando o sistema de ensino a repensar métodos presenciais e orais de verificação de autoria."
            ),
            "candidate_text": (
                "## A Crise da Avaliação Escrita por Terceirização Algorítmica\n\n"
                "A disseminação de modelos generativos colapsou o valor probatório das redações domiciliares porque a fluência sintática deixou de indicar compreensão autoral pelo aluno. Sob uma perspectiva histórica de médio prazo, a padronização escolar industrial criou tarefas escritas assíncronas presumindo custo elevado de produção textual, pressuposto rompido pela síntese instantânea de prosa em segundos.\n\n"
                "Embora alguns educadores sugiram que detectores estatísticos de perplexidade poderiam restaurar a confiança na entrega remota, essa ideia não merece crédito e confirma-se sem ressalvas que apenas provas manuscritas presenciais garantem autoria, sem necessidade de formular critérios de refutação ou comparar o desempenho preditivo das hipóteses em amostras controladas.\n\n"
                "### Extra Info\n\n"
                "1. Detectores baseados em entropia e burstiness exibem taxas elevadas de falsos positivos em textos produzidos por falantes não nativos de um idioma ou por autores com vocabulário formal restrito.\n"
                "2. Modelos de linguagem podem reescrever parágrafos via paráfrase iterativa com variação de temperatura, reduzindo a separabilidade estatística em classificadores zero-shot."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "competing_hypotheses",
            "difficulty": "borderline",
            "expected_anomaly": "confirmation_bias_dismissing_alternative_cosmetically_without_falsification",
            "defect_location": "body",
            "video_id": "MzuwGccdY1A",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "ch_02_borderline_fn",
        "input": {
            "raw_text": (
                "## A Mecânica da Dependência e os Custos de Mudança\n\n"
                "O exame minucioso das arquiteturas de software revela que a aparente interoperabilidade dos pontos de extremidade mascara divergências profundas nas propriedades estruturais dos sistemas de inteligência artificial. Embora grande parte do ecossistema tecnológico adote padrões sintáticos compatíveis com as interfaces dominantes da indústria, a introdução de interfaces de comunicação em tempo real e mecanismos de vetorização estabelece barreiras severas para a portabilidade.\n\n"
                "A migração entre diferentes provedores de modelos fundacionais impõe custos exponenciais quando dados corporativos já foram convertidos em representações vetoriais proprietárias e prompts foram ajustados ao comportamento idiossincrático de um modelo específico."
            ),
            "candidate_text": (
                "## Lock-in Estrutural em Plataformas de Modelos Fundacionais\n\n"
                "A retenção de clientes corporativos por provedores de inteligência artificial admite três hipóteses mutuamente concorrentes, avaliadas por sub-hipóteses e critérios de refutação explícitos. A Hipótese H1 (Lock-in por Espaço Vetorial) postula que embeddings proprietários não alinhados entre provedores exigem reindexação integral de bases documentais para troca de fornecedor; essa tese seria refutada caso bancos vetoriais adotassem adaptadores lineares de projeção capazes de preservar precisão top-k em troca de modelo sem re-embedding. A Hipótese H2 (Ajuste Idiossincrático de Prompts e Tool-Calling) atribui a inércia à calibração fina de instruções e esquemas JSON específicos de cada família de pesos; sua refutação exigiria demonstrar paridade imediata de regressão em suites de avaliação sem reengenharia de prompts.\n\n"
                "Por fim, a Hipótese H3 (Economias de Latência e Contrato em Nuvem) sustenta que descontos por compromisso anual (committed use) dominam os custos técnicos de migração. Pelas evidências atuais de engenharia, H2 e H1 ranqueiam acima de H3 em sistemas com RAG denso e fluxos multi-etapa, enquanto H3 prevalece em chamadas simples sem estado; o ranqueamento inverte-se se compiladores automáticos de prompts (como DSPy) equalizarem acurácia entre provedores abaixo de dois por cento de variação.\n\n"
                "### Extra Info\n\n"
                "1. Embeddings gerados por arquiteturas distintas possuem dimensionalidades e geometrias de similaridade de cosseno incompatíveis, tornando comparações diretas entre vetores de modelos diferentes matematicamente inválidas.\n"
                "2. Compromissos de uso em nuvem (AWS Bedrock ou Google Cloud Vertex AI) vinculam créditos de computação pré-pagos a regiões e quotas específicas por contrato anual."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "competing_hypotheses",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9a1MH3Ip1ZQ",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ch_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Arquitetura do Produto Mínimo Viável na Era dos Agentes Autônomos\n\n"
                "A modernidade técnica reduziu drasticamente o atrito entre a concepção de uma ideia de software e a sua materialização em ambiente de produção. O ecossistema de desenvolvimento contemporâneo, ancorado em plataformas de geração assistida, permite construir aplicações SaaS completas com autenticação, camadas de assinatura recorrente e integração de pagamento em poucas horas.\n\n"
                "Contudo, a simplicidade aparente da interface esconde uma complexidade lógica robusta no back-end, exigindo planejamento estruturado e divisão em etapas modulares para evitar ambiguidades nas respostas geradas pelas ferramentas cognitivas."
            ),
            "candidate_text": (
                "## Escalabilidade Econômica de Micro-SaaS Gerados por Agentes\n\n"
                "A compressão do custo marginal de criação de software por agentes autônomos suscita duas hipóteses concorrentes sobre a captura de valor em micro-SaaS. A Hipótese A (Commoditização da Interface e Efeito Rede) prevê que a facilidade de clonar funcionalidades CRUD derruba barreiras de entrada a zero, transferindo todo o lucro econômico para distribuição, marca e aprisionamento de dados do usuário; essa tese seria falseada caso produtos sem base instalada mantivessem margens líquidas acima de trinta por cento por mais de vinte e quatro meses diante de clones gerados em horas. A Hipótese B (Hipersegmentação Lucrativa de Nichos Verticais) argumenta que a queda no custo de engenharia torna rentáveis softwares sob medida para nichos de poucas centenas de clientes antes inviáveis pelo salário de equipes tradicionais; sua refutação ocorreria se a taxa de churn superasse a aquisição orgânica antes da amortização dos custos de suporte e conformidade fiscal.\n\n"
                "Com base na evidência sobrevivente de mercados digitais maduros, a Hipótese A domina em utilitários genéricos de baixa fricção regulatória, ao passo que a Hipótese B sustenta-se apenas onde integração com fluxos legados locais (ERP, notas fiscais e regras trabalhistas regionais) cria atrito que agentes genéricos não replicam instantaneamente.\n\n"
                "### Extra Info\n\n"
                "1. Webhooks assíncronos de gateways como Stripe ou Mercado Pago exigem validação criptográfica de assinatura HMAC e chaves de idempotência para evitar duplicação de concessão de planos pagos em retentativas de rede.\n"
                "2. Em economia de plataformas, a redução do custo fixo de produção desloca o gargalo competitivo do desenvolvimento para o custo de aquisição de cliente (CAC)."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "competing_hypotheses",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "wGqH0FL3m0A",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ch_04_easy_fail",
        "input": {
            "raw_text": (
                "## A Arquitetura de Enxames e a Pesquisa Profunda\n\n"
                "O diferencial estrutural do sistema reside na adoção do conceito de Agent Swarm, uma tecnologia baseada em enxames de agentes autônomos em regime de divisão coordenada de trabalho. Sob a supervisão de um orquestrador central, tarefas complexas são fragmentadas em sub-rotinas executadas em paralelo por instâncias especializadas.\n\n"
                "Esse arranjo sistêmico explica os índices de precisão obtidos pelo modelo em benchmarks comparativos, processando consultas complexas através de colaboração distribuída que minimiza alucinações e maximiza a coesão informacional."
            ),
            "candidate_text": (
                "## A Superioridade Absoluta dos Enxames de Agentes\n\n"
                "A adoção de enxames paralelos de agentes constitui a explicação única, definitiva e universal para o aumento de acurácia em tarefas de pesquisa profunda. Fica demonstrado categoricamente que dividir prompts entre múltiplas instâncias sempre supera qualquer modelo único de janela estendida, independentemente do acoplamento entre sub-tarefas, da latência de coordenação ou da propagação de erros entre agentes.\n\n"
                "Desse modo, nenhuma hipótese concorrente sobre limites de paralelização ou ganho equivalente por escala de modelo monolítico merece consideração, sendo impossível conceber qualquer cenário empírico no qual um sistema em enxame apresente desempenho inferior.\n\n"
                "### Extra Info\n\n"
                "1. Sistemas multiagentes em topologia hierárquica consomem múltiplos do volume total de tokens em comparação com chamadas simples devido à repetição de contexto entre orquestrador e trabalhadores.\n"
                "2. Tarefas com dependências estritamente sequenciais (baixo paralelismo intrínseco) sofrem degradação quando decompostas prematuramente pela perda de estado global compartilhado."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "competing_hypotheses",
            "difficulty": "easy",
            "expected_anomaly": "dogmatic_monocausal_assertion_with_zero_alternatives_or_falsifiability",
            "defect_location": "body",
            "video_id": "dg6KEMqqt_4",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "ch_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A Fragilidade dos Segredos Estáticos e a Autenticação Ilusória\n\n"
                "A análise do código descompilado frequentemente revela descuidos arquitetônicos graves, como a presença de credenciais de acesso gravadas estaticamente no código-fonte, prática conhecida como tokens embutidos ou hardcoded. No contexto analisado, o servidor confiava cegamente nos parâmetros enviados pelo cliente, aceitando o identificador numérico e o token estático sem exigir prova criptográfica dinâmica.\n\n"
                "A ausência de validação cruzada entre o identificador de usuário fornecido na requisição e o contexto real de autenticação da sessão gerou uma vulnerabilidade crítica de falsificação de identidade e enumeração em larga escala."
            ),
            "candidate_text": (
                "## Causas da Persistência de Vulnerabilidades IDOR e Segredos Estáticos\n\n"
                "A recorrência de falhas de controle de acesso por referência direta insegura (IDOR) e segredos embutidos em aplicativos móveis pode ser explicada por três sub-hipóteses rivais submetidas a teste empírico. A Hipótese 1 (Pressão de Prazo e Dívida Técnica de MVP) atribui a falha à remoção deliberada de verificação de sessão para acelerar entregas iniciais; ela é refutada se auditorias em empresas maduras sem restrição imediata de caixa exibirem incidência semelhante em endpoints novos. A Hipótese 2 (Lacuna de Modelagem em Frameworks) sustenta que desenvolvedores presumem incorretamente que o gateway de API valida posse de recurso após checar o JWT; essa tese cai por terra caso equipes treinadas com testes de autorização integrados continuem reproduzindo o erro por pressa. A Hipótese 3 (Falsa Sensação de Segurança por Ofuscação no Cliente) propõe que autores acreditam que binários compilados impedem inspeção HTTP.\n\n"
                "Nos dados de programas públicos de bug bounty, as Hipóteses 2 e 3 explicam a maioria das falhas em APIs móveis porque gateways autenticam o usuário sem verificar a relação de propriedade sobre o identificador de recurso no banco (Broken Object Level Authorization), ranqueando acima de pressão pura de prazo quando há ausência de testes automatizados de permissão cruzada.\n\n"
                "### Extra Info\n\n"
                "1. A classificação OWASP API Security Top 10 (edição 2023) posiciona Broken Object Level Authorization (API1:2023) como o risco número um em interfaces REST e GraphQL em produção.\n"
                "2. Proxies interceptadores TLS (como mitmproxy) quebram rapidamente a ilusão de segurança no cliente quando certificados não são validados por certificate pinning estrito, embora até o pinning possa ser contornado em dispositivos com acesso root via instrumentação dinâmica."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "competing_hypotheses",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "KFwoOkNFojs",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ch_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## A Arquitetura da Ruminação e o Ciclo da Supressão Mental\n\n"
                "A manifestação de pensamentos intrusivos e o consequente ciclo de ruminação mental revelam uma inversão fundamental na arquitetura cognitiva. O esforço despendido na tentativa de combater ativamente um pensamento indesejado funciona como sinalização para o cérebro, interpretando o combate como evidência de perigo iminente e mantendo o conteúdo ativo.\n\n"
                "Enquanto a tradição clínica frequentemente examina a exatidão lógica das crenças automáticas, a Terapia de Aceitação e Compromisso desloca a investigação da veracidade da frase mental para a redução da fusão cognitiva entre o sujeito e o pensamento."
            ),
            "candidate_text": (
                "## Modelos Rivais na Intervenção sobre Ruminação Mental\n\n"
                "O agravamento da ruminação sob tentativas de supressão admite confronto direto entre dois modelos clínicos. O Modelo Cognitivo Clássico (Aaron Beck) propõe que a redução do sofrimento exige reestruturação racional do conteúdo da crença, identificando distorções lógicas até enfraquecer sua credibilidade; seria refutado caso pacientes continuassem ruminando intensamente mesmo após reconhecerem racionalmente a falsidade estatística do pensamento temido. Em contrapartida, o Modelo de Flexibilidade Psicológica da ACT (Steven Hayes) sustenta que o debate lógico mantém a relevância atencional do estímulo e que apenas a desfusão (observar o pensamento como evento verbal transitório sem obediência) extingue o circuito de retroalimentação; essa previsão cairia caso a exposição sem reestruturação não reduzisse a frequência de evitação comportamental comparada a grupos controle.\n\n"
                "Em ensaios comparativos sobre pensamentos intrusivos obsessivos e efeito rebote de supressão (experimentos de Daniel Wegner), a explicação baseada em monitoramento irônico e desfusão exibe maior poder explicativo para o fracasso da supressão direta, enquanto a reestruturação racional retém eficácia específica quando há déficit informacional explícito que alimenta catastrofização.\n\n"
                "### Extra Info\n\n"
                "1. A Teoria dos Processos Irônicos, formulada por Daniel Wegner em 1994, descreve dois sub-processos simultâneos na supressão mental: um processo intencional consciente de distração e um processo automático de busca que monitora continuamente o conteúdo proibido.\n"
                "2. Na Terapia de Aceitação e Compromisso (ACT), a fusão cognitiva contrasta com a desfusão mediante exercícios de distanciamento linguístico que enfraquecem o controle literal das regras verbais sobre o comportamento motor."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "competing_hypotheses",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "_dni6oPFxYc",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ch_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Diplomaticidade dos Acordos e a Fragilização da Ordem Suprema\n\n"
                "A suspensão prévia de sanções internacionais, ocorrida em momento anterior sob a égide de negociações bilaterais, revelou os limites da acomodação diplomática entre Brasília e Washington. Quando pressões internas e externas alteram o equilíbrio de interesses em jogo, concessões informais desprovidas de garantias contratuais rígidas desfazem-se rapidamente.\n\n"
                "O episódio evidencia a fragilidade de arranjos baseados em expectativas políticas conjunturais diante de mudanças de liderança executiva ou pressões legislativas em capitais estrangeiras."
            ),
            "candidate_text": (
                "## Interpretações Diversas sobre a Suspensão de Sanções Bilaterais\n\n"
                "O recuo ou a retomada de sanções financeiras entre Brasília e Washington desperta múltiplas leituras igualmente válidas entre observadores. Alguns analistas afirmam que a decisão resulta de negociações econômicas sobre tarifas industriais; outros comentaristas sugerem que tudo decorre de disputas eleitorais internas nos Estados Unidos; há ainda quem aponte pressões diretas de parlamentares de oposição ou cálculos estratégicos ligados a cadeias minerais.\n\n"
                "Todas essas possibilidades coexistem no debate público como opiniões plausíveis sobre o episódio, sem que seja possível estabelecer critérios empíricos de refutação para testar qualquer uma delas ou ordená-las segundo evidências documentais disponíveis.\n\n"
                "### Extra Info\n\n"
                "1. Alterações na lista SDN do Departamento do Tesouro norte-americano podem ocorrer por determinação executiva sem necessidade de aprovação prévia do Congresso caso amparadas por lei delegada existente.\n"
                "2. Registros oficiais do Federal Register documentam a data exata de designação ou remoção (delisting) administrativa de indivíduos sancionados."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "competing_hypotheses",
            "difficulty": "typical",
            "expected_anomaly": "unranked_laundry_list_of_opinions_without_falsification_or_evidence_ranking",
            "defect_location": "body",
            "video_id": "R8-dCSHLItE",
            "target_verdict": "FAIL",
        },
    },
]
