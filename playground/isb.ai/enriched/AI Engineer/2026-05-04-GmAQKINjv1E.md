<config_file>
# Engenharia de Habilidades para Agentes de IA: Do Conceito à Avaliação Sistemática no Supabase

## A Evolução da Experiência do Agente (AX) no Ecossistema de Software

O avanço acelerado dos agentes de inteligência artificial no desenvolvimento de software impôs uma redefinição nos critérios de usabilidade das plataformas tecnológicas. Além da tradicional Experiência do Desenvolvedor (_Developer Experience_ - DX), a engenharia moderna passou a priorizar a **Experiência do Agente** (_Agent Experience_ - AX), disciplinando como arquiteturas de dados, APIs e ferramentas de desenvolvimento são estruturadas para facilitar a navegação autônoma por sistemas computacionais. No âmbito dessa transformação, o engenheiro **Pedro Rodrigues**, da equipe da **Supabase**, destaca a utilização de **Habilidades de Agente** (_Agent Skills_) como o mecanismo central para otimizar o desempenho de agentes autônomos em ambientes de retaguarda complexos.

As habilidades operam como repositórios estruturados de instruções, scripts operacionais e arquivos de referência organizados em diretórios específicos. Diferente do carregamento massivo de documentação ou ferramentas no contexto de um modelo de linguagem, a arquitetura de habilidades fundamenta-se no princípio da **Divulgação Progressiva** (_Progressive Disclosure_). Esse conceito determina que apenas o cabeçalho descritivo contido no arquivo principal — o manifesto em formato Markdown conhecido como `skill.md` — seja inicialmente injetado na janela de contexto do agente. O conteúdo integral e as referências associadas são carregados dinamicamente apenas quando a inteligência artificial identifica a necessidade explícita de consultar determinado fluxo de trabalho.

## Diferenciação Arquitetônica: Habilidades, MCP e Scripts Locais

### O Papel Integrador do Model Context Protocol (MCP)

A estruturação de ecossistemas automatizados exige a diferenciação clara entre os papéis desempenhados pelo **Model Context Protocol** (MCP) e pelas habilidades. O MCP atua como o protocolo de integração responsável por expor ferramentas, recursos de banco de dados e APIs remotas sem a necessidade de conceder acesso ao terminal de linha de comando (_bash_). Essa camada garante que as operações no servidor ocorram sob esquemas de autenticação padronizados e sem dependência do ambiente operacional do cliente.

### Habilidades e Scripts no Ambiente Local

Enquanto o MCP fornece os pontos de entrada para chamadas de ferramentas, as habilidades fornecem a camada narrativa e procedural, detalhando Procedimentos Operacionais Padrão (SOPs), diretrizes arquitetônicas e sequências de decisão. Adicionalmente, as habilidades podem conter scripts executáveis em linguagens como Python ou Bash. Tais scripts são carregados e executados diretamente no ambiente do usuário, exigindo compatibilidade com o sistema operacional local. A sinergia ideal manifesta-se quando as habilidades orientam o agente sobre como e quando invocar as ferramentas expostas pelo MCP, reduzindo o consumo indevido da janela de contexto.

## Desenvolvimento Orientado a Avaliações (_Eval-Driven Development_)

### A Natureza Não-Determinística do Teste de Agentes

A validação da eficácia de uma habilidade diverge substancialmente dos testes unitários ou de integração tradicionais. Devido ao caráter probabilístico dos modelos de linguagem, a verificação de comportamento apoia-se em **Avaliações Não-Determinísticas** (_Evals_). O processo inicia-se com a definição prévia das métricas de sucesso, antecedendo a própria escrita da instrução técnica.

A arquitetura de teste estruturada pela indústria estabelece um ciclo iterativo contínuo. Inicialmente, definem-se os cenários de controle com as entradas do usuário e os comportamentos esperados. Em seguida, a habilidade é codificada e submetida a execuções automatizadas em ambientes isolados. A análise dos resultados determina se o acréscimo de contexto instrucional promoveu melhoria efetiva ou se introduziu viés indesejado, guiando refatorações sucessivas.

### A Metodologia do LLM como Juiz

Na ausência de saídas estritamente determinísticas, a automação dos testes de avaliação utiliza a técnica de **LLM como Juiz** (_LLM-as-a-Judge_). Nessa abordagem, um modelo de linguagem secundário avalia o raciocínio, a escolha de ferramentas e os artefatos gerados pelo agente primário, emitindo pontuações baseadas em critérios de aprovação predefinidos. Frameworks de observabilidade como **_Braintrust_** e **_LangFuse_**, alinhados ao **Agent Skills Open Standard**, fornecem infraestrutura para executar matrizes de testes comparando execuções com e sem a presença da habilidade avaliada.

## Caso Prático: Segurança em Nível de Linha no Supabase e Postgres

### A Vulnerabilidade de Visualizações no PostgreSQL

