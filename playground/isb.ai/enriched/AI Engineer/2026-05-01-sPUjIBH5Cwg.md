<config_file>
# Agentes de Inteligência Artificial em Telas Infinitas: A Experiência Interativa do tldraw

## Contexto e Visão Geral

Na conferência de engenharia de inteligência artificial de 2026, **Steve Ruiz**, fundador do **tldraw**, apresentou a evolução do ecossistema de quadros brancos virtuais como interface primária para colaboração entre humanos e agentes autônomos. Sediada em Londres, a startup desenvolve uma plataforma de código aberto e um kit de desenvolvimento de software (SDK) baseado em _React_ que fundamenta telas infinitas interativas em ferramentas corporativas como o _Replit Agent Canvas_ e o _Luma AI_.

A apresentação explorou desde as primeiras experiências de conversão de esboços visuais em protótipos de código em 2023 (_Make Real_) até a implementação de agentes virtuais colaborativos diretamente no espaço bidimensional da tela (_Fairydraw_).

---

## 1. Da Visão Computacional ao Código Funcional: O Projeto Make Real

Lançado no final de 2023 juntamente com os primeiros modelos de linguagem com capacidade de visão multimodal, o projeto **Make Real** demonstrou a possibilidade de desenhar elementos de interface de usuário sobre uma tela e convertê-los autonomamente em protótipos funcionais em HTML, CSS e JavaScript.

### 1.1 Inversão de Coordenadas e Desafios de Dados Estruturados

A geração de layouts vetoriais estruturados diretamente por modelos de linguagem enfrentou incompatibilidades gramaticais e espaciais inerentes aos dados de treinamento:
* **Conflitos de Sistemas de Coordenadas**: Em gráficos cartesianos tradicionais, o valor do eixo Y cresce de baixo para cima. No ambiente de renderização da Web e do DOM, o ponto zero encontra-se no canto superior esquerdo e o eixo Y cresce para baixo, gerando inversões espaciais nas saídas do modelo.
* **Saída Vetorial Declarativa**: Em vez de sintetizar imagens rasterizadas por difusão, o **tldraw** orientou os modelos a gerar estruturas de dados textuais baseadas nas primitivas nativas do SDK (círculos, retângulos, setas e textos), permitindo edição posterior por usuários humanos.

---

## 2. Agentes Colaborativos em Telas Virtuais (Fairydraw)

Concebido como um experimento em dezembro de 2025, o projeto **Fairydraw** introduziu "fadas" virtuais — avatares de agentes autônomos que operam visualmente dentro da própria área de trabalho do quadro branco.

### 2.1 Orquestração Multiagente e Hierarquia de Agentes

A interação em tela infinita introduziu um paradigma de colaboração transparente em tempo real:
* **Visibilidade Espacial do Estado**: Os avatares exibem graficamente a posição de trabalho de cada agente no plano cartesiano, os itens selecionados e os pensamentos intermediários do modelo.
* **Coordenação Lógica por Eleição**: Quando múltiplos agentes atuam sobre um mesmo objetivo (como desenhar ilustrações complexas ou criar mapas de interface), o sistema elege um agente líder encarregado de construir a lista de tarefas e delegar a execução aos agentes subordinados.
* **Inspeção de Limites de Trabalho**: O agente líder monitora a conclusão dos elementos e valida se a execução cumpre os requisitos definidos pelo usuário humano, impedindo a sobreposição de edições sobre o mesmo objeto.

---

## 3. Aplicações Locais e Injeção de Scripts no Ambiente Desktop

A evolução da autonomia dos agentes na tela levou à integração com o aplicativo desktop do **tldraw** (desenvolvido com _Electron_), permitindo aos modelos inspecionar e alterar dinamicamente o código do ambiente cliente.

### 3.1 Manipulação Local do DOM e Integração com Servidores Locais

Ao expor um ponto de extremidade HTTP local para o modelo de linguagem, o agente ganha capacidade de executar scripts diretamente no ambiente de renderização local. Essa funcionalidade viabiliza a criação de componentes interativos em tempo real, onde o agente ajusta estilos CSS, inclui comportamentos de passar o mouse (_hover_) ou manipular estados de formulários dinamicamente sem exigir a reinicialização da aplicação.

---

## Notas Informativas

1. **tldraw**: Biblioteca de código aberto e biblioteca de componentes em _React_ destinada à criação de telas infinitas, quadros brancos interativos e ferramentas de anotação gráfica.
2. **Make Real**: Projeto experimental pioneiro lançado pelo **tldraw** em 2023 que utilizava a API de visão do GPT-4 para transformar esboços em código web funcional.
3. **Electron**: Framework de desenvolvimento de código aberto mantido pela comunidade que permite a criação de aplicações desktop nativas utilizando tecnologias web como JavaScript, HTML e CSS.
</config_file>
