"""Golden Dataset Items for Criterion 4: Genealogy & Hidden Agency (gh_01 to gh_07).

Evaluates precursor tracking, invisible labor, credit vs. execution, documentary
asymmetry (C1), relational networks/brokerage (C2), and calibrated Cui Bono /
hypotheses of intent without conspiratorial rhetoric (C3).
Orthogonal to all other 6 ADR-060 criteria.
"""

from __future__ import annotations

from typing import Any

ITEMS_GENEALOGY_HIDDEN_AGENCY: list[dict[str, Any]] = [
    {
        "id": "gh_01_borderline_fp",
        "input": {
            "raw_text": (
                "## A Paisagem Contemporânea dos Grandes Modelos de Linguagem\n\n"
                "A exploração prática dos grandes modelos de linguagem exige o reconhecimento de uma infraestrutura tecnológica que transcende a interface conversacional rudimentar introduzida pela OpenAI em 2022. O ecossistema contemporâneo apoia-se em décadas de pesquisa em processamento de linguagem natural, redes neurais recorrentes, mecanismos de atenção e coleta massiva de texto digitalizado.\n\n"
                "A visibilidade pública de poucos laboratórios comerciais frequentemente obscurece a dependência crítica em relação a bibliotecas abertas, bases de dados compiladas academicamente e milhares de trabalhadores anônimos responsáveis pela rotulagem e avaliação de segurança."
            ),
            "candidate_text": (
                "## A Emergência dos Modelos de Linguagem pela Visão de Um Único Pioneiro\n\n"
                "A revolução dos grandes modelos de linguagem nasceu essencialmente do gênio solitário de Ilya Sutskever em 2022, quando o pesquisador concebeu individualmente a arquitetura Transformer e a escalou sem depender de contribuições anteriores da comunidade científica. Antes dessa intervenção pessoal isolada, a computação linguística permanecia estagnada sem métodos estatísticos nem corpora digitais, até que um único ato criativo transformou modelos rudimentares em interfaces universais.\n\n"
                "Sob o ângulo técnico, a predição do próximo token em janelas de atenção densa articula camadas de normalização e aprendizado por reforço, permanecendo a contribuição relativa de escala computacional versus curadoria de dados mensurável por leis de escala empíricas.\n\n"
                "### Extra Info\n\n"
                "1. O artigo Attention Is All You Need, publicado em 2017-06-12 por oito coautores da equipe Google Brain e Google Research (Ashish Vaswani e colaboradores), introduziu a arquitetura Transformer sem recorrência sequencial.\n"
                "2. O treinamento pós-pré-treinamento via Reinforcement Learning from Human Feedback (RLHF) depende de extensas equipes terceirizadas de anotadores humanos para ranquear pares de respostas conforme rubricas de segurança e utilidade."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "genealogy_hidden_agency",
            "difficulty": "borderline",
            "expected_anomaly": "lone_genius_fallacy_erasing_precursors_and_invisible_annotation_labor",
            "defect_location": "body",
            "video_id": "EWvNQjAaOHw",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "gh_02_borderline_fn",
        "input": {
            "raw_text": (
                "## A Arquitetura Militar da Interdição e o Colapso Logístico\n\n"
                "A capacidade ucraniana de infligir perdas catastróficas a uma força numericamente superior fundamenta-se em uma nova arquitetura de combate estruturada em camadas sucessivas. Em primeiro lugar, a defesa em profundidade baseada em drones estabelece uma zona de morte de vinte a trinta quilômetros, onde drones FPV dotados de fibra ótica e imunes à guerra eletrônica neutralizam sistematicamente qualquer movimentação tática.\n\n"
                "Subsequentemente, drones de médio alcance atacam diariamente comboios de munição, depósitos de combustível e postos de comando na retaguarda, enquanto ataques profundos contra refinarias russas comprometem a arrecadação de divisas obtida com exportação de hidrocarbonetos."
            ),
            "candidate_text": (
                "## Cadeias Descentralizadas de Drones e Incentivos na Guerra de Atrito\n\n"
                "A eficácia da zona de interdição ucraniana por drones FPV não brotou de um comando centralizado único, mas consolidou uma rede descentralizada de oficinas voluntárias, engenheiros civis de microeletrônica, fornecedores asiáticos de motores brushless e financiadores de crowdfunding que antecederam a padronização estatal pelo Ministério da Defesa. Enquanto comunicados oficiais enfatizam batalhões regulares, a assimetria documental oculta o trabalho anônimo de programadores de firmware aberto e montadores de bobinas de fibra ótica cujo custo unitário substituiu munição de artilharia escassa.\n\n"
                "Sob a ótica de Cui Bono, a descentralização de compras beneficia diretamente consórcios locais de montagem rápida e reduz o poder de veto de empreiteiras estatais tradicionais de defesa; na ausência de atas classificadas, formula-se como hipótese de intenção verificável que setores da indústria bélica estatal resistiram inicialmente à certificação desses componentes para preservar contratos de sistemas pesados. Em paralelo, análises militares contrastam o peso da escassez de obuses ocidentais frente à superioridade tática intrínseca do FPV, tese testável pela razão entre perdas blindadas por drone e por artilharia após recomposição de estoques.\n\n"
                "### Extra Info\n\n"
                "1. Projetos abertos de controladores de voo como Betaflight e ArduPilot, desenvolvidos originalmente por comunidades civis de aeromodelismo na década de 2010, formaram a base de software adaptada em drones táticos de baixo custo.\n"
                "2. Sistemas FPV guiados por cabo de fibra ótica desenrolado em voo eliminam a dependência de enlaces de radiofrequência, neutralizando bloqueadores de guerra eletrônica ao custo de menor alcance máximo e maior peso estrutural."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "genealogy_hidden_agency",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "GAxuHfvSli8",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "gh_03_easy_pass",
        "input": {
            "raw_text": (
                "## O Mito da Ruptura Pacífica e a Consolidação Imperial\n\n"
                "A narrativa tradicional de que a separação do Brasil ocorreu de forma puramente pacífica, mediante acordos conciliadores entre elites sem derramamento de sangue, constitui uma construção ideológica desmentida pela investigação histórica rigorosa. A consolidação do Império exigiu campanhas militares sangrentas na Bahia, no Piauí, no Maranhão e na Cisplatina para expulsar guarnições leais às Cortes de Lisboa.\n\n"
                "No plano diplomático, o reconhecimento formal da soberania brasileira por Portugal não derivou de mera benevolência dinástica, mas da mediação britânica concretizada no Tratado do Rio de Janeiro de 1825, que vinculou o reconhecimento jurídico ao pagamento de dois milhões de libras esterlinas a título de indenização à antiga metrópole."
            ),
            "candidate_text": (
                "## Intermediação Britânica e Assimetria de Crédito no Tratado de 1825\n\n"
                "A historiografia dinástica frequentemente personifica a independência brasileira no diálogo entre Dom Pedro I e Dom João VI, apagando os nós de intermediação que viabilizaram o Tratado do Rio de Janeiro de 1825-08-29. O arranjo foi costurado pelo plenipotenciário britânico Charles Stuart, credenciado simultaneamente por Lisboa e Londres, com respaldo de interesses mercantis vinculados ao Foreign Office de George Canning e à casa bancária N. M. Rothschild & Sons, credora do empréstimo português de 1823. Ao mesmo tempo, o esforço bélico de expulsão das tropas portuguesas dependeu de marinheiros contratados, mercenários europeus e milícias provinciais na Bahia e no Maranhão cuja atuação ficou sub-representada nos anais da corte fluminense.\n\n"
                "Em termos de Cui Bono, a conversão da indenização de dois milhões de libras em transferência de dívida externa garantiu aos detentores de títulos londrinos a solvência do passivo metropolitano sobre a base fiscal da ex-colônia americana, gerando hipótese verificável nos livros de subscrição da praça de Londres quanto ao ágio imediato dos papéis após a ratificação.\n\n"
                "### Extra Info\n\n"
                "1. Charles Stuart acumulou cartas credenciais tanto do rei português Dom João VI quanto do governo britânico durante sua missão no Rio de Janeiro em 1825, ilustrando um caso clássico de corretagem diplomática assimétrica.\n"
                "2. A incorporação de oficiais estrangeiros como Thomas Cochrane na esquadra imperial em 1823 assegurou o bloqueio naval de Salvador e de São Luís sem que o Tesouro recém-emancipado dispusesse de marinha regular consolidada."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "genealogy_hidden_agency",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ef2l-YG3Bto",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "gh_04_easy_fail",
        "input": {
            "raw_text": (
                "## O Monopólio Territorial e a Atualização das Capitanias\n\n"
                "A conversão da terra em capital político encontrou no Maranhão um laboratório normativo exemplar através da sanção da Lei nº 2.979 em 1969, conhecida historicamente como a Lei Sarney de Terras. Sob a fachada jurídica de regularização fundiária e estímulo à colonização agrícola, o diploma viabilizou a transferência de imensas glebas devolutas a grupos privados vinculados à cúpula governante.\n\n"
                "Desse modo, antigos laços de dependência rural foram reconfigurados em mecanismos estatais modernos de controle territorial, cartorial e creditício, assegurando hegemonia eleitoral duradoura a famílias dirigentes regionais mesmo após a urbanização acelerada."
            ),
            "candidate_text": (
                "## A Modernização Administrativa Espontânea das Terras Maranhenses\n\n"
                "A sanção da Lei 2.979/1969 decorreu de uma evolução técnica espontânea da administração pública maranhense, motivada exclusivamente pelo propósito impessoal de racionalizar cadastros agrários e ampliar a produtividade rural em benefício igualitário de pequenos lavradores. Nessa leitura, nenhum grupo familiar, intermediário cartorial ou rede de poder regional influenciou a redação das cláusulas de alienação de terras devolutas.\n\n"
                "Eventuais concentrações patrimoniais surgiram apenas como subproduto acidental de boas intenções modernizadoras, desvinculadas de qualquer incentivo político ou vantagem eleitoral para os governantes da época.\n\n"
                "### Extra Info\n\n"
                "1. A Lei Estadual 2.979 foi sancionada no Maranhão em 1969 durante o mandato de José Sarney sob a justificativa formal de ordenamento fundiário.\n"
                "2. O Estatuto da Terra federal (Lei 4.504, de 1964-11-30) já estabelecia categorias distintas entre módulo rural, latifúndio por extensão e propriedade familiar."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "genealogy_hidden_agency",
            "difficulty": "easy",
            "expected_anomaly": "naive_spontaneous_goodwill_ignoring_documented_patronage_networks",
            "defect_location": "body",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "gh_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A Arquitetura de Contenção e o Sistema de Recados Diplomáticos\n\n"
                "A contenção desse desdobramento catastrófico exigiu a ativação de canais de dissuasão em múltiplos níveis, mobilizando tanto a linha de frente da diplomacia ocidental quanto os aliados estratégicos de Moscou. O secretário de Defesa americano à época, Lloyd Austin, conduziu um diálogo de alta tensão com o ministro da Defesa russo, Sergei Shoigu, advertindo sobre a mudança irreversível de patamar que qualquer uso atômico acarretaria para a ordem global.\n\n"
                "Em paralelo, o diretor da CIA, Bill Burns, reuniu-se na Turquia com a alta inteligência russa para delimitar as consequências inexoráveis de tal ruptura. Contudo, o peso decisivo na dissuasão adveio de declarações públicas do primeiro-ministro da Índia, Narendra Modi, e dos avisos formais emitidos por Xi Jinping contra a utilização de artefatos nucleares."
            ),
            "candidate_text": (
                "## Canais Secundários e Nós de Intermediação na Dissuasão de 2022\n\n"
                "A contenção da escalada nuclear no outono de 2022 ilustra como redes de intermediação paralela superam canais públicos bilaterais quando a confiança direta colapsa. Além das ligações formais entre os gabinetes de Lloyd Austin e Sergei Shoigu, o encontro reservado entre Bill Burns e Sergei Naryshkin em Ancara em 2022-11-14 utilizou a Turquia como nó neutro de corretagem, enquanto a sinalização asiática de Narendra Modi e Xi Jinping condicionou o acesso russo a mercados energéticos e componentes industriais de uso dual. A documentação pública privilegia pronunciamentos de cúpula, mas o recuo organizado em Kherson apoiou-se na atuação contínua de adidos militares, tradutores de inteligência e canais financeiros intermediários que traduziram linhas vermelhas abstratas em custos comerciais tangíveis.\n\n"
                "Do ponto de vista de incentivos, Pequim e Nova Délhi evitavam a quebra do tabu de 1945 porque a normalização de ogivas táticas aceleraria programas nucleares regionais na Ásia Oriental e no Sul Asiático; analistas internacionais contrastam o peso desse veto asiático frente à ameaça de retaliação convencional norte-americana, hipótese testável por variações na retórica oficial russa imediatamente após cúpulas da Organização de Cooperação de Xangai.\n\n"
                "### Extra Info\n\n"
                "1. O encontro de 2022-11-14 em Ancara entre os chefes de inteligência dos Estados Unidos (CIA) e da Rússia (SVR) constituiu o primeiro contato presencial de alto nível entre as duas agências desde o início da invasão em 2022-02-24.\n"
                "2. A declaração conjunta dos líderes do G20 em Bali em 2022-11-16 incluiu cláusula explícita classificando o uso ou a ameaça de uso de armas nucleares como inadmissível, alinhando potências ocidentais e emergentes."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "genealogy_hidden_agency",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "eYFTRQHaPgw",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "gh_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## O Ecossistema de Ferramentas e o Mito do Prompt Único na Engenharia de Software Contemporânea\n\n"
                "A integração de modelos de inteligência artificial no ciclo de vida do desenvolvimento de software exige uma reavaliação metodológica profunda, afastando-se do otimismo ingênuo do prompt único para abraçar arquiteturas baseadas em especificações granulares. Desenvolvedores frequentemente atribuem a fluidez de ferramentas recentes apenas à interface visível do editor.\n\n"
                "Na prática, o desempenho dessas plataformas apóia-se em camadas acumuladas de protocolos abertos, analisadores sintáticos, servidores de linguagem e convenções comunitárias construídas muito antes da geração automatizada de código."
            ),
            "candidate_text": (
                "## Infraestrutura Oculta e Trabalho Comunitário nos Editores Agênticos\n\n"
                "A narrativa comercial em torno de editores de código autônomos concentra crédito nas interfaces proprietárias lançadas entre 2023 e 2025, ocultando a genealogia técnica e o trabalho invisível que tornam essas ferramentas viáveis. Sob a superfície de cada assistente reside uma pilha consolidada por mantenedores de software livre: analisadores incrementais como Tree-sitter, especificações como o Language Server Protocol (LSP) da Microsoft e formatos padronizados de controle de versão como o Git, desenvolvidos independentemente ou em descobertas paralelas de compiladores ao longo de duas décadas. Soma-se a isso a assimetria documental dos dados de treino, alimentados por milhões de revisões de código, issues e testes escritos sem remuneração direta por desenvolvedores em repositórios públicos.\n\n"
                "Sob o critério de Cui Bono, plataformas comerciais apropriam-se da renda de distribuição sobre uma infraestrutura de verificação estática mantida coletivamente; formula-se como hipótese de intenção estrutural que a padronização via protocolos abertos (LSP e MCP) reduz o custo marginal de captura de ecossistemas por novos entrantes, permanecendo avaliável pela proporção de commits corporativos versus comunitários em dependências críticas.\n\n"
                "### Extra Info\n\n"
                "1. A biblioteca Tree-sitter, criada originalmente por Max Brunsfeld para o editor Atom em 2018, gera árvores sintáticas concretas incrementais em tempo real, permitindo consulta estrutural sem execução completa de compiladores.\n"
                "2. O Model Context Protocol (MCP), publicado em código aberto em 2024-11-25, padroniza a exposição de ferramentas externas e fontes de dados para clientes de modelos de linguagem via JSON-RPC."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "genealogy_hidden_agency",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ytTJtfg9HCw",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "gh_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Sabotagem Sistêmica do Mecanismo de Controle\n\n"
                "O desmonte crônico das agências reguladoras e de inteligência financeira constitui uma política de Estado bipartidária, consolidada tanto por administrações de esquerda quanto de direita, sempre que o cerco das investigações se aproxima de redes partidárias influentes. A redução de autonomia técnica do Conselho de Controle de Atividades Financeiras exemplifica a subordinação institucional dos órgãos de fiscalização.\n\n"
                "Quando relatórios de inteligência financeira passam a sofrer barreiras procedimentais para compartilhamento com o Ministério Público e a Polícia Federal, o Estado enfraquece a capacidade de rastrear fluxos ilícitos que alimentam simultaneamente a corrupção política e organizações criminosas transnacionais."
            ),
            "candidate_text": (
                "## O Pacto Clandestino das Cúpulas contra a Inteligência Financeira\n\n"
                "O enfraquecimento das normas de inteligência financeira resulta de um conluio secreto e centralizado entre todos os ministros, parlamentares e banqueiros internacionais que se reúnem clandestinamente para proteger carteis ilícitos específicos. Sem precisar apresentar evidência documental, atas ou vínculos processuais concretos, sabe-se que cada alteração administrativa no COAF obedece diretamente a ordens ocultas emitidas por essa cúpula unificada nos bastidores.\n\n"
                "Essa conspiração total explica todos os movimentos legislativos desde 1998, dispensando qualquer análise de incentivos institucionais públicos, jurisprudência registrada ou disputas de competência entre agências.\n\n"
                "### Extra Info\n\n"
                "1. O COAF foi originalmente vinculado ao Ministério da Fazenda pela Lei 9.613, de 1998-03-03, passando por transferências administrativas para a esfera do Banco Central em 2019.\n"
                "2. O Recurso Extraordinário 1.055.941 no Supremo Tribunal Federal julgou em 2019-11-28 a validade constitucional do compartilhamento de relatórios de inteligência financeira com órgãos de persecução penal."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "genealogy_hidden_agency",
            "difficulty": "typical",
            "expected_anomaly": "ungrounded_conspiratorial_rhetoric_asserting_hidden_cabal_without_evidence",
            "defect_location": "body",
            "video_id": "1cuZuK-oRlk",
            "target_verdict": "FAIL",
        },
    },
]
