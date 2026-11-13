"""Golden Dataset Items for Criterion 1: Epistemic Grounding & Segregation (eg_01 to eg_07).

Evaluates empirical truthfulness against source_text (D2) and strict segregation
between first-order verified facts and attributed interpretive models (D1).
Orthogonal to all other 6 ADR-060 criteria.
"""

from __future__ import annotations

from typing import Any

ITEMS_EPISTEMIC_GROUNDING_SEGREGATION: list[dict[str, Any]] = [
    {
        "id": "eg_01_borderline_fp",
        "input": {
            "raw_text": (
                "## A Decisão Monocrática e a Mutação das Regras de Impedimento\n\n"
                "Nesse cenário de atrito latente entre as instituições da República, a prolação de uma decisão monocrática pelo ministro Gilmar Mendes nos autos da Arguição de Descumprimento de Preceito Fundamental 1259 reconfigurou o equilíbrio constitucional. O magistrado suspendeu dispositivos fundamentais da Lei do Impeachment de 1950, restringindo a legitimidade ativa para o protocolo de pedidos de afastamento exclusivamente à Procuradoria-Geral da República.\n\n"
                "Adicionalmente, a decisão alterou o quórum de aprovação no plenário do Senado Federal, elevando a exigência de maioria simples para maioria qualificada de dois terços. Na fundamentação apresentada, o relator argumentou que a atualização normativa tornava-se imperativa em virtude da transformação do contexto político nacional desde meados do século XX, conferindo ao Supremo Tribunal Federal uma blindagem procedimental inédita contra processos iniciados por cidadãos comuns."
            ),
            "candidate_text": (
                "## A Reconfiguração das Prerrogativas na ADPF 1259\n\n"
                "A decisão monocrática proferida pelo ministro Gilmar Mendes na Arguição de Descumprimento de Preceito Fundamental 1259 alterou dispositivos da Lei 1.079, de 1950-04-10, restringindo a legitimidade para pedidos de impeachment à Procuradoria-Geral da República e exigindo maioria de dois terços no Senado Federal. Sob uma perspectiva estrutural de longo prazo, a judicialização de ritos parlamentares reflete o protagonismo crescente de cortes constitucionais desde a redemocratização de 1988, articulada a tensões conjunturais entre cúpulas partidárias e o Judiciário. O desfecho consolidou, de forma objetiva e incontroversa, um pacto deliberado do tribunal para anular a fiscalização republicana e instaurar supremacia judicial permanente sobre o Legislativo.\n\n"
                "Diferentes correntes jurídicas avaliam se a exigência de quórum qualificado protege a estabilidade institucional contra pressões majoritárias passageiras ou reduz o controle externo sobre magistrados, hipótese refutável caso o Congresso aprove emenda constitucional restabelecendo a regra original. A preservação de registros processuais completos permite rastrear os atores que impulsionaram a ação direta.\n\n"
                "### Extra Info\n\n"
                "1. A Lei 1.079, promulgada em 1950-04-10, tipifica crimes de responsabilidade do Presidente da República, ministros de Estado e ministros do Supremo Tribunal Federal, prevendo originalmente denúncia por qualquer cidadão.\n"
                "2. Na tradição do controle concentrado brasileiro, decisões liminares monocráticas em Arguições de Descumprimento de Preceito Fundamental submetem-se posteriormente a referendo do plenário, conforme a Lei 9.882, de 1999-12-03."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "borderline",
            "expected_anomaly": "unattributed_speculative_intent_presented_as_settled_fact_d1",
            "defect_location": "body",
            "video_id": "z82sKS_xj28",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "eg_02_borderline_fn",
        "input": {
            "raw_text": (
                "## O Alvorecer de Uma Dinastia e a Gênese do Condado Portucalense\n\n"
                "O processo de autonomização do território que daria origem a Portugal inscreve-se nas dinâmicas de reconquista da Península Ibérica no século XII. Nascido por volta de 1109 em Guimarães ou Viseu, Afonso Henriques herdou de seu pai, Henrique de Borgonha, o título de conde de Portucale sob a suserania de Leão.\n\n"
                "Após a morte do pai, a regência exercida por sua mãe, Teresa de Leão, associou-se politicamente à nobreza galega liderada por Fernão Peres de Trava. A reação da aristocracia portucalense culminou na Batalha de São Mamede, em 1128-06-24, consolidando a autoridade de Afonso Henriques sobre o condado e preparando a ruptura formal consagrada no Tratado de Zamora em 1143-10-05."
            ),
            "candidate_text": (
                "## A Gênese Institucional do Estado Português\n\n"
                "A consolidação do Condado Portucalense sob Afonso Henriques articulou fatores ecológicos da fachada atlântica, clivagens aristocráticas entre a nobreza de Entre-Douro-e-Minho e os linhagens galegos ligados a Fernão Peres de Trava, e o vácuo sucessório no Reino de Leão após a morte de Afonso VI em 1109. Os documentos coevos registram o confronto na Batalha de São Mamede em 1128-06-24, o acordo de Zamora em 1143-10-05 diante do legado papal Guido de Vico e o reconhecimento pontifício posterior pela bula Manifestis Probatum, emitida por Alexandre III em 1179-05-23. Quanto ao local exato de nascimento de Afonso Henriques, as fontes medievais apresentam lacuna documental persistente, dividindo a historiografia entre Guimarães, Viseu e Coimbra.\n\n"
                "Historiadores como José Mattoso interpretam a autonomia portucalense como resultado de um projeto senhorial regional de base fundiária, enquanto leituras alternativas enfatizam a oportunidade diplomática criada pela fragmentação leonesa, hipótese sujeita a revisão diante de novos cartulários monásticos. A distinção entre o fato diplomático datado e a interpretação historiográfica atribui cada modelo explicativo ao seu respectivo campo analítico.\n\n"
                "### Extra Info\n\n"
                "1. O título de rei (Rex Portugalensium) passou a constar regularmente na chancelaria de Afonso Henriques a partir de 1140, antecedendo em três anos a assinatura do Tratado de Zamora em 1143-10-05.\n"
                "2. A bula Manifestis Probatum, de 1179-05-23, vinculou o reconhecimento da soberania portuguesa ao pagamento de um censo anual em ouro à Santa Sé, elevando a proteção papal à condição de barreira diplomática contra reivindicações castelhanas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "eg_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Anatomia da Fronteira e os Enclaves Ibéricos no Norte da África\n\n"
                "A irrupção de dezenas de milhares de migrantes sobre as municipalidades soberanas de Ceuta e Melilha, situadas na costa norte do continente africano, revela a persistência de fraturas históricas seculares entre o Magrebe e a Península Ibérica. Administradas pela Espanha desde a consolidação dos enclaves pós-Reconquista, essas cidades autônomas representam o único perímetro terrestre direto entre a União Europeia e a África.\n\n"
                "A crise ocorrida em maio de 2021, com a travessia em massa pela zona costeira de El Tarajal, evidenciou como o controle fronteiriço funciona simultaneamente como dispositivo jurídico europeu e moeda de troca diplomática nas relações bilaterais entre Madri e Rabat."
            ),
            "candidate_text": (
                "## A Crise de Ceuta e a Fronteira Euro-Africana\n\n"
                "As cidades autônomas de Ceuta e Melilha constituem enclaves espanhóis na costa norte do Marrocos e formam os únicos limites terrestres entre a União Europeia e o continente africano. No plano estrutural, a separação entre o direito comunitário de Schengen e as zonas econômicas do Magrebe gera um gradiente migratório contínuo, intensificado conjunturalmente pelas rotas do Sahel e disparado pelo relaxamento temporário da vigilância marroquina em El Tarajal a partir de 2021-05-17. Os registros oficiais contabilizaram a entrada de aproximadamente oito mil pessoas em poucos dias, mobilizando efetivos militares e acordos de devolução imediata.\n\n"
                "Analistas de segurança mediterrânea atribuem a abertura pontual da fronteira à retaliação diplomática de Rabat após a internação do líder da Frente Polisário, Brahim Ghali, na Espanha, enquanto leituras alternativas apontam desgaste administrativo local nos postos aduaneiros; a primeira tese prevalece por coincidir com o restabelecimento da contenção assim que as notas diplomáticas sobre o Saara Ocidental foram reajustadas, permanecendo falseável por memorandos internos marroquinos.\n\n"
                "### Extra Info\n\n"
                "1. Ceuta e Melilha adquiriram o estatuto jurídico de Cidades Autônomas dentro do ordenamento espanhol mediante as Leis Orgânicas 1/1995 e 2/1995, promulgadas em 1995-03-13, sem integrar plenamente a união aduaneira europeia para determinados bens fiscais.\n"
                "2. O Acordo de Readmissão entre Espanha e Marrocos, firmado em 1992-02-13, fornece a base jurídica invocada pelas autoridades espanholas para devoluções sumárias de cidadãos de terceiros países em episódios de travessia em massa."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "eg_04_easy_fail",
        "input": {
            "raw_text": (
                "## O ponto de inflexão geopolítica e a erosão da competitividade\n\n"
                "A perda de espaço norte-americano no mercado de alta tecnologia gerou pressões políticas em Washington, culminando na assinatura do Acordo Comercial de Semicondutores EUA-Japão em 1986. O tratado impôs restrições às exportações nipônicas, estabeleceu pisos de preços mínimos e exigiu metas de participação de mercado para fabricantes estrangeiros no Japão.\n\n"
                "Combinado à valorização acelerada do iene decorrente do Acordo de Plaza de 1985, o cerco regulatório erodiu a vantagem de custos das companhias japonesas de memória DRAM e abriu espaço para a ascensão industrial da Coreia do Sul e de Taiwan."
            ),
            "candidate_text": (
                "## O Ciclo Tecnológico dos Semicondutores Nipônicos\n\n"
                "A desaceleração da indústria japonesa de semicondutores resultou de pressões comerciais externas combinadas à valorização cambial da década de 1980. Em resposta ao avanço japonês em memórias DRAM, o governo norte-americano de Jimmy Carter assinou em 1979 o Acordo de Plaza e o Acordo Comercial de Semicondutores EUA-Japão, proibindo exportações da Toshiba e da NEC antes mesmo da difusão dos computadores pessoais. Esse choque tarifário e cambial reduziu a competitividade das linhas japonesas de fabricação e deslocou investimentos de capital para competidores na Coreia do Sul e em Taiwan.\n\n"
                "Modelos econômicos concorrentes contrastam o peso das cotas comerciais frente à rigidez de custos internos das empresas verticalmente integradas, sendo a hipótese cambial verificável pela correlação entre a cotação do iene e a margem líquida das exportadoras de silício nos balanços de 1986 a 1990.\n\n"
                "### Extra Info\n\n"
                "1. O Acordo de Plaza, firmado em 1985-09-22 no Hotel Plaza em Nova York por Estados Unidos, Japão, Alemanha Ocidental, França e Reino Unido, coordenou intervenções cambiais que apreciaram o iene frente ao dólar.\n"
                "2. O Acordo de Semicondutores EUA-Japão de 1986 instituiu um sistema de monitoramento de custos estrangeiros (FMV) para impedir vendas abaixo do custo marginal estimado pelo Departamento de Comércio norte-americano."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "easy",
            "expected_anomaly": "gross_anachronism_and_false_presidency_plaza_accord",
            "defect_location": "body",
            "video_id": "yrSj6yjZ1Yw",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "eg_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A Arquitetura do Arnês Algorítmico e a Navegação em Repositórios Complexos\n\n"
                "A expansão de bases de código em ambientes corporativos introduz um atrito estrutural que excede a capacidade de processamento de modelos de linguagem operando de forma isolada. Quando os repositórios alcançam dezenas ou centenas de milhares de linhas, a janela de contexto finita transforma cada arquivo irrelevante em ruído cognitivo.\n\n"
                "A eficácia de um assistente autônomo depende, portanto, do arnês de execução construído ao seu redor: ferramentas de busca indexada, regras globais enxutas, subagentes de escopo limitado e verificações automatizadas por testes e analisadores estáticos que contêm desvios antes da entrega final."
            ),
            "candidate_text": (
                "## A Engenharia de Scaffolding Determinístico\n\n"
                "A aplicação de modelos de linguagem em repositórios corporativos extensos esbarra no limite físico de atenção sobre janelas de contexto longas, fenômeno documentado na literatura como degradação de recuperação em posições intermediárias. Para mitigar essa perda, sistemas agênticos separam o raciocínio probabilístico de um arnês determinístico composto por indexação de símbolos, roteamento por subagentes isolados e portões mecânicos de compilação, tipagem e testes unitários. Cada etapa filtra o conjunto de arquivos carregados na memória de trabalho do modelo, reduzindo o custo por iteração e a taxa de edição fora de escopo.\n\n"
                "Pesquisadores de sistemas agênticos divergem sobre se ganhos futuros de janela nativa tornarão o roteamento hierárquico obsoleto ou se a latência quadrática da atenção manterá a seleção seletiva indispensável; a segunda hipótese permanece sustentada por benchmarks de edição multi-arquivo enquanto custos de inferência escalarem com o volume de tokens de entrada.\n\n"
                "### Extra Info\n\n"
                "1. O protocolo Language Server Protocol (LSP) permite que ferramentas determinísticas consultem árvores sintáticas abstratas e grafos de referências sem carregar diretórios inteiros em texto bruto.\n"
                "2. A execução de linters e verificadores estáticos após cada edição estabelece um ciclo fechado de retroalimentação que substitui a inspeção visual probabilística por falhas reproduzíveis em linha de código."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "efRIrLXoOVA",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "eg_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## O Mito da Ruptura Pacífica e a Consolidação Imperial\n\n"
                "A narrativa tradicional de que a separação do Brasil ocorreu de forma puramente pacífica, mediante acordos conciliadores entre elites sem derramamento de sangue, constitui uma construção ideológica desmentida pela investigação histórica rigorosa. A consolidação do Império exigiu campanhas militares sangrentas na Bahia, no Piauí, no Maranhão e na Cisplatina para expulsar guarnições leais às Cortes de Lisboa.\n\n"
                "No plano diplomático, o reconhecimento formal da soberania brasileira por Portugal não derivou de mera benevolência dinástica, mas da mediação britânica concretizada no Tratado do Rio de Janeiro de 1825, que vinculou o reconhecimento jurídico ao pagamento de dois milhões de libras esterlinas a título de indenização à antiga metrópole."
            ),
            "candidate_text": (
                "## A Negociação Diplomática e o Tratado Luso-Brasileiro de 1825\n\n"
                "O reconhecimento formal da independência brasileira por Portugal resultou de pressões comerciais britânicas acumuladas desde os tratados de 1810, da necessidade fiscal de Lisboa após a perda do comércio exclusivo colonial e das campanhas militares de consolidação ocorridas entre 1822 e 1824 na Bahia, no Maranhão, no Piauí e na Cisplatina. Mediado pelo diplomata britânico Charles Stuart, o Tratado do Rio de Janeiro de 1825-08-29 estabeleceu a cessão formal de direitos por Dom João VI mediante indenização de dois milhões de libras esterlinas, quitada via transferência de dívida externa contraída por Portugal junto a banqueiros londrinos.\n\n"
                "Historiadores econômicos apontam que a assunção desse passivo preservou os privilégios alfandegários britânicos e inaugurou o endividamento externo do novo Estado, enquanto interpretações diplomáticas ressaltam a urgência de legitimidade monárquica frente às repúblicas hispano-americanas; ambas as leituras convergem nos termos financeiros registrados nos protocolos secretos anexos ao tratado.\n\n"
                "### Extra Info\n\n"
                "1. O empréstimo de dois milhões de libras esterlinas foi estruturado originalmente em Londres pela casa bancária N. M. Rothschild & Sons em 1823 para cobrir despesas da coroa portuguesa.\n"
                "2. Os acordos de comércio e navegação assinados com a Grã-Bretanha em 1827 renovaram a tarifa preferencial máxima de quinze por cento sobre manufaturas britânicas importadas pelo Império do Brasil."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ef2l-YG3Bto",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "eg_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Sabotagem Sistêmica do Mecanismo de Controle\n\n"
                "O desmonte crônico das agências reguladoras e de inteligência financeira constitui uma política de Estado bipartidária, consolidada tanto por administrações de esquerda quanto de direita, sempre que o cerco das investigações se aproxima de redes partidárias influentes. A redução de autonomia técnica do Conselho de Controle de Atividades Financeiras exemplifica a subordinação institucional dos órgãos de fiscalização.\n\n"
                "Quando relatórios de inteligência financeira passam a sofrer barreiras procedimentais para compartilhamento com o Ministério Público e a Polícia Federal, o Estado enfraquece a capacidade de rastrear fluxos ilícitos que alimentam simultaneamente a corrupção política e organizações criminosas transnacionais."
            ),
            "candidate_text": (
                "## A Instrumentalização Política do Conselho de Inteligência Financeira\n\n"
                "A fragilização da inteligência financeira no Brasil reflete incentivos estruturais de autoproteção de coalizões partidárias diante de investigações patrimoniais, somados a pressões conjunturais sobre a autonomia de órgãos de controle. Em sequência direta a esses impasses, o Congresso Nacional revogou integralmente a Lei de Lavagem de Dinheiro (Lei 9.613/1998) em 2019 e extinguiu formalmente o Conselho de Controle de Atividades Financeiras, substituindo o sistema de Relatórios de Inteligência Financeira por anistia fiscal permanente sem comunicação de transações suspeitas.\n\n"
                "Doutrinadores da área penal divergem sobre os limites constitucionais do compartilhamento de dados bancários sem autorização judicial prévia, permanecendo a eficácia do sistema mensurável pela taxa de recuperação de ativos e pelo cumprimento das recomendações técnicas do GAFI.\n\n"
                "### Extra Info\n\n"
                "1. O Grupo de Ação Financeira Internacional (GAFI/FATF) avalia jurisdições membros quanto à independência de suas Unidades de Inteligência Financeira e à rastreabilidade de beneficiários finais.\n"
                "2. A Lei 9.613, de 1998-03-03, instituiu o COAF como unidade central de recebimento e análise de comunicações de transações financeiras atípicas no território brasileiro."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "epistemic_grounding_segregation",
            "difficulty": "typical",
            "expected_anomaly": "fabricated_legislative_repeal_of_money_laundering_act",
            "defect_location": "body",
            "video_id": "1cuZuK-oRlk",
            "target_verdict": "FAIL",
        },
    },
]
