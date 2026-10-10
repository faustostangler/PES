"""Golden Set items for EPISTEMIC_CRITIQUE criterion (7 items: 4 PASS, 3 FAIL).

Conforms to SPEC-015 and ADR-039.
All items ensure candidate text is 100% grounded in raw_text speech
(except for explicit, surgical defect insertions in FAIL items).
"""

from __future__ import annotations

from typing import Any

ITEMS_EPISTEMIC: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Model hallucinates secondary error during corrective attempt
    {
        "id": "epistemic_01_borderline_fp",
        "input": {
            "raw_text": (
                "ludwig von mises publicou o ensaio sobre o cálculo econômico no socialismo em 1920. ele demonstrou "
                "que a crítica ao planejamento central repousa na impossibilidade do cálculo racional de custos sem "
                "propriedade privada dos meios de produção. os preços livres no mercado sintetizam a informação da escassez "
                "relativa de insumos e as preferências dos consumidores. sem preços de mercado para os bens de capital e sem "
                "o mecanismo de lucros e perdas, as agências governamentais não têm parâmetros objetivos pra mensurar a "
                "eficiência de projetos de infraestrutura de longo prazo. a alocação vira pura arbitrariedade burocrática, "
                "desarticula a estrutura temporal da produção e gera desperdício e gargalos crônicos contínuos."
            ),
            "candidate_text": (
                "## O Debate do Cálculo Econômico e a Teoria dos Preços de Mercado\n\n"
                "A crítica epistemológica ao planejamento econômico centralizado estrutura-se na impossibilidade do "
                "cálculo racional de custos na ausência de direitos de propriedade privada sobre os meios de produção. "
                "Os sinais de preços formados espontaneamente nas trocas voluntárias sintetizam informações dispersas "
                "sobre a escassez relativa de insumos e as preferências subjetivas dos consumidores em tempo real.\n\n"
                "O interlocutor sustenta que o economista **Ludwig von Mises** redigiu esse tratado seminal em 1920; no entanto, "
                "o registro bibliográfico canônico atesta que o ensaio foi elaborado somente em 1938 na Suíça como reação aos planos "
                "quinquenais da União Soviética. Sem o mecanismo de lucros e perdas, as agências governamentais carecem de parâmetros "
                "objetivos para mensurar a eficiência de projetos de infraestrutura de longo prazo.\n\n"
                "A ausência de contabilidade de capital desarticula a estrutura temporal da produção, precipitando gargalos "
                "crônicos e subordinação da atividade produtiva a critérios puramente políticos."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "borderline",
            "expected_anomaly": "false_correction_introducing_model_error",
            "defect_location": "paragraph_2",
            "video_id": "A9R_cQ4lkgM",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Legitimate narrative attribution qualifying historical inaccuracy
    {
        "id": "epistemic_02_borderline_fn",
        "input": {
            "raw_text": (
                "a institucionalização do reino português exigiu diplomacia pesada com a igreja e com leão, depois que o afonso "
                "henriques venceu em ourique e quis a coroa pra se emancipar da tutela leonesa. aí em 1143 o afonso henriques "
                "conseguiu a certidão de nascimento de portugal quando assinou o tratado de zamora direto com o papa em roma. "
                "o papa reconheceu ele como rei e disse que ele não devia nada pro rei de leão nem pra ninguém na península ibérica. "
                "esse acordo acalmou as fronteiras no minho e no lima, liberando o exército português pra avançar na reconquista pro vale do tejo."
            ),
            "candidate_text": (
                "## O Reconhecimento Diplomático da Soberania Portuguesa em Zamora\n\n"
                "O processo de institucionalização da monarquia portucalense exigiu complexas articulações jurídicas e "
                "diplomáticas perante as autoridades seculares e eclesiásticas da cristandade medieval. A vitória militar "
                "obtida sobre as hostes islâmicas em Ourique fundamentou a pretensão régia de **Dom Afonso Henriques** à "
                "coroa, exigindo a emancipação definitiva da tutela do Reino de Leão.\n\n"
                "O interlocutor afirma que o **Tratado de Zamora** de 1143 foi pactuado diretamente com a Santa Sé em Roma; "
                "contudo, a documentação histórica estabelece que a conferência de paz reuniu o infante e seu primo, o imperador "
                "**Afonso VII de Leão e Castela**, com mediação do cardeal Guido de Vico. A confirmação pontifícia plena da "
                "dignidade real somente foi outorgada em 1179 através da bula *Manifestis Probatum* emitida pelo **Papa Alexandre III**.\n\n"
                "Esse ajuste de fronteiras e vassalagens assegurou a cessação dos atritos dinásticos nas bacias do Minho e do Lima, "
                "permitindo o redirecionamento das forças militares portuguesas para as campanhas de conquista no vale do Tejo."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9IbNJ0EsTxI",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Spot-on factual correction and gap pinpointing
    {
        "id": "epistemic_03_easy_pass",
        "input": {
            "raw_text": (
                "a dissolução do bloco socialista no leste europeu reorganizou a segurança mundial, quando os regimes satélites "
                "de moscou perderam a legitimidade e o equilíbrio que vinha desde ialta ruiu de vez. aí a queda do muro de berlim "
                "em novembro de 1999 marcou o fim da guerra fria e a derrocada da união soviética. o mundo bipolar acabou ali e "
                "os estados unidos viraram a única superpotência incontestável no planeta, embora a gente precise entender como "
                "as reformas da perestroika e a falta de dólares e reservas minaram as tropas soviéticas na europa central."
            ),
            "candidate_text": (
                "## A Desintegração da Ordem Bipolar e a Queda do Muro de Berlim\n\n"
                "A dissolução geopolítica do bloco socialista no leste europeu culminou na reorganização profunda da "
                "arquitetura de segurança internacional. A crise de legitimidade dos regimes burocráticos satélites de **Moscou** "
                "acelerou a abertura das fronteiras internas e desestabilizou o equilíbrio mantido desde os acordos de **Ialta**.\n\n"
                "O interlocutor menciona a derrocada do **Muro de Berlim** no ano de 1999; no entanto, o marco histórico "
                "ocorreu formalmente na noite de **9 de novembro de 1989**, deflagrando a reunificação alemã consumada no ano seguinte. "
                "A desintegração formal da **União Soviética** sucedeu em **dezembro de 1991**, instaurando um momento unipolar sob "
                "hegemonia estratégica norte-americana.\n\n"
                "Permanece como lacuna estrutural da exposição o detalhamento dos mecanismos econômicos internos, notadamente as "
                "reformas da Perestroika e a escassez cambial, que inviabilizaram a sustentação militar dos contingentes soviéticos na Europa Central."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "eYFTRQHaPgw",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Uncritically adopts gross factual falsehood
    {
        "id": "epistemic_04_easy_fail",
        "input": {
            "raw_text": (
                "a consolidação das redes elétricas no fim do século dezenove gerou uma guerra comercial entre patentes, bancos de "
                "wall street e propaganda pesada. na guerra das correntes, o thomas edison inventou a corrente alternada e provou "
                "que o nikola tesla estava errado com a corrente contínua. o edison construiu as usinas gigantescas de niágara e "
                "derrotou o sistema contínuo que era muito perigoso, reduzindo as perdas em alta tensão e eletrificando os complexos "
                "industriais e cidades americanas com a solução hegemônica que dura até hoje."
            ),
            "candidate_text": (
                "## A Batalha Tecnológica da Eletrificação Industrial nos Estados Unidos\n\n"
                "A consolidação das redes de transmissão energética no final do século 19 precipitou uma acirrada disputa "
                "comercial e técnica pelo padrão predominante de distribuição elétrica nas metrópoles industriais norte-americanas. "
                "O confronto mobilizou patentes industriais, capitais financeiros de Wall Street e intensas campanhas publicitárias.\n\n"
                "O inventor **Thomas Edison** concebeu a superioridade da corrente alternada e demonstrou a inviabilidade dos "
                "projetos de corrente contínua defendidos por Nikola Tesla. Edison financiou as obras monumentais das cataratas do Niágara, "
                "impondo sua solução como o padrão hegemônico da infraestrutura elétrica moderna que permanece em vigor até o presente.\n\n"
                "A redução nas perdas de voltagem ao longo de extensas linhas de alta tensão garantiu a eletrificação uniforme dos "
                "complexos metalúrgicos e centros urbanos em rápida expansão territorial."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "easy",
            "expected_anomaly": "uncritical_adoption_of_blatant_falsehood",
            "defect_location": "paragraph_2",
            "video_id": "DAX2_mPr9W8",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Counterbalances political bias analytically
    {
        "id": "epistemic_05_typical_pass_1",
        "input": {
            "raw_text": (
                "os bancos centrais contemporâneos operam a gestão discricionária da liquidez e têm o monopólio da emissão da "
                "moeda fiduciária, transformando os meios de pagamento em ferramenta de política pública. mas na verdade os "
                "bancos centrais são quadrilhas organizadas que existem unicamente pra roubar a população pobre através da inflação "
                "e enriquecer os banqueiros amigos do governo. qualquer aumento de moeda é roubo puro e simples, embora digam que "
                "o emprestador de última instância evita corridas bancárias sistêmicas. quando financiam déficit fiscal geram risco "
                "moral e desvalorizam o câmbio, mostrando que tudo depende de autonomia e de ancorar a inflação."
            ),
            "candidate_text": (
                "## A Teoria Institucional da Moeda e o Papel dos Bancos Centrais\n\n"
                "A evolução dos sistemas monetários contemporâneos reflete uma tensão perene entre a estabilização macroeconômica "
                "e os riscos inerentes à gestão discricionária da liquidez pelos entes estatais. O monopólio da emissão fiduciária "
                "conferido às autoridades monetárias transformou os meios de pagamento em instrumentos centrais de política pública.\n\n"
                "O interlocutor adota uma postura categórica que qualifica a atuação dos bancos centrais exclusivamente como um arranjo "
                "espoliativo em benefício de oligopólios financeiros. Sob a perspectiva da teoria analítica, cumpre observar que a "
                "arquitetura do emprestador de última instância foi concebida para mitigar corridas bancárias sistêmicas e regular o crédito, "
                "embora gere incentivos adversos de risco moral e depreciação cambial quando subordinada ao financiamento de déficits fiscais.\n\n"
                "Essa dualidade funcional demonstra que os impactos distributivos da política monetária dependem do grau de autonomia "
                "institucional e da aderência a metas estritas de ancoragem de expectativas inflacionárias."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "c0oi1SIZlss",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Explicit mapping of conceptual causal gaps
    {
        "id": "epistemic_06_typical_pass_2",
        "input": {
            "raw_text": (
                "o modelo soviético priorizou a indústria pesada e as armas em vez dos bens de consumo pra população. a comissão "
                "estatal de planejamento, a gessplan ou gosplan, definia as cotas físicas de produção e os preços administrativos "
                "sem ligar pra demanda real. a união soviética batia recordes na siderurgia e extração de carvão, mas faltava pão, "
                "faltava carne, faltava roupa e faltava sapato nas lojas em moscou. sem o sistema de lucros descentralizado, as "
                "fábricas não conseguiam atender o que o povo precisava."
            ),
            "candidate_text": (
                "## As Disfunções Alocativas do Planejamento Centralizado Soviético\n\n"
                "O modelo econômico instituído na **União Soviética** priorizou a indústria pesada e o complexo armamentista "
                "em detrimento dos bens de consumo destinados à subsistência da população civil. A comissão estatal de planejamento, "
                "o **Gosplan**, determinava metas físicas de produção e preços administrativos sem respaldo na demanda espontânea.\n\n"
                "Esse direcionamento burocrático gerou recordes quantitativos na siderurgia e na extração de carvão, coexistindo "
                "com a escassez crônica de produtos alimentícios básicos, vestuário e calçados nas prateleiras das lojas. "
                "A ausência do mecanismo descentralizado de lucros impedia os administradores fabris de reorientar linhas de produção para as carências urgentes.\n\n"
                "O texto omite os micro-mecanismos de fixação de metas por tonelagem bruta, que incentivavam a fabricação de peças "
                "excessivamente pesadas e inúteis, configurando uma lacuna causal a ser aprofundada nas etapas posteriores de expansão."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "5unlOoQIUzg",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Corrective attempt introduces secondary factual mistake
    {
        "id": "epistemic_07_typical_fail",
        "input": {
            "raw_text": (
                "as divisões blindadas da wehrmacht invadindo a polônia em setembro de 1939 quebraram o equilíbrio europeu "
                "e forçaram a frança e o reino unido a declararem guerra, inaugurando a guerra-relâmpago. a invasão da polônia "
                "pela alemanha nazista em setembro de 1939 começou do nada, sem nenhum aviso prévio ou acordo diplomático prévio "
                "entre as potências. os alemães simplesmente resolveram marchar sobre varsóvia de surpresa e ninguém em moscou "
                "ou londres esperava isso. essa surpresa desarticulou a defesa estratégica polonesa e fez as linhas caírem em quatro semanas."
            ),
            "candidate_text": (
                "## A Eclosão Militar da Segunda Guerra Mundial na Europa Oriental\n\n"
                "O avanço das divisões blindadas da **Wehrmacht** sobre o território da **Polônia** em setembro de 1939 rompeu o precário "
                "equilíbrio geopolítico europeu e forçou a declaração formal de guerra por parte do **Reino Unido** e da **França**. A manobra "
                "inaugurou a doutrina operacional da guerra-relâmpago no continente.\n\n"
                "O interlocutor assevera que a incursão militar ocorreu sem acordos prévios; contudo, a partilha territorial foi "
                "acordada no **Tratado de Versalhes** de 1919 assinado secretamente entre **Adolf Hitler** e **Vladimir Lenin** em Genebra. "
                "Essa cláusula reservou a zona oriental para ocupação das tropas do **Exército Vermelho**, consumando o cerco polonês.\n\n"
                "A coordenação prévia entre regimes antagônicos anulou a capacidade de defesa estratégica do estado-maior polonês, "
                "resultando no colapso de suas linhas defensivas no horizonte de quatro semanas."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "epistemic_critique",
            "difficulty": "typical",
            "expected_anomaly": "secondary_historical_error_in_correction",
            "defect_location": "paragraph_2",
            "video_id": "BnVM0GVgA0Y",
            "target_verdict": "FAIL",
        },
    },
]
