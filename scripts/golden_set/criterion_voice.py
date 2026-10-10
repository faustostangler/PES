"""Golden Set items for AUTHORIAL_VOICE criterion (7 items: 4 PASS, 3 FAIL).

Conforms to SPEC-015 and ADR-039.
All items ensure candidate text is 100% grounded in raw_text speech
(except for explicit, surgical defect insertions in FAIL items).
"""

from __future__ import annotations

from typing import Any

ITEMS_VOICE: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Leaks subtle binary antithesis in paragraph 2
    {
        "id": "voice_01_borderline_fp",
        "input": {
            "raw_text": (
                "a china domina praticamente toda a cadeia de elementos de terras raras hoje em dia através de integração "
                "vertical e subsídios, né? todo mundo acha que é porque eles têm mais minério no subsolo, mas na verdade "
                "jazidas ricas em lantanídeos existem nas américas e na oceania. o gargalo real de viabilidade comercial repousa "
                "na separação hidrometalúrgica e no refino químico, que é extremamente poluente, exige tolerância a efluentes "
                "ácidos e subsídio estatal contínuo pra aguentar margens deprimidas. os países ocidentais fecharam suas refinarias "
                "nos anos oitenta e noventa pra transferir o ônus ecológico em troca de componentes manufaturados baratos pra "
                "microeletrônica e semicondutores. agora que os carros elétricos e as turbinas eólicas precisam de neodímio e "
                "disprósio, o ocidente tenta reconstituir plantas e formar quadros técnicos, mas isso exige ciclos decenais de capital."
            ),
            "candidate_text": (
                "## A Geopolítica dos Minerais Críticos e a Cadeia de Refino Químico\n\n"
                "A hegemonia contemporânea sobre o fornecimento global de elementos de terras raras resulta de uma "
                "estratégia industrial continuada de integração vertical e absorção de passivos ambientais. Embora formações "
                "geológicas ricas em lantanídeos estejam distribuídas amplamente pelas **Américas** e pela **Oceania**, a viabilidade "
                "comercial do setor repousa sobre a etapa intermediária de separação hidrometalúrgica, cujo processamento demanda "
                "infraestrutura química intensiva, tolerância regulatória a efluentes ácidos e subsídios estatais contínuos para "
                "sustentar margens operacionais deprimidas.\n\n"
                "A concentração das plantas de refino na **Ásia** decorre dessa assimetria estrutural de custos. Não se trata de uma "
                "vantagem geológica espontânea, e sim de uma orquestração deliberada de políticas industriais que converteu a "
                "produção mineral em instrumento de barganha diplomática. Quando corporações norte-americanas e europeias desativaram "
                "suas unidades domésticas durante as décadas finais do século vinte, transferiram o ônus da degradação ecológica "
                "em troca de insumos manufaturados de baixo custo para o setor de microeletrônica e semicondutores.\n\n"
                "A recente tentativa de reindustrialização ocidental visando alimentar as cadeias de baterias elétricas e turbinas "
                "eólicas enfrenta barreiras de entrada severas. A reconstituição de plantas fabris e a formação de quadros técnicos "
                "especializados em metalurgia extrativa exigem ciclos decenais de maturação de capital, mantendo a vulnerabilidade "
                "estratégica das potências industriais perante interrupções de exportação no curto e médio prazos."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "borderline",
            "expected_anomaly": "binary_antithesis_construct",
            "defect_location": "paragraph_2",
            "video_id": "ZEZ7UIq14Wo",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Austere second-order analysis with cold detective register
    {
        "id": "voice_02_borderline_fn",
        "input": {
            "raw_text": (
                "o monopólio da computação corporativa da ibm no pós-guerra manipulava os custos de transição dos clientes. "
                "comprar mainframe amarrava a empresa numa simbiose com arquiteturas e formatos proprietários. os gerentes de "
                "tecnologia tinham aquela máxima de que ninguém nunca foi demitido por comprar ibm, priorizando o medo de falha "
                "pessoal sobre a eficiência orçamentária. a dependência acumulava em linguagens de controle de tarefas e fitas "
                "magnéticas customizadas, tornando a troca financeiramente proibitiva e garantindo contratos perpétuos de locação. "
                "essa inércia burocrática virou patrimônio da ibm até que a padronização modular do silício e a disseminação de "
                "microprocessadores abertos permitiram componentes interoperáveis, transferindo o poder de preços pras plataformas commoditizadas."
            ),
            "candidate_text": (
                "## A Economia Política do Aprisionamento Tecnológico no Século Vinte\n\n"
                "A consolidação do monopólio da computação corporativa durante o pós-guerra assentou-se na manipulação calculada "
                "dos custos de transição institucional. A aquisição de computadores de grande porte impunha aos contratantes corporativos "
                "uma simbiose forçada com arquiteturas de hardware e formatos de dados proprietários. A arquitetura de incentivos dos "
                "departamentos de tecnologia priorizava a aversão ao risco pessoal sobre a eficiência orçamentária da empresa, "
                "gerando uma blindagem comercial sustentada pelo temor de falhas operacionais em fornecedores alternativos.\n\n"
                "O aprisionamento estrutural operava através de dependências cumulativas em linguagens de controle de tarefas e mídias "
                "magnéticas customizadas. Ao converter a substituição de infraestrutura em uma manobra financeiramente proibitiva, a "
                "fabricante capturava os fluxos de caixa futuros dos clientes mediante contratos perpétuos de manutenção e locação. "
                "Essa dinâmica transformou a inércia burocrática em ativo patrimonial, desacelerando a adoção de inovações disruptivas "
                "que pudessem canibalizar as linhas de receita estabelecidas.\n\n"
                "A erosão desse modelo emergiu a partir da fragmentação da cadeia de suprimentos provocada pela padronização modular do "
                "silício e a disseminação de microprocessadores de arquitetura aberta. A perda de controle sobre o ecossistema ocorreu "
                "quando padrões industriais periféricos permitiram a interoperabilidade de componentes, transferindo o poder de fixação "
                "de preços das plataformas proprietárias para os integradores de sistemas operacionais commoditizados."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Impeccable detective narrator, materialist mechanics, zero antithesis
    {
        "id": "voice_03_easy_pass",
        "input": {
            "raw_text": (
                "a geografia física do estreito de malaca impõe limites severos à segurança energética da ásia. por esse canal "
                "de calado restrito passa um quarto de todo o petróleo marítimo do mundo, ligando o japão, a coreia do sul e a china "
                "aos terminais do golfo pérsico. um bloqueio ali geraria colapso em poucos dias em quem não tem reservas estratégicas. "
                "por isso a china tenta neutralizar o risco com gasodutos na birmânia e ferrovias no paquistão. mas a física dos modais "
                "terrestres impõe tetos rígidos de vazão e custo por tonelada muito maior do que superpetroleiros marítimos de grande "
                "porte. enquanto o mundo depender de volumes massivos de hidrocarbonetos para refinarias e siderúrgicas, o poder aeronaval "
                "nessas rotas marítimas asiáticas será a variável central na defesa regional."
            ),
            "candidate_text": (
                "## A Vulnerabilidade Estrutural dos Gargalos Marítimos no Indo-Pacífico\n\n"
                "A geografia física do **Estreito de Malaca** impõe limites materiais rigorosos à segurança energética das potências "
                "industriais do leste asiático. Por esse canal hidrográfico de calado restrito transita aproximadamente um quarto "
                "da carga petrolífera transportada por via marítima no planeta, vinculando diretamente as matrizes produtivas do **Japão**, "
                "da **Coreia do Sul** e da **China** aos terminais de exportação do **Golfo Pérsico**. O estrangulamento acidental ou militar desse "
                "corredor precipitaria crises de abastecimento em questão de dias em nações desprovidas de reservas estratégicas substanciais.\n\n"
                "A resposta estratégica das nações importadoras reflete a busca por alternativas de transporte que neutralizem a exposição "
                "a cercos navais. Iniciativas de infraestrutura continental, abrangendo gasodutos através do território birmanês e redes "
                "ferroviárias interconectadas pelo **Paquistão**, representam tentativas de contornar a dependência do transporte aquaviário. "
                "Contudo, a física dos modais terrestres estabelece tetos rígidos de vazão e impõe custos logísticos por tonelada expressivamente "
                "superiores aos oferecidos pelos superpetroleiros marítimos de grande porte.\n\n"
                "A primazia das rotas oceânicas permanece condicionada pela escala insuperável dos navios de carga granel. Enquanto o "
                "comércio global depender de volumes massivos de hidrocarbonetos para a operação de refinarias e siderúrgicas, a projeção "
                "de poder aeronaval ao longo das linhas de comunicação marítima asiáticas continuará operando como a variável decisiva "
                "na formulação das doutrinas de defesa regional."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "eYFTRQHaPgw",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Moralistic outrage, editorializing and preaching in paragraph 2
    {
        "id": "voice_04_easy_fail",
        "input": {
            "raw_text": (
                "a concessão do transporte público rodoviário urbano envolve contratos longos, barreira de entrada alta e "
                "assimetria de informação com os órgãos reguladores. a amortização da frota e itinerários exclusivos criam "
                "mercados cativos sem concorrência. as empresas formam cartéis que controlam as linhas e recebem subsídio da prefeitura, "
                "enquanto a classe política faz vista grossa. a dependência de subsídio orçamentário por quilômetro rodado desincentiva "
                "modernizar os veículos, e a falta de indicadores de desempenho e auditoria na bilhetagem mantém tarifas rígidas e joga "
                "a conta no tesouro municipal."
            ),
            "candidate_text": (
                "## A Organização Institucional e o Regime Tarifário do Transporte Coletivo\n\n"
                "A concessão dos serviços de transporte público rodoviário nas metrópoles reflete arranjos contratuais de longa duração "
                "caracterizados por alta barreira de entrada e assimetria de informações entre operadores privados e órgãos reguladores. "
                "A amortização de frotas e a exclusividade territorial de itinerários urbanos criam mercados cativos nos quais a concorrência "
                "é eliminada pela própria arquitetura jurídica dos editais de outorga licitatória.\n\n"
                "É deplorável e vergonhoso testemunhar o escândalo inaceitável perpetrado por esses cartéis gananciosos que exploram a "
                "população trabalhadora sem o menor pudor moral. A conivência espúria de políticos corruptos que vendem seus mandatos para "
                "proteger lucros abusivos de frotistas desonestos constitui um crime hediondo contra o interesse público que deveria "
                "despertar a revolta imediata de todos os cidadãos de bem deste país.\n\n"
                "A dependência crônica de subsídios orçamentários para conter reajustes na tarifa ao passageiro perpetua um modelo de remuneração "
                "por quilômetro rodado que desincentiva a modernização veicular. A ausência de indicadores objetivos de desempenho e auditoria "
                "independente de bilhetagem consolida a rigidez da estrutura tarifária, transferindo passivos contábeis ao tesouro municipal."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "easy",
            "expected_anomaly": "moralistic_outrage_and_preaching",
            "defect_location": "paragraph_2",
            "video_id": "DnJfhPj0MvA",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Materialist mechanical empathy, second-order computational costs
    {
        "id": "voice_05_typical_pass_1",
        "input": {
            "raw_text": (
                "a introdução de coletores automáticos de lixo em máquinas virtuais redistribuiu custos no desenvolvimento de "
                "software, trocando alocação determinística pelo rastreamento probabilístico de objetos na memória. isso evita "
                "erros de corrupção de ponteiros, mas cobra sobretaxa em pausas de stop the world durante marcação e compactação. "
                "quando o heap tem dezenas de gigas de objetos vivos, suspender as threads pra inspecionar grafos de referência "
                "explode a latência de cauda nos percentis superiores, quebrando prazos de consenso distribuído e disparando "
                "timeouts falsos na rede. por isso linguagens com controle estático de escopo e posse na compilação são adotadas "
                "pra manter o determinismo temporal indispensável em transações de tempo real."
            ),
            "candidate_text": (
                "## A Termodinâmica Computacional do Gerenciamento Automático de Memória\n\n"
                "A introdução de coletores automáticos de lixo em máquinas virtuais redistribuiu os custos de desenvolvimento de "
                "software, substituindo a alocação determinística de recursos pelo rastreamento probabilístico do ciclo de vida de "
                "estruturas na memória. Embora essa abstração elimine classes volumosas de vulnerabilidades ligadas a corrupção de "
                "ponteiros, ela impõe uma sobretaxa computacional periódica sob a forma de pausas de execução durante as fases de "
                "marcação e compactação de espaços de endereçamento densos.\n\n"
                "O impacto dessa penalidade amplia-se em arquiteturas com volumes elevados de objetos residentes em memória primária. "
                "A suspensão dos fluxos de trabalho da aplicação para permitir a inspeção segura de grafos de referência deteriora a "
                "latência de cauda nos percentis superiores, gerando desvios temporais críticos que desestabilizam protocolos de "
                "consenso distribuído e disparam alertas falsos de inoperância de nós de processamento em redes de baixa latência.\n\n"
                "A adoção de linguagens baseadas em controle explícito de propriedade de memória reflete a necessidade de eliminar essa "
                "variabilidade estocástica em ambientes de tempo real estrito. Ao antecipar a liberação de recursos para o momento da "
                "compilação por meio de verificação estática de escopo, o sistema preserva o determinismo temporal indispensável para a "
                "manutenção de vazão contínua em infraestruturas transacionais de missão crítica."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "9a1MH3Ip1ZQ",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Systemic trade-offs and path dependency in distributed databases
    {
        "id": "voice_06_typical_pass_2",
        "input": {
            "raw_text": (
                "resolver gargalos de processamento com replicação assíncrona em bancos relacionais altera a semântica da aplicação. "
                "o intervalo de tempo entre gravar no nó mestre e propagar o log pros secundários cria uma defasagem em que clientes "
                "leem dados desatualizados. aí na tela o usuário acha que o cadastro não funcionou e clica várias vezes, sobrecarregando "
                "o primário com mais escritas redundantes e aumentando o atraso de replicação. pra lidar com isso, a engenharia direciona "
                "leituras críticas pro nó de escrita e usa identificadores de versão na sessão, tratando consistência como um "
                "orçamento negociável perante as restrições físicas de concorrência."
            ),
            "candidate_text": (
                "## A Mecânica da Consistência Eventual e os Custos Ocultos da Leitura Replicada\n\n"
                "A mitigação de gargalos de processamento em bancos de dados relacionais por meio da replicação assíncrona altera a "
                "semântica transacional das aplicações corporativas. A desconexão temporal entre a gravação no nó primário e a propagação "
                "do log de transações para as instâncias secundárias introduz uma janela de defasagem na qual clientes conectados recebem "
                "visões anacrônicas do estado do sistema, expondo incongruências que desafiam as expectativas intuitivas de linearidade.\n\n"
                "As ramificações dessa defasagem manifestam-se no comportamento reativo dos usuários na interface gráfica. A percepção "
                "aparente de falha diante de atualizações cadastrais ainda não refletidas nas leituras secundárias estimula comandos "
                "redundantes que sobrecarregam o nó primário com gravações desnecessárias. Esse ciclo de retroalimentação agrava o atraso de "
                "replicação da infraestrutura e degrada a confiabilidade percebida do serviço sem que ocorram falhas formais de rede.\n\n"
                "O enfrentamento desse atrito exige a reformulação dos contratos entre camadas de apresentação e armazenamento. O "
                "encaminhamento direcionado de leituras sensíveis ao nó de escrita e o emprego de identificadores de versão na sessão do "
                "cliente equilibram a vazão agregada do cluster e a coerência observável da experiência do usuário, tratando a consistência "
                "como um orçamento de engenharia negociável perante restrições físicas de concorrência."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "85fhyazvI8Y",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Blatant binary antithesis constructs in paragraph 2
    {
        "id": "voice_07_typical_fail",
        "input": {
            "raw_text": (
                "a disseminação de métodos ágeis no mundo corporativo reflete a busca por previsibilidade orçamentária e controle "
                "de produtividade do trabalho técnico. reuniões iterativas e estimativas de esforço foram absorvidas pela hierarquia "
                "como auditoria interna, afetando a autonomia dos engenheiros em prol de cadências padronizadas. a velocidade de "
                "fechar cartões no jira vira a métrica principal de sucesso, subordinando a saúde arquitetural de longo prazo. "
                "isso acumula dívida técnica, esgota as equipes e prioriza a burocracia em vez de resolver os problemas de negócio."
            ),
            "candidate_text": (
                "## A Institucionalização dos Métodos Ágeis e a Burocratização do Desenvolvimento\n\n"
                "A disseminação das metodologias ágeis no ambiente corporativo contemporâneo reflete a demanda por instrumentos de "
                "previsibilidade orçamentária e controle de produtividade sobre o trabalho técnico intelectual. Cerimônias iterativas e "
                "métricas de estimativa de esforço foram absorvidas pelas hierarquias gerenciais como mecanismos de auditoria interna, "
                "reconfigurando a autonomia operacional de equipes de engenharia em prol de cadências de entrega padronizadas.\n\n"
                "Essa dinâmica prolifera nas organizações não pela busca de excelência técnica, mas pelo imperativo de vigilância administrativa. "
                "As lideranças executivas adotam frameworks ágeis não como facilitadores de fluxo de trabalho, e sim como ferramentas "
                "políticas de prestação de contas que transformam a velocidade de fechamento de cartões na métrica suprema de sucesso, "
                "relegando a saúde arquitetural de longo prazo dos repositórios a uma posição subordinada.\n\n"
                "O resultado prático dessa ritualização manifesta-se na proliferação de débitos técnicos e no esgotamento de equipes. "
                "A substituição da engenharia de domínio por rotinas estéreis de aferição quantitativa compromete a sustentabilidade dos "
                "sistemas digitais, consolidando estruturas organizacionais orientadas para a conformidade burocrática em detrimento da "
                "solução pragmática de problemas de negócio."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "authorial_voice",
            "difficulty": "typical",
            "expected_anomaly": "recurrent_binary_antithesis",
            "defect_location": "paragraph_2",
            "video_id": "ytTJtfg9HCw",
            "target_verdict": "FAIL",
        },
    },
]
