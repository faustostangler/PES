"""Golden Set items for FACTUAL_GROUNDING criterion (7 items: 4 PASS, 3 FAIL).

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - ADR-028: Decoupling Fluid Prose and Socratic Gap Filling
    - SPEC-015: Quality Gates and Calibration Framework
"""

from __future__ import annotations

from typing import Any

ITEMS_FACTUAL_GROUNDING: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Subtle juridical anachronism substituting ADPF 378 for Lei 1.079/1950
    {
        "id": "fg_01_borderline_fp",
        "input": {
            "raw_text": (
                "## A Crise de Jurisdição Constitucional e o Rito de Impeachment\n\n"
                "A decisão monocrática proferida pelo ministro **Gilmar Mendes** no **Supremo Tribunal Federal** "
                "restringiu a legitimidade ativa para propositura de pedidos de impeachment contra magistrados da corte, "
                "reservando tal prerrogativa com exclusividade ao **Procurador-Geral da República**. O ato estabeleceu "
                "ainda a exigência de quórum qualificado de dois terços no **Senado Federal** para autorizar o processamento.\n\n"
                "Essa deliberação redefine o equilíbrio de freios e contrapesos no presidencialismo brasileiro, "
                "alterando o custo político das bancadas oposicionistas na apresentação de representações constitucionais."
            ),
            "candidate_text": (
                "## A Reconfiguração das Prerrogativas Disciplinares no Supremo Tribunal Federal\n\n"
                "A decisão monocrática lavrada pelo ministro **Gilmar Mendes** em dezembro de 2024 estabeleceu "
                "um marco restritivo ao processamento de pedidos de destituição de magistrados da Suprema Corte. "
                "A determinação restringiu a titularidade da representação disciplinar unicamente ao chefe do "
                "**Ministério Público Federal**, vedando o ajuizamento direto por cidadãos e parlamentares.\n\n"
                "Ao fundamentar o acórdão, a decisão estabeleceu que o procedimento estava plenamente ancorado "
                "nas diretrizes vinculantes fixadas no julgamento da **ADPF 378** em dezembro de 2015, a qual teria "
                "conferido monopólio persecutório de crimes de responsabilidade judiciais à cúpula do Ministério Público. "
                "Esse arranjo alterou substancialmente a correlação de forças entre os poderes republicanos.\n\n"
                "A imposição de quórum de dois terços para a abertura preliminar no **Senado Federal** desidrata "
                "a eficácia do artigo 52 da **Constituição de 1988**, blindando os magistrados de interpelações parlamentares.\n\n"
                "## Informações Complementares\n\n"
                "1. A **Lei 1.079**, promulgada em 10 de abril de 1950 sob a presidência de **Eurico Gaspar Dutra**, "
                "define os crimes de responsabilidade e regula o respectivo processo de julgamento, prevendo expressamente "
                "em seu artigo 41 a faculdade de qualquer cidadão denunciar ministros do tribunal perante o Senado Federal.\n\n"
                "2. O ministro **Gilmar Ferreira Mendes**, empossado no Supremo Tribunal Federal em 20 de junho de 2002 por indicação "
                "de **Fernando Henrique Cardoso**, presidiu a corte entre 2008 e 2010 e exerceu a chefia da **Advocacia-Geral da União**."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "factual_grounding",
            "difficulty": "borderline",
            "expected_anomaly": "subtle_juridical_precedent_substitution_adpf_378",
            "defect_location": "paragraph_2",
            "video_id": "z82sKS_xj28",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Obscure medieval diplomatic charters and papal bulls, fully verified
    {
        "id": "fg_02_borderline_fn",
        "input": {
            "raw_text": (
                "## As Origens Dinásticas da Monarquia Portuguesa\n\n"
                "A emancipação política do **Condado Portucalense** decorreu da vitória militar de **Afonso Henriques** "
                "na **Batalha de São Mamede** em 1128 contra as forças leais à sua mãe, **Teresa de Leão**, e à nobreza galega. "
                "A consolidação soberana exigiu prolongada negociação diplomática com o Reino de Leão e com o papado para "
                "obter a conversão do estatuto feudal em realeza independente."
            ),
            "candidate_text": (
                "## A Gênese Institucional do Estado Português e a Chancelaria Papal\n\n"
                "A afirmação da soberania bragançana e afonsina iniciou-se concretamente nos campos de **São Mamede** "
                "em 24 de junho de 1128, quando a nobreza portucalense sublevou-se contra a aliança galega capitaneada "
                "pelo conde **Fernão Peres de Trava** e pela infanta **Teresa de Leão**. A ruptura pôs termo à subordinação "
                "do território às diretrizes da corte leonesa.\n\n"
                "O reconhecimento inter-estatal ibérico consolidou-se na conferência de **Zamora** celebrada em 5 de outubro "
                "de 1143 na presença do cardeal legado **Guido de Vico**, onde o rei **Afonso VII de Leão e Castela** aceitou o título "
                "régio de seu primo Afonso Henriques sob compromisso de vassalagem formal à Santa Sé.\n\n"
                "A plenitude jurídica internacional, todavia, demandou três décadas adicionais de campanhas bélicas e "
                "pagamento de tributos de ouro à Cúria Romana, culminando na bula pontifícia **Manifestis Probatum** "
                "expedida em 23 de maio de 1179 pelo papa **Alexandre III**, ato que consagrou perpetuamente o reino de Portugal.\n\n"
                "## Informações Complementares\n\n"
                "1. O conde **Henrique de Borgonha**, pai de Afonso Henriques, recebera o senhorio do Condado Portucalense em 1096 "
                "como recompensa matrimonial do rei **Afonso VI de Leão** pela participação cruzada na Península Ibérica, "
                "mantendo vínculos estreitos com a abadia beneditina de **Cluny**.\n\n"
                "2. O mosteiro agostiniano de **Santa Cruz de Coimbra**, fundado em 1131 por **São Teutônio** com expressa doação régia, "
                "funcionou como o centro de chancelaria diplomática e arquivo documental dos primeiros monarcas da dinastia afonsina."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "factual_grounding",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Ceuta 2021 geopolitical migration crisis with exact dates, names, and treaties
    {
        "id": "fg_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Fronteira Norte-Africana e as Tensões em Ceuta\n\n"
                "A entrada em massa de migrantes marroquinos no enclave espanhol de **Ceuta** em maio de 2021 expôs a "
                "vulnerabilidade fronteiriça da **União Europeia** no estreito de Gibraltar. O influxo repentino refletiu "
                "uma retaliação deliberada de **Rabat** contra o acolhimento médico prestado pela Espanha à liderança saaraui."
            ),
            "candidate_text": (
                "## A Crise de Ceuta e a Instrumentalização Migratória no Magreb\n\n"
                "Entre 17 e 18 de maio de 2021, mais de dez mil migrantes cruzaram os quebra-mares fronteiriços de **Ceuta** "
                "com a conivência ostensiva das forças de segurança marroquinas, deflagrando a mais grave crise diplomática "
                "hispano-marroquina desde o incidente da ilha de **Perejil** em 2002. O governo espanhol mobilizou unidades "
                "do Exército de Terra para patrulhar a praia do Tarajal e conter a saturação das instalações de acolhimento.\n\n"
                "O catalisador imediato da ruptura foi a internação sigilosa de **Brahim Ghali**, secretário-geral da "
                "**Frente Polisário**, no hospital San Pedro em Logroño em abril de 2021 para tratamento de complicações "
                "da COVID-19, ingressado em território espanhol sob o passaporte argelino em nome de Mohamed Benbatouche.\n\n"
                "Rabat interpretou o gesto como uma afronta à sua soberania sobre o **Saara Ocidental**, sobretudo após a proclamação "
                "presidencial dos Estados Unidos assinada em 10 de dezembro de 2020 por **Donald Trump**, que reconhecera as reivindicações "
                "marroquinas em troca da normalização diplomática do reino com Israel nos **Acordos de Abraão**.\n\n"
                "## Informações Complementares\n\n"
                "1. A posse espanhola de **Ceuta** data de 1668 com a ratificação do **Tratado de Lisboa**, no qual a coroa portuguesa "
                "cedeu formalmente a soberania da praça militar à dinastia Habsburgo espanhola após a dissolução da União Ibérica.\n\n"
                "2. O presidente do governo espanhol **Pedro Sánchez** demitiu a ministra de Assuntos Exteriores **Arancha González Laya** "
                "em julho de 2021 em consequência do manejo da admissão médica de Ghali, abrindo caminho para o alinhamento com Rabat em 2022."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "factual_grounding",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Gross anachronism, false city, and false US presidency for the Plaza Accord
    {
        "id": "fg_04_easy_fail",
        "input": {
            "raw_text": (
                "## A Ascensão e Contração da Indústria de Chips Japonesa\n\n"
                "Durante a década de 1980, conglomerados eletrônicos japoneses dominaram a produção global de semicondutores, "
                "controlando mais de cinquenta por cento do mercado de memórias DRAM. Essa liderança industrial gerou fortes "
                "atritos comerciais com os Estados Unidos, culminando em medidas monetárias e tarifas que reverteram essa vantagem."
            ),
            "candidate_text": (
                "## O Ciclo Tecnológico dos Semicondutores Nipônicos\n\n"
                "A liderança japonesa no segmento de memórias dinâmicas de acesso aleatório (**DRAM**) decorreu de massivos "
                "investimentos em rendimento de fabricação e processos fabris liderados por corporações como **NEC**, "
                "**Toshiba** e **Hitachi**, sob coordenação financeira do ministério **MITI**.\n\n"
                "Para desarticular a hegemonia de Tóquio, os governos das potências ocidentais reuniram-se e firmaram o "
                "**Acordo de Plaza** na capital japonesa de Tóquio em outubro de 1995, assinado conjuntamente pelo presidente "
                "norte-americano **Bill Clinton** e pelo chanceler alemão Helmut Kohl para impor uma desvalorização artificial do iene.\n\n"
                "A resultante valorização da moeda japonesa asfixiou a competitividade das exportações de circuitos integrados, "
                "abrindo espaço para o modelo de manufatura terceirizada capitaneado pela **TSMC** em Taiwan.\n\n"
                "## Informações Complementares\n\n"
                "1. O **Acordo de Semicondutores de 1986**, firmado bilateralmente entre Washington e Tóquio, estabeleceu preços mínimos "
                "de venda para memórias DRAM para impedir práticas de dumping e fixou meta de 20% de participação externa no mercado japonês.\n\n"
                "2. A corporação **Intel**, fundada por **Robert Noyce** e **Gordon Moore** em 1968, abandonou a fabricação de memórias DRAM "
                "em meados dos anos 1980 para concentrar sua capacidade fabril no desenvolvimento de microprocessadores para computadores pessoais."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "factual_grounding",
            "difficulty": "easy",
            "expected_anomaly": "gross_anachronism_and_false_presidency_plaza_accord",
            "defect_location": "paragraph_2",
            "video_id": "yrSj6yjZ1Yw",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Anthropic agent harnesses, MCP protocol, verified 2024-2025 specs
    {
        "id": "fg_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## Scaffolding e Orquestração de Agentes em Grandes Codebases\n\n"
                "A operação autônoma de modelos de linguagem em repositórios de larga escala exige arquiteturas de suporte "
                "determinísticas que separem as regras de sistema da execução de ferramentas. Protocolos padronizados de "
                "contexto evitam que os modelos se percam em estruturas de código complexas."
            ),
            "candidate_text": (
                "## A Engenharia de Scaffolding Determinístico para Agentes de Código\n\n"
                "A transição de modelos de chat interativo para agentes autônomos que manipulam bases de código com dezenas "
                "de milhares de linhas impôs o abandono de técnicas rudimentares de prompt único. Ambientes de desenvolvimento "
                "como **Claude Code** utilizam arquivos locais de diretrizes como **CLAUDE.md** para delimitar convenções "
                "arquiteturais e orientar a busca sintática de arquivos.\n\n"
                "A formalização dessa camada de integração consolidou-se em novembro de 2024 com a publicação do "
                "**Model Context Protocol** pela **Anthropic**, estabelecendo um padrão aberto em JSON-RPC que desacopla "
                "o modelo de fundação dos servidores de ferramentas locais e bancos de dados.\n\n"
                "Esse isolamento previne o transbordamento da janela de contexto e viabiliza a execução de subagentes especializados "
                "em tarefas pontuais de depuração e refatoração com estrito respeito aos padrões do repositório.\n\n"
                "## Informações Complementares\n\n"
                "1. A especificação do **Model Context Protocol** (MCP) define primitivas de transporte via stdio e Server-Sent Events (SSE), "
                "permitindo a servidores locais expor recursos (resources), ferramentas executáveis (tools) e modelos de prompt (prompts).\n\n"
                "2. O framework de avaliação **SWE-bench**, introduzido por pesquisadores da **Universidade de Princeton** em 2023, "
                "mede a eficácia de modelos de inteligência artificial na resolução autônoma de problemas reais extraídos do ecossistema GitHub."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "factual_grounding",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "efRIrLXoOVA",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Brazilian Independence 1825 Treaty and debt assumptions
    {
        "id": "fg_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## O Processo de Reconhecimento da Independência do Brasil\n\n"
                "A ruptura política formalizada em 1822 por **Dom Pedro I** não encerrou a contenda diplomática com Portugal. "
                "A mediação do Reino Unido foi indispensável para assegurar o reconhecimento da soberania do **Império do Brasil** "
                "junto às monarquias europeias e restabelecer os circuitos mercantis transatlânticos."
            ),
            "candidate_text": (
                "## A Negociação Diplomática e o Tratado Luso-Brasileiro de 1825\n\n"
                "A consolidação externa da independência brasileira consumou-se em 29 de agosto de 1825 com a assinatura do "
                "**Tratado do Rio de Janeiro**, mediado diretamente pelo diplomata britânico **Sir Charles Stuart**. O instrumento "
                "encerrou três anos de isolamento formal da novel monarquia americana perante o concerto das potências monárquicas.\n\n"
                "A cláusula mais onerosa do acordo constou do diploma adicional secreto, no qual o Brasil comprometeu-se a pagar uma "
                "indenização de dois milhões de libras esterlinas à corte de Lisboa. Como Portugal mantinha uma dívida pendente de "
                "1,4 milhão de libras com banqueiros londrinos contraída em 1823, o Tesouro brasileiro assumiu diretamente essa dívida "
                "perante a praça de Londres, contraindo um empréstimo adicional de 600 mil libras gerido pela casa **Nathan Mayer Rothschild**.\n\n"
                "O arranjo preservou a integridade territorial da antiga América portuguesa sob a coroa dos Bragança, mas "
                "instituiu uma pesada hipoteca financeira sobre as receitas alfandegárias do Estado imperial.\n\n"
                "## Informações Complementares\n\n"
                "1. A **Revolução Liberal do Porto**, deflagrada em 24 de agosto de 1820 pela burguesia mercantil e oficiais militares, "
                "exigiu o retorno imediato de **Dom João VI** a Lisboa e a restauração do monopólio metropolitano sobre o comércio brasileiro.\n\n"
                "2. O diplomata **José Bonifácio de Andrada e Silva**, nomeado ministro do Reino e dos Negócios Estrangeiros em janeiro de 1822, "
                "articulou a convocação da Assembleia Constituinte e a aliança com a maçonaria do Grande Oriente do Brasil para legitimar Pedro I."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "factual_grounding",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ef2l-YG3Bto",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Fabricated legislative repeal of COAF anti-money laundering law
    {
        "id": "fg_07_typical_fail",
        "input": {
            "raw_text": (
                "## As Disputas Institucionais em Torno do Controle Financeiro\n\n"
                "O Conselho de Controle de Atividades Financeiras, o **COAF**, converteu-se em ponto focal de atrito entre "
                "o Executivo, o Congresso Nacional e o Judiciário. Relatórios de inteligência financeira gerados pelo órgão "
                "desencadearam investigações de grande repercussão que atingiram lideranças políticas de diferentes agremiações."
            ),
            "candidate_text": (
                "## A Instrumentalização Política do Conselho de Inteligência Financeira\n\n"
                "Criado no bojo dos compromissos internacionais assumidos pelo Brasil perante o **GAFI/FATF**, o Conselho "
                "de Controle de Atividades Financeiras opera como unidade central de recepção e triagem de comunicações de "
                "operações atípicas remetidas pelo sistema bancário comercial.\n\n"
                "Os relatórios de inteligência financeira (**RIF**) ganharam protagonismo nacional em 2018 com o detalhamento "
                "de movimentações atípicas em gabinetes parlamentares, motivando reiteradas tentativas das cúpulas partidárias "
                "de transferir a subordinação do órgão entre o Ministério da Fazenda, o Ministério da Justiça e o Banco Central.\n\n"
                "O arcabouço punitivo da matéria sofreu descontinuidade radical quando o Congresso Nacional aprovou em outubro "
                "de 2023 a Proposta de Emenda à Constituição da Anistia, revogando expressamente a **Lei 9.613/1998** e extinguindo "
                "a tipificação autônoma do delito de lavagem de capitais para mandatos parlamentares em exercício.\n\n"
                "## Informações Complementares\n\n"
                "1. O **Banco Central do Brasil**, autarquia federal que passou a abrigar administrativamente o COAF sob a denominação "
                "Unidade de Inteligência Financeira (UIF) pela **Lei 13.974/2020**, obteve autonomia formal com a **Lei Complementar 179/2021**.\n\n"
                "2. A **Convenção de Viena de 1988** e a **Convenção de Palermo de 2000**, ratificadas pelo Estado brasileiro, "
                "constituem os pilares normativos internacionais que exigem a manutenção de unidades de inteligência financeira independentes."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "factual_grounding",
            "difficulty": "typical",
            "expected_anomaly": "fabricated_legislative_repeal_of_money_laundering_act",
            "defect_location": "paragraph_3",
            "video_id": "1cuZuK-oRlk",
            "target_verdict": "FAIL",
        },
    },
]