A aplicação prática da engenharia de habilidades é ilustrada pela gestão de segurança em bancos de dados operados pela **_Supabase_**, um serviço de **Backend como Serviço** (BaaS) construído sobre o **_PostgreSQL_**. Em arquiteturas que utilizam **Segurança em Nível de Linha** (_Row-Level Security_ - RLS), as tabelas restringem a visualização de dados com base na identidade e no papel do usuário autenticado.

Contudo, ao instruir um agente a criar uma nova visualização (_view_) no banco de dados, o comportamento padrão do _PostgreSQL_ cria o objeto com as credenciais do usuário criador. Essa configuração ignora as políticas de RLS vigentes nas tabelas subjacentes, expondo dados sensíveis a usuários não autorizados através da visualização recém-criada.

### A Habilidade de Segurança e o Sinalizador _Security Invoker_

Para corrigir o viés do agente, desenvolve-se uma habilidade dedicada à segurança. A instrução exige explicitamente que todas as visualizações criadas em esquemas públicos sejam consolidadas com o sinalizador **_Security Invoker_**, funcionalidade introduzida a partir da versão 15 do _PostgreSQL_. Esse parâmetro garante que a visualização herde e aplique rigorosamente as políticas de RLS do usuário que consulta o banco de dados.

Com a instalação da habilidade no repositório — utilizando gerenciadores como a CLI **_skills_** em diretórios padronizados —, a instrução é carregada na janela de contexto quando o agente detecta operações de alteração de esquema. A avaliação automatizada compara as migrações geradas com e sem a habilidade, comprovando que o acréscimo instrucional elimina a falha de segurança sem violar a funcionalidade da aplicação.

## Boas Práticas para a Manutenção de Habilidades em Produção

A gestão de habilidades em escala industrial requer a incorporação desses artefatos ao fluxo tradicional de Engenharia e Desenvolvimento (P&D). As habilidades devem ser tratadas como documentação viva, passando por revisões de código e atualizações periódicas sempre que a arquitetura do produto evoluir.

Nos ambientes de Integração Contínua (CI), recomenda-se manter apenas as habilidades estritamente necessárias para os fluxos de trabalho daquele repositório, evitando a poluição do contexto e o disparo indevido de ferramentas. A auditoria constante das descrições nos arquivos de manifesto assegura que o mecanismo de divulgação progressiva permaneça preciso, maximizando a taxa de sucesso da execução autônoma.

---

## Notas Informativas

### Pedro Rodrigues e o Desenvolvimento de Ferramentas na Supabase
**Pedro Rodrigues** é engenheiro especialista em ferramentas de inteligência artificial na **Supabase**, sediado em Lisboa, Portugal. Sua atuação foca na otimização de interfaces e protocolos para garantir que a infraestrutura da plataforma seja diretamente operável por agentes autônomos de código.

### Supabase e a Arquitetura Backend-as-a-Service
A **Supabase** é uma plataforma de código aberto do tipo **Backend como Serviço** (BaaS), concebida como alternativa ao **_Firebase_**. A tecnologia encapsula um banco de dados relacional **_PostgreSQL_**, serviços de autenticação, armazenamento de arquivos e funções executadas em borda (_Edge Functions_), permitindo a integração direta com interfaces sem a necessidade de servidores intermediários.

### O Padrão Aberto Agent Skills
O **Agent Skills Open Standard** é uma iniciativa da indústria destinada a padronizar o formato, a estrutura de diretórios e o protocolo de descoberta de habilidades para agentes de IA. A especificação define o uso de metadados YAML nos arquivos `skill.md` e estabelece modelos para testes locais de avaliação.

---

## Informações Complementares

### Segurança em Nível de Linha (RLS) e _Security Invoker_
A **Segurança em Nível de Linha** (RLS) é um mecanismo do **_PostgreSQL_** que controla o acesso a linhas individuais em tabelas com base em políticas definidas por comandos SQL. A cláusula `security_invoker = true`, introduzida no _Postgres 15_, força as visualizações a avaliarem as políticas de RLS utilizando a identidade do usuário que executa a consulta, prevenindo vazamentos de dados por elevação indevida de privilégios.

### Avaliação Não-Determinística e Plataformas de Evals
A avaliação de sistemas baseados em inteligência artificial requer matrizes de testes que analisam trajetórias de execução e chamadas de ferramentas em vez de respostas literais. Plataformas como **_Braintrust_** e **_LangFuse_** automatizam esse processo, fornecendo rastreabilidade completa dos passos tomados pelo agente durante as rodadas de testes.

### A CLI de Habilidades e a Gestão de Dependências
A distribuição de habilidades entre diferentes ambientes de desenvolvimento foi simplificada por utilitários de linha de comando como o pacote **_skills_**, mantido pela **Vercel**. A ferramenta permite instalar habilidades locais ou remotas, criando links simbólicos em diretórios padronizados como `.agents/` para compatibilidade com múltiplos clientes de IA.
</config_file>
