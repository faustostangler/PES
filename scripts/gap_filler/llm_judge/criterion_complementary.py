"""Golden Set items for COMPLEMENTARY_SECTION_RIGOR criterion (7 items: 4 PASS, 3 FAIL).

Conforms to:
    - ADR-039: Progressive LLM-as-a-Judge Calibration Lifecycle (Stage 2 gap_filler)
    - ADR-028: Decoupling Fluid Prose and Socratic Gap Filling
    - SPEC-015: Quality Gates and Calibration Framework
"""

from __future__ import annotations

from typing import Any

ITEMS_COMPLEMENTARY: list[dict[str, Any]] = [
    # 1. Borderline Potential FP (FAIL) - Tautological complementary section paraphrasing body text
    {
        "id": "cs_01_borderline_fp",
        "input": {
            "raw_text": (
                "## O Reconhecimento da Independência do Brasil em 1825\n\n"
                "Portugal exigiu uma indenização de dois milhões de libras esterlinas para reconhecer a independência do Brasil. "
                "O imperador Dom Pedro I assumiu as dívidas portuguesas contraídas junto a banqueiros britânicos em troca do "
                "tratado bilateral mediado pelo diplomata Charles Stuart."
            ),
            "candidate_text": (
                "## A Soberania Negociada: A Dívida de Reconhecimento da Independência em 1825\n\n"
                "A formalização diplomática da independência brasileira perante as cortes europeias exigiu a celebração do "
                "Tratado de Paz e Aliança em agosto de 1825, mediado pelo enviado britânico **Charles Stuart**. O governo de "
                "**Dom Pedro I** comprometeu-se a indenizar a coroa de Dom João VI em dois milhões de libras esterlinas, "
                "inaugurando a dependência financeira do jovem império perante o mercado de capitais londrino.\n\n"
                "A estruturação da transação financeira envolveu a assunção direta de um empréstimo de um milhão e quatrocentas mil "
                "libras que Portugal havia contraído em Londres em 1823, transferindo a hipoteca fiscal para a alfândega do Rio de Janeiro. "
                "A diplomacia de George Canning subordinou a emancipação política da antiga colônia à preservação das vantagens tarifárias "
                "concedidas aos produtos manufaturados britânicos pelo tratado de 1810.\n\n"
                "Essa negociação consagrou a inserção subordinada da economia agroexportadora brasileira na divisão internacional do trabalho, "
                "comprometendo os balanços do Tesouro Nacional pelas décadas subsequentes.\n\n"
                "## Informações Complementares\n\n"
                "1. Dom Pedro I concordou em pagar uma indenização de dois milhões de libras para que Portugal reconhecesse a independência "
                "do Brasil, conforme estipulado no tratado bilateral assinado com a coroa portuguesa.\n\n"
                "2. O diplomata britânico Charles Stuart atuou como mediador no tratado de paz de 1825, no qual o Brasil assumiu compromissos "
                "financeiros com banqueiros de Londres para compensar a corte de Lisboa."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "complementary_substance",
            "difficulty": "borderline",
            "expected_anomaly": "tautological_repetition_of_body_text_in_complementary_section",
            "defect_location": "complementary_section_items_1_and_2",
            "video_id": "ef2l-YG3Bto",
            "target_verdict": "FAIL",
        },
    },
    # 2. Borderline Potential FN (PASS) - Substantive treaty clauses, sterling conversions, and secret conventions
    {
        "id": "cs_02_borderline_fn",
        "input": {
            "raw_text": (
                "## O Reconhecimento da Independência do Brasil em 1825\n\n"
                "Portugal exigiu uma indenização de dois milhões de libras esterlinas para reconhecer a independência do Brasil. "
                "O imperador Dom Pedro I assumiu as dívidas portuguesas contraídas junto a banqueiros britânicos em troca do "
                "tratado bilateral mediado pelo diplomata Charles Stuart."
            ),
            "candidate_text": (
                "## A Soberania Negociada: A Dívida de Reconhecimento da Independência em 1825\n\n"
                "A formalização diplomática da independência brasileira perante as cortes europeias exigiu a celebração do "
                "Tratado de Paz e Aliança em agosto de 1825, mediado pelo enviado britânico **Charles Stuart**. O governo de "
                "**Dom Pedro I** comprometeu-se a indenizar a coroa de Dom João VI em dois milhões de libras esterlinas, "
                "inaugurando a dependência financeira do jovem império perante o mercado de capitais londrino.\n\n"
                "A estruturação da transação financeira envolveu a assunção direta de um empréstimo de um milhão e quatrocentas mil "
                "libras que Portugal havia contraído em Londres em 1823, transferindo a hipoteca fiscal para a alfândega do Rio de Janeiro. "
                "A diplomacia de George Canning subordinou a emancipação política da antiga colônia à preservação das vantagens tarifárias "
                "concedidas aos produtos manufaturados britânicos pelo tratado de 1810.\n\n"
                "Essa negociação consagrou a inserção subordinada da economia agroexportadora brasileira na divisão internacional do trabalho, "
                "comprometendo os balanços do Tesouro Nacional pelas décadas subsequentes.\n\n"
                "## Informações Complementares\n\n"
                "1. A Convenção Secreta de 29 de agosto de 1825 discriminou o pagamento parcelado: além do saldo da dívida portuguesa com a "
                "banca Rothschild, o Império pagou 600.000 libras em compensação pela apreensão de propriedades privadas portuguesas.\n\n"
                "2. A taxa de juros do empréstimo de reconhecimento emitido pela Casa Rothschild e Baring Brothers alcançou 5% ao ano "
                "com deságio de 15% sobre o valor nominal, exigindo caução expressa sobre as receitas alfandegárias de Salvador e Santos."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "complementary_substance",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ef2l-YG3Bto",
            "target_verdict": "PASS",
        },
    },
    # 3. Easy PASS - Substantive empirical, legal, and regulatory complementary data on notarial cartels
    {
        "id": "cs_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Receita dos Cartórios Extrajudiciais no Brasil\n\n"
                "Levantamentos oficiais do Conselho Nacional de Justiça apontam que os cartórios no Brasil arrecadam dezenas "
                "de bilhões de reais por ano. Cartórios de registro de imóveis e protesto concentram as maiores fatias da renda "
                "gerada por atos notariais em capitais como São Paulo e Rio de Janeiro."
            ),
            "candidate_text": (
                "## A Concentração de Rendimentos nas Serventias Extrajudiciais Brasileiras\n\n"
                "Os dados consolidados do programa Justiça Aberta revelam a magnitude econômica do setor notarial e registral no Brasil. "
                "Em 2023, as cerca de treze mil serventias extrajudiciais em atividade registraram faturamento bruto superior a vinte "
                "e seis bilhões de reais, operando sob regime de custos fixos reduzidos e margens operacionais elevadas garantidas "
                "por tabelas estaduais de custas compulsórias.\n\n"
                "Essa concentração reproduz assimetrias estruturais severas. Menos de cinco por cento dos cartórios, localizados "
                "majoritariamente nas capitais do Centro-Sul, concentram mais da metade do faturamento de todo o setor, enquanto serventias "
                "de registro civil em municípios do semiárido dependem de fundos estaduais compensatórios de ressarcimento por atos gratuitos.\n\n"
                "A manutenção de delegações hereditárias anteriores à exigência do concurso público constitucional perpetua dinastias "
                "locais que combinam influência judiciária e poder financeiro no controle do território.\n\n"
                "## Informações Complementares\n\n"
                "1. A Lei Federal 8.935/1994 (Lei dos Notários e Registradores) regulamentou o artigo 236 da Constituição Federal, "
                "definindo a fiscalização dos atos judiciais pelas corregedorias estaduais de justiça e os critérios para vacância.\n\n"
                "2. O Provimento 74/2018 da Corregedoria Nacional de Justiça estabeleceu padrões mínimos de segurança da informação e "
                "continuidade operacional para serventias com arrecadação semestral superior a duzentos mil reais."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "complementary_substance",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "PASS",
        },
    },
    # 4. Easy FAIL - Superficial trivia and biographical noise in complementary section
    {
        "id": "cs_04_easy_fail",
        "input": {
            "raw_text": (
                "## O Protocolo MCP para Conexão de Modelos e Fontes de Dados\n\n"
                "O Model Context Protocol (MCP) introduz um padrão aberto para integrar assistentes de inteligência artificial "
                "a ferramentas e servidores de contexto. A arquitetura cliente-servidor padroniza a descoberta dinâmica de ferramentas "
                "e a execução controlada de consultas externas."
            ),
            "candidate_text": (
                "## A Arquitetura Aberta do Model Context Protocol na Engenharia de Agentes\n\n"
                "A proliferação de integrações proprietárias entre grandes modelos de linguagem e ferramentas corporativas gerou um "
                "cenário de fragmentação tecnológica análogo aos primórdios da internet pré-HTTP. O padrão **Model Context Protocol** "
                "(**MCP**), introduzido pela Anthropic em novembro de 2024, propõe um protocolo unificado baseado em JSON-RPC 2.0 "
                "para desacoplar a camada de inferência dos conectores de infraestrutura.\n\n"
                "Na especificação do protocolo, o modelo atua como cliente solicitante, enquanto servidores locais ou remotos expõem "
                "três primitivas essenciais: Prompts estruturados, Recursos de leitura e Ferramentas executáveis com tipagem estrita "
                "validada por esquemas JSON. Essa padronização permite que plataformas como o Claude Desktop ou editores de código "
                "acessem bases de dados locais e repositórios sem código customizado.\n\n"
                "O protocolo reduz a complexidade de manutenção em sistemas multiagentes, substituindo integrações monolíticas "
                "por ecossistemas interoperáveis de utilitários plug-and-play.\n\n"
                "## Informações Complementares\n\n"
                "1. A Anthropic é uma empresa fundada por ex-funcionários da OpenAI que gostam muito de gatos e organizam conferências "
                "de tecnologia bastante interessantes em San Francisco nos Estados Unidos.\n\n"
                "2. Protocolos de computador são muito importantes para conectar aparelhos e softwares porque sem eles a tecnologia "
                "não funcionaria direito e as pessoas teriam muitas dificuldades para trabalhar com inteligência artificial no dia a dia."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "complementary_substance",
            "difficulty": "easy",
            "expected_anomaly": "superficial_trivial_noise_in_complementary_section",
            "defect_location": "complementary_section_items_1_and_2",
            "video_id": "efRIrLXoOVA",
            "target_verdict": "FAIL",
        },
    },
    # 5. Typical PASS 1 - Technical specifications, tokenizer constants, and mathematical context
    {
        "id": "cs_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## O Processamento de Texto em Tokenizers de Modelos de Linguagem\n\n"
                "Antes de processar texto, redes neurais transformam sequências de caracteres em números inteiros através do "
                "algoritmo Byte Pair Encoding (BPE). O tamanho do vocabulário do tokenizer define o equilíbrio entre granularidade "
                "semântica e eficiência computacional na matriz de embeddings."
            ),
            "candidate_text": (
                "## A Tokenização Subvocabular e a Compressão Informacional em Redes Neurais\n\n"
                "A conversão de cadeias arbitrárias de caracteres em representações vetoriais densas constitui o gargalo inicial "
                "na arquitetura dos transformadores generativos. Modelos modernos utilizam variações do algoritmo **Byte Pair Encoding** "
                "(**BPE**), operando diretamente sobre fluxos de bytes codificados em UTF-8 para garantir completude lexical sem "
                "dependência de tabelas de palavras fora do vocabulário (tokens desconhecidos).\n\n"
                "O processo de construção do vocabulário itera sobre frequências de pares de bytes consecutivos, agregando combinações "
                "recorrentes em unidades simbólicas unificadas. Esse mecanismo permite que palavras comuns sejam codificadas em um "
                "único token numérico, enquanto termos técnicos raros ou neologismos são decompostos em subunidades morfológicas menores.\n\n"
                "A dimensão do vocabulário condiciona diretamente o consumo de memória na camada de entrada e na cabeça de projeção softmax "
                "final, onde cada token adicional expande os parâmetros da matriz linear em proporção direta à dimensão latente da rede.\n\n"
                "## Informações Complementares\n\n"
                "1. O tokenizer **tiktoken**, desenvolvido pela OpenAI para a família GPT-4, adota vocabulário de aproximadamente "
                "100.277 tokens (cl100k_base), empregando expressões regulares para isolar pontuações antes da fusão subvocabular.\n\n"
                "2. O algoritmo BPE foi concebido originalmente em 1994 por Philip Gage como técnica de compressão de dados, "
                "sendo adaptado para processamento de linguagem natural por Rico Sennrich, Barry Haddow e Alexandra Birch em 2016."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "complementary_substance",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "EWvNQjAaOHw",
            "target_verdict": "PASS",
        },
    },
    # 6. Typical PASS 2 - Substantive regulatory and statutory frameworks for international financial sanctions
    {
        "id": "cs_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## Articulações de Sanções Internacionais contra Membros do STF\n\n"
                "Grupos de oposição articulam junto a congressistas americanos a aplicação de sanções previstas na Lei Magnitsky "
                "contra ministros do Supremo Tribunal Federal. O mecanismo prevê restrições de visto e congelamento de ativos sob "
                "jurisdição do Departamento do Tesouro dos Estados Unidos para autoridades acusadas de violações a direitos humanos."
            ),
            "candidate_text": (
                "## A Extraterritorialidade Financeira e a Aplicação da Lei Magnitsky ao Judiciário Brasileiro\n\n"
                "A mobilização diplomática e parlamentar para submeter magistrados do **Supremo Tribunal Federal** a sanções sob o "
                "regime da **Global Magnitsky Act** ilustra a crescente internacionalização dos conflitos institucionais brasileiros. "
                "No plano material, a eficácia desse instrumento repousa na centralidade hegemônica do dólar e da rede interbancária "
                "internacional, na qual qualquer bloqueio determinado pelo Escritório de Controle de Ativos Estrangeiros (**OFAC**) "
                "impede transações com cartões de crédito globais, investimentos em custódia e serviços de infraestrutura em nuvem.\n\n"
                "A viabilidade de tais penalidades transcende a retórica política interna, dependendo da formulação de dossiês probatórios "
                "validados pelas comissões de relações exteriores do Senado e da Câmara dos Representantes dos Estados Unidos. As alegações "
                "de censura prévia e inobservância do devido processo legal nos inquéritos originários do tribunal são enquadradas sob as "
                "cláusulas de violação grosseira de direitos civis internacionalmente reconhecidos.\n\n"
                "Essa pressão transnacional converte restrições administrativas unilaterais em alavanca de dissuasão institucional, "
                "transferindo a arbitragem de disputas domésticas para a esfera geopolítica de Washington.\n\n"
                "## Informações Complementares\n\n"
                "1. A **Global Magnitsky Human Rights Accountability Act** foi aprovada pelo Congresso dos Estados Unidos como parte do "
                "National Defense Authorization Act de 2017 (Public Law 114-328), autorizando a imposição de sanções e revogação de vistos.\n\n"
                "2. A inclusão formal na lista de Cidadãos Especialmente Designados e Pessoas Bloqueadas (lista SDN) da **OFAC** impõe o "
                "bloqueio compulsório de ativos e veda pessoas e corporações norte-americanas de celebrar transações com os sancionados."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "complementary_substance",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "R8-dCSHLItE",
            "target_verdict": "PASS",
        },
    },
    # 7. Typical FAIL - Vacuous and generic definitions with zero informational density
    {
        "id": "cs_07_typical_fail",
        "input": {
            "raw_text": (
                "## Concorrência e Gargalos em Bancos Relacionais sob Alta Carga\n\n"
                "Em testes de estresse com milhares de requisições simultâneas por segundo, o banco de dados PostgreSQL "
                "apresenta degradação severa de latência quando as conexões não são limitadas. "
                "O esgotamento de recursos decorre da contenção de bloqueios em linhas concorrentes e do custo de "
                "context switching entre múltiplos processos no sistema operacional."
            ),
            "candidate_text": (
                "## O Esgotamento de Recursos em Bancos Relacionais sob Concorrência Extrema\n\n"
                "Em cenários de estresse computacional caracterizados por taxas elevadas de transações simultâneas, "
                "a arquitetura do **PostgreSQL** manifesta variações desproporcionais na latência percebida pelos clientes. "
                "A saturação de conexões sem pooling adequado impõe um ônus operacional que degrada o rendimento global "
                "da aplicação sob teste de estresse na infraestrutura em contêineres **Docker**.\n\n"
                "A contenção de bloqueios no motor de controle de concorrência multiversão (**MVCC**) gera filas de espera "
                "em tabelas centrais de escrituração, enquanto a sobrecarga do agendador do Linux despende ciclos excessivos de "
                "CPU na alternância de contexto entre centenas de processos bifurcados.\n\n"
                "A estabilidade do cluster exige portanto a limitação estrita de clientes ativos e a otimização de planos de execução.\n\n"
                "## Informações Complementares\n\n"
                "1. O PostgreSQL é um banco de dados relacional muito popular e amplamente utilizado por empresas de tecnologia no mundo "
                "inteiro para armazenar dados em tabelas de computador de forma organizada e segura.\n\n"
                "2. O Linux é um sistema operacional de código aberto bastante conhecido que muitos programadores utilizam para rodar "
                "servidores de internet e programas de computador em data centers pelo planeta."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "complementary_substance",
            "difficulty": "typical",
            "expected_anomaly": "vacuous_platitudinous_definitions_without_technical_density",
            "defect_location": "complementary_section_items_1_and_2",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
]
