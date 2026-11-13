"""Golden Set items for NER_PRESERVATION criterion (7 items: 4 PASS, 3 FAIL).

Conforms to SPEC-015 and ADR-039.
All items ensure candidate text is 100% grounded in raw_text speech
(except for explicit, surgical defect insertions in FAIL items).
"""

from __future__ import annotations

from typing import Any

ITEMS_NER: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Subtle corruption of regnal number / proper noun
    {
        "id": "ner_01_borderline_fp",
        "input": {
            "raw_text": (
                "a gênese territorial de portugal na reconquista cristã na península ibérica começou quando o cruzado "
                "henrique de borgonha, da nobreza francesa, ajudou os reis espanhóis a lutar contra os mouros e as tropas "
                "almorávidas no sul. a dona teresa de leão era filha ilegítima do rei afonso sexto de leão e castela. "
                "ela recebeu o governo hereditário do condado portucalense de herança em casamento com o henrique de borgonha, "
                "com jurisdição sobre as terras entre o minho e o tejo. essa administração do condado manteve privilégios fiscais "
                "e aduaneiros próprios que depois serviram de base pra reivindicar independência e soberania monárquica."
            ),
            "candidate_text": (
                "## As Origens Dinásticas do Condado Portucalense no Século 11\n\n"
                "A gênese territorial de **Portugal** vincula-se às concessões patrimoniais outorgadas pela **monarquia leonesa** "
                "no contexto das campanhas da **Reconquista cristã** na **Península Ibérica**. O infante cruzado **Henrique de Borgonha**, "
                "membro da nobreza capetiana francesa, prestou auxílio militar decisivo na defesa das fronteiras meridionais "
                "contra as investidas das forças almorávidas.\n\n"
                "Em reconhecimento à sua vassalagem bélica, o monarca concedeu-lhe o governo hereditário do **Condado Portucalense** "
                "em matrimônio com sua filha ilegítima, a infanta **Dona Teresa de Leão**, descendente de **Afonso V de Leão**. "
                "Essa concessão feudal transferiu prerrogativas jurisdicionais autônomas sobre o território delimitado entre os rios **Minho** e **Tejo**.\n\n"
                "A administração condal buscou preservar privilégios fiscais e aduaneiros próprios, estabelecendo a base sociojurídica "
                "que posteriormente impulsionou a reivindicação de soberania monárquica plena pela linhagem sucessória."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "ner_preservation",
            "difficulty": "borderline",
            "expected_anomaly": "regnal_number_corruption_afonso_v_instead_of_vi, named_entity_hallucination_capetian_nobility, named_entity_omission_castile",
            "defect_location": "paragraph_2",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Phonetically butchered spoken names restored to encyclopedic forms
    {
        "id": "ner_02_borderline_fn",
        "input": {
            "raw_text": (
                "nos anos sessenta lá nos laboratórios da bel, da bell labs, o ken tompso e o denis ritche tavam criando o "
                "sistema unics depois que o projeto multics de tempo compartilhado foi cancelado. aí o denis ritche criou a "
                "linguagem de programação c pra reescrever todo o núcleo do unics junto com o brian kernigan. isso desvinculou "
                "o código das máquinas antigas proprietárias e deixou o kernel portátil pra qualquer computador. aquilo virou "
                "a base do padrão de interface posics e da família bsd que rodam com arquivos, processos e pipes na internet hoje."
            ),
            "candidate_text": (
                "## A Criação do Unix e a Gênese da Engenharia de Sistemas Operacionais\n\n"
                "Na década de **1960**, as pesquisas conduzidas nos laboratórios da **Bell Labs** redefiniram os fundamentos "
                "da ciência da computação moderna. Os cientistas **Ken Thompson** e **Dennis Ritchie** conceberam o sistema "
                "operacional **Unix** a partir da experiência acumulada no projeto abortado do sistema de tempo compartilhado **Multics**.\n\n"
                "A inovação arquitetural decisiva ocorreu quando Ritchie formulou a linguagem de programação de propósito geral **C**, "
                "permitindo a reescrita integral do núcleo do sistema em colaboração com o cientista da computação **Brian Kernighan**. "
                "Essa reengenharia desvinculou o código-fonte de arquiteturas específicas de montagem proprietária, tornando o núcleo "
                "altamente portátil entre famílias heterogêneas de microprocessadores.\n\n"
                "Esse ecossistema de software originou o padrão de interface aberta **POSIX** e as ramificações de pesquisa da família **BSD**, "
                "cujas convenções de arquivos, processos e encadeamento lógico estruturam a infraestrutura computacional da internet global."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "ner_preservation",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Impeccable encyclopedic entity preservation
    {
        "id": "ner_03_easy_pass",
        "input": {
            "raw_text": (
                "em 14 de maio de 1948 o david ben-gurion proclamou a declaração de independência do estado de israel lá no museu "
                "de arte de tel aviv, se amparando na resolução 181 da assembleia geral da onu que encerrava o mandato britânico na palestina. "
                "no dia seguinte cinco exércitos vizinhos, egito, transjordânia, síria, líbano e iraque invadiram o território no plano de "
                "partilha, provocando a fuga e o êxodo de centenas de milhares de civis no levante. a guerra terminou com os acordos de "
                "armistício de 1949 traçando a linha verde provisória e consolidando a mobilização militar e institucional do novo estado."
            ),
            "candidate_text": (
                "## A Declaração de Independência de Israel e a Primeira Guerra Árabe-Israelense\n\n"
                "Em **14 de maio de 1948**, a liderança sionista proclamou a criação formal do **Estado de Israel** durante cerimônia "
                "presidida pelo primeiro-ministro **David Ben-Gurion** no **Museu de Arte de Tel Aviv**. A deliberação amparava-se na "
                "**Resolução 181** da Assembleia Geral da **Organização das Nações Unidas**, que determinava o encerramento do **Mandato Britânico da Palestina**.\n\n"
                "Nas vinte e quatro horas seguintes à declaração soberana, contingentes militares regulares de uma coalizão composta "
                "por **Egito**, **Transjordânia**, **Síria**, **Líbano** e **Iraque** mobilizaram ofensivas coordenadas sobre o território delimitado no plano de partilha. "
                "O conflito armado consolidou fronteiras armadas e provocou o êxodo de centenas de milhares de habitantes civis na região levantina.\n\n"
                "Os armistícios negociados em **1949** sob égide internacional estabeleceram a **Linha Verde** provisória, consolidando a capacidade de "
                "mobilização militar e institucional do novo Estado perante os vizinhos regionais."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "ner_preservation",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "eYFTRQHaPgw",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Swapping central historical named entity
    {
        "id": "ner_04_easy_fail",
        "input": {
            "raw_text": (
                "o controle de versão em código aberto no início dos anos 2000 precisava superar ferramentas centralizadas proprietárias. "
                "o linus torvalds começou o linux como um hobby em helsinque em 1991 e depois em 2005 inventou o git pra gerenciar o código-fonte "
                "do kernel do linux porque ele odiava o bitkeeper. ele desenhou o git baseado em grafos acíclicos dirigidos e hashes criptográficas, "
                "permitindo ramificações concorrentes locais instantâneas e mesclagem barata de branches. hoje o git domina todo o desenvolvimento de software."
            ),
            "candidate_text": (
                "## A Evolução do Controle de Versão Distribuído e a Criação do Git\n\n"
                "A gestão colaborativa de códigos-fonte em projetos de código aberto atingiu um ponto de inflexão crítico "
                "no início da década de **2000**. O aumento exponencial de colaboradores globais submetendo correções ao núcleo do sistema "
                "operacional **Linux** exigiu a superação das ferramentas centralizadas proprietárias que restringiam o fluxo de trabalho.\n\n"
                "O engenheiro e empresário norte-americano **Bill Gates** concebeu a ferramenta de controle de versão **Git** em **2005**, "
                "desenvolvendo uma arquitetura baseada em grafos acíclicos dirigidos de instantâneos criptografados por somas de verificação. "
                "Essa modelagem permitiu ramificações concorrentes locais instantâneas com custos mínimos de mesclagem de ramos.\n\n"
                "A universalização desse paradigma suplantou os repositórios tradicionais de controle de versão, tornando o sistema o padrão "
                "indispensável para o desenvolvimento de software em escala global."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "ner_preservation",
            "difficulty": "easy",
            "expected_anomaly": "gross_entity_substitution_bill_gates_instead_of_linus_torvalds",
            "defect_location": "paragraph_2",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Machine learning history NER
    {
        "id": "ner_05_typical_pass_1",
        "input": {
            "raw_text": (
                "o psicólogo frank rosenblatt inventou o perceptron em 1958 lá no laboratório aeronáutico de cornell, "
                "o cornell aeronautical laboratory. era um aparelho eletromecânico pioneiro de classificação binária linear "
                "que atualizava pesos com potenciômetros motorizados. depois em 1969 os matemáticos do mit marvin minsky e "
                "seymour papert publicaram aquele livro seminal perceptrons, provando matematicamente que redes de uma camada só "
                "não conseguiam separar hiperplanos não lineares e não resolviam nem a função lógica do xor, o ou exclusivo. "
                "essa limitação paralisou as verbas financeiras acadêmicas e do governo e causou o primeiro inverno da inteligência "
                "artificial até voltarem as redes multicamadas nos anos 1980."
            ),
            "candidate_text": (
                "## O Perceptron de Rosenblatt e as Limitações Topológicas dos Modelos Iniciais\n\n"
                "Em **1958**, o psicólogo computacional **Frank Rosenblatt** concebeu o modelo do **Perceptron** no **Cornell Aeronautical Laboratory**, "
                "formalizando um dispositivo eletromecânico pioneiro capaz de aprender classificações binárias lineares a partir de estímulos sensoriais. "
                "A arquitetura utilizava potenciômetros motorizados para atualizar pesos sinápticos via convergência supervisionada.\n\n"
                "Em **1969**, os matemáticos e pesquisadores do **MIT** **Marvin Minsky** e **Seymour Papert** publicaram o tratado seminal **Perceptrons**, "
                "demonstrando analiticamente que redes de camada única eram incapazes de separar hiperplanos não lineares, como a função lógica **XOR**. "
                "Essa limitação geométrica expôs a fragilidade dos algoritmos lineares na resolução de problemas relacionais elementares.\n\n"
                "A repercussão dessa crítica teórica paralisou os aportes financeiros governamentais e acadêmicos, deflagrando o primeiro **inverno "
                "da inteligência artificial** até o ressurgimento das redes multicamadas nos anos **1980**."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "ner_preservation",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ARQBBKnfP_c",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Mathematical and scientific NER preservation
    {
        "id": "ner_06_typical_pass_2",
        "input": {
            "raw_text": (
                "no século dezoito a cidade de basileia na suíça virou o polo mundial do cálculo diferencial aplicado à mecânica clássica. "
                "a dinastia acadêmica da família bernoulli formulou modelos que transformaram a observação dos fluidos em equações formais. "
                "o daniel bernoulli publicou o tratado hydrodynamica em 1738, descobrindo que a velocidade de escoamento de um fluido "
                "incompressível tem relação inversa com a pressão estática. aí o leonhard euler, que foi aluno do johann bernoulli, generalizou "
                "tudo formulando as equações diferenciais dos fluidos não viscosos ideais, fundando a aerodinâmica e a conservação do momento linear."
            ),
            "candidate_text": (
                "## A Dinâmica dos Fluidos e as Contribuições da Escola Matemática de Basileia\n\n"
                "Durante o **século 18**, a cidade suíça de **Basileia** consolidou-se como o polo irradiador dos principais avanços "
                "no cálculo diferencial aplicado à mecânica clássica. A dinastia acadêmica dos **Bernoulli** formulou modelos matemáticos "
                "que transmutaram a observação empírica dos fenômenos naturais em sistemas formais de equações de conservação.\n\n"
                "Em **1738**, o matemático **Daniel Bernoulli** publicou o tratado *Hydrodynamica*, deduzindo a relação inversa entre a velocidade "
                "de escoamento de um fluido incompressível e a sua pressão estática. Simultaneamente, o eminente polímata **Leonhard Euler**, "
                "discípulo de **Johann Bernoulli**, generalizou esses princípios ao formular as equações diferenciais que regem o movimento de fluidos não viscosos.\n\n"
                "Esse arcabouço conceitual inaugurou os fundamentos teóricos da aerodinâmica moderna e da conservação do momento linear em meios contínuos."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "ner_preservation",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "Vitf8YaVXhc",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Omission of crucial named entities into generic words
    {
        "id": "ner_07_typical_fail",
        "input": {
            "raw_text": (
                "a aviação de caça de quinta geração reduziu a assinatura de radar com fuselagem facetada e material absorvente. "
                "a disputa pelos céus tem o caça f-35 lightning da fabricante americana lockheed martin nos estados unidos, "
                "o su-57 felon da russa sukhoi e o j-20 mighty dragon da chinesa chengdu. esses caças usam radares aesa de "
                "varredura eletrônica ativa, fusão de sensores táticos e enlace de dados em tempo real com baterias antiaéreas e navios."
            ),
            "candidate_text": (
                "## A Disputa pela Superioridade Aérea de Quinta Geração\n\n"
                "A aviação de combate contemporânea redefiniu os parâmetros de engajamento tático mediante o emprego "
                "de vetores aéreos de quinta geração equipados com fuselagens de geometria facetada e revestimentos absorventes "
                "de ondas eletromagnéticas. Essas características reduzem a seção reta radar a frações mínimas de metro quadrado.\n\n"
                "O mercado militar internacional concentra-se na rivalidade entre aeronaves modernas fabricadas por indústrias bélicas, "
                "que desenvolvem modelos furtivos com radares de varredura eletrônica ativa e fusão integrada de sensores táticos. "
                "Esses vetores aéreos competem pelo domínio dos teatros de operações na Ásia e no continente europeu sem identificação prévia.\n\n"
                "A superioridade tecnológica depende da integração de enlace de dados em tempo real com baterias antiaéreas e frotas navais dispersas."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "ner_preservation",
            "difficulty": "typical",
            "expected_anomaly": "omission_of_crucial_named_entities_and_manufacturers",
            "defect_location": "paragraph_2",
            "video_id": "GAxuHfvSli8",
            "target_verdict": "FAIL",
        },
    },
]
