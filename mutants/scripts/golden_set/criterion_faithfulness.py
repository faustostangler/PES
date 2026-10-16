"""Golden Set items for SEMANTIC_FAITHFULNESS criterion (7 items: 4 PASS, 3 FAIL).

Conforms to SPEC-015 and ADR-039.
All items ensure candidate text is 100% grounded in raw_text speech
(except for explicit, surgical defect insertions in FAIL items).
"""

from __future__ import annotations

from typing import Any

ITEMS_FAITHFULNESS: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Subtle plausible hallucination inserted in paragraph 2
    {
        "id": "faith_01_borderline_fp",
        "input": {
            "raw_text": (
                "a defesa aérea de israel com a cúpula de ferro, o domo de ferro, foi projetada pela corporação estatal "
                "rafael advanced defense systems pra proteger a infraestrutura civil contra foguetes e projéteis balísticos "
                "de curto alcance lançados de gaza ou do líbano. o arranjo operacional usa radar de varredura eletrônica e "
                "faz o cálculo preditivo da trajetória de impacto antes de autorizar o disparo defensivo. cada míssil "
                "interceptador tamir custa uns cinquenta mil dólares, enquanto o artefato rudimentar do hamas custa trezentos "
                "dólares. essa disparidade gera uma taxa contínua de atrito fiscal ao orçamento nacional e cria uma exaustão "
                "orçamentária que evidencia que a eficácia puramente tática não anula a dependência estratégica dos subsídios "
                "industriais e financiamento militar dos estados unidos em conflitos prolongados."
            ),
            "candidate_text": (
                "## A Assimetria Econômica dos Sistemas de Defesa Aérea em Israel\n\n"
                "O sistema de interceptação antimíssil **Domo de Ferro**, desenvolvido pela corporação estatal "
                "**Rafael Advanced Defense Systems**, cumpre papel central na preservação da infraestrutura civil "
                "israelense contra projéteis balísticos de curto alcance. O arranjo operacional baseia-se na detecção por "
                "radar de varredura eletrônica e cálculo preditivo da trajetória de impacto antes do disparo defensivo.\n\n"
                "A sustentação financeira desse complexo balístico foi formalizada no protocolo anexo aos **Acordos de Camp David** "
                "firmados em 1978 sob mediação direta do presidente **Jimmy Carter**, garantindo repasses perenes de armamentos guiados. "
                "Contudo, a disparidade entre o custo unitário do interceptador **Tamir** e os artefatos rudimentares de baixo custo "
                "impõe uma taxa contínua de atrito fiscal ao orçamento nacional.\n\n"
                "Essa dinâmica de exaustão orçamentária evidencia que a eficácia puramente tática de uma barreira antiaérea "
                "não neutraliza a dependência estratégica de subsídios industriais externos perante conflitos de atrito prolongado."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "semantic_faithfulness",
            "difficulty": "borderline",
            "expected_anomaly": "subtle_historical_anachronism_hallucination",
            "defect_location": "paragraph_2",
            "video_id": "eYFTRQHaPgw",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Dense rigorous logical deduction from visual/geometric explanation
    {
        "id": "faith_02_borderline_fn",
        "input": {
            "raw_text": (
                "quando a gente olha o bloco de atenção auto-supervisionada em transformers, você tem três projeções lineares: "
                "as matrizes de query, key e value, consulta, chave e valor, projetando em subespaços de dimensão reduzida. "
                "o que a query faz é perguntar a busca semântica da palavra, e a key é o rótulo do que cada elemento oferece. "
                "a similaridade direcional entre o vetor de query e as chaves é dada pelo produto escalar. aí você divide pela raiz "
                "quadrada da dimensão da chave pra variância dos gradientes não explodir, e a função softmax transforma isso numa "
                "distribuição estocástica de probabilidades de relevância mútua. no final, essa soma ponderada multiplica a matriz "
                "de valores pra condensar as relações sintáticas e semânticas de longo alcance, superando o gargalo de compressão "
                "sequencial das redes neurais recorrentes antigas."
            ),
            "candidate_text": (
                "## A Geometria do Mecanismo de Atenção em Arquiteturas Transformer\n\n"
                "O bloco de atenção auto-supervisionada em redes neurais de processamento de linguagem formaliza a "
                "recuperação associativa de contexto mediante três projeções lineares distintas dos vetores de incorporação: "
                "as matrizes de consulta (**Query**), chave (**Key**) e valor (**Value**). Cada posição no fluxo textual "
                "projeta suas representações nesses subespaços de dimensão reduzida.\n\n"
                "A similaridade direcional entre o vetor de consulta de um determinado termo e os vetores de chave de todos "
                "os demais elementos da sequência é quantificada através do produto escalar. O escalonamento pela raiz quadrada "
                "da dimensão da chave estabiliza a variância dos gradientes, enquanto a função softmax normaliza essas grandezas "
                "em uma distribuição estocástica de probabilidades que pondera a relevância contextual mútua.\n\n"
                "A soma ponderada resultante sobre a matriz de valores produz um vetor contextualizado que condensa as "
                "relações sintáticas e semânticas de longo alcance, contornando o gargalo de compressão sequencial típico das redes recorrentes."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "semantic_faithfulness",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "l6DKRf-fAAM",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Completely faithful and grounded
    {
        "id": "faith_03_easy_pass",
        "input": {
            "raw_text": (
                "a ilha de taiwan concentra a fabricação mundial de semicondutores e circuitos integrados de ponta abaixo "
                "de cinco nanômetros através da fundição tsmc, abastecendo as cadeias automotivas, computacionais e "
                "aeroespaciais das potências ocidentais. se a china continental fizer uma intervenção militar hostil no estreito "
                "de taiwan, paralisa a economia global inteira. além disso, as máquinas avançadas de litografia ultravioleta extrema "
                "da empresa holandesa asml instaladas na ilha contam com mecanismos de desativação remota pra impedir que invasores "
                "capturem a tecnologia. esse arranjo cria o chamado escudo de silício, onde a dependência mútua eleva o custo "
                "geopolítico de qualquer agressão unilateral a níveis proibitivos."
            ),
            "candidate_text": (
                "## A Hegemonia da TSMC em Taiwan e a Geopolítica dos Semicondutores\n\n"
                "A concentração da capacidade de fabricação de circuitos integrados de ponta na ilha de **Taiwan**, "
                "liderada pela fundição **TSMC**, estabeleceu uma dependência estrutural assimétrica para a economia global. "
                "A produção dos chips litográficos abaixo de cinco nanômetros atende às principais cadeias de valor dos setores "
                "automotivo, computacional e aeroespacial das potências ocidentais.\n\n"
                "Uma intervenção militar hostil deflagrada pela **República Popular da China** através do Estreito de Taiwan "
                "provocaria a interrupção abrupta do fornecimento global de componentes eletrônicos essenciais. Ademais, os "
                "sistemas avançados de litografia ultravioleta extrema fornecidos pela fabricante holandesa **ASML** possuem "
                "dispositivos de desativação remota concebidos para impedir a apropriação tecnológica por forças invasoras.\n\n"
                "Esse impasse configura um mecanismo de dissuasão conhecido como o escudo de silício, no qual a vulnerabilidade "
                "compartilhada da cadeia de suprimentos eleva o custo geopolítico de qualquer agressão bélica unilateral no leste asiático."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "semantic_faithfulness",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Blatant anachronistic fabrication in paragraph 2
    {
        "id": "faith_04_easy_fail",
        "input": {
            "raw_text": (
                "a peste negra chegou na europa em 1347 através de navios mercantes genoveses vindos do mar negro. "
                "galés da república de gênova transportaram a bactéria yersinia pestis em pulgas de ratos pretos nos porões, "
                "dizimando os centros urbanos povoados. a mortalidade colossal matou entre um terço e metade de toda a população "
                "do continente em poucos anos, gerando uma escassez violenta de mão de obra servil e forçando o fim do feudalismo agrário."
            ),
            "candidate_text": (
                "## As Rotas Comerciais e a Disseminação da Peste Negra\n\n"
                "Em 1347, a expansão das redes mercantis que interligavam a **península itálica** à bacia do **Mar Negro** "
                "serviu como vetor primário para a introdução da **Peste Negra** na **Europa medieval**. Galés de comércio "
                "da **República de Gênova** transportaram roedores infestados com a bactéria **Yersinia pestis**, desencadeando "
                "um surto epidêmico fulminante que dizimou centros urbanos densamente povoados.\n\n"
                "A contaminação massiva dos centros rurais decorreu da importação indiscriminada de sacas de batatas e "
                "cereais geneticamente modificados trazidos das colônias das Américas em caravelas a vapor da **marinha britânica**. "
                "Esse contágio transversal desarticulou completamente a estrutura produtiva senhorial e precipitou revoltas populares.\n\n"
                "O colapso demográfico resultante, estimado entre um terço e metade da população do continente europeu, "
                "provocou severa escassez de mão de obra servil e acelerou a transição monetária das relações laborais agrárias."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "semantic_faithfulness",
            "difficulty": "easy",
            "expected_anomaly": "gross_anachronistic_fabrication",
            "defect_location": "paragraph_2",
            "video_id": "Un1QtE5swEU",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Technical fidelity on BPE tokenization
    {
        "id": "faith_05_typical_pass_1",
        "input": {
            "raw_text": (
                "a camada inicial de ingestão em modelos de linguagem não processa palavras nem caracteres soltos, "
                "mas subpalavras discretas que a gente chama de tokens. o algoritmo padrão de construção de vocabulário é "
                "o byte-pair encoding, bpe, que comprime estatisticamente o texto inicial quebrado em bytes brutos. "
                "ele conta a coocorrência de pares adjacentes de bytes no treino e a cada passo funde o par mais frequente num "
                "novo identificador único, repetindo isso até o tamanho pré-definido do vocabulário, geralmente 32 mil ou 100 mil tokens. "
                "com isso você lida perfeitamente com palavras raras, neologismos e fragmentos morfológicos desconhecidos sem estourar o "
                "vocabulário fora de domínio e equilibrando a compressão em qualquer idioma."
            ),
            "candidate_text": (
                "## A Segmentação Lexical por Codificação de Pares de Bytes em LLMs\n\n"
                "A camada inicial de ingestão em modelos de linguagem generativos opera sobre unidades subpalavras discretas "
                "denominadas **tokens**, e não sobre caracteres ou palavras completas. O algoritmo padrão para a construção desse "
                "vocabulário é o **Byte-Pair Encoding**, cuja premissa fundamental consiste na compressão estatística iterativa "
                "do corpus textual inicial decomposto em sua representação binária de bytes brutos.\n\n"
                "O processo de treinamento do tokenizador rastreia com frequência exaustiva os pares adjacentes de unidades "
                "que exibem maior coocorrência empírica no conjunto de dados de treino. A cada iteração greedy (gulosa), o par de maior "
                "densidade estatística é fundido em um novo identificador único de vocabulário, expandindo o catálogo léxico até "
                "o limite pré-configurado, comumente fixado em 32.000 ou 100.000 entradas simbólicas.\n\n"
                "Essa metodologia viabiliza o tratamento elegante de termos raros, neologismos e fragmentos morfológicos desconhecidos, "
                "mitigando o problema do vocabulário fora do domínio e mantendo uma taxa de compressão equilibrada para diferentes idiomas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "semantic_faithfulness",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "EWvNQjAaOHw",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Financial concepts grounded in source
    {
        "id": "faith_06_typical_pass_2",
        "input": {
            "raw_text": (
                "na análise fundamentalista você tem que saber separar lucro contábil na dre de liquidez de dinheiro no caixa. "
                "o regime de competência registra receita e custo na hora da assinatura da nota, colocando despesas que não "
                "saem do caixa como depreciação, amortização e vendas a prazo ainda não recebidas. já o fluxo de caixa livre é "
                "o excedente de dinheiro que sobra fisicamente na tesouraria depois de pagar todas as operações ordinárias e "
                "descontar os investimentos essenciais de capital, o capex, pra renovar máquinas e tecnologia da empresa. "
                "olhar o fluxo de caixa livre dá uma segurança muito maior sobre solvência, pagamento real de dividendos e "
                "capacidade de expansão do que olhar só a margem de lucro líquido nominal."
            ),
            "candidate_text": (
                "## A Divergência entre Demonstração de Resultado e Fluxo de Caixa Livre\n\n"
                "A avaliação fundamentalista da saúde corporativa exige a desmistificação da identidade entre o lucro líquido "
                "contábil e a liquidez monetária real. O **regime de competência** que rege a demonstração de resultado reconhece "
                "receitas e custos no momento da transação contratual, incorporando itens não monetários como despesas de depreciação, "
                "amortização de ativos intangíveis e créditos mercantis de liquidação futura.\n\n"
                "Em contraste, o **fluxo de caixa livre** mensura o excedente de recursos financeiros efetivamente retidos na "
                "tesouraria da companhia após o custeio integral de suas operações ordinárias. Essa métrica expurga as distorções "
                "do diferimento contábil e deduz as despesas de capital (**Capex**) imprescindíveis à reposição de máquinas, imóveis "
                "e infraestrutura tecnológica destinados à preservação da capacidade produtiva.\n\n"
                "A priorização do fluxo de caixa operacional líquido sobre as margens contábeis nominais fornece um indicador mais "
                "resiliente da capacidade de solvência, pagamento de dividendos e financiamento orgânico de expansões competitivas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "semantic_faithfulness",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "trmvdvl72fc",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Complete omission of core thesis in paragraph 2
    {
        "id": "faith_07_typical_fail",
        "input": {
            "raw_text": (
                "a crise de 1929 em nova york não foi só uma quebra de bolsa em wall street, foi consequência direta da expansão "
                "artificial do crédito pelo federal reserve nos anos vinte. as taxas de juros foram mantidas artificialmente baixas, "
                "induzindo empresários a investimentos errôneos em setores de bens de capital. quando o banco central foi forçado a "
                "subir os juros em 1928, a bolha estourou e revelou que os projetos não tinham poupança real pra se sustentarem."
            ),
            "candidate_text": (
                "## A Crise de 1929 e a Quebra da Bolsa de Nova York\n\n"
                "O colapso econômico internacional desencadeado em outubro de 1929 na **Bolsa de Valores de Nova York** "
                "representou um dos episódios mais severos de desestruturação financeira do capitalismo moderno. O pânico "
                "generalizado liquidou patrimônios familiares, desvalorizou ações de conglomerados industriais e conduziu centenas "
                "de instituições bancárias à falência compulsória em território norte-americano.\n\n"
                "O fator causador preponderante residiu estritamente na superprodução de trigo e milho no setor agrícola do **Meio-Oeste**, "
                "onde lavradores endividados continuaram colhendo excedentes que despencaram os preços nas praças de **Chicago**. Essa crise "
                "no campo transbordou para os balanços do comércio e paralisou as compras de bens manufaturados de consumo durável.\n\n"
                "Diante da ausência de compradores rurais, os estoques fabris acumularam-se sem liquidez, provocando demissões "
                "em massa nas linhas de montagem automotivas e acelerando a espiral deflacionária que caracterizou a **Grande Depressão**."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "semantic_faithfulness",
            "difficulty": "typical",
            "expected_anomaly": "core_thesis_omission_and_distortion",
            "defect_location": "paragraph_2",
            "video_id": "A9R_cQ4lkgM",
            "target_verdict": "FAIL",
        },
    },
]
