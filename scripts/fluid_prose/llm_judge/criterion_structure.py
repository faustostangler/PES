"""Golden Set items for STRUCTURAL_COMPLIANCE criterion (7 items: 4 PASS, 3 FAIL).

Conforms to SPEC-015 and ADR-039.
All items ensure candidate text is 100% grounded in raw_text speech
(except for explicit, surgical formatting defect insertions in FAIL items).
"""

from __future__ import annotations

from typing import Any

ITEMS_STRUCTURE: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Subtly leaks forbidden em-dash in paragraph 2
    {
        "id": "struct_01_borderline_fp",
        "input": {
            "raw_text": (
                "quando você compila um programa em c ou rust, o compilador divide o pipeline em frontend e backend. "
                "o analisador léxico converte caracteres em tokens, depois o analisador sintático monta a árvore sintática abstrata, "
                "a ast, validando a gramática da linguagem. aí ele gera a representação intermediária pro otimizador, tipo o llvm, "
                "fazer transformações estáticas pesadas como desdobramento de loops e eliminação de código inalcançável sem depender "
                "do hardware. por fim o backend consome essa representação intermediária pra alocar registradores físicos e "
                "gerar o binário de baixo nível pra microprocessadores x86 e arm."
            ),
            "candidate_text": (
                "## As Fases da Compilação de Software e a Infraestrutura LLVM\n\n"
                "A transformação de código-fonte de alto nível em instruções executáveis de máquina requer um pipeline "
                "modular composto por extremidades frontal e traseira desacopladas. O analisador léxico converte o fluxo "
                "de caracteres em tokens formais, permitindo que o analisador sintático construa a árvore sintática abstrata "
                "que valida as regras gramaticais da linguagem.\n\n"
                "A representação intermediária — concebida para abstrair particularidades dos conjuntos de instruções de hardware — "
                "permite que o otimizador execute transformações estáticas sofisticadas, como desdobramento de laços e eliminação "
                "de código inalcançável. Essa arquitetura centralizada potencializa a reutilização de rotinas de otimização entre compiladores.\n\n"
                "Por fim, a extremidade traseira consome a representação otimizada para alocar registradores físicos e sintetizar "
                "as sequências binárias de baixo nível compatíveis com microprocessadores **x86** e **ARM**."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "borderline",
            "expected_anomaly": "forbidden_em_dash_in_body",
            "defect_location": "paragraph_2",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Radical thematic untangling of disorganized circular speech
    {
        "id": "struct_02_borderline_fn",
        "input": {
            "raw_text": (
                "aí a guerra da ucrânia começou em 2022, mas na verdade a crimeia foi anexada pela rússia em 2014, só que antes disso "
                "teve a revolução de maidan derrubando o governo e o confronto armado no donbas. mas voltando pra 2022, a invasão russa "
                "reconfigurou o xadrez econômico com sanções energéticas e apoio em armas do ocidente virando uma guerra de atrito prolongada. "
                "mas se você olhar lá atrás na cúpula de bucareste da otan em 2008, já sinalizavam publicamente aceitar a ucrânia no tratado "
                "de defesa mútua, desafiando a segurança de moscou no mar negro. e em 2014 teve os protocolos de minsk que ninguém cumpriu "
                "porque faltavam garantias reais de desmilitarização e estatuto autonômico pro donbas, então tudo explodiu em 2022."
            ),
            "candidate_text": (
                "## A Genealogia do Conflito Russo-Ucraniano e a Expansão da OTAN\n\n"
                "A eclosão das hostilidades militares no **leste europeu** em **2022** constitui o desfecho de uma trajetória de atritos "
                "geopolíticos acumulados ao longo de décadas na bacia do **Mar Negro**. Os antecedentes estratégicos remontam à **Cúpula de "
                "Bucareste** em **2008**, quando a **Organização do Tratado do Atlântico Norte** sinalizou publicamente a futura integração "
                "da **Ucrânia** em sua estrutura de defesa mútua, desafiando os parâmetros de segurança estabelecidos por **Moscou**.\n\n"
                "### A Crise de 2014 e o Fracasso Diplomático de Minsk\n\n"
                "A ruptura política precipitada pela **Revolução de Maidan** em **2014** culminou na anexação russa da **Crimeia** e na deflagração "
                "do confronto armado no **Donbas**. Os sucessivos **Protocolos de Minsk** falharam em estabilizar as linhas de contato devido à "
                "ausência de compromissos críveis de desmilitarização regional e divergências inconciliáveis sobre o estatuto autonômico territorial.\n\n"
                "### A Ofensiva de 2022 e a Polarização Global\n\n"
                "A subsequente **incursão militar de 2022** reconfigurou o xadrez econômico global, impondo regimes de sanções energéticas e "
                "consolidando o apoio armamentista ocidental que transformou o teatro de operações em uma guerra de atrito prolongada."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Impeccable formatting contract
    {
        "id": "struct_03_easy_pass",
        "input": {
            "raw_text": (
                "o conceito de derivada na análise matemática moderna formaliza a taxa instantânea de variação de grandezas contínuas, "
                "desenvolvido no século dezessete de forma independente por isaac newton e gottfried wilhelm leibniz transacionando de médias "
                "intervalares pra valores pontuais. a inclinação de uma reta secante entre dois pontos de uma curva contínua expressa a razão "
                "média de mudança da variável. quando o incremento de delta x tende a zero pelo operador de limite, a reta secante converge "
                "pra reta tangente naquele ponto da curva, dando a inclinação instantânea exata. essa modelagem quantitativa precisa permitiu "
                "calcular a aceleração mecânica, o escoamento de calor e a propagação de ondas eletromagnéticas."
            ),
            "candidate_text": (
                "## A Interpretação Geométrica da Derivada e o Limite Fundamental\n\n"
                "O conceito de derivada fundamenta a análise matemática moderna ao formalizar a taxa instantânea de variação "
                "de grandezas contínuas. A gênese conceitual do método, desenvolvida de forma independente por **Isaac Newton** e "
                "**Gottfried Wilhelm Leibniz** no **século 17**, apoia-se na transição rigorosa entre médias intervalares e valores pontuais.\n\n"
                "A inclinação de uma reta secante traçada através de dois pontos de uma curva contínua expressa a razão média de mudança "
                "da variável dependente. À medida que o incremento temporal ou espacial tende a zero, a reta secante converge gradualmente "
                "para a reta tangente naquele ponto da trajetória, definindo o valor exato da inclinação instantânea através do operador de limite.\n\n"
                "Essa formulação viabilizou a modelagem quantitativa precisa da aceleração mecânica, do escoamento de calor e da propagação de ondas eletromagnéticas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "3Blue1Brown",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Starts with forbidden H1 title and includes markdown table
    {
        "id": "struct_04_easy_fail",
        "input": {
            "raw_text": (
                "na alocação de carteiras no mercado financeiro você divide ações entre empresas consolidadas e ativos de menor "
                "capitalização. as grandes empresas, as blue chips com valor acima de cinquenta bilhões, têm fluxo de caixa previsível, "
                "distribuição contínua de proventos e risco moderado. já as small caps de até cinco bilhões têm risco elevado e mais oscilação. "
                "essa divisão ajuda a diversificar investimentos quando os juros estão altos."
            ),
            "candidate_text": (
                "# Classificação e Métricas de Ativos de Renda Variável\n\n"
                "A alocação estratégica de portfólios no mercado financeiro estabelece distinções qualitativas entre corporações "
                "consolidadas e ativos de menor capitalização de mercado. As empresas de grande porte apresentam previsibilidade de "
                "geração de caixa e distribuição contínua de proventos tributários.\n\n"
                "| Categoria | Capitalização | Risco |\n"
                "| **Blue Chips** | Acima de 50 bilhões | Moderado |\n"
                "| **Small Caps** | Até 5 bilhões | Elevado |\n\n"
                "Essa segmentação orienta a diversificação de carteiras em horizontes cíclicos de juros elevados."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "easy",
            "expected_anomaly": "h1_title_and_markdown_table",
            "defect_location": "paragraph_1_and_2",
            "video_id": "5NDhlIW-C_g",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - High cohesive transition
    {
        "id": "struct_05_typical_pass_1",
        "input": {
            "raw_text": (
                "a sustentabilidade do retorno sobre o capital de uma empresa depende de barreiras institucionais e econômicas "
                "contra novos concorrentes, o que a análise fundamentalista chama de fosso econômico, o moat. ele protege os lucros "
                "contra a pressão competitiva do mercado. os vetores principais são os custos de transição que aprisionam clientes "
                "em ecossistemas de software, os efeitos de rede onde cada novo usuário aumenta o valor da plataforma pra todo mundo, "
                "e patentes exclusivas na biotecnologia. se a empresa não tiver essas proteções, os lucros anormais atraem novo capital "
                "concorrente e as margens operacionais despencam até o custo de oportunidade."
            ),
            "candidate_text": (
                "## As Vantagens Competitivas Estruturais e o Conceito de Fosso Econômico\n\n"
                "A sustentabilidade dos **retornos sobre o capital investido** depende da existência de barreiras institucionais e "
                "econômicas à entrada de concorrentes potenciais. O conceito analítico de **fosso econômico**, formulado na tradição "
                "do investimento **fundamentalista**, descreve os mecanismos operacionais que protegem a rentabilidade das companhias "
                "contra a equalização de lucros imposta pela pressão competitiva do mercado.\n\n"
                "Entre os vetores primários de preservação de margens destacam-se os custos de transição que aprisionam clientes em "
                "ecossistemas de software consolidados, os efeitos de rede onde cada usuário adicional expande o valor agregado "
                "da plataforma para os demais participantes, e a titularidade exclusiva de patentes em setores de alta densidade biotecnológica.\n\n"
                "Na ausência desses diferenciais de proteção, a atração exercida por retornos anormais estimula a alocação de novo capital concorrente, "
                "comprimindo progressivamente as margens operacionais em direção aos custos de oportunidade do setor."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "trmvdvl72fc",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Structured sections with ## and ###
    {
        "id": "struct_06_typical_pass_2",
        "input": {
            "raw_text": (
                "a abertura econômica do brasil nos anos noventa teve na desestatização das telecomunicações um marco decisivo. "
                "o modelo anterior da holding estatal telebrás sofria com falta crônica de investimentos e racionamento severo de linhas fixas. "
                "ter uma linha telefônica era um bem de capital caríssimo que as pessoas alugavam informalmente e precisavam declarar no "
                "imposto de renda, estrangulando os serviços e a produtividade do país. aí no leilão de 1998 grupos privados internacionais "
                "compraram as concessões regionais com metas rígidas de universalização contratual, expandindo a telefonia celular em massa."
            ),
            "candidate_text": (
                "## A Reestruturação das Telecomunicações Brasileiras e a Desestatização do Sistema Telebrás\n\n"
                "O processo de **abertura econômica do Brasil** durante a **década de 1990** teve na desregulamentação do setor de "
                "telecomunicações um de seus marcos estruturais mais decisivos. O modelo estatal precedente, centralizado na "
                "holding **Telebrás**, caracterizava-se por crônica escassez de investimentos em infraestrutura e racionamento severo "
                "de linhas de acesso comutado.\n\n"
                "### A Crise de Acesso no Monopólio Estatal\n\n"
                "A posse de um terminal telefônico fixo constituía um ativo de capital patrimonial de elevado custo de aquisição, "
                "frequentemente submetido a aluguel informal e exigência de declaração fiscal de bens. Esse estrangulamento de oferta "
                "restringia o desenvolvimento de serviços digitais e impunha perdas de produtividade à malha produtiva nacional.\n\n"
                "### Os Leilões de 1998 e a Expansão da Telefonia Móvel\n\n"
                "O **leilão das concessões regionais** em **1998** atraiu grupos privados internacionais, condicionando os contratos de "
                "exploração a metas estritas de universalização que impulsionaram a implantação célere da telefonia celular em escala massiva."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Giant unstructured monolithic wall of text
    {
        "id": "struct_07_typical_fail",
        "input": {
            "raw_text": (
                "a discussão no congresso sobre o marco regulatório das plataformas digitais e redes sociais gerou uma crise institucional "
                "enorme no brasil. o projeto de lei impõe dever de cuidado e responsabilidade civil ampliada às big techs se elas não tirarem "
                "conteúdos ilegais após notificação prévia. as empresas de tecnologia reagiram fazendo campanhas institucionais nos seus "
                "canais de busca avisando contra riscos à livre manifestação e encargos de moderação privada. aí o supremo tribunal federal "
                "entrou cobrando explicações compulsórias dos executivos sobre os algoritmos. esse choque expõe como os freios e contrapesos "
                "tradicionais sofrem na velocidade das redes digitais, mantendo uma indefinição jurídica sobre moderação e mandatos populares."
            ),
            "candidate_text": (
                "## A Tensão Institucional entre Poder Legislativo e Plataformas Digitais no Marco Regulatório\n\n"
                "A deliberação parlamentar sobre o **marco legal dos provedores de aplicação na internet** precipitou uma crise "
                "institucional de grandes proporções no cenário institucional brasileiro. O projeto legislativo impõe deveres de "
                "cuidado e regime de responsabilidade civil ampliada às grandes corporações tecnológicas caso conteúdos ilícitos "
                "não sejam removidos após notificação prévia sumária. As companhias de tecnologia reagiram veiculando campanhas institucionais "
                "diretas de contestação nos canais de busca, alertando para potenciais restrições à livre manifestação e encargos de "
                "moderação privada de discursos cívicos. Diante do impasse entre as partes, o **Supremo Tribunal Federal** avocou a competência "
                "de fiscalização regulatória cautelar, determinando esclarecimentos compulsórios aos dirigentes empresariais sobre o uso de algoritmos. "
                "Esse litígio cruzado expõe a fragilidade dos mecanismos tradicionais de freios e contrapesos frente à velocidade dos "
                "fluxos de informação em redes digitais descentralizadas, prolongando a indefinição jurídica sobre os limites de moderação e a "
                "soberania dos mandatos representativos populares perante órgãos reguladores independentes no país."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "structural_compliance",
            "difficulty": "typical",
            "expected_anomaly": "monolithic_wall_of_text_without_paragraph_breaks",
            "defect_location": "paragraph_1",
            "video_id": "1cuZuK-oRlk",
            "target_verdict": "FAIL",
        },
    },
]
