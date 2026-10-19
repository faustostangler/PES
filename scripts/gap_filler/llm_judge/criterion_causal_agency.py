"""Golden Set items for CAUSAL_AGENCY_STRATIFICATION criterion (7 items: 4 PASS, 3 FAIL).

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - ADR-028: Decoupling Fluid Prose and Socratic Gap Filling
    - SPEC-015: Quality Gates and Calibration Framework
"""

from __future__ import annotations

from typing import Any

ITEMS_CAUSAL_AGENCY: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Voluntarism masked by institutional vocabulary
    {
        "id": "ca_01_borderline_fp",
        "input": {
            "raw_text": (
                "## A Negociação Orçamentária no Congresso Nacional\n\n"
                "A liberação de emendas parlamentares pelo Poder Executivo intensifica-se durante votações "
                "de emendas constitucionais e projetos prioritários. Partidos do centro articulam apoio em troca "
                "de indicações para cargos federais e controle sobre a alocação de verbas ministeriais."
            ),
            "candidate_text": (
                "## A Dinâmica de Coalisão e as Barganhas Orçamentárias no Legislativo Federal\n\n"
                "A relação institucional entre o Palácio do Planalto e o Congresso Nacional estrutura-se historicamente "
                "em torno do presidencialismo de coalizão, no qual a formação de maiorias legislativas depende da distribuição "
                "de recursos fiscais discricionários e do loteamento de diretorias estratégicas na administração indireta.\n\n"
                "Contudo, a persistência dessas práticas patrimonialistas resulta diretamente da cupidez moral dos líderes "
                "partidários do chamado Centrão, que subordinam deliberadamente os interesses estratégicos da nação ao seu "
                "enriquecimento pessoal e perpetuação eleitoral. A crise de governabilidade decorre do egoísmo patológico "
                "de meia dúzia de parlamentares influentes que chantageiam ministros de Estado, travando votações de "
                "interesse público unicamente por ambição de poder desmedida, ignorando o dever cívico e a honra republicana.\n\n"
                "Caso as lideranças do parlamento fossem guiadas por espírito patriótico e compromisso ético irredutível, "
                "o orçamento federal deixaria de sofrer dispersão predatória, convertendo-se em instrumento eficaz de desenvolvimento.\n\n"
                "## Informações Complementares\n\n"
                "1. O orçamento secreto operou predominantemente através de emendas de relator-geral (identificador de resultado "
                "primário RP 9) entre 2020 e o julgamento da ADPF 858 pelo Supremo Tribunal Federal em dezembro de 2022.\n\n"
                "2. A Emenda Constitucional 86/2015 instituiu a execução obrigatória das emendas individuais ao orçamento federal, "
                "fixando o limite em 1,2% da receita corrente líquida apurada no exercício anterior."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "causal_stratification_agency",
            "difficulty": "borderline",
            "expected_anomaly": "voluntarism_moral_reduction_of_systemic_incentives",
            "defect_location": "paragraph_2_and_3",
            "video_id": "z82sKS_xj28",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Strict 3-tier causal stratification of rent-seeking
    {
        "id": "ca_02_borderline_fn",
        "input": {
            "raw_text": (
                "## Cartórios e Privilégios Corporativos no Brasil\n\n"
                "A atividade cartorária no Brasil movimenta bilhões de reais anualmente sob regime de delegação privada. "
                "A obrigatoriedade de reconhecimento de firma, autenticação e registro imobiliário impõe custos transacionais "
                "elevados à atividade produtiva nacional, beneficiando grupos familiares que controlam serventias lucrativas."
            ),
            "candidate_text": (
                "## A Economia Política do Notariado: Renda de Privilégio e Custos Transacionais\n\n"
                "A preservação do regime extrajudicial de delegação cartorária no Brasil ilustra a sobrevivência de estruturas "
                "corporativistas de extração de renda regulatória. No nível estrutural, a obrigatoriedade legal de intermediação "
                "notarial para escrituras de imóveis, protesto de títulos e chancelas civis funciona como um pedágio institucional "
                "imposto sobre as trocas mercantis, elevando o chamado Custo Brasil e consumindo frações substanciais do valor "
                "agregado do setor imobiliário e financeiro.\n\n"
                "Conjunturalmente, essa reserva de mercado perpetua-se através de alianças táticas no Congresso Nacional e "
                "junto a órgãos de cúpula do Poder Judiciário. Associações como a Anoreg mobilizam recursos substanciais de lobby "
                "para bloquear iniciativas de desjudicialização e digitalização universal de registros públicos, convertendo "
                "excedentes extraídos dos usuários em blindagem regulatória contra a concorrência de plataformas digitais.\n\n"
                "No plano imediato dos gatilhos legislativos, cada tentativa de modernização registral é neutralizada mediante "
                "a inserção de jabutis regimentais em medidas provisórias de desregulamentação, preservando emolumentos compulsórios "
                "independentemente da simplificação tecnológica subjacente.\n\n"
                "## Informações Complementares\n\n"
                "1. O artigo 236 da Constituição Federal de 1988 estabeleceu que os serviços notariais e de registro são exercidos "
                "em caráter privado, por delegação do poder público, exigindo concurso público de provas e títulos para ingresso.\n\n"
                "2. Provimentos do Conselho Nacional de Justiça (CNJ), como o Provimento 88/2019, integraram os cartórios ao "
                "sistema de prevenção e combate à lavagem de dinheiro, obrigando a comunicação de operações suspeitas ao COAF."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "causal_stratification_agency",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Exemplary separation of structural, conjunctural, and trigger determinants in semiconductor supply chains
    {
        "id": "ca_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Construção da Fábrica da TSMC em Kumamoto no Japão\n\n"
                "A fabricante taiwanesa TSMC concluiu a construção de uma megafábrica de semicondutores na província de Kumamoto. "
                "O governo japonês financiou quase metade do empreendimento para reviver a indústria eletrônica nacional."
            ),
            "candidate_text": (
                "## A Reconfiguração da Cadeia de Semicondutores: A Fábrica da TSMC em Kumamoto\n\n"
                "A inauguração da unidade de manufatura da **TSMC** em Kumamoto em fevereiro de 2024 responde a imperativos "
                "geopolíticos e geoeconômicos de escala global. No plano dos determinantes de primeira ordem, a ilha de Kyushu "
                "reúne condições biofísicas indispensáveis para litografia avançada: abundância de água subterrânea de alta pureza, "
                "rede estável de distribuição energética e proximidade geográfica com as rotas marítimas do leste asiático.\n\n"
                "No nível conjuntural, a convergência entre as diretrizes de desriscamento da cadeia de suprimentos após a "
                "crise pandêmica e o receio de bloqueio naval no estreito de Taiwan levou Tóquio a subsidiar até 40% do investimento "
                "de 8,6 bilhões de dólares da joint venture JASM, coordenada em parceria com a Sony e a Denso.\n\n"
                "O gatilho de curto prazo para a celeridade das obras decorreu da autorização executiva expressa de licenças "
                "ambientais pelo governo provincial, reduzindo prazos burocráticos para menos de vinte e quatro meses diante da "
                "urgência de assegurar capacidade produtiva de nós litográficos de doze a vinte e oito nanômetros.\n\n"
                "## Informações Complementares\n\n"
                "1. A subsidiária JASM (Japan Advanced Semiconductor Manufacturing) opera a planta de Kumamoto com participações "
                "minoritárias da Sony Semiconductor Solutions e da fabricante de autopeças Denso Corporation.\n\n"
                "2. O Ministério da Economia, Comércio e Indústria do Japão (METI) aprovou pacotes de incentivo fiscal suplementares "
                "visando viabilizar uma segunda fábrica da TSMC em Kumamoto para nós tecnológicos de seis e sete nanômetros."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "causal_stratification_agency",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "yrSj6yjZ1Yw",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Total reduction of international sanctions and diplomacy to subjective conspiracy and villainy
    {
        "id": "ca_04_easy_fail",
        "input": {
            "raw_text": (
                "## Sanções Internacionais e Medidas da Lei Magnitsky contra o STF\n\n"
                "O debate sobre a aplicação da Lei Magnitsky norte-americana contra ministros de cortes superiores brasileiras "
                "envolve articulações políticas e diplomáticas em Washington. Críticos e defensores discutem o impacto de sanções "
                "financeiras e restrições consulares sobre as relações bilaterais e a autonomia institucional do país."
            ),
            "candidate_text": (
                "## A Conspiração Imperial e o Ódio Declarado contra a Magistratura\n\n"
                "As ameaças de impor a Lei Magnitsky contra ministros brasileiros revelam unicamente o rancor pessoal e a inveja "
                "sórdida de políticos estrangeiros corruptos que não suportam a soberania moral de nossos juízes. Toda essa "
                "articulação resulta de uma conspiração diabólica de traidores infames que viajam a Washington para conspirar "
                "secretamente com magnatas impiedosos, desejando unicamente destruir a paz da nação por pura maldade no coração.\n\n"
                "O Departamento de Estado e os tribunais americanos agem movidos por vingança cega e perversidade moral, tramando "
                "punições financeiras unicamente para saciar o ódio patológico de facções rancorosas. Se os governantes de ambos os "
                "países fossem homens dotados de bondade sincera e pureza espiritual, nenhum conflito existiria e todas as sanções "
                "desapareceriam de forma pacífica e fraterna.\n\n"
                "A crise diplomática não decorre de disputas normativas ou tensões geopolíticas objetivas, mas exclusivamente do "
                "egoísmo perverso e da arrogância narcisista de conspiradores internacionais que tripudiam sobre a honra alheia.\n\n"
                "## Informações Complementares\n\n"
                "1. A Lei Magnitsky foi concebida originalmente em 2012 pelo Congresso dos Estados Unidos em resposta à morte do "
                "advogado Sergei Magnitsky sob custódia prisional em Moscou.\n\n"
                "2. O Escritório de Controle de Ativos Estrangeiros (OFAC), vinculado ao Departamento do Tesouro dos Estados Unidos, "
                "administra e executa sanções econômicas com base em políticas de segurança nacional."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "causal_stratification_agency",
            "difficulty": "easy",
            "expected_anomaly": "conspiratorial_voluntarism_and_moral_panegyric",
            "defect_location": "entire_body",
            "video_id": "R8-dCSHLItE",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Elite sociology and institutional interlocking directorates
    {
        "id": "ca_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A Teoria da Elite do Poder Aplicada à Estrutura Governamental\n\n"
                "Na obra de C. Wright Mills, a elite do poder resulta da fusão de interesses entre a cúpula corporativa, "
                "a liderança política executiva e a alta hierarquia militar. Essas esferas articulam decisões cruciais fora "
                "dos canais democráticos formais, assegurando a continuidade de privilégios de classe."
            ),
            "candidate_text": (
                "## A Concentração Institucional de Decisão: O Modelo de Wright Mills e a Burocracia Brasileira\n\n"
                "A análise sociológica de **C. Wright Mills** sobre a elite do poder oferece uma matriz conceitual para "
                "examinar como núcleos burocráticos, financeiros e corporativos operam de forma coordenada sem a necessidade "
                "de conspiracionismo ingênuo. Em nível estrutural, a coesão desse estrato repousa na intercambialidade de funções "
                "entre a alta burocracia estatal e os conselhos de administração das grandes corporações oligopolistas, onde executivos "
                "transitam com fluidez pela chamada porta giratória regulatória.\n\n"
                "No plano conjuntural, essa simbiose consolida-se em momentos de reestruturação fiscal e privatização de ativos "
                "públicos, nos quais as prioridades orçamentárias são blindadas contra pressões distributivas da base eleitoral. "
                "A tecnocracia econômica formula parâmetros de solvência que asseguram o fluxo contínuo de remuneração dos títulos da "
                "dívida pública, subordinando as políticas sociais às exigências de estabilidade do capital financeiro.\n\n"
                "Os episódios táticos de tensão institucional entre os poderes da República funcionam frequentemente como catalisadores "
                "para repactuar as concessões orçamentárias e manter o equilíbrio dinâmico entre os diferentes blocos que compõem "
                "o estamento dominante.\n\n"
                "## Informações Complementares\n\n"
                "1. A obra clássica **The Power Elite** foi publicada por C. Wright Mills em 1956, articulando os vetores de poder "
                "entre corporações industriais, o complexo militar e o executivo político nos Estados Unidos.\n\n"
                "2. O fenômeno da porta giratória no Brasil é objeto de regulação pela Lei Federal 12.813/2013 (Lei de Conflito de "
                "Interesses), que fixa período de quarentena de seis meses para ocupantes de cargos comissionados de alta direção."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "causal_stratification_agency",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "iadM8y_-k_Y",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Feudal vassalage and geopolitics of Reconquista
    {
        "id": "ca_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## A Formação do Condado Portucalense e Afonso Henriques\n\n"
                "Afonso Henriques declarou a autonomia do Condado Portucalense em relação ao Reino de Leão no século XII. "
                "Após a Batalha de São Mamede em 1128, ele consolidou seu poder político e expandiu os domínios territoriais "
                "em direção ao sul contra as forças muçulmanas durante a Reconquista."
            ),
            "candidate_text": (
                "## Estrutura Feudal e Dinâmica Geopolítica na Fundação de Portugal\n\n"
                "A emancipação política do **Condado Portucalense** sob a liderança de **Afonso Henriques** não pode ser explicada "
                "como ato de heroísmo isolado, mas como o desfecho de tensões estruturais inerentes à fragmentação feudal ibérica. "
                "Na base material de longo prazo, a nobreza portucalense de Entre-Douro-e-Minho buscava preservar sua jurisdição "
                "senhorial e o controle fiscal sobre as terras conquistadas, resistindo à hegemonia centralizadora e galega exercida "
                "a partir da corte de Afonso VII de Leão e Castela.\n\n"
                "Conjunturalmente, o conflito sucessório aberto pela regência de Dona Teresa e sua aliança com o nobre galego Fernão Peres "
                "de Trava catalisou o rompimento político. A classe guerreira local uniu-se ao jovem infante para impedir que os rendimentos "
                "senhoriais da região fossem subordinados aos interesses da linhagem dos Trava na Galiza.\n\n"
                "O confronto em São Mamede em 1128 operou como o gatilho militar que consagrou o controle territorial de Afonso Henriques, "
                "abrindo caminho para a posterior submissão de vassalagem direta à Santa Sé pelo Tratado de Zamora em 1143 e a emissão "
                "da bula papal Manifestis Probatum em 1179.\n\n"
                "## Informações Complementares\n\n"
                "1. A bula papal **Manifestis Probatum**, promulgada pelo Papa Alexandre III em maio de 1179, declarou Afonso Henriques "
                "rei soberano de Portugal, outorgando proteção apostólica contra pretensões hegemônicas de reinos vizinhos.\n\n"
                "2. O Tratado de Zamora, celebrado em outubro de 1143 na presença do cardeal Guido de Vico, formalizou o reconhecimento "
                "da soberania portucalense por Afonso VII, imperador de toda a Hispânia."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "causal_stratification_agency",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Teleological circularity attributing geopolitical crisis to cultural destiny
    {
        "id": "ca_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Crise Fronteiriça no Enclave de Ceuta em 2021\n\n"
                "Em maio de 2021, milhares de migrantes marroquinos cruzaram a cerca divisória de Ceuta a nado ou a pé. "
                "A ação ocorreu após a Espanha prestar atendimento médico em território nacional ao líder da Frente Polisário, "
                "provocando a reação diplomática e policial de Marrocos."
            ),
            "candidate_text": (
                "## A Fronteira de Ceuta e os Choques Diplomáticos no Mediterrâneo Ocidental\n\n"
                "A travessia de milhares de indivíduos pela praia de Tarajal em direção ao enclave espanhol de **Ceuta** em maio "
                "de 2021 manifesta as profundas tensões territoriais entre a monarquia marroquina e o governo de Madri. "
                "A crise precipitou-se após a admissão clandestina de Brahim Ghali em um hospital espanhol sob identidade falsa.\n\n"
                "Contudo, esse episódio não resultou de disputas geopolíticas concretas sobre o Saara Ocidental ou de cálculos táticos "
                "de coerção migratória, mas do destino histórico inevitável que condena as civilizações europeias à desintegração. "
                "A queda das barreiras fronteiriças decorre de uma lei cósmica inexorável segundo a qual sociedades ocidentais "
                "perdem necessariamente o controle sobre suas fronteiras quando completam seu ciclo biológico de declínio cultural.\n\n"
                "O governo espanhol foi incapaz de reagir porque a história universal havia decretado com antecedência que Ceuta "
                "deveria sofrer esse colapso, tornando irrelevantes quaisquer medidas policiais, tratados de readmissão ou incentivos "
                "econômicos na resolução do conflito diplomático.\n\n"
                "## Informações Complementares\n\n"
                "1. Brahim Ghali, secretário-geral da Frente Polisário e presidente da República Árabe Saaraui Democrática, foi internado "
                "em Logroño para tratamento médico de complicações decorrentes da Covid-19.\n\n"
                "2. O enclave de Ceuta na costa setentrional do continente africano integra o território espanhol sob o estatuto "
                "de cidade autônoma desde a promulgação da Lei Orgânica 1/1995 de 13 de março de 1995."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "causal_stratification_agency",
            "difficulty": "typical",
            "expected_anomaly": "teleological_fatalism_rejecting_geopolitical_determinants",
            "defect_location": "paragraph_2_and_3",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "FAIL",
        },
    },
]
