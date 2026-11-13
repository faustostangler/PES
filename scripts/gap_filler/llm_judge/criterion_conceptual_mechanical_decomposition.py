"""Golden Dataset Items for Criterion 2: Conceptual & Mechanical Decomposition (cm_01 to cm_07).

Evaluates non-circular definitions + operational boundary conditions (A1),
complete intermediate causal gearing A -> B -> C (A2), and unstated assumptions /
2nd-3rd-order feedback loops (D3). Orthogonal to all other 6 ADR-060 criteria.
"""

from __future__ import annotations

from typing import Any

ITEMS_CONCEPTUAL_MECHANICAL_DECOMPOSITION: list[dict[str, Any]] = [
    {
        "id": "cm_01_borderline_fp",
        "input": {
            "raw_text": (
                "## Persistência Relacional e a Otimização de Consultas\n\n"
                "O banco de dados relacional PostgreSQL, frequentemente subestimado e rotulado como o principal gargalo de sistemas web, demonstra uma eficiência notável quando submetido a cargas controladas de transações atômicas. A adoção de estratégias adequadas de indexação, como o uso de índices GIN combinados com a extensão de trigramas pg_trgm, possibilita buscas textuais parciais com latências na casa de poucos milissegundos.\n\n"
                "Essa abordagem elimina a necessidade de incorporar motores externos de busca distribuída na arquitetura inicial, reduzindo a complexidade de sincronização de dados e garantindo a integridade transacional nativa do sistema."
            ),
            "candidate_text": (
                "## A Indexação por Trigramas no PostgreSQL\n\n"
                "No PostgreSQL, o índice GIN combinado à extensão pg_trgm acelera consultas textuais com curingas à esquerda e à direita em comparação com varreduras sequenciais lineares. O ganho de latência decorre diretamente do fato de o otimizador escolher o caminho indexado na memória e devolver as linhas correspondentes em poucos milissegundos, dispensando soluções externas como Elasticsearch em estágios iniciais do projeto.\n\n"
                "Sob o ângulo histórico da engenharia de software, a consolidação de bancos relacionais extensíveis refletiu a preferência por manter integridade ACID centralizada diante de orçamentos enxutos, sendo o limite econômico da estratégia verificável pelo ponto de saturação de CPU durante picos de escrita concorrente.\n\n"
                "### Extra Info\n\n"
                "1. Índices Generalized Inverted Index (GIN) armazenam listas de ponteiros para tuplas associadas a chaves compostas extraídas de valores compostos como vetores ou textos.\n"
                "2. A extensão pg_trgm integra-se ao catálogo padrão de módulos contribuídos do PostgreSQL, exigindo criação explícita por banco via instrução CREATE EXTENSION."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "borderline",
            "expected_anomaly": "explanatory_vacuum_missing_trigram_tokenization_and_write_amplification_gearing",
            "defect_location": "body",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "cm_02_borderline_fn",
        "input": {
            "raw_text": (
                "## Arquiteturas de Raciocínio e Modelos de Pensamento\n\n"
                "A evolução recente na engenharia de redes neurais introduziu uma ruptura metodológica com o advento dos modelos orientados ao raciocínio profundo. Mediante a aplicação de aprendizado por reforço em ambientes controlados de resolução de problemas, essas arquiteturas desenvolveram a capacidade intrínseca de gerar cadeias extensas de pensamento interno antes de emitir uma resposta definitiva.\n\n"
                "Esse mecanismo confere ao sistema a habilidade de decompor premissas, detectar contradições lógicas em tempo de inferência e explorar caminhos alternativos de solução, elevando significativamente o desempenho em domínios formais como matemática e engenharia de software."
            ),
            "candidate_text": (
                "## Cadeias de Raciocínio e Limites do Aprendizado por Reforço\n\n"
                "Define-se um modelo de raciocínio por tempo de inferência como uma rede autorregressiva treinada por aprendizado por reforço contra verificadores objetivos para alocar tokens latentes de rascunho antes da resposta final. A engrenagem intermediária percorre três etapas encadeadas: primeiramente, o verificador determinístico (compilador ou gabarito matemático) emite sinal binário de recompensa sobre o resultado final; em seguida, o algoritmo de atualização de política reforça trajetórias intermediárias que contêm autoverificações e retrocessos lógicos; por fim, em tempo de execução, cada token de rascunho condiciona a distribuição de probabilidades subsequente no contexto ativo.\n\n"
                "Contudo, a fronteira de aplicabilidade dessa arquitetura rompe-se em domínios abertos desprovidos de verificadores objetivos, pois a otimização sem critério externo degenera em reward hacking e prolixidade vazia. Pressupõe-se tacitamente que o custo adicional de latência compensa o ganho de precisão, gerando como efeito de segunda ordem a amplificação de erros quando a premissa inicial da cadeia contém viés incorrigível. Pesquisadores discutem se modelos de recompensa aprendidos suprem a ausência de verificadores formais, hipótese falseável por queda de desempenho fora da distribuição.\n\n"
                "### Extra Info\n\n"
                "1. O algoritmo Group Relative Policy Optimization (GRPO) estima a linha de base de vantagem a partir de grupos de amostras geradas para o mesmo prompt, eliminando a necessidade de uma rede crítica do mesmo porte do modelo gerador.\n"
                "2. Em benchmarks como AIME e SWE-bench, a curva de acurácia exibe retornos decrescentes logarítmicos conforme o orçamento de tokens de raciocínio ultrapassa o limite de coerência de atenção da arquitetura."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "EWvNQjAaOHw",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "cm_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Anatomia Oculta do Voto Legislativo\n\n"
                "A engenharia eleitoral contemporânea beneficia-se da desatenção sistemática do eleitorado, transformando o sufrágio para o poder legislativo em um mecanismo opaco de transferência de capital político. Numa democracia representativa regida pelo sistema proporcional de lista aberta, o eleitor acredita sufragar exclusivamente a trajetória ética e as propostas programáticas de um único candidato individual.\n\n"
                "Contudo, a mecânica aritmética subjacente à apuração das urnas subverte essa percepção intuitiva, pois os votos nominais fluem primeiramente para a legenda partidária ou federação, permitindo que candidatos com votações massivas arrastem correligionários pouco conhecidos e frequentemente alinhados a pautas diametralmente opostas às do eleitor original."
            ),
            "candidate_text": (
                "## A Aritmética do Quociente Eleitoral na Lista Aberta\n\n"
                "O sistema proporcional de lista aberta define um método de conversão de sufrágios em cadeiras parlamentares no qual a unidade primária de alocação é o partido ou federação, e o limite de aplicabilidade dessa regra restringe-se às eleições para casas legislativas baixas (Câmara dos Deputados, assembleias estaduais e câmaras municipais), cessando no sistema majoritário do Senado e do Executivo. O mecanismo processa-se em quatro engrenagens sequenciais: inicialmente, somam-se todos os votos nominais e de legenda válidos e divide-se o total pelo número de vagas em disputa para obter o quociente eleitoral; em seguida, divide-se a votação de cada legenda pelo quociente eleitoral para fixar suas cadeiras diretas; na terceira etapa, vagas remanescentes distribuem-se pelo cálculo das maiores médias (método D'Hondt); por fim, as cadeiras conquistadas preenchem-se pelos candidatos mais votados internamente na lista partidária que atinjam a cláusula individual de desempenho de dez por cento do quociente.\n\n"
                "Esse desenho parte do pressuposto não declarado de que a identidade ideológica do partido supera o vínculo pessoal do candidato com o eleitor, produzindo como feedback de segunda ordem a busca por celebridades puxadoras de voto capazes de subsidiar candidatos de cúpula pouco competitivos. Teóricos da Escolha Pública (Anthony Downs; James Buchanan) e institucionalistas comparados divergem quanto à magnitude do efeito de informação racionalmente ignorante versus incentivos de financiamento partidário, hipótese testável por séries de transferência de votos intrapartidários.\n\n"
                "### Extra Info\n\n"
                "1. A cláusula de desempenho individual de dez por cento do quociente eleitoral foi introduzida no Código Eleitoral brasileiro pela Lei 13.165, de 2015-09-29, e a exigência para distribuição das sobras passou por ajustes na Lei 14.211, de 2021-10-01.\n"
                "2. Sob o critério de médias D'Hondt, o divisor aplicado a cada legenda cresce conforme a fórmula V / (s + 1), onde V representa os votos válidos do partido e s o total de cadeiras já atribuídas naquela circunscrição."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "7tZdt2UQtbg",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "cm_04_easy_fail",
        "input": {
            "raw_text": (
                "## A Decisão Monocrática e a Mutação das Regras de Impedimento\n\n"
                "Nesse cenário de atrito latente entre as instituições da República, a prolação de uma decisão monocrática pelo ministro Gilmar Mendes nos autos da Arguição de Descumprimento de Preceito Fundamental 1259 reconfigurou o equilíbrio constitucional. O magistrado suspendeu dispositivos fundamentais da Lei do Impeachment de 1950, restringindo a legitimidade ativa para o protocolo de pedidos de afastamento exclusivamente à Procuradoria-Geral da República.\n\n"
                "Adicionalmente, a decisão alterou o quórum de aprovação no plenário do Senado Federal, elevando a exigência de maioria simples para maioria qualificada de dois terços. Na fundamentação apresentada, o relator argumentou que a atualização normativa tornava-se imperativa em virtude da transformação do contexto político nacional desde meados do século XX, conferindo ao Supremo Tribunal Federal uma blindagem procedimental inédita contra processos iniciados por cidadãos comuns."
            ),
            "candidate_text": (
                "## O Julgamento da Lei de Impeachment no Supremo\n\n"
                "Uma decisão monocrática do ministro Gilmar Mendes na Arguição de Descumprimento de Preceito Fundamental 1259 modificou regras da Lei 1.079/1950. O despacho reservou à Procuradoria-Geral da República a iniciativa exclusiva para denunciar ministros do tribunal e elevou o quórum exigido no Senado Federal para dois terços dos parlamentares.\n\n"
                "Segundo a fundamentação exposta nos autos, mudanças políticas ocorridas desde 1950 justificariam a releitura do estatuto legal, ampliando a proteção procedimental dos magistrados diante de pedidos individuais protocolados por cidadãos.\n\n"
                "### Extra Info\n\n"
                "1. A Lei 1.079, de 1950-04-10, disciplina os crimes de responsabilidade e o rito de processamento no Senado Federal.\n"
                "2. A ADPF é uma ação do controle concentrado de constitucionalidade prevista no parágrafo primeiro do artigo 102 da Constituição de 1988."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "easy",
            "expected_anomaly": "near_verbatim_paraphrase_without_mechanical_decomposition",
            "defect_location": "body",
            "video_id": "z82sKS_xj28",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "cm_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A consolidação da hegemonia e o projeto VLSI\n\n"
                "O lançamento do Projeto de Circuito Integrado em meados da década de 1960 permitiu que empresas como NEC, Toshiba e Hitachi saltassem da fabricação isolada de transistores para a produção de circuitos integrados em escala comercial. A criação do consórcio cooperativo VLSI entre 1976 e 1979 consolidou a liderança tecnológica japonesa na fabricação de memórias dinâmicas de acesso aleatório.\n\n"
                "A convergência entre o financiamento coordenado pelo Ministério do Comércio Internacional e Indústria, a disciplina industrial de controle de defeitos e a escala das corporações verticalmente integradas colocou os fabricantes nipônicos à frente dos concorrentes norte-americanos no limiar da década de 1980."
            ),
            "candidate_text": (
                "## A Engrenagem do Consórcio VLSI e a Qualidade de Rendimento\n\n"
                "Define-se um consórcio tecnológico pré-competitivo, no caso do programa Very Large Scale Integration (VLSI, 1976–1979), como o arranjo institucional no qual rivais industriais compartilham pesquisa básica de processo enquanto preservam competição na comercialização; sua utilidade cessa quando o paradigma arquitetural estabiliza-se e a diferenciação migra para design proprietário de sistemas. A engrenagem produtiva conectou três elos: inicialmente, o MITI aportou subsídios condicionados para laboratórios conjuntos com Fujitsu, Hitachi, Mitsubishi Electric, NEC e Toshiba visando litografia por feixe de elétrons e purificação de wafers de silício; na etapa fabril, a redução de partículas microscópicas em salas limpas elevou a taxa de rendimento (yield) por lâmina acima dos patamares norte-americanos; por fim, o menor custo unitário gerado pelo yield superior financiou novos ciclos de capex em memórias DRAM de 64 Kb e 256 Kb.\n\n"
                "O modelo assumia demanda previsível de grandes mainframes e estabilidade cambial, produzindo como efeito de segunda ordem excesso de capacidade fixa quando a computação pessoal deslocou o valor econômico da memória padronizada para microprocessadores lógicos. Analistas industriais debatem se o sucesso decorreu mais da coordenação estatal japonesa ou da subinversão de empresas norte-americanas focadas em retorno trimestral, tese falseável via comparação das taxas de reinvestimento em P&D entre 1976 e 1984.\n\n"
                "### Extra Info\n\n"
                "1. O Laboratório Cooperativo do projeto VLSI registrou mais de mil patentes conjuntas entre 1976 e 1980 em equipamentos de litografia ótica, deposição química e inspeção de máscaras.\n"
                "2. Em fabricação de semicondutores, o custo marginal por chip funcional varia inversamente à densidade de defeitos por centímetro quadrado de silício, segundo o modelo estatístico de rendimento de Poisson."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "yrSj6yjZ1Yw",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "cm_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## A Arquitetura dos Agentes Autônomos\n\n"
                "A transição da inteligência artificial contemporânea é marcada pela superação do modelo estático de conversação, onde grandes modelos de linguagem funcionam como oráculos passivos que exigem intervenção humana contínua. A introdução de capacidades agênticas transforma esses sistemas em entidades capazes de formular planos, acionar interfaces de programação de aplicações e executar sequências prolongadas de ações digitais.\n\n"
                "Esse deslocamento arquitetural altera fundamentalmente a interação entre humanos e sistemas computacionais, delegando não apenas a síntese textual, mas o encadeamento completo de decisões intermediárias e correções de rota em ambientes dinâmicos."
            ),
            "candidate_text": (
                "## O Ciclo de Controle em Sistemas Agênticos Autônomos\n\n"
                "Um agente autônomo baseado em modelos de linguagem define-se como um sistema em malha fechada que alterna raciocínio linguístico, seleção estruturada de ferramentas e atualização de estado externo até atingir critério de parada; o conceito perde validade prática quando o ambiente carece de sinais verificáveis de estado ou quando ações são irreversíveis sem confirmação humana. O ciclo executivo desdobra-se em etapas causais explícitas: o planejador converte a meta em subobjetivos; o seletor de ferramentas serializa chamadas tipadas (APIs, bancos de dados ou shell); o ambiente retorna observações que reingressam no contexto; por último, o avaliador decide entre prosseguir, corrigir parâmetros ou encerrar a rotina.\n\n"
                "Tal arquitetura assume tacitamente que a latência e a probabilidade de erro por passo permanecem baixas o bastante para evitar divergência exponencial em horizontes longos (com erro composto dado por $1 - p^n$ em $n$ etapas dependentes), gerando como efeito colateral de segunda ordem a necessidade de guardrails determinísticos e orçamentos estritos de execução. Engenheiros de confiabilidade contrastam arquiteturas de planejamento prévio rígido com ciclos reativos curtos, verificáveis por taxas de sucesso em tarefas multi-etapa sob injeção de falhas.\n\n"
                "### Extra Info\n\n"
                "1. No padrão arquitetural ReAct (Reasoning and Acting), traços explícitos de pensamento intercalam-se às invocações de ferramentas para ancorar decisões intermediárias em observações reais do ambiente e reduzir alucinação de parâmetros.\n"
                "2. Ambientes com efeitos colaterais externos adotam o padrão de idempotência ou confirmação em duas fases (dry-run seguido de commit) para impedir que loops de retentativa dupliquem transações financeiras ou mutações destrutivas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "V04bm-3d6EQ",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "cm_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Gênese do Coronelismo e a Economia da Fraqueza\n\n"
                "A arquitetura do poder político no Brasil contemporâneo encontra suas raízes mais profundas na desagregação do Império e na consolidação da Primeira República. Ao contrário da leitura ingênua que enxerga o coronelismo como manifestação de força estatal absoluta no interior, a análise histórica demonstra que o fenômeno nasceu precisamente da incapacidade financeira e administrativa da União e dos governos estaduais.\n\n"
                "Sem recursos fiscais para sustentar burocracias locais, o poder central terceirizou o policiamento, a justiça de paz e a arrecadação aos grandes proprietários rurais, criando o sistema de compromisso no qual votos do curral eleitoral financiavam obras e nomeações em escala regional."
            ),
            "candidate_text": (
                "## A Persistência do Poder dos Coronéis Regionais\n\n"
                "O coronelismo caracteriza-se pelo domínio político exercido pelos coronéis sobre os municípios rurais, fenômeno no qual os chefes locais controlam as populações porque concentram autoridade tradicional e prestígio hereditário. Em virtude desse ascendente absoluto sobre os eleitores do interior, as oligarquias garantiam vitórias eleitorais constantes e consolidavam sua hegemonia nas assembleias estaduais.\n\n"
                "Sob o prisma histórico de longa duração, a concentração fundiária colonial preparou o terreno para a política dos governadores na Primeira República, sendo a influência regional identificável na continuidade de sobrenomes políticos nas casas legislativas.\n\n"
                "### Extra Info\n\n"
                "1. A obra clássica Coronelismo, Enxada e Voto, publicada por Victor Nunes Leal em 1949, sistematizou a análise do poder local brasileiro durante a Primeira República.\n"
                "2. A política dos governadores foi articulada durante a presidência de Campos Sales (1898–1902) para alinhar bancadas estaduais no Congresso Nacional."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "conceptual_mechanical_decomposition",
            "difficulty": "typical",
            "expected_anomaly": "circular_definition_and_missing_fiscal_weakness_mechanism",
            "defect_location": "body",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "FAIL",
        },
    },
]
