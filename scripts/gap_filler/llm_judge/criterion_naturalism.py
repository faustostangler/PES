"""Golden Set items for AUTHORIAL_NATURALISM_VOICE criterion (7 items: 4 PASS, 3 FAIL).

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - ADR-028: Decoupling Fluid Prose and Socratic Gap Filling
    - SPEC-015: Quality Gates and Calibration Framework
"""

from __future__ import annotations

from typing import Any

ITEMS_NATURALISM: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Disguised antitheses and subtle moralizing tone in tech critique
    {
        "id": "an_01_borderline_fp",
        "input": {
            "raw_text": (
                "## A Falácia do Prompt Engineering como Habilidade Duradoura\n\n"
                "Muitos analistas de tecnologia acreditam que o ajuste artesanal de prompts garante relevância profissional "
                "no ecossistema de inteligência artificial. Com a rápida evolução dos modelos para raciocínio estruturado, "
                "a dependência de macetes verbais perde valor diante de arquiteturas de software sólidas."
            ),
            "candidate_text": (
                "## O Esgotamento das Heurísticas Verbais: Da Engenharia de Prompts à Arquitetura de Sistemas\n\n"
                "A corrida frenética por fórmulas mágicas de comando reflete a ilusão ingênua de que atalhos linguísticos "
                "podem substituir o rigor fundamental da engenharia de software. Não se trata de uma especialização técnica legítima, "
                "mas sim de um modismo passageiro explorado por oportunistas que vendem manuais simplórios para profissionais desatentos.\n\n"
                "Longe de constituir uma competência perene na era dos transformadores, a manipulação de adjetivos e instruções em linguagem "
                "natural revela-se uma prática lamentavelmente estéril. Os novos modelos de raciocínio avançado, como o OpenAI o1, internalizam "
                "cadeias de pensamento estruturadas em tempo de inferência, tornando os antigos truques de formulação obsoletos e ridículos.\n\n"
                "A verdadeira engenharia reside não no empirismo ingênuo dos prompts, mas no design determinístico de pipelines com esquemas "
                "validados por Pydantic e interfaces assíncronas resilientes.\n\n"
                "## Informações Complementares\n\n"
                "1. A técnica de Chain-of-Thought (CoT), descrita por Jason Wei e colaboradores em 2022, demonstrou que a indução "
                "explícita de etapas intermediárias de cálculo melhora a acurácia em raciocínio aritmético e simbólico.\n\n"
                "2. A especificação JSON Schema, mantida pelo consórcio IETF, padroniza anotações e regras de validação para dados "
                "estruturados trocados em interfaces de programação de aplicações (APIs)."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "authorial_naturalism",
            "difficulty": "borderline",
            "expected_anomaly": "disguised_antitheses_and_moralistic_condescension",
            "defect_location": "paragraphs_1_and_2",
            "video_id": "ytTJtfg9HCw",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Rigorous biological and thermodynamic naturalism in public choice
    {
        "id": "an_02_borderline_fn",
        "input": {
            "raw_text": (
                "## A Escolha Pública e o Comportamento Burocrático\n\n"
                "A escola da Escolha Pública demonstra que agentes governamentais buscam maximizar seus próprios interesses "
                "orçamentários e regulatórios. A expansão contínua da máquina estatal responde a incentivos internos da própria burocracia, "
                "independentemente do bem-estar social prometido nas leis."
            ),
            "candidate_text": (
                "## A Mecânica Biofísica da Apropriação: A Escola da Escolha Pública e a Termodinâmica Burocrática\n\n"
                "A persistência do aparato estatal moderno assemelha-se à homeostase de um organismo complexo submetido à "
                "pressão seletiva de recursos limitados. Sob a formulação de **James Buchanan** e **Gordon Tullock**, o agente público "
                "opera despido de inclinações heroicas ou altruístas: trata-se de uma unidade biológica racional que busca maximizar seu "
                "consumo metabólico de poder discricionário, prestígio institucional e estabilidade de renda.\n\n"
                "A multiplicação de regulamentações atua como uma barreira física de atrito sobre o sistema produtivo, análoga ao "
                "aumento de viscosidade em um fluido circulatório. Ao criar nós de estrangulamento procedimental na concessão de licenças "
                "e alvarás, o órgão regulador gera um gradiente artificial de escassez que obriga os operadores econômicos a despender "
                "energia metabólica sob a forma de taxas de conformidade e honorários de despachantes para destravar o fluxo operacional.\n\n"
                "Nesse ecossistema concorrencial, a ampliação da complexidade legal não decorre de desvios individuais, mas da própria lógica "
                "de autopreservação e expansão de área de contato do tecido burocrático.\n\n"
                "## Informações Complementares\n\n"
                "1. A obra fundadora **The Calculus of Consent: Logical Foundations of Constitutional Democracy** foi publicada por James "
                "Buchanan e Gordon Tullock em 1962, aplicando modelos de escolha racional aos processos de votação legislativa.\n\n"
                "2. O economista William Niskanen formalizou o modelo de maximização orçamentária do burocrata em 1971, postulando que o "
                "tamanho do orçamento de uma agência serve como métrica aproximada para a utilidade pessoal do administrador."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "authorial_naturalism",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "7tZdt2UQtbg",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Exemplary naturalism, geographic and demographic determinism without sentimentality
    {
        "id": "an_03_easy_pass",
        "input": {
            "raw_text": (
                "## O Enclave de Ceuta e a Geopolítica do Estreito de Gibraltar\n\n"
                "Ceuta ocupa uma posição estratégica na entrada ocidental do Mediterrâneo sob soberania espanhola há séculos. "
                "A cidade enfrenta pressões demográficas e migratórias permanentes por ser a única fronteira terrestre da União Europeia "
                "no continente africano."
            ),
            "candidate_text": (
                "## A Topografia da Fricção: O Enclave de Ceuta e o Equilíbrio Hidrográfico no Estreito\n\n"
                "A estabilidade geopolítica do promontório de **Ceuta** repousa em contingências orográficas e oceanográficas "
                "que subordinam qualquer cálculo diplomático temporário. Localizada no istmo da península de Almina, a praça-forte espanhola "
                "funciona como um ponto de estrangulamento que vigia os dezoito quilômetros de largura do canal de Gibraltar, canalizando "
                "o fluxo de circulação marítima entre o Atlântico e a bacia mediterrânica.\n\n"
                "A barreira perimetral de oito quilômetros e duzentos metros erguida em torno do perímetro territorial atua como uma "
                "membrana seletiva submetida a gradientes de pressão demográfica extremos. De um lado, a transição etária acelerada da "
                "península Ibérica convive com excedentes populacionais jovens no Magreb e no Sahel subsaariano, gerando uma tensão mecânica "
                "contínua sobre os postos de controle de Tarajal e Benzú.\n\n"
                "A gestão desse atrito fronteiriço reflete o equilíbrio de forças físicas e hidrocarbonetos entre o reino alauita e os estados "
                "membros de Schengen, convertendo o fluxo migratório em válvula hidrostática de compensação geopolítica.\n\n"
                "## Informações Complementares\n\n"
                "1. A posse de Ceuta foi formalizada pela coroa espanhola em 1668 pelo Tratado de Lisboa, após a Restauração da Independência "
                "portuguesa, quando os habitantes locais optaram por jurar fidelidade a Carlos II da Espanha.\n\n"
                "2. A cerca de segurança de Ceuta conta com monitoramento por câmeras térmicas, sensores de movimento subterrâneos e sistema "
                "integrado de vigilância externa operado pela Guarda Civil espanhola."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "authorial_naturalism",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - High moralistic indignation and sensationalist outrage
    {
        "id": "an_04_easy_fail",
        "input": {
            "raw_text": (
                "## Pedidos de Impeachment contra Ministros do STF\n\n"
                "Parlamentares da oposição protocolaram sucessivos pedidos de impeachment contra o ministro Gilmar Mendes no Senado Federal. "
                "O presidente da casa legislativa mantém as representações arquivadas ou sem tramitação, gerando críticas sobre blindagem mútua."
            ),
            "candidate_text": (
                "## A Blindagem Desavergonhada: O Senado de Joelhos e o Escândalo Gilmar Mendes\n\n"
                "É uma vergonha nacional inadmissível o que o presidente do Senado faz ao engavetar os justos pedidos de impedimento "
                "do ministro Gilmar Mendes. Uma corte que deveria ser o templo sagrado da Constituição transformou-se em um balcão de negócios "
                "nojento, onde a impunidade zomba descaradamente da cara do cidadão de bem que trabalha de sol a sol para pagar impostos extorsivos!\n\n"
                "O ministro cometeu abusos escandalosos e deveria ser sumariamente expulso e preso para servir de exemplo moral. Sua conduta "
                "revoltante mancha a honra do país perante o mundo civilizado. Como pode um magistrado viajar em jatinhos de magnatas e rir "
                "da nossa miséria sem que o povo saia às ruas para derrubar esses canalhas?\n\n"
                "A omissão covarde dos senadores é uma traição inominável que clama aos céus por justiça e queima na alma dos verdadeiros "
                "patriotas que não aceitam viver sob a bota imunda da ditadura da toga.\n\n"
                "## Informações Complementares\n\n"
                "1. A Lei Federal 1.079/1950 (Lei do Impeachment) define os crimes de responsabilidade e estabelece a competência privativa "
                "do Senado Federal para processar e julgar os ministros do Supremo Tribunal Federal.\n\n"
                "2. O artigo 52, inciso II, da Constituição Federal de 1988 exige quórum de dois terços dos votos dos membros do Senado "
                "Federal para a condenação definitiva à perda do cargo em processo de impedimento."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "authorial_naturalism",
            "difficulty": "easy",
            "expected_anomaly": "moralistic_outrage_sensationalism_and_civic_indignation",
            "defect_location": "entire_body",
            "video_id": "z82sKS_xj28",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Cool sociological dissection of financial surveillance
    {
        "id": "an_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## O Monitoramento Financeiro pelo COAF e a Lei de Lavagem de Dinheiro\n\n"
                "O Conselho de Controle de Atividades Financeiras centraliza dados de movimentações atípicas comunicadas por bancos. "
                "Relatórios de inteligência financeira subsidiam inquéritos policiais sem necessidade de autorização judicial prévia, "
                "provocando debates sobre sigilo bancário."
            ),
            "candidate_text": (
                "## A Cibernética da Vigilância Financeira: A Malha do COAF e a Fluidez do Capital\n\n"
                "A estruturação do Conselho de Controle de Atividades Financeiras (**COAF**) materializa a doutrina contemporânea "
                "de contenção de fluxos monetários ilícitos através de telemetria bancária contínua. Operando como nó de agregação informacional, "
                "o conselho não desempenha funções jurisdicionais punitivas: atua como filtro de desvio padrão algorítmico, identificando "
                "incongruências entre a capacidade contributiva declarada e o volume de depósitos fracionados em espécie.\n\n"
                "A obrigatoriedade de notificação imposta às instituições de crédito terceiriza o custo de policiamento para os departamentos "
                "de conformidade privados, sob pena de sanções administrativas severas. Esse mecanismo converte os gerentes de risco em "
                "sensores periféricos do aparato estatal, registrando operações atípicas em relatórios analíticos de inteligência financeira (**RIF**).\n\n"
                "A expansão dessa rede reduz a liquidez das operações informais e eleva a fricção transacional sobre setores intensivos em papel-moeda, "
                "delimitando o perímetro de circulação do capital dentro das fronteiras monitoráveis do sistema de pagamentos instantâneos.\n\n"
                "## Informações Complementares\n\n"
                "1. A Lei Federal 9.613/1998 criou o COAF e tipificou os crimes de lavagem de dinheiro, sendo profundamente reformada "
                "pela Lei Federal 12.683/2012, que extinguiu o rol taxativo de crimes antecedentes.\n\n"
                "2. A Circular 3.978/2020 do Banco Central do Brasil disciplinou a política, os procedimentos e os controles internos "
                "a serem adotados pelas instituições financeiras para identificação e monitoramento de clientes e operações suspeitas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "authorial_naturalism",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "1cuZuK-oRlk",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Hard mechanical engineering constraints on memory and processor architecture
    {
        "id": "an_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## A Gestão de Memória e Concorrência em Sistemas de Baixa Latência\n\n"
                "A alternância de contexto e as falhas de cache de CPU impõem custos severos em serviços web de alto rendimento. "
                "A alocação excessiva de ponteiros em heap fragmenta o acesso à memória e degrada o desempenho dos núcleos de processamento."
            ),
            "candidate_text": (
                "## A Física do Silício: Localidade Espacial, Falhas de Cache e Fricção em Concorrência\n\n"
                "Em sistemas computacionais de alto rendimento, o gargalo de execução não reside na sofisticação algorítmica abstrata, "
                "mas na distância física e no tempo de trânsito dos elétrons entre o registrador do processador e as barras de memória RAM. "
                "A penalidade temporal imposta por uma falha de cache L3 gira em torno de duzentos ciclos de CPU, equivalendo a uma eternidade "
                "mecânica em pipelines orientados a dezenas de milhares de operações por milissegundo.\n\n"
                "Quando threads concorrentes disputam estruturas de dados desalinhadas na mesma linha de cache de sessenta e quatro bytes, "
                "ocorre o fenômeno destrutivo de falso compartilhamento. O protocolo de coerência de cache (MESI) invalida continuamente os estados "
                "das caches dos núcleos vizinhos, forçando barramentos a transmitir mensagens de sincronização que anulam o paralelismo do hardware.\n\n"
                "O design eficiente de sistemas impõe portanto a compactação de layouts de dados contíguos em memória para maximizar o pré-carregamento "
                "espacial e eliminar trocas de contexto desnecessárias no agendador do sistema operacional.\n\n"
                "## Informações Complementares\n\n"
                "1. O protocolo MESI (Modified, Exclusive, Shared, Invalid) é o padrão de coerência de cache de escrita que sincroniza "
                "o estado das linhas de dados entre processadores com múltiplos núcleos independentes.\n\n"
                "2. O fenômeno da parede de memória (Memory Wall) foi formulado em 1995 por Wm. A. Wulf e Sally A. McKee, descrevendo a "
                "divergência exponencial entre a velocidade de processamento dos núcleos e a largura de banda da memória principal."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "authorial_naturalism",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Academic legalese, ornamental Latinisms, and repetitive antitheses
    {
        "id": "an_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Estrutura Notarial e Registral sob o Prisma Institucional\n\n"
                "A delegação das funções notariais a particulares garante segurança jurídica às transações privadas no Brasil. "
                "Contudo, a rigidez corporativa das associações de classe dificulta a modernização tecnológica e a redução de taxas."
            ),
            "candidate_text": (
                "## A Hermenêutica Registral e o Desiderato Notarial no Ordenamento Pátrio\n\n"
                "Convém assentar ab initio que o instituto da delegação extrajudicial não consubstancia uma mera benesse estatal, "
                "mas sim uma conditio sine qua non para a mantença da higidez transacional no tecido societário. Mutatis mutandis, "
                "a chancela pública outorgada aos tabelionatos opera não apenas como garantia formal, mas sobretudo como baluarte inescusável "
                "contra a eclosão de lides patrimoniais temerárias.\n\n"
                "Não se pode olvidar, data venia, que as resistências corporativas à inovação digital decorrem não da inércia dos agentes, "
                "mas fundamentalmente do temor reverencial ante a precarização das solenidades milenares do direito registral. Não se trata "
                "de privilégio anacrônico, mas sim de solene prerrogativa indispensável à tutela da dignidade negocial.\n\n"
                "Cumpre aos operadores do direito sopesar tais vetores com a devida prudência pretoriana, evitando reformas afoitas "
                "que venham a vulnerar a segurança jurídica que há séculos alicerça a propriedade imobiliária nacional.\n\n"
                "## Informações Complementares\n\n"
                "1. O princípio da publicidade notarial impõe a oponibilidade erga omnes dos registros regularmente lavrados nos livros "
                "das serventias de registro de imóveis da comarca competente.\n\n"
                "2. A Lei 6.015/1973 (Lei de Registros Públicos) estabelece o princípio da continuidade registral, exigindo que cada "
                "nova inscrição patrimonial esteja formalmente encadeada ao assento precedente."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "authorial_naturalism",
            "difficulty": "typical",
            "expected_anomaly": "academic_legalese_ornamental_latinisms_and_repetitive_antitheses",
            "defect_location": "entire_body",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "FAIL",
        },
    },
]
