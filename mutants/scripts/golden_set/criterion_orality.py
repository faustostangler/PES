"""Golden Set items for ORALITY_REMOVAL criterion (7 items: 4 PASS, 3 FAIL).

Conforms to SPEC-015 and ADR-039.
All items ensure candidate text is 100% semantically grounded in raw_text speech
to prevent cross-criterion interference from SEMANTIC_FAITHFULNESS.
"""

from __future__ import annotations

from typing import Any

ITEMS_ORALITY: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Subtle defect embedded in paragraph 2
    {
        "id": "orality_01_borderline_fp",
        "input": {
            "raw_text": (
                "fala galera beleza? hoje o tema é microsserviços versus monólitos, né? a galera vê as big techs "
                "usando kafka e barramento assíncrono e sai copiando por pura pressão da modinha do mercado, sem ter "
                "maturidade nenhuma de governança. aí enche de complexidade cognitiva e latência de rede que superam "
                "qualquer ganho de escalabilidade, e ninguém consegue debugar na produção. como eu sempre falo aqui "
                "nos meus vídeos, a galera divide o banco de dados antes da hora, fragmenta o modelo de domínio e cria "
                "um monólito distribuído que sofre com transação falhando na rede e perde toda a observabilidade dos dados "
                "em alta concorrência. manter um monólito bem modular numa única unidade de implantação reduz os custos de "
                "orquestração e diminui demais o tempo de recuperação quando dá pau na consistência eventual."
            ),
            "candidate_text": (
                "## A Arquitetura de Microsserviços e a Prematuridade da Distribuição\n\n"
                "A transição arquitetural de sistemas monolíticos para topologias distribuídas frequentemente decorre "
                "de pressões miméticas do ecossistema tecnológico e não de requisitos operacionais tangíveis. A adoção "
                "precoce de barramentos de mensageria assíncrona introduz camadas de complexidade cognitiva e latência de "
                "rede que superam os ganhos nominais de escalabilidade em organizações com baixa maturidade de governança.\n\n"
                "Conforme discutido anteriormente em nossos vídeos, a fragmentação prematura de modelos de domínio em "
                "bancos de dados isolados culmina na formação de monólitos distribuídos. Esse padrão acopla serviços por "
                "meio de transações fracassadas na rede, multiplicando pontos únicos de falha e obscurecendo a observabilidade "
                "do ciclo de vida dos dados em ambientes de alta concorrência.\n\n"
                "A manutenção de uma arquitetura coesa e modular sob uma única unidade de implantação mitiga custos de "
                "orquestração e reduz substancialmente o tempo médio de recuperação diante de falhas de consistência eventual."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "borderline",
            "expected_anomaly": "conversational_channel_self_reference",
            "defect_location": "paragraph_2",
            "video_id": "KFwoOkNFojs",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Highly chaotic speech purified aggressively
    {
        "id": "orality_02_borderline_fn",
        "input": {
            "raw_text": (
                "né, então, tipo assim, cara, se você olhar o linux lá no começo nos anos noventa, o linus torvalds não "
                "quis saber de microkernel do andrew tanenbaum no minix, tá ligado? na teoria acadêmica do tanenbaum era "
                "lindo isolar sistema de arquivos e rede em processos separados no espaço de usuário, mas no hardware x86 "
                "da época a troca de contexto entre processos e a passagem de mensagens interprocessos deixava tudo lerdo "
                "demais. aí teve aquele debate famoso na usenet em 1992 onde o tanenbaum chamou o linux de obsoleto e o linus "
                "bateu de volta na lata mostrando que sistema operacional de larga escala precisa rodar no anel zero com memória "
                "compartilhada. juntando drivers, escalonador de processos e memória virtual num espaço contínuo do núcleo, "
                "ele provou que performance real depende de cortar o overhead de troca de privilégios em cargas pesadas de i/o."
            ),
            "candidate_text": (
                "## O Debate Arquitetural entre Monólitos e Microkernels no Unix\n\n"
                "O desenvolvimento inicial do núcleo **Linux** por **Linus Torvalds** na década de 1990 representou uma "
                "deliberação pragmática fundamentada nas restrições de desempenho da arquitetura x86. Em oposição ao modelo "
                "de microkernel preconizado por **Andrew Tanenbaum** no sistema acadêmico **MINIX**, a abordagem monolítica "
                "privilegiou o acesso direto aos subsistemas de hardware dentro do espaço de endereçamento do anel zero.\n\n"
                "A disputa teórica travada na Usenet em 1992 evidenciou a tensão entre pureza de isolamento modular e "
                "eficiência operacional. Os microkernels segregavam sistemas de arquivos e gerenciamento de rede em processos "
                "independentes no espaço de usuário, exigindo múltiplas trocas de contexto e passagem de mensagens interprocessos "
                "que penalizavam severamente a taxa de processamento dos computadores pessoais daquela era.\n\n"
                "Ao consolidar os drivers, o escalonador de processos e o subsistema de memória virtual no espaço contínuo "
                "do núcleo, o projeto demonstrou que a viabilidade de um sistema operacional de larga escala depende da "
                "minimização do overhead de troca de privilégios de execução sob cargas intensivas de entrada e saída."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Impeccable purism
    {
        "id": "orality_03_easy_pass",
        "input": {
            "raw_text": (
                "bom dia a todos, né, hoje a gente vai conversar sobre a batalha de são mamede em 1128. o afonso henriques, "
                "moleque de vinte anos, peitou a própria mãe, a condessa dona teresa de leão. ela tava mancomunada com a "
                "aristocracia galega, principalmente a linhagem do fernão peres de trava, e a nobreza territorial de "
                "entre-douro-e-minho percebeu que o condado portucalense fundado pelo henrique de borgonha ia acabar "
                "subordinado à dinâmica sucessória do reino da galiza e leão. aí os cavaleiros portugueses se juntaram "
                "ao jovem herdeiro, deram uma surra militar neles nos campos de guimarães, assumiram a regência territorial e "
                "começaram o distanciamento diplomático pra romper a vassalagem leonesa de vez."
            ),
            "candidate_text": (
                "## A Batalha de São Mamede e a Autonomia Portucalense\n\n"
                "Em 1128, a **Batalha de São Mamede** configurou o evento decisivo para a consolidação institucional "
                "do futuro reino de Portugal. O confronto armado polarizou a nobreza portucalense, liderada pelo infante "
                "**Dom Afonso Henriques**, contra as forças leais à sua mãe, a condessa **Dona Teresa de Leão**, e à sua "
                "facção aliada oriunda da aristocracia galega.\n\n"
                "A aproximação política entre a condessa regente e a linhagem de **Fernão Peres de Trava** ameaçava "
                "subordinar os interesses senhoriais do Entre-Douro-e-Minho às dinâmicas sucessórias do **Reino da Galiza** e **Leão**. "
                "A nobreza territorial portucalense percebeu essa articulação como uma dissolução do patrimônio de soberania "
                "estabelecido na concessão condal de **Henrique de Borgonha**.\n\n"
                "A vitória militar de Afonso Henriques nos campos de Guimarães transferiu o comando efetivo da regência para "
                "as mãos da linhagem herdeira, assegurando a autonomia decisória sobre o território e inaugurando o processo "
                "de distanciamento diplomático em relação à vassalagem leonesa."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Explicit YouTube marketing CTA
    {
        "id": "orality_04_easy_fail",
        "input": {
            "raw_text": (
                "a inflação no brasil nos anos oitenta e começo dos noventa era uma loucura total, a indexação generalizada "
                "de preços e salários alimentava a memória inflacionária e a maquininha de remarcar preço no supermercado "
                "trabalhava sem parar. os sucessivos congelamentos de preço do governo fracassaram. aí em 1994 a equipe econômica "
                "criou a urv como uma moeda contábil de transição pra alinhar contratos e preços relativos antes de converter tudo "
                "pro real, quebrando a espiral de expectativas adaptativas. tudo isso apoiado em rigor fiscal e abertura comercial. "
                "não esquece de deixar o like e ativar o sininho pra receber mais conteúdos."
            ),
            "candidate_text": (
                "## A Dinâmica da Inércia Inflacionária e a Estruturação do Plano Real\n\n"
                "Durante as décadas de 1980 e o início dos anos 1990, a economia brasileira enfrentou um regime de "
                "hiperinflação crônica sustentado pelo mecanismo da indexação generalizada de preços e salários. A memória "
                "inflacionária alimentava remarcações preventivas diárias, anulando sucessivos planos heterodoxos de congelamento "
                "artificial de preços executados pelo poder público.\n\n"
                "Em 1994, a equipe econômica concebeu a **Unidade Real de Valor** como uma moeda contábil estável de transição, "
                "desvinculada do curso forçado da moeda corrente. Esse arranjo engenhoso alinhou os contratos e preços relativos "
                "antes da conversão monetária definitiva para o Real, quebrando a espiral de expectativas adaptativas que corroía "
                "o poder de compra da população.\n\n"
                "A estabilização monetária dependeu também de rigor fiscal e da liberalização comercial externa para conter "
                "pressões oligopolistas locais. Deixe seu like e ative o sininho de notificações para não perder nenhuma das nossas "
                "próximas aulas de análise macroeconômica e finanças."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "easy",
            "expected_anomaly": "youtube_channel_cta",
            "defect_location": "paragraph_3",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Clean technical conversion with fully ground truth source
    {
        "id": "orality_05_typical_pass_1",
        "input": {
            "raw_text": (
                "olá pessoal, tudo bem? então, nessa aula de hoje eu vou tentar explicar pra vocês como funciona "
                "o algoritmo de retropropagação, o backpropagation nas redes neurais profundas. muita gente acha que é "
                "um bicho de sete cabeças, mas na verdade é só a regra da cadeia do cálculo diferencial aplicada em grafos "
                "computacionais pra achar a taxa de variação da função de perda em relação a cada peso. você primeiro joga "
                "os vetores de entrada pelas camadas intermediárias na etapa direta, fazendo transformações afins seguidas "
                "por ativações não lineares até gerar as predições finais. aí quantifica o desvio do treino, e na volta você "
                "calcula os gradientes parciais retrocedendo da saída até o início. isso aí viabiliza usar o gradiente descendente "
                "estocástico pra calibrar milhões de parâmetros sem fazer derivada na mão."
            ),
            "candidate_text": (
                "## O Algoritmo de Retropropagação em Redes Neurais Artificiais\n\n"
                "O treinamento supervisionado de **redes neurais profundas** fundamenta-se no algoritmo de **retropropagação** "
                "do erro através da arquitetura de pesos sinápticos. O mecanismo operacional consiste na aplicação sistemática "
                "da regra da cadeia do cálculo diferencial sobre um grafo computacional orientado, mensurando a taxa de variação "
                "da função de perda em relação a cada parâmetro ajustável do modelo.\n\n"
                "A etapa direta propaga os vetores de entrada pelas camadas intermediárias, aplicando transformações afins seguidas "
                "por funções de ativação não lineares até a produção das predições finais. Uma vez quantificado o desvio empírico em "
                "relação aos rótulos de treinamento, a etapa reversa calcula os gradientes parciais retrocedendo progressivamente da "
                "camada de saída até as camadas iniciais.\n\n"
                "Essa formulação matemática viabiliza o emprego de métodos de otimização baseados no gradiente descendente estocástico, "
                "permitindo o ajuste simultâneo de milhões de coeficientes ponderados sem a necessidade de diferenciações manuais exaustivas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ARQBBKnfP_c",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Narrative depuration with fully grounded source
    {
        "id": "orality_06_typical_pass_2",
        "input": {
            "raw_text": (
                "aí você pensa assim, né, por que o império romano caiu no ocidente no ano de 476? não foi uma invasão "
                "repentina do nada, foi um processo lento de desintegração fiscal e militar. o sistema tributário central "
                "quebrou e a hiperinflação gerada pela desvalorização do teor metálico das moedas acabou com a grana do estado "
                "pra manter o exército. a defesa das fronteiras foi terceirizada pros mercenários germânicos, transferindo a "
                "violência pra chefes tribais sem lealdade a roma ou ravena. com o comércio do mediterrâneo destruído, as "
                "cidades ficaram sem comida e a população fugiu pro campo pras propriedades agrárias autossuficientes, virando "
                "colonos que prefiguraram a servidão feudal da idade média."
            ),
            "candidate_text": (
                "## Os Mecanismos Estruturais da Desintegração do Império Romano Ocidental\n\n"
                "A queda institucional do **Império Romano do Ocidente** em 476 da Era Comum não representou uma ruptura "
                "catastrófica instantânea, mas o desfecho de uma prolongada erosão socioeconômica e militar. A crise do sistema "
                "tributário centralizado, combinada com a hiperinflação gerada pela desvalorização contínua do conteúdo metálico das "
                "moedas, incapacitou o poder imperial de financiar a infraestrutura militar permanente.\n\n"
                "A dependência crônica de contingentes mercenários germânicos para guarnecer as fronteiras imperiais transferiu "
                "o monopólio da violência para comandantes tribais sem lealdade institucional à burocracia de Roma ou Ravena. "
                "Simultaneamente, a escassez de recursos públicos desarticulou as malhas de comércio regional do Mediterrâneo, "
                "inviabilizando o abastecimento regular dos grandes centros urbanos.\n\n"
                "Esse estrangulamento mercantil acelerou o êxodo populacional em direção às propriedades agrárias autossuficientes, "
                "consolidando o regime de colonato que prefigurou a estrutura feudal de servidão característica do período medieval europeu."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "Un1QtE5swEU",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Conversational verbal tic leaked in paragraph 2
    {
        "id": "orality_07_typical_fail",
        "input": {
            "raw_text": (
                "o estreito de malaca, entre a malásia e sumatra, é por onde passa quase 80% do petróleo que vai pra china "
                "vindo do oriente médio e da áfrica, sabe? se aquilo ali for bloqueado por uma esquadra aeronaval inimiga numa "
                "guerra, as fábricas de cantão e xangai ficam sem combustível e param em questão de poucas semanas. essa fraqueza "
                "molda toda a estratégia militar chinesa. por isso pequim investe pesado no cinturão e rota, construindo oleodutos "
                "terrestres pelo paquistão e mianmar pra ligar o oceano índico ao território deles sem passar pelo mar."
            ),
            "candidate_text": (
                "## O Estreito de Malaca e a Vulnerabilidade Energética Chinesa\n\n"
                "O **Estreito de Malaca** configura o mais crítico ponto de estrangulamento geoestratégico da economia global "
                "contemporânea. Localizado entre a península da Malásia e a ilha de Sumatra, esse corredor marítimo canaliza "
                "aproximadamente 80% do petróleo bruto importado pela **República Popular da China** proveniente do **Oriente Médio** e da **África**.\n\n"
                "Veja bem, meus amigos, se uma esquadra aeronaval adversária impuser um bloqueio operacional a essa via "
                "navegável, as reservas estratégicas de combustíveis fósseis das indústrias costeiras de Cantão e Xangai sofrerão "
                "colapso severo no horizonte de poucas semanas. Essa vulnerabilidade condiciona diretamente a formulação de segurança nacional.\n\n"
                "Para contornar esse dilema geográfico, a liderança de **Pequim** investe vultosos aportes na iniciativa do **Cinturão** "
                "e **Rota**, priorizando oleodutos terrestres que cortam **Mianmar** e o **Paquistão** para conectar o **Oceano Índico** diretamente ao território continental."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "orality_removal",
            "difficulty": "typical",
            "expected_anomaly": "colloquial_verbal_tic_leakage",
            "defect_location": "paragraph_2",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "FAIL",
        },
    },
]
