"""Golden Dataset Items for Criterion 7: Linear Style & Naturalism (ls_01 to ls_07).

Evaluates strict cresmo-style-guide compliance: linear continuous prose without
digressions/flashbacks, zero meta-discourse/conversational offers, zero em-dashes,
zero binary antitheses ('nao X, mas Y'), zero metonymy or moralistic outrage, and
zero restricted vocabulary lemmas (forjar, operar, moldar, abrigar, fardo).
"""

from __future__ import annotations

from typing import Any

ITEMS_LINEAR_STYLE_NATURALISM: list[dict[str, Any]] = [
    {
        "id": "ls_01_borderline_fp",
        "input": {
            "raw_text": (
                "## O Ecossistema de Ferramentas e o Mito do Prompt Único na Engenharia de Software Contemporânea\n\n"
                "A integração de modelos de inteligência artificial no ciclo de vida do desenvolvimento de software exige uma reavaliação metodológica profunda, afastando-se do otimismo ingênuo do prompt único para abraçar arquiteturas baseadas em especificações granulares. Desenvolvedores frequentemente atribuem a fluidez de ferramentas recentes apenas à interface visível do editor.\n\n"
                "Na prática, o desempenho dessas plataformas apoia-se em camadas acumuladas de protocolos abertos, analisadores sintáticos, servidores de linguagem e convenções comunitárias construídas muito antes da geração automatizada de código."
            ),
            "candidate_text": (
                "## O Esgotamento das Heurísticas Verbais na Engenharia Assistida\n\n"
                "A transição de instruções avulsas para especificações formais em engenharia de software assistida por inteligência artificial consolida o deslocamento da tentativa e erro conversacional para portões determinísticos de verificação. Não se trata de uma preferência estética passageira de equipes de tecnologia, mas de uma exigência estrutural imposta pela natureza estocástica da decodificação autorregressiva que molda o comportamento dos geradores atuais. Quando especificações contratuais, tipos estáticos e suítes de teste precedem a geração, cada passo produz saída auditável.\n\n"
                "Sob perspectiva comparada, a padronização de fluxos reproduz o amadurecimento histórico das linguagens tipadas diante de scripts improvisados, permanecendo a redução de retrabalho verificável em métricas de regressão por entrega.\n\n"
                "### Extra Info\n\n"
                "1. Em modelos autorregressivos, o erro acumulado cresce exponencialmente ao longo de decisões sequenciais desprovidas de validação intermediária determinística.\n"
                "2. Fluxos baseados em contratos (Design by Contract) separam pré-condições de entrada e pós-condições de saída verificáveis automaticamente por suítes unitárias."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "linear_style_naturalism",
            "difficulty": "borderline",
            "expected_anomaly": "disguised_binary_antithesis_and_restricted_lemma_moldar",
            "defect_location": "body",
            "video_id": "ytTJtfg9HCw",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "ls_02_borderline_fn",
        "input": {
            "raw_text": (
                "## Mecanismos de Controle e o Comércio de Vagas\n\n"
                "O controle interno dessas chapas proporcionais revela a dureza subjacente à competição política, onde a estabilidade dos acordos de cúpula não pode ser ameaçada por surpresas decorrentes do desempenho nas urnas. Quando diretórios partidários administram fundos eleitorais bilionários e tempo de propaganda em rádio e televisão, os recursos são canalizados seletivamente para candidatos alinhados ao núcleo dirigente.\n\n"
                "A distribuição assimétrica desses ativos determina de antemão a visibilidade pública de cada concorrente, convertendo a escolha aparentemente livre do eleitor em validação posterior de listas previamente hierarquizadas pelos caciques partidários."
            ),
            "candidate_text": (
                "## A Alocação Assimétrica de Fundos nas Chapas Proporcionais\n\n"
                "A concentração decisória nas direções partidárias brasileiras resulta diretamente da arquitetura de financiamento público instituída pelo Fundo Especial de Financiamento de Campanha e pelo Fundo Partidário. Ao deterem o monopólio legal da assinatura de repasses financeiros e da cessão de minutos em cadeia de rádio e televisão, as executivas nacionais transformam a competição intrapartidária em um mercado interno administrado: candidaturas com potencial de surpreender lideranças consolidadas recebem dotações residuais, enquanto nomes alinhados ao núcleo dirigente concentram verbas de produção audiovisual e cabos eleitorais.\n\n"
                "Sob o ângulo da Escolha Pública (James Buchanan; Gordon Tullock), esse comportamento reflete a racionalidade de maximização de controle por incumbentes em contextos de baixa informação do eleitorado médio. A hipótese de que a concentração financeira prediz a renovação parlamentar melhor do que a votação histórica prévia permanece falseável mediante regressão entre repasses declarados ao TSE e cadeiras conquistadas por faixa de gasto.\n\n"
                "### Extra Info\n\n"
                "1. O Fundo Especial de Financiamento de Campanha (FEFC) foi criado pela Lei 13.487 em 2017-10-06 após o Supremo Tribunal Federal vedar doações empresariais a campanhas eleitorais em 2015-09-17 (ADI 4.650).\n"
                "2. Pelas normas do Tribunal Superior Eleitoral, ao menos trinta por cento dos recursos do FEFC e do tempo gratuito de propaganda devem ser destinados às candidaturas femininas proporcionalmente em cada circunscrição."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "linear_style_naturalism",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "7tZdt2UQtbg",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ls_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Herança da Reconquista e a Gênese dos Enclaves\n\n"
                "A presença ibérica no norte da África remonta aos desdobramentos estratégicos da Guerra da Reconquista, processo secular de expansão cristã na Península Ibérica concluído no final do século XV. A tomada de Ceuta em 1415 pelos portugueses e a incorporação posterior da cidade à coroa espanhola após a União Ibérica estabeleceram postos avançados permanentes na margem sul do Estreito de Gibraltar.\n\n"
                "Juntamente com Melilha, ocupada pela coroa de Castela em 1497, esses enclaves funcionaram durante séculos como praças fortificadas para controle das rotas comerciais mediterrânicas e contenção da pirataria corsária norte-africana."
            ),
            "candidate_text": (
                "## A Topografia da Fricção: Ceuta e Melilha desde o Século XV\n\n"
                "A permanência de Ceuta e Melilha sob soberania espanhola na costa norte africana decorre diretamente da projeção marítima ibérica que sucedeu a fase final da Reconquista. Conquistada por Portugal em 1415-08-21 sob comando de Dom João I e mantida sob domínio de Madri após o encerramento da União Ibérica pelo Tratado de Lisboa de 1668-02-13, Ceuta somou-se a Melilha, ocupada pelas forças castelhanas do Duque de Medina Sidonia em 1497-09-17. Durante a Idade Moderna, ambas as praças guarneceram o estrangulamento naval do Estreito de Gibraltar contra incursões corsárias magrebinas e projeções otomanas no Mediterrâneo ocidental.\n\n"
                "Na conjuntura contemporânea, a integração da Espanha à Comunidade Econômica Europeia em 1986 converteu essas fortificações históricas na única fronteira terrestre direta entre o espaço de Schengen e a África, criando um gradiente econômico e jurídico contínuo. Historiadores mediterrânicos debatem se a manutenção dos enclaves responde hoje mais à dissuasão estratégica sobre o estreito ou à resistência política eleitoral doméstica na Espanha, controvérsia mensurável pela evolução dos orçamentos militares locais e fluxos aduaneiros.\n\n"
                "### Extra Info\n\n"
                "1. O Tratado de Lisboa de 1668-02-13, que encerrou a Guerra da Restauração portuguesa, reconheceu a soberania de Portugal sobre suas colônias ultramarinas, excetuando Ceuta, cuja guarnição e cabildo municipal optaram por permanecer vinculados à Coroa espanhola.\n"
                "2. Embora integrem politicamente a União Europeia como Cidades Autônomas espanholas, Ceuta e Melilha gozam de regime fiscal especial (IPSI) fora da diretiva comum do Imposto sobre Valor Agregado europeu."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "linear_style_naturalism",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ls_04_easy_fail",
        "input": {
            "raw_text": (
                "## O Dilema do Poder Legislativo entre a Conivência e a Reação\n\n"
                "Diante da alteração unilateral das regras do jogo institucional, a iniciativa encontra-se novamente no campo do poder legislativo, historicamente marcado pela relutância em confrontar decisões do judiciário. As alternativas disponíveis ao Senado Federal oscilam entre a aceitação tácita de restrições regimentais e a aprovação de emendas constitucionais que restaurem prerrogativas parlamentares.\n\n"
                "Contudo, a vulnerabilidade de dezenas de parlamentares a inquéritos em curso na corte suprema cria um mecanismo de dissuasão silenciosa que paralisa comissões e adia votações sensíveis."
            ),
            "candidate_text": (
                "## A Paralisia do Senado e os Caminhos Regimentais\n\n"
                "Abaixo apresento a expansão analítica estruturada conforme o Eixo A1 e o Passo 2 da metodologia, mantendo rigor formal. O impasse entre o Senado Federal e o Supremo Tribunal Federal decorre da coexistência de dois incentivos contraditórios: de um lado, a preservação abstrata das competências constitucionais do Legislativo; de outro, o cálculo individual de sobrevivência política de senadores sujeitos a investigações penais sob jurisdição da própria corte.\n\n"
                "Se você desejar aprofundar esta análise com novos exemplos históricos do Brasil Império ou comparar outros países, basta solicitar a continuação na próxima interação.\n\n"
                "### Extra Info\n\n"
                "1. O artigo 52, inciso II, da Constituição Federal de 1988 atribui privativamente ao Senado Federal a competência para processar e julgar os ministros do Supremo Tribunal Federal nos crimes de responsabilidade.\n"
                "2. Propostas de Emenda à Constituição exigem aprovação em dois turnos em cada casa do Congresso Nacional por maioria qualificada de três quintos dos votos dos respectivos membros."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "linear_style_naturalism",
            "difficulty": "easy",
            "expected_anomaly": "prompt_scaffolding_metadiscourse_and_conversational_offer",
            "defect_location": "body",
            "video_id": "z82sKS_xj28",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "ls_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A Sabotagem Sistêmica do Mecanismo de Controle\n\n"
                "O desmonte crônico das agências reguladoras e de inteligência financeira constitui uma política de Estado bipartidária, consolidada tanto por administrações de esquerda quanto de direita, sempre que o cerco das investigações se aproxima de redes partidárias influentes. A redução de autonomia técnica do Conselho de Controle de Atividades Financeiras exemplifica a subordinação institucional dos órgãos de fiscalização.\n\n"
                "Quando relatórios de inteligência financeira passam a sofrer barreiras procedimentais para compartilhamento com o Ministério Público e a Polícia Federal, o Estado enfraquece a capacidade de rastrear fluxos ilícitos que alimentam simultaneamente a corrupção política e organizações criminosas transnacionais."
            ),
            "candidate_text": (
                "## A Arquitetura de Vigilância do COAF e os Filtros Bipartidários\n\n"
                "A redução recorrente de autonomia do Conselho de Controle de Atividades Financeiras ilustra como incentivos de autopreservação de coalizões governantes convergem acima de clivagens partidárias. Instituído pela Lei 9.613 em 1998-03-03, o órgão centraliza comunicações de transações atípicas remetidas por bancos e cartórios sem exercer poder policial próprio; sua função consiste em cruzar registros patrimoniais e encaminhar Relatórios de Inteligência Financeira quando identificados indícios consistentes de ocultação de ativos.\n\n"
                "Quando alterações administrativas ou interpretações restritivas elevam o atrito procedimental para o compartilhamento desses relatórios com o Ministério Público e a Polícia Federal, o sistema de prevenção perde velocidade de detecção justamente em casos complexos envolvendo agentes públicos e lavagem transnacional. Cientistas políticos contrastam a hipótese de captura deliberada por elites parlamentares vulneráveis frente à tese garantista de proteção contra pesca probatória sem supervisão judicial, divergência mensurável pela taxa de anulação processual versus recuperação de ativos ilícitos.\n\n"
                "### Extra Info\n\n"
                "1. Os Relatórios de Inteligência Financeira (RIFs) classificam-se em espontâneos, quando gerados proativamente pelo cruzamento de alertas bancários, e de intercâmbio, quando solicitados formalmente por autoridades investigativas.\n"
                "2. A Recomendação 29 do Grupo de Ação Financeira Internacional (GAFI) estipula que as Unidades de Inteligência Financeira devem possuir independência de decisão para disseminar relatórios sem interferência política externa."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "linear_style_naturalism",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "1cuZuK-oRlk",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ls_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## A Arquitetura do Desempenho e as Ilusões da Engenharia de Software\n\n"
                "O ecossistema contemporâneo de desenvolvimento de software frequentemente confunde a complexidade acidental com a essencial, gerando artefatos que acumulam camadas de abstração sem fundamentos empíricos sólidos. O fenômeno manifesta-se na adoção acrítica de arquiteturas distribuídas para problemas que caberiam em um único servidor relacional bem ajustado.\n\n"
                "A dissociação entre o modelo mental de código de alto nível e a realidade física do hardware (latência de rede, alocação de memória e serialização) impõe custos severos de infraestrutura e manutenção que poderiam ser evitados por decisões técnicas mais sóbrias."
            ),
            "candidate_text": (
                "## Complexidade Acidental e Custo Físico na Engenharia de Sistemas\n\n"
                "A proliferação de arquiteturas de microsserviços em sistemas de tráfego moderado substitui chamadas de função em memória na escala de nanossegundos por requisições de rede serializadas na escala de milissegundos. Esse salto de quatro a seis ordens de grandeza na latência introduz falhas parciais, necessidade de retentativas idempotentes, rastreamento distribuído e coordenação transacional eventual onde um monólito modular com banco único resolveria a mesma carga mediante transações ACID locais.\n\n"
                "Na dimensão histórica e institucional da indústria, a adoção prematura de topologias concebidas para hiperescala (como os padrões da Netflix e do Google para milhares de engenheiros) decorre frequentemente de isomorfismo mimético descrito por teóricos organizacionais e da sinalização curricular de equipes. A hipótese de que a fragmentação precoce reduz velocidade de entrega abaixo de certo limiar de equipe permanece verificável por métricas DORA (lead time para mudanças e frequência de implantação) em organizações equivalentes.\n\n"
                "### Extra Info\n\n"
                "1. A Lei de Conway, formulada por Melvin Conway em 1968, postula que organizações projetam sistemas cuja estrutura de comunicação espelha a estrutura comunicacional da própria organização.\n"
                "2. Em benchmarks clássicos de latência computacional, um acesso à memória RAM consome aproximadamente 100 nanossegundos, enquanto uma ida e volta de pacote TCP entre centros de dados distintos consome dezenas de milissegundos."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "linear_style_naturalism",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ls_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Mutação Institucional e a Adaptação dos Clãs\n\n"
                "Com a irrupção da Revolução de 1930 e a criação da Justiça Eleitoral em 1932, que instituiu o voto secreto, a infraestrutura material do coronelismo tradicional sofreu um abalo sísmico, mas a lógica subjacente adaptou-se aos novos meios de comunicação e regulação estatal. Grupos políticos regionais migraram do controle exclusivo do curral rural para a captura de concessões de rádio e televisão.\n\n"
                "Esse fenômeno, amplamente descrito na ciência política como coronelismo eletrônico, manteve a intermediação entre o eleitorado local e os recursos federais por meio de outorgas públicas distribuídas a parlamentares e governadores alinhados."
            ),
            "candidate_text": (
                "## A Outorga de Rádios — Uma Aberração Vergonhosa de Brasília\n\n"
                "Brasília decidiu entregar o espectro eletromagnético às velhas oligarquias locais — uma aberração vergonhosa e imoral que perpetua a servidão eleitoral no interior brasileiro. Antes de prosseguir, vale recordar brevemente uma lembrança pessoal de quando o rádio a pilha chegou às feiras sertanejas nos anos 1950, mudando a paisagem sonora das praças. Retomando o fio normativo, a repartição escandalosa de concessões transformou o patrimônio público em propriedade privada de famílias cínicas e corruptas.\n\n"
                "Enquanto o cidadão honesto sofre com a manipulação descarada dos microfones regionais, o Congresso permanece conivente com esse privilégio repugnante que fere a dignidade da República.\n\n"
                "### Extra Info\n\n"
                "1. O Código Brasileiro de Telecomunicações (Lei 4.117, de 1962-08-27) atribuiu ao Poder Executivo federal a competência originária para outorgar canais de radiodifusão em território nacional.\n"
                "2. O artigo 223 da Constituição de 1988 estabeleceu prazos de dez anos para outorgas de rádio e quinze anos para televisão sujeitos à apreciação posterior do Congresso Nacional."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "linear_style_naturalism",
            "difficulty": "typical",
            "expected_anomaly": "em_dash_style_violation",
            "defect_location": "body",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "FAIL",
        },
    },
]
