<config_file>
# Automação de Agentes com Supervisão Humana (Human-in-the-Loop) no n8n

## Contexto e Visão Geral

Na conferência de engenharia de inteligência artificial de 2026, **Liam McGarrigle**, especialista em relações com desenvolvedores da **n8n**, apresentou as metodologias de orquestração visual para a construção de agentes de inteligência artificial autônomos e supervisionados. O workshop utilizou a automação do **Gmail** e do **Google Calendar** como estudo de caso para demonstrar a criação de fluxos operacionais auditáveis, controlados e resilientes.

A apresentação focou no dilema da opacidade dos agentes de IA ("caixa preta") em ambientes corporativos e demonstrou como a interceptação de chamadas de ferramentas (_tool calls_) por nós de aprovação humana (_Human-in-the-Loop_) garante governança e segurança sem comprometer a flexibilidade dos modelos de linguagem.

---

## 1. Fundamentos da Plataforma n8n e Arquitetura Agêntica Visual

O **n8n** é uma ferramenta de automação visual de fluxos de trabalho que combina a simplicidade de conectores visuais declarativos com a capacidade de executar código customizado em _JavaScript_.

### 1.1 Estrutura de Nós, Gatilhos e Controle de Fluxo

* **Gatilhos (_Triggers_)**: Pontos de entrada assíncronos que iniciam o fluxo de trabalho (como mensagens recebidas no _Slack_, webhooks, formulários de entrada ou acionamentos por cronograma).
* **Nós de Agente de IA**: Componentes especializados que recebem modelos de linguagem grandes (_LLMs_), memória contextual e um catálogo de ferramentas acionáveis.
* **Módulos de Memória**: Abstrações configuráveis (como memória simples por janela de contexto ou integração com bancos de dados relacionais como _PostgreSQL_) para armazenar o histórico de mensagens da sessão sem sobrecarregar o modelo.

---

## 2. Injeção Modular de Ferramentas e Isolamento de Escopo

Diferente do acesso irrestrito concedido a agentes de codificação em ambiente local, o **n8n** aplica restrições estritas de escopo em cada conector de API.

### 2.1 Mapeamento Declarativo de Parâmetros

Para cada ferramenta conectada ao nó do agente (como envio de e-mails ou criação de eventos na agenda):
* **Restrição de Campos**: O desenvolvedor especifica exatamente quais parâmetros o modelo pode alterar (por exemplo, apenas o assunto e o corpo da mensagem), impedindo que o modelo modifique parâmetros críticos de autenticação ou chaves de sistema.
* **Instruções de Escopo nas Descrições dos Nós**: A especificação do comportamento de uma ferramenta é codificada no próprio nome e na descrição do nó visual. Essa modularidade permite copiar e reutilizar ferramentas entre fluxos de trabalho distintos mantendo as diretrizes de segurança.

---

## 3. Supervisão Humana no Fluxo de Execução (Human-in-the-Loop)

Para ações consideradas destrutivas ou de alto impacto comercial — como o disparo de e-mails institucionais, exclusão de arquivos ou movimentação financeira —, o sistema insere barreiras de contenção que exigem validação prévia.

### 3.1 Interceptação de Chamadas de Ferramentas (Tool Interception)

A arquitetura do **n8n** permite interceptar chamadas de ferramentas de forma transparente para o modelo de linguagem:
* **Inexistência de Percepção pelo Modelo**: O modelo de linguagem gera a intenção da chamada da ferramenta (`tool call`) acreditando que a ação será executada imediatamente.
* **Pausa e Renderização do Nó de Aprovação**: O fluxo é pausado pelo nó de revisão humana, que renderiza uma mensagem legível com os parâmetros propostos (destinatário, assunto e corpo da mensagem).
* **Validação por Interface de Chat ou Provedores Externos**: O operador humano inspeciona os parâmetros propostos e pode aprovar o envio, rejeitar a ação ou responder com correções em linguagem natural (exigindo que o modelo reformule o texto antes de uma nova submissão).

---

## Notas Informativas

1. **n8n**: Plataforma open-source e em nuvem de automação de fluxos de trabalho baseada em nós visuais e código estendível em JavaScript/TypeScript.
2. **Human-in-the-Loop (HITL)**: Paradigma de design de sistemas de inteligência artificial no qual a execução autônoma é interrompida em pontos críticos para solicitar a validação, revisão ou decisão de um operador humano.
3. **OpenRouter**: Serviço unificado de roteamento de APIs que oferece acesso a múltiplos modelos de linguagem fundacionais (como Claude, GPT e Llama) sob uma única chave de autenticação.
</config_file>
