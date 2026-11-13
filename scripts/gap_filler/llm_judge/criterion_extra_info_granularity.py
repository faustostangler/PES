"""Golden Dataset Items for Criterion 6: Extra Info Granularity (ei_01 to ei_07).

Evaluates the mandatory '### Extra Info' section: strict non-redundancy against
main body, numbered continuous paragraphs ('1. ', '2. ') with zero bullets,
and high-density tertiary technical/archival saturation specifics.
Orthogonal to all other 6 ADR-060 criteria.
"""

from __future__ import annotations

from typing import Any

ITEMS_EXTRA_INFO_GRANULARITY: list[dict[str, Any]] = [
    {
        "id": "ei_01_borderline_fp",
        "input": {
            "raw_text": (
                "## O Mito da Ruptura Pacífica e a Consolidação Imperial\n\n"
                "A narrativa tradicional de que a separação do Brasil ocorreu de forma puramente pacífica, mediante acordos conciliadores entre elites sem derramamento de sangue, constitui uma construção ideológica desmentida pela investigação histórica rigorosa. A consolidação do Império exigiu campanhas militares sangrentas na Bahia, no Piauí, no Maranhão e na Cisplatina para expulsar guarnições leais às Cortes de Lisboa.\n\n"
                "No plano diplomático, o reconhecimento formal da soberania brasileira por Portugal não derivou de mera benevolência dinástica, mas da mediação britânica concretizada no Tratado do Rio de Janeiro de 1825, que vinculou o reconhecimento jurídico ao pagamento de dois milhões de libras esterlinas a título de indenização à antiga metrópole."
            ),
            "candidate_text": (
                "## A Soberania Negociada: O Tratado de 1825\n\n"
                "O reconhecimento da independência brasileira por Portugal consumou-se por meio de conflitos provinciais na Bahia, Piauí, Maranhão e Cisplatina combinados à mediação britânica de Charles Stuart no Tratado do Rio de Janeiro de 1825-08-29. O tratado impôs ao Império do Brasil o pagamento de dois milhões de libras esterlinas como indenização à coroa portuguesa mediante assunção de passivo financeiro em Londres.\n\n"
                "Sob perspectiva de longa duração, a dependência comercial frente à Grã-Bretanha desde os tratados de 1810 condicionou os termos econômicos da emancipação, enquanto correntes historiográficas debatem o peso da ameaça republicana sul-americana frente à preservação das tarifas preferenciais britânicas, tese aferível pelos relatórios consulares do Foreign Office.\n\n"
                "### Extra Info\n\n"
                "1. O Tratado do Rio de Janeiro, assinado em 1825-08-29 sob mediação britânica de Charles Stuart, formalizou o reconhecimento da independência do Brasil por Portugal mediante indenização de dois milhões de libras esterlinas.\n"
                "2. A separação brasileira envolveu guerras provinciais na Bahia, no Piauí, no Maranhão e na Cisplatina para expulsar tropas fiéis às Cortes de Lisboa, contrariando a visão de transição puramente pacífica."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "extra_info_granularity",
            "difficulty": "borderline",
            "expected_anomaly": "tautological_repetition_of_body_text_in_extra_info",
            "defect_location": "extra_info",
            "video_id": "ef2l-YG3Bto",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "ei_02_borderline_fn",
        "input": {
            "raw_text": (
                "## O Mito da Ruptura Pacífica e a Consolidação Imperial\n\n"
                "A narrativa tradicional de que a separação do Brasil ocorreu de forma puramente pacífica, mediante acordos conciliadores entre elites sem derramamento de sangue, constitui uma construção ideológica desmentida pela investigação histórica rigorosa. A consolidação do Império exigiu campanhas militares sangrentas na Bahia, no Piauí, no Maranhão e na Cisplatina para expulsar guarnições leais às Cortes de Lisboa.\n\n"
                "No plano diplomático, o reconhecimento formal da soberania brasileira por Portugal não derivou de mera benevolência dinástica, mas da mediação britânica concretizada no Tratado do Rio de Janeiro de 1825, que vinculou o reconhecimento jurídico ao pagamento de dois milhões de libras esterlinas a título de indenização à antiga metrópole."
            ),
            "candidate_text": (
                "## A Soberania Negociada e o Circuito Financeiro de Londres\n\n"
                "O reconhecimento da emancipação política brasileira em 1825-08-29 consolidou a intersecção entre as campanhas militares provinciais de 1822–1824 e a arbitragem diplomática britânica sobre a sucessão atlântica. A vinculação jurídica entre soberania e assunção da dívida de dois milhões de libras inseriu o novo Império nos mercados de títulos de Londres, atendendo simultaneamente às exigências fiscais de Lisboa e ao interesse comercial britânico na preservação do mercado sul-americano.\n\n"
                "Correntes historiográficas contrastam se o endividamento decorreu primariamente da urgência de legitimidade dinástica de Dom Pedro I ou da condicionalidade imposta pelo Foreign Office para reconhecer o novo Estado; a preservação dos registros de subscrição permite testar o ágio imediato dos títulos em Londres.\n\n"
                "### Extra Info\n\n"
                "1. O empréstimo português de 1823 assumido pelo Brasil possuía valor nominal de 1.500.000 libras com cupom de cinco por cento ao ano (amortizado em trinta anos), complementado por saque adicional de 600.000 libras em letras do Tesouro contra os rendimentos alfandegários do Rio de Janeiro e de Salvador, sob comissão de subscrição à casa N. M. Rothschild & Sons.\n"
                "2. A Convenção Adicional Secreta de 1825-08-29 liquidou ainda reclamações privadas de súditos portugueses cujas propriedades e navios haviam sido sequestrados durante a guerra na Bahia e no Maranhão, elevando o desembolso efetivo acima da cifra pública do tratado principal."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "extra_info_granularity",
            "difficulty": "borderline",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "ef2l-YG3Bto",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ei_03_easy_pass",
        "input": {
            "raw_text": (
                "## A Mutação Institucional e a Adaptação dos Clãs\n\n"
                "Com a irrupção da Revolução de 1930 e a criação da Justiça Eleitoral em 1932, que instituiu o voto secreto, a infraestrutura material do coronelismo tradicional sofreu um abalo sísmico, mas a lógica subjacente adaptou-se aos novos meios de comunicação e regulação estatal. Grupos políticos regionais migraram do controle exclusivo do curral rural para a captura de concessões de rádio e televisão.\n\n"
                "Esse fenômeno, amplamente descrito na ciência política como coronelismo eletrônico, manteve a intermediação entre o eleitorado local e os recursos federais por meio de outorgas públicas distribuídas a parlamentares e governadores alinhados."
            ),
            "candidate_text": (
                "## O Coronelismo Eletrônico e a Captura de Outorgas de Radiodifusão\n\n"
                "A introdução do voto secreto pelo Código Eleitoral de 1932-02-24 e a urbanização acelerada do pós-1945 deslocaram o eixo de patronagem regional do controle direto de cédulas rurais para o domínio de canais locais de rádio e televisão. Mediante a concessão discricionária de frequências pelo Poder Executivo e sua posterior ratificação parlamentar, oligarquias estaduais passaram a controlar a visibilidade eleitoral e a agenda informacional em circunscrições distantes das grandes metrópoles, preservando a lógica de compromisso entre governadores e bancadas federais.\n\n"
                "Cientistas políticos divergem sobre se a expansão da internet após 2010 dissolveu a renda eleitoral dessas emissoras regionais ou apenas realocou a intermediação para redes de verbas publicitárias institucionais, tese mensurável pela correlação entre posse societária de retransmissoras e taxas de reeleição municipal.\n\n"
                "### Extra Info\n\n"
                "1. O Código Brasileiro de Telecomunicações (Lei 4.117, de 1962-08-27) centralizou na União a competência de outorga de serviços de radiodifusão sonora e de sons e imagens por prazos renováveis de dez anos para rádio e quinze anos para televisão.\n"
                "2. A Constituição de 1988, no artigo 223, transferiu a palavra final sobre renovações e novas outorgas para apreciação do Congresso Nacional, exigindo quórum mínimo de dois quintos em votação nominal para o cancelamento ou não renovação de concessões existentes."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "extra_info_granularity",
            "difficulty": "easy",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "MRG6d9bQC8Q",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ei_04_easy_fail",
        "input": {
            "raw_text": (
                "## A Dinâmica das Regras Globais e a Revelação Progressiva\n\n"
                "O componente fundamental da camada de inteligência artificial reside nas regras globais, especificadas em arquivos de configuração que estabelecem o comportamento basal do agente durante toda a sessão de desenvolvimento. Para evitar a saturação prematura da janela de contexto com centenas de páginas de instruções irrelevantes, sistemas maduros adotam o princípio da revelação progressiva.\n\n"
                "Sob essa estratégia arquitetural, apenas os metadados descritivos de cada habilidade permanecem visíveis no início da execução, carregando-se os manuais completos sob demanda exclusiva quando a tarefa corrente aciona o domínio correspondente."
            ),
            "candidate_text": (
                "## Revelação Progressiva e Economia de Contexto em Agentes\n\n"
                "A adoção de carregamento sob demanda em agentes de codificação resolve o conflito entre abrangência normativa e degradação de atenção em contextos extensos. No lugar de injetar integralmente todas as especificações técnicas no prompt de sistema inicial, o orquestrador expõe um índice compacto com nome e gatilho de cada habilidade, hidratando as instruções detalhadas somente quando o planejador classifica a requisição naquele domínio específico.\n\n"
                "Sob o ponto de vista de engenharia de sistemas, esse padrão reproduz o carregamento dinâmico (lazy loading) de sistemas de arquivos virtuais, mantendo as taxas de acerto em seleção de ferramentas estáveis à medida que o catálogo cresce.\n\n"
                "### Extra Info\n\n"
                "- O padrão de Agent Skills utiliza arquivos SKILL.md com cabeçalho YAML contendo apenas nome e descrição curta para indexação inicial.\n"
                "- O Model Context Protocol separa ferramentas descobertas dinamicamente dos recursos estáticos carregados por URI explícita."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "extra_info_granularity",
            "difficulty": "easy",
            "expected_anomaly": "bullet_markers_in_complementary",
            "defect_location": "extra_info",
            "video_id": "efRIrLXoOVA",
            "target_verdict": "FAIL",
        },
    },
    {
        "id": "ei_05_typical_pass_1",
        "input": {
            "raw_text": (
                "## A Paisagem Contemporânea dos Grandes Modelos de Linguagem\n\n"
                "A exploração prática dos grandes modelos de linguagem exige o reconhecimento de uma infraestrutura tecnológica que transcende a interface conversacional rudimentar introduzida pela OpenAI em 2022. A compreensão correta do funcionamento desses sistemas demanda mapear a separação entre pré-treinamento sobre grandes volumes de texto, ajuste fino supervisionado e alinhamento por preferências.\n\n"
                "Além da arquitetura neural subjacente, os custos marginais de inferência, a quantização de pesos e a representação numérica das palavras por subunidades léxicas determinam diretamente a latência e a viabilidade econômica de cada aplicação."
            ),
            "candidate_text": (
                "## Tokenização, Pós-Treinamento e Economia de Inferência em LLMs\n\n"
                "A engenharia moderna de grandes modelos de linguagem articula três fases distintas após a coleta de corpora: o pré-treinamento auto-supervisionado para compressão estatística do conhecimento mundial, o ajuste supervisionado (SFT) para formatação dialógica de assistente e o aprendizado por reforço para alinhamento de segurança e raciocínio. Em produção, a camada de entrada converte caracteres em sequências discretas mediante tokenização por Byte Pair Encoding (BPE), condicionando diretamente o consumo de memória da atenção durante toda a geração autorregressiva.\n\n"
                "Pesquisadores debatem se arquiteturas sem tokenizador fixo (byte-level ou patch-level) eliminarão vieses multilingues do BPE sem elevar o custo quadrático de sequência, hipótese verificável pela comparação de bits-por-byte em tarefas de código e idiomas não latinos.\n\n"
                "### Extra Info\n\n"
                "1. O algoritmo Byte Pair Encoding (BPE), adaptado por Rico Sennrich em 2016 para tradução neural, mescla iterativamente os pares de bytes adjacentes mais frequentes até atingir um vocabulário fixo entre 32.000 e 128.000 tokens.\n"
                "2. Durante a inferência autorregressiva, o armazenamento do Key-Value Cache (KV Cache) em precisão FP8 ou via Multi-Query/Grouped-Query Attention reduz a largura de banda de memória HBM por token gerado, constituindo o principal determinante de custo em janelas longas."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "extra_info_granularity",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "EWvNQjAaOHw",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ei_06_typical_pass_2",
        "input": {
            "raw_text": (
                "## A Arquitetura da Coerção Transnacional e o Desarranjo Institucional\n\n"
                "A dinâmica do poder contemporâneo manifesta-se frequentemente na intersecção entre a soberania estatal formal e os fluxos financeiros globais, onde sanções unilaterais funcionam como instrumentos de engenharia política. No episódio envolvendo sanções aplicadas contra autoridades judiciárias brasileiras sob a égide de legislação estrangeira, evidenciou-se a vulnerabilidade de atores domésticos às infraestruturas de liquidação denominadas em dólar.\n\n"
                "A inclusão ou remoção de nomes em listas restritivas repercute diretamente sobre o acesso a sistemas internacionais de cartões, contas correspondentes e redes de compensação bancária, demonstrando o alcance extraterritorial da jurisdição financeira norte-americana."
            ),
            "candidate_text": (
                "## Extraterritorialidade do Dólar e Compensação Financeira Global\n\n"
                "A eficácia coercitiva de sanções unilaterais norte-americanas sobre indivíduos ou instituições estrangeiras sem ativos físicos nos Estados Unidos apoia-se no monopólio estrutural da infraestrutura de liquidação em dólar. Como pagamentos transfronteiriços e bandeiras internacionais de cartões dependem de contas correspondentes vinculadas ao sistema bancário norte-americano, bancos situados em terceiros países cumprem preventivamente determinações do Tesouro dos EUA para evitar a perda de licença de compensação em dólar (de-risking).\n\n"
                "Analistas geopolíticos avaliam se redes bilaterais em moedas locais ou sistemas alternativos de mensageria reduzem essa assimetria no médio prazo ou esbarram na baixa liquidez de mercados secundários fora do dólar, hipótese mensurável pela participação do dólar nas reservas e liquidações cambiais globais.\n\n"
                "### Extra Info\n\n"
                "1. A câmara privada Clearing House Interbank Payments System (CHIPS) e o sistema Fedwire do Federal Reserve liquidam diariamente trilhões de dólares em transações internacionais, conferindo jurisdição indireta norte-americana sobre qualquer transferência que transite por bancos correspondentes em Nova York.\n"
                "2. O padrão de mensageria financeira ISO 20022, adotado progressivamente pela rede SWIFT entre 2023 e 2025, estrutura metadados granulares de ordenantes e beneficiários finais que facilitam a triagem automatizada contra listas do OFAC."
            ),
        },
        "expected_output": {"verdict": "PASS"},
        "metadata": {
            "criterion": "extra_info_granularity",
            "difficulty": "typical",
            "expected_anomaly": "none",
            "defect_location": "none",
            "video_id": "R8-dCSHLItE",
            "target_verdict": "PASS",
        },
    },
    {
        "id": "ei_07_typical_fail",
        "input": {
            "raw_text": (
                "## Persistência Relacional e a Otimização de Consultas\n\n"
                "O banco de dados relacional PostgreSQL, frequentemente subestimado e rotulado como o principal gargalo de sistemas web, demonstra uma eficiência notável quando submetido a cargas controladas de transações atômicas. A adoção de estratégias adequadas de indexação, como o uso de índices GIN combinados com a extensão de trigramas pg_trgm, possibilita buscas textuais parciais com latências na casa de poucos milissegundos.\n\n"
                "Essa abordagem elimina a necessidade de incorporar motores externos de busca distribuída na arquitetura inicial, reduzindo a complexidade de sincronização de dados e garantindo a integridade transacional nativa do sistema."
            ),
            "candidate_text": (
                "## A Indexação Textual Nativa no PostgreSQL\n\n"
                "O emprego de índices GIN com trigramas no PostgreSQL reduz a latência de consultas com correspondência parcial ao dividir cadeias de caracteres em blocos de três letras indexados em árvore invertida, dispensando buscas sequenciais completas na tabela principal. A engrenagem exige atenção às taxas de atualização, pois cada gravação altera múltiplas entradas no índice invertido, gerando amplificação de escrita mitigada por listas pendentes (fastupdate).\n\n"
                "Sob o ângulo arquitetural, manter busca textual e integridade relacional no mesmo motor reduz falhas de consistência eventual em equipes enxutas, hipótese testável por benchmarks de latência p99 sob carga mista de leitura e escrita.\n\n"
                "### Extra Info\n\n"
                "1. O PostgreSQL é um sistema gerenciador de banco de dados relacional muito popular e gratuito usado por desenvolvedores no mundo todo.\n"
                "2. Índices de banco de dados são estruturas auxiliares úteis que tornam as pesquisas mais rápidas em tabelas grandes."
            ),
        },
        "expected_output": {"verdict": "FAIL"},
        "metadata": {
            "criterion": "extra_info_granularity",
            "difficulty": "typical",
            "expected_anomaly": "vacuous_dictionary_definitions_without_tertiary_technical_density",
            "defect_location": "extra_info",
            "video_id": "-yGHG3pnHLg",
            "target_verdict": "FAIL",
        },
    },
]
