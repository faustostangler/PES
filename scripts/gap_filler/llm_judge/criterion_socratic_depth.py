"""Golden Set items for SOCRATIC_EPISTEMIC_DEPTH criterion (7 items: 4 PASS, 3 FAIL).

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - ADR-028: Decoupling Fluid Prose and Socratic Gap Filling
    - SPEC-015: Quality Gates and Calibration Framework
"""

from __future__ import annotations

from typing import Any

ITEMS_SOCRATIC_DEPTH: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Erudite technical paraphrase that omits intermediate causal mechanisms
    {
        "id": "se_01_borderline_fp",
        "input": {
            "raw_text": (
                "## Concorrência e Gargalos em Bancos Relacionais sob Alta Carga\n\n"
                "Em testes de estresse com milhares de requisições simultâneas por segundo, o banco de dados **PostgreSQL** "
                "frequentemente apresenta degradação severa de latência quando as conexões não são limitadas. "
                "O esgotamento de recursos decorre da contenção de bloqueios em linhas concorrentes e do custo de "
                "context switching entre múltiplos processos no sistema operacional."
            ),
            "candidate_text": (
                "## O Esgotamento de Recursos em Bancos Relacionais sob Concorrência Extrema\n\n"
                "Em cenários de estresse computacional caracterizados por taxas elevadas de transações simultâneas, "
                "a arquitetura do **PostgreSQL** manifesta variações desproporcionais na latência percebida pelos clientes. "
                "A saturação de conexões sem pooling adequado impõe um ônus operacional que degrada o rendimento global "
                "da aplicação sob teste de estresse na infraestrutura em contêineres **Docker**.\n\n"
                "A degradação manifesta-se através de disputas intensas por recursos compartilhados, onde diferentes "
                "processos disputam o acesso aos mesmos registros de tabelas financeiras. A sobrecarga de gerenciar "
                "dezenas de processos paralelos força o núcleo do sistema operacional a despender ciclos valiosos de "
                "processamento em trocas de contexto em vez de executar consultas analíticas úteis.\n\n"
                "Essas perturbações confirmam a necessidade de dimensionar corretamente o agrupamento de conexões "
                "e revisar a modelagem de consultas para preservar a estabilidade da camada de persistência.\n\n"
                "## Informações Complementares\n\n"
                "1. O gerenciador de conexões **PgBouncer**, amplamente utilizado em ambientes de produção com PostgreSQL, "
                "opera em três modos distintos de agrupamento: sessão, transação e instrução, mitigando o custo de criação de processos.\n\n"
                "2. O comando **EXPLAIN ANALYZE** do PostgreSQL executa a consulta e retorna o plano de execução real juntamente "
                "com os custos de nós de varredura sequencial (Seq Scan) e tempo de execução consumido em buffers compartilhados."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "socratic_epistemic_depth",
            "difficulty": "borderline",
            "expected_anomaly": "explanatory_vacuum_missing_mvcc_intermediate_mechanisms",
            "defect_location": "paragraph_2",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Rigorous multi-dimensional audit of LLM inference mechanics
    {
        "id": "se_02_borderline_fn",
        "input": {
            "raw_text": (
                "## O Funcionamento Cognitivo dos Modelos de Linguagem\n\n"
                "Modelos de linguagem como o **ChatGPT** operam fundamentalmente como sistemas de predição estatística "
                "de próximo token treinados em extensos corpora textuais. Usuários frequentemente atribuem capacidades "
                "de raciocínio autônomo a essas ferramentas, ignorando que as respostas decorrem de padrões probabilísticos "
                "ajustados por aprendizagem por reforço com feedback humano."
            ),
            "candidate_text": (
                "## A Natureza Probabilística e os Limites Epistêmicos dos Modelos de Linguagem\n\n"
                "A interpretação do comportamento de modelos de linguagem de grande porte (**LLM**) oscila entre o fascínio "
                "pela fluência sintática e o equívoco de atribuir intencionalidade consciente a uma arquitetura puramente estocástica. "
                "Na formulação conceituada por **Andrej Karpathy**, o modelo base funciona como um compressor de padrões que estima "
                "a distribuição condicional de probabilidades sobre um vocabulário discreto de tokens através de camadas de auto-atenção.\n\n"
                "A transição entre o modelo pré-treinado e o assistente conversacional não introduz raciocínio dedutivo novo, "
                "mas restringe o espaço amostral mediante ajuste fino supervisionado (**SFT**) e aprendizagem por reforço com feedback "
                "humano (**RLHF**). Esse processo mascara o mecanismo de predição estocástica com uma persona prestativa, gerando "
                "alucinações factuais exatamente nos domínios em que a densidade de dados estatísticos é insuficiente.\n\n"
                "Operacionalmente, a memória de trabalho do sistema limita-se ao buffer da **KV-cache** contido na janela de contexto ativo. "
                "Quando o usuário delega tarefas sem scaffolding externo, o modelo opera no equivalente computacional do Sistema 1 "
                "(resposta instintiva rápida descrita por **Daniel Kahneman**), falhando em problemas que requerem verificação algorítmica deliberada.\n\n"
                "## Informações Complementares\n\n"
                "1. A técnica de **Decodificação Especulativa** (Speculative Decoding) utiliza um modelo menor e mais veloz para gerar "
                "candidatos a tokens subsequentes que são validados em paralelo pelo modelo principal, acelerando a taxa de geração sem perda de fidelidade.\n\n"
                "2. O artigo seminal **Attention Is All You Need**, publicado em 2017 por pesquisadores do **Google Brain**, "
                "introduziu a arquitetura Transformer baseada no mecanismo de produto escalar escalado (scaled dot-product attention)."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "socratic_epistemic_depth",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "EWvNQjAaOHw",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Public Choice theory applied to Brazilian electoral corruption
    {
        "id": "se_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Recorrência da Corrupção Política nas Eleições Brasileiras\n\n"
                "A persistência de parlamentares processados ou condenados por corrupção em sucessivas legislaturas "
                "é frequentemente atribuída à ignorância ou alienação moral do eleitorado. No entanto, a análise econômica "
                "da política demonstra que essa dinâmica decorre de estruturas de incentivos e das regras eleitorais."
            ),
            "candidate_text": (
                "## A Economia Política do Voto e a Teoria da Escolha Pública\n\n"
                "A explicação moralista que reduz a reeleição sistemática de agentes políticos desonestos a uma suposta "
                "falha ética do eleitorado negligencia os postulados fundamentais da **Teoria da Escolha Pública** formulados "
                "por **James M. Buchanan** e **Gordon Tullock**. Os agentes políticos atuam como maximizadores de utilidade pessoal, "
                "buscando poder, prestígio e recursos sob a lógica dos incentivos institucionais vigentes.\n\n"
                "O conceito de **Ignorância Racional**, delineado por **Anthony Downs** em 1957, elucida o cálculo do cidadão comum: "
                "como a probabilidade de um voto individual alterar o resultado eleitoral é próxima de zero e o custo de auditar "
                "votações e prontuários judiciais é elevado, o eleitor racionalmente abstém-se de gastar tempo investigando seus candidatos. "
                "Ao mesmo tempo, coalizões de interesses organizados operam com a lógica de benefícios concentrados pagos por custos difusos.\n\n"
                "Um subsídio ou emenda parlamentar de cinquenta milhões de reais financiada por milhões de contribuintes dilui o custo "
                "em poucos centavos por cidadão, enquanto o benefício bilionário canalizado para empreiteiras e sindicatos locais "
                "fornece o capital concentrado e a militância necessários para assegurar a recondução eleitoral do grupo político.\n\n"
                "## Informações Complementares\n\n"
                "1. O economista **Mancur Olson**, em sua obra **A Lógica da Ação Coletiva** publicada em 1965, demonstrou que pequenos "
                "grupos com interesses homogêneos possuem enorme facilidade de organização e lobby frente a maiorias desorganizadas.\n\n"
                "2. O **Fundo Especial de Financiamento de Campanha** (Fundo Eleitoral), instituído pela **Lei 13.487/2017**, "
                "alocou bilhões de reais de recursos públicos aos diretórios partidários nacionais, reforçando a blindagem das cúpulas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "socratic_epistemic_depth",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "7tZdt2UQtbg",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Superficial paraphrase with zero epistemic expansion or mechanistic explanation
    {
        "id": "se_04_easy_fail",
        "input": {
            "raw_text": (
                "## A Decisão do STF sobre a Lei de Impeachment\n\n"
                "O ministro **Gilmar Mendes** suspendeu trechos da **Lei 1.079/1950** que permitiam a qualquer cidadão "
                "apresentar pedidos de impeachment contra membros do **Supremo Tribunal Federal**. A liminar transferiu "
                "a exclusividade dessa iniciativa para a **Procuradoria-Geral da República** e estabeleceu quórum qualificado "
                "de dois terços para o Senado admitir a denúncia."
            ),
            "candidate_text": (
                "## O Julgamento da Lei de Impeachment no Supremo Tribunal Federal\n\n"
                "O ministro **Gilmar Mendes** determinou a suspensão de dispositivos da **Lei 1.079/1950** que autorizavam "
                "qualquer pessoa comum a protocolar representações de impeachment contra os integrantes da suprema corte. "
                "A decisão judicial concentrou a prerrogativa nas mãos da **Procuradoria-Geral da República**.\n\n"
                "Além dessa restrição de iniciativa, a medida estabeleceu que o **Senado Federal** precisa de dois terços dos "
                "votos para aceitar qualquer denúncia desse tipo, dificultando bastante os processos de impeachment de ministros.\n\n"
                "A medida causou polêmica na comunidade jurídica porque alterou as regras que estavam em vigor há décadas.\n\n"
                "## Informações Complementares\n\n"
                "1. A **Lei 1.079** foi sancionada em 1950 durante o mandato do presidente Eurico Gaspar Dutra.\n\n"
                "2. O Senado Federal é composto por 81 senadores que representam os estados da federação brasileira."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "socratic_epistemic_depth",
            "difficulty": "easy",
            "expected_anomaly": "near_verbatim_paraphrase_without_epistemic_expansion",
            "defect_location": "paragraph_1_and_2",
            "video_id": "z82sKS_xj28",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Japanese semiconductor decline intermediate industrial mechanisms
    {
        "id": "se_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A Crise Estrutural da Indústria Eletrônica Japonesa\n\n"
                "A hegemonia do Japão no mercado de chips colapsou na década de 1990 devido à incapacidade dos conglomerados "
                "locais de acompanhar a transição do segmento de memórias padronizadas para microprocessadores e sistemas móveis. "
                "A ascensão do modelo fabless fragmentou a cadeia global de suprimentos."
            ),
            "candidate_text": (
                "## A Desconstrução do Modelo Vertical Integrado na Manufatura de Circuitos\n\n"
                "A derrocada dos conglomerados japoneses (**keiretsus**) no mercado de semicondutores após 1990 constitui um caso clássico "
                "do dilema da inovação analisado sob a perspectiva dos custos de coordenação. Corporações como **Toshiba**, **NEC** e **Fujitsu** "
                "estruturavam-se como fabricantes de dispositivos integrados (**IDM**), mantendo sob o mesmo teto corporativo o design "
                "de circuitos, as plantas de litografia e a montagem de produtos finais de consumo.\n\n"
                "Esse modelo alcançou produtividade extraordinária enquanto a vantagem competitiva esteve assentada em memórias **DRAM**, "
                "onde melhorias incrementais na pureza do silício e taxas de defeito por wafer garantiam margens expressivas. Contudo, "
                "a introdução da arquitetura **PC** aberta pela **IBM** deslocou o núcleo de valor do silício da memória física para os "
                "microprocessadores lógicos de alta velocidade dominados pela **Intel**, que exigiam ciclos rápidos de iteração de design.\n\n"
                "A ruptura definitiva consolidou-se com o modelo de fundição pura concebido por **Morris Chang** na **TSMC** em 1987. "
                "Ao desacoplar o projeto lógico da pesada depreciação de capital das salas limpas (cleanrooms), empresas americanas "
                "sem fábrica própria (**fabless**) puderam escalar projetos arrojados sem carregar o imobilizado de fábricas bilionárias, "
                "tornando obsoleta a rigidez de alocação de capital dos consórcios fabris japoneses.\n\n"
                "## Informações Complementares\n\n"
                "1. A **Lei de Moore**, formulada em 1965 por **Gordon Moore**, postulou a duplicação periódica do número de transistores "
                "em circuitos integrados a cada dois anos, impondo uma corrida de despesas de capital (CapEx) insustentável para players não especializados.\n\n"
                "2. O projeto cooperativo de semicondutores **VLSI** (Very Large Scale Integration), coordenado pelo **MITI** entre 1976 e 1980, "
                "uniu concorrentes japoneses para desenvolver a tecnologia básica de litografia que garantiu o domínio transitório de DRAM nos anos 1980."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "socratic_epistemic_depth",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "yrSj6yjZ1Yw",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Multi-agent AI systems game-theoretic intermediate state transitions
    {
        "id": "se_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## A Coordenação Autônoma em Sistemas Multiagente de IA\n\n"
                "Quando múltiplos agentes de inteligência artificial interagem em ambientes compartilhados sem controle centralizado, "
                "comportamentos emergentes imprevisíveis surgem rapidamente. A dinâmica pode convergir para cooperação estável "
                "ou para colapsos sistêmicos provocados por assimetria de informação."
            ),
            "candidate_text": (
                "## Dinâmicas Emergentes e Teoria dos Jogos em Ecossistemas Multiagente\n\n"
                "A transição de modelos isolados para enxames de agentes autônomos transforma o problema de alinhamento em um desafio "
                "de governança de sistemas complexos. Na formulação investigada pelos pesquisadores da **Google DeepMind**, cada agente "
                "atua como um tomador de decisão algorítmico munido de funções de utilidade e políticas de execução próprias, "
                "interagindo através de barramentos de mensageria assíncrona.\n\n"
                "O colapso da cooperação ocorre tipicamente por dilemas de coordenação análogos à **Tragédia dos Comuns**: na ausência "
                "de mecanismos de verificação e penalização com custos de transação nulos, agentes individuais maximizam suas chamadas "
                "a APIs e saturação de largura de banda, provocando starvation dos agentes vizinhos e degradação em cascata do sistema.\n\n"
                "A mitigação dessa entropia não decorre de prompts apelativos, mas da imposição de equilíbrios de **Nash** mediante "
                "incentivos estruturais, como orçamentos criptográficos de cota (token-budgeting) e protocolos de reputação rastreáveis. "
                "Esse arranjo assegura que o vetor de recompensa do agente coincida matematicamente com a estabilidade de longo prazo do ecossistema.\n\n"
                "## Informações Complementares\n\n"
                "1. O conceito de **Equilíbrio Correlacionado**, introduzido pelo matemático **Robert Aumann** em 1974, amplia o equilíbrio "
                "de Nash ao permitir que os jogadores coordenem suas escolhas a partir de sinais públicos gerados por um mediador independente.\n\n"
                "2. O framework de avaliação **AutoGPT**, lançado em março de 2023 por **Toran Bruce Richards**, evidenciou as limitações "
                "de loops autônomos ingênuos de reflexão, que entravam em ciclos recursivos infinitos sem atingir o estado terminal da tarefa."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "socratic_epistemic_depth",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "V04bm-3d6EQ",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Explanatory vacuum jumping from oligarchy presence to state capture without mechanisms
    {
        "id": "se_07_typical_fail",
        "input": {
            "raw_text": (
                "## A Perpetuação de Clãs Políticos no Brasil Contemporâneo\n\n"
                "Famílias tradicionais como os **Sarney** no Maranhão, os **Barbalho** no Pará e os **Calheiros** em Alagoas "
                "mantêm o controle político de seus estados há várias gerações. Esse fenômeno sobreviveu à transição democrática "
                "e se consolidou através da ocupação de postos-chave nos poderes Executivo e Legislativo."
            ),
            "candidate_text": (
                "## As Dinâmicas Hereditárias do Poder Político Regional\n\n"
                "A longevidade das dinastias políticas estaduais no Brasil representa um dos traços mais marcantes da federação "
                "republicana. A preservação do poder hegemônico por clãs familiares nas regiões Norte e Nordeste estende-se por "
                "mais de quatro décadas sem descontinuidade substantiva após a promulgação da **Constituição de 1988**.\n\n"
                "Essas famílias simplesmente controlam todo o aparelho de Estado porque a população local aceita passivamente "
                "sua dominação e vota regularmente nos herdeiros dos clãs, fazendo com que o poder passe de pai para filho de forma "
                "automática sem qualquer tipo de resistência social ou disputa de poder.\n\n"
                "Dessa maneira, a política brasileira permanece refém dessas linhagens que governam os estados e determinam os "
                "rumos da nação sem que os mecanismos democráticos consigam produzir qualquer tipo de renovação das lideranças.\n\n"
                "## Informações Complementares\n\n"
                "1. **José Sarney**, eleito governador do Maranhão em 1965 pelo partido UDN, presidiu a República entre 1985 e 1990 "
                "e exerceu sucessivos mandatos como presidente do Senado Federal.\n\n"
                "2. **Jader Barbalho**, governador do Pará por dois mandatos e presidente do Senado em 2001, consolidou a influência "
                "de sua família, cujo filho **Helder Barbalho** foi eleito governador do estado em 2018 e reeleito em 2022."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "socratic_epistemic_depth",
            "difficulty": "typical",
            "expected_anomaly": "causal_vacuum_jumping_to_passive_domination_without_mechanisms",
            "defect_location": "paragraph_2",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "FAIL",
        },
    },
]
