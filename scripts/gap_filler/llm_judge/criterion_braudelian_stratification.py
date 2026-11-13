"""Golden Dataset Items for Criterion 3: Braudelian Stratification (bs_01 to bs_07).

Evaluates explicit 3-tier Braudelian temporality: structural longue duree (B1),
conjunctural cycles (B2), and short-term événementiel triggers (B3), without
flattening causality onto surface events or moralistic voluntarism.
Orthogonal to all other 6 ADR-060 criteria.
"""

from __future__ import annotations

from typing import Any

ITEMS_BRAUDELIAN_STRATIFICATION: list[dict[str, Any]] = [
    {
        "id": "bs_01_borderline_fp",
        "input": {
            "raw_text": (
                "## A Configuração das Elites no Brasil Contemporâneo\n\n"
                "A aplicação da sociologia política das elites ao cenário brasileiro revela um arranjo institucional marcado pelo patrimonialismo e pelo clientelismo, onde a fronteira entre os interesses econômicos privados e a máquina pública torna-se porosa. Os grupos dirigentes acumulam controle simultâneo sobre recursos orçamentários, regulações setoriais e canais de representação parlamentar.\n\n"
                "Essa sobreposição dificulta a alternância substantiva de políticas econômicas, pois novas coalizões eleitorais frequentemente negociam com as mesmas bancadas temáticas e os mesmos conglomerados financiadores para assegurar governabilidade no curto prazo."
            ),
            "candidate_text": (
                "## Ciclos Recentes de Governabilidade e Patronagem no Congresso\n\n"
                "A captura orçamentária no Brasil contemporâneo decorre de ciclos conjunturais de médio prazo instaurados a partir da fragmentação partidária da década de 1990 e ampliados pela expansão das emendas impositivas entre 2015 e 2024. Sob essa dinâmica de médio prazo, governos minoritários passaram a depender de blocos parlamentares heterogêneos para aprovar medidas fiscais, enquanto gatilhos imediatos como votações de confiança ou trocas ministeriais reconfiguram a distribuição de fundos a cada sessão legislativa. O fenômeno explica-se integralmente por essa aritmética parlamentar pós-1988 e pelas negociações orçamentárias anuais, dispensando remontar a estruturas históricas anteriores à Constituinte.\n\n"
                "Em termos mecânicos, o repasse de recursos discricionários vincula a sobrevivência eleitoral municipal à fidelidade em plenário, gerando como hipótese concorrente o peso do financiamento privado frente às transferências diretas do Tesouro, verificável em bases de prestação de contas eleitorais.\n\n"
                "### Extra Info\n\n"
                "1. A Emenda Constitucional 86, promulgada em 2015-03-17, tornou obrigatória a execução das emendas parlamentares individuais até o limite de 1,2 por cento da receita corrente líquida.\n"
                "2. O sistema de presidencialismo de coalizão conceitua a necessidade de o chefe do Executivo brasileiro construir maiorias multipartidárias no Congresso Nacional por meio de distribuição de cargos e agenda legislativa."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "braudelian_stratification",
            "difficulty": "borderline",
            "expected_anomaly": "missing_structural_longue_duree_tier_b1_only_b2_and_b3",
            "defect_location": "body",
            "video_id": "iadM8y_-k_Y",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "bs_02_borderline_fn",
        "input": {
            "raw_text": (
                "## O Monopólio Territorial e a Atualização das Capitanias\n\n"
                "A conversão da terra em capital político encontrou no Maranhão um laboratório normativo exemplar através da sanção da Lei nº 2.979 em 1969, conhecida historicamente como a Lei Sarney de Terras. Sob a fachada jurídica de regularização fundiária e estímulo à colonização agrícola, o diploma viabilizou a transferência de imensas glebas devolutas a grupos privados vinculados à cúpula governante.\n\n"
                "Desse modo, antigos laços de dependência rural foram reconfigurados em mecanismos estatais modernos de controle territorial, cartorial e creditício, assegurando hegemonia eleitoral duradoura a famílias dirigentes regionais mesmo após a urbanização acelerada."
            ),
            "candidate_text": (
                "## A Persistência Fundiária e a Lei 2.979 de 1969 no Maranhão\n\n"
                "A concentração fundiária institucionalizada pela Lei Estadual 2.979/1969 no Maranhão exemplifica a articulação de três temporalidades históricas distintas. Na camada estrutural de longa duração, a matriz colonial das sesmarias e da imprecisão demarcatória ibérica consolidou a posse privada da terra como vetor primário de jurisdição local e acesso a crédito. Na camada conjuntural de médio prazo, a expansão da fronteira agrícola amazônica e a centralização autoritária do regime militar entre 1964 e 1985 criaram instrumentos administrativos para titular terras devolutas via agências estaduais de colonização. Por fim, no plano do acontecimento imediato, a sanção do diploma em 1969 e os registros subsequentes em serventias locais desencadearam o fechamento de campos de uso comum.\n\n"
                "A distinção entre a herança sesmarial e o ato legislativo de 1969 evidencia que a norma estadual canalizou fluxos pré-existentes de patronagem sem criar do nada a assimetria agrária. Historiadores agrários debatem o peso relativo da titulação cartorial frente ao acesso a subsídios federais da SUDENE/SUDAM como fator dominante de concentração, tese mensurável em processos discriminatórios fundiários.\n\n"
                "### Extra Info\n\n"
                "1. A Lei Imperial 601, de 1850-09-18 (Lei de Terras), extinguiu o acesso gratuito por posse após o fim das sesmarias e determinou a aquisição exclusivamente por compra, definindo o estatuto das terras devolutas.\n"
                "2. A Superintendência do Desenvolvimento do Nordeste (SUDENE), instituída pela Lei 3.692 em 1959-12-15, e o Fundo de Investimento da Amazônia canalizaram incentivos fiscais atrelados à apresentação de títulos dominiais."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "braudelian_stratification",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "bs_03_easy_pass",
        "input": {
            "raw_text": (
                "## A gênese industrial e a arquitetura do milagre tecnológico japonês\n\n"
                "A ascensão do Japão à hegemonia global na indústria de semicondutores durante a década de 1980 constitui um dos fenômenos mais notáveis de reorganização econômica do século XX. O território nipônico, devastado pela Segunda Guerra Mundial e desprovido de reservas minerais e energéticas relevantes, transformou a escassez de recursos naturais em imperativo de eficiência industrial.\n\n"
                "A combinação de elevada taxa de poupança doméstica, disciplina educacional voltada à engenharia e coordenação de crédito direcionado pelo Ministério do Comércio Internacional e Indústria viabilizou o salto de bens leves para eletrônica de precisão e memórias de silício."
            ),
            "candidate_text": (
                "## As Três Temporalidades do Salto Japonês em Semicondutores\n\n"
                "A liderança japonesa em microeletrônica na década de 1980 resultou da convergência entre três estratos temporais. No plano estrutural secular, a ausência de recursos minerais em arquipélago densamente povoado, somada a uma tradição administrativa pré-industrial herdada da restauração Meiji voltada à absorção seletiva de técnica estrangeira, impôs a exportação de manufaturados de alto valor agregado como condição de sobrevivência econômica. No plano conjuntural (1945–1985), a ordem monetária de Bretton Woods, o guarda-chuva de segurança norte-americano durante a Guerra Fria e o direcionamento de poupança doméstica pelo MITI forneceram capital paciente às empresas eletrônicas. No nível dos eventos imediatos, a introdução das linhas de DRAM de 64 Kb no início dos anos 1980 e o choque do Acordo de Plaza em 1985-09-22 reordenaram rapidamente as quotas globais de mercado.\n\n"
                "Economistas institucionais (Chalmers Johnson) e teóricos neoclássicos debatem se o crédito subsidiado acelerou a fronteira tecnológica ou gerou superinvestimento crônico punido na década de 1990, controvérsia testável pela comparação de produtividade total dos fatores entre setores protegidos e expostos à concorrência externa.\n\n"
                "### Extra Info\n\n"
                "1. O sistema bancário principal japonês (main bank system) consolidado no pós-guerra permitiu alavancagem superior à anglo-saxônica porque bancos comerciais detinham participações cruzadas nas firmas industriais financiadas.\n"
                "2. Entre 1950 e 1973, o câmbio fixo de 360 ienes por dólar sob Bretton Woods protegeu as margens exportadoras japonesas até a flutuação definitiva das moedas principais."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "braudelian_stratification",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "yrSj6yjZ1Yw",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "bs_04_easy_fail",
        "input": {
            "raw_text": (
                "## A Arquitetura da Coerção Transnacional e o Desarranjo Institucional\n\n"
                "A dinâmica do poder contemporâneo manifesta-se frequentemente na intersecção entre a soberania estatal formal e os fluxos financeiros globais, onde sanções unilaterais funcionam como instrumentos de engenharia política. No episódio envolvendo sanções aplicadas contra autoridades judiciárias brasileiras sob a égide de legislação estrangeira, evidenciou-se a vulnerabilidade de atores domésticos às infraestruturas de liquidação denominadas em dólar.\n\n"
                "A inclusão ou remoção de nomes em listas restritivas repercute diretamente sobre o acesso a sistemas internacionais de cartões, contas correspondentes e redes de compensação bancária, demonstrando o alcance extraterritorial da jurisdição financeira norte-americana."
            ),
            "candidate_text": (
                "## O Gatilho Imediato da Disputa sobre Sanções Financeiras\n\n"
                "O conflito em torno de sanções aplicadas a autoridades brasileiras explica-se inteiramente pelos eventos ocorridos na última semana de votações e declarações públicas em Brasília e Washington. Na quarta-feira daquele mês, uma declaração diplomática irritou parlamentares estrangeiros, que protocolaram o pedido de inclusão na lista na sexta-feira seguinte, levando bancos comerciais a bloquearem cartões na segunda-feira subsequente.\n\n"
                "Essa sequência instantânea de notificações administrativas demonstra que toda a crise nasceu exclusivamente daquela troca pontual de declarações pessoais entre dois interlocutores na mesma semana, sem qualquer antecedente estrutural na arquitetura monetária internacional nem ciclo regulatório prévio.\n\n"
                "### Extra Info\n\n"
                "1. A Global Magnitsky Human Rights Accountability Act, sancionada nos Estados Unidos em 2016-12-23, autoriza o Executivo a impor bloqueios de ativos e restrições de visto a estrangeiros designados.\n"
                "2. A lista de Specially Designated Nationals (SDN), mantida pelo Office of Foreign Assets Control (OFAC), obriga instituições financeiras com vínculo de compensação em dólar a congelarem relações comerciais com designados."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "braudelian_stratification",
            "difficulty": "easy",
            "expected_anomaly": "evenementiel_flattening_reducing_causality_to_surface_week_events",
            "defect_location": "body",
            "video_id": "R8-dCSHLItE",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "bs_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A Configuração das Elites no Brasil Contemporâneo\n\n"
                "A aplicação da sociologia política das elites ao cenário brasileiro revela um arranjo institucional marcado pelo patrimonialismo e pelo clientelismo, onde a fronteira entre os interesses econômicos privados e a máquina pública torna-se porosa. Os grupos dirigentes acumulam controle simultâneo sobre recursos orçamentários, regulações setoriais e canais de representação parlamentar.\n\n"
                "Essa sobreposição dificulta a alternância substantiva de políticas econômicas, pois novas coalizões eleitorais frequentemente negociam com as mesmas bancadas temáticas e os mesmos conglomerados financiadores para assegurar governabilidade no curto prazo."
            ),
            "candidate_text": (
                "## Estamento Burocrático e Coalizões Fiscais no Brasil\n\n"
                "A persistência de alianças entre grandes grupos econômicos e o orçamento público brasileiro responde a três escalas temporais superpostas. Na longa duração, o legado patrimonialista ibérico descrito por Raymundo Faoro estruturou a precedência do estamento estatal sobre o mercado autônomo desde o período colonial, condicionando o acesso à acumulação de capital à proximidade com concessões públicas. Na camada conjuntural de médio prazo, o ciclo desenvolvimentista de 1930 a 1980 e a redemocratização sob presidencialismo de coalizão ampliaram bancos públicos de fomento e fundos setoriais capturáveis por bancadas temáticas. Na superfície eventual, eleições bienais e aprovações de leis orçamentárias reajustam periodicamente os beneficiários imediatos sem dissolver o núcleo do arranjo.\n\n"
                "Cientistas sociais divergem entre a interpretação weberiana do estamento autônomo e a leitura marxista instrumental do Estado como comitê de frações empresariais dominantes, divergência testável pelo grau de sobrevivência de subsídios setoriais após alternâncias ideológicas completas no Executivo.\n\n"
                "### Extra Info\n\n"
                "1. O conceito de estamento burocrático foi sistematizado por Raymundo Faoro em Os Donos do Poder (1958) a partir da categoria weberiana de dominação patrimonial.\n"
                "2. Dados de renúncias fiscais da Receita Federal e desembolsos de crédito direcionado ilustram a estabilidade intertemporal de benefícios tributários mesmo entre governos de orientação programática oposta."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "braudelian_stratification",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "iadM8y_-k_Y",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "bs_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## A Arquitetura da Independência e o Reconhecimento Soberano\n\n"
                "A expansão militar sobre os domínios mouros consolidou a autoridade bélica de Afonso Henriques, culminando em eventos de forte ressonância política e simbólica, como a Batalha de Ourique em 1139. A autonomia conquistada no campo militar exigiu, contudo, tradução jurídica no sistema feudal europeu.\n\n"
                "Mediante o Tratado de Zamora em 1143 e a posterior bula Manifestis Probatum de 1179, a coroa portuguesa transformou a posse territorial de fato em soberania reconhecida pela Santa Sé, neutralizando pretensões de vassalagem da coroa de Leão e Castela."
            ),
            "candidate_text": (
                "## Geografia Atlântica, Reconquista e Soberania Portuguesa\n\n"
                "A emergência de Portugal como reino autônomo no século XII ilustra a interação entre permanências geográficas, ciclos político-militares e atos diplomáticos pontuais. Na longa duração, a faixa atlântica entre os rios Minho e Tejo combinava portos naturais navegáveis, pluviosidade regular e barreiras montanhosas a leste que dificultavam o controle administrativo contínuo a partir da Meseta Central ibérica. No tempo conjuntural da Reconquista (séculos XI–XIII), o deslocamento da fronteira cristã para o sul e a fragmentação dinástica do Reino de Leão após 1109 abriram espaço fiscal e militar para a aristocracia senhorial portucalense financiar campanhas próprias. Sobre essa base assentaram-se os eventos imediatos: a vitória em Ourique em 1139-07-25, o Tratado de Zamora em 1143-10-05 e a bula Manifestis Probatum em 1179-05-23.\n\n"
                "Historiadores debatem se a consolidação fronteiriça decorreu mais da especificidade ecológica e mercantil atlântica ou da habilidade militar de linhagens guerreiras em fronteira aberta, tese mensurável pelo peso precoce das receitas portuárias e forais urbanos nos reinados de Afonso Henriques e Sancho I.\n\n"
                "### Extra Info\n\n"
                "1. Os forais medievais concediam autonomia judicial e privilégios tributários a concelhos urbanos recém-povoados em troca de serviço militar fronteiriço (cavalaria vilã) e rendas diretas à Coroa.\n"
                "2. A conquista de Lisboa em 1147-10-25 contou com apoio naval de cruzados anglo-normandos, flamengos e germânicos em rota atlântica rumo à Terra Santa."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "braudelian_stratification",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "bs_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Instrumentação Migratória como Manobra Estratégica\n\n"
                "A repetição cíclica de pressões migratórias em massa sobre Ceuta e Melilha revela a eficácia do uso de deslocamentos populacionais como instrumento de barganha geopolítica. A aproximação diplomática entre o governo de Madri e lideranças separatistas do Saara Ocidental produziu historicamente respostas imediatas na forma de afrouxamento da vigilância fronteiriça por parte do Marrocos.\n\n"
                "Nesse tabuleiro assimétrico, fluxos humanos vulneráveis convertem-se em vetores de pressão estatal para extrair concessões territoriais, comerciais e financeiras da União Europeia sem o disparo de um único projétil."
            ),
            "candidate_text": (
                "## A Fronteira de Ceuta como Destino Inevitável da Geografia\n\n"
                "As crises migratórias em Ceuta e Melilha constituem um destino histórico imutável no qual qualquer Estado norte-africano está fatalmente condenado a colidir com a Europa, independentemente de ciclos econômicos ou decisões diplomáticas concretas. Como a distância marítima no Estreito de Gibraltar permanece constante há milênios, episódios como o de maio de 2021 não passam de repetições automáticas de uma lei geográfica eterna que anula o papel de regimes de fronteira, pactos de segurança ou conjunturas políticas.\n\n"
                "Dessa forma, torna-se desnecessário distinguir entre transformações econômicas do século XX, acordos bilaterais de readmissão ou decisões pontuais de policiamento, visto que o determinismo físico explica integralmente cada travessia.\n\n"
                "### Extra Info\n\n"
                "1. O Fundo Fiduciário de Emergência da União Europeia para a África destinou verbas específicas ao controle de fronteiras e cooperação policial no norte africano a partir de 2015.\n"
                "2. O Estreito de Gibraltar possui largura mínima aproximada de 14 quilômetros entre a costa ibérica e o território marroquino."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "braudelian_stratification",
            "difficulty": "typical",
            "expected_anomaly": "ahistorical_geographical_fatalism_erasing_conjunctural_and_event_tiers",
            "defect_location": "body",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "FAIL",
        },
    },
]
