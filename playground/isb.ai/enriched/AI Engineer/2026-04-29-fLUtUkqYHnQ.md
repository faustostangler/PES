<config_file>
# Arquitetura e Pós-Treinamento de Modelos de Linguagem Pequenos para Dispositivos de Borda

## Contexto e Visão Geral

No âmbito da conferência de engenharia de inteligência artificial de 2026, **Maxime Labonne**, chefe de pré-treinamento na **Liquid AI**, apresentou os avanços metodológicos e os desafios técnicos na criação de modelos de linguagem pequenos de fronteira (_Frontier Small Models_). A empresa desenvolve arquiteturas multimodais (texto, imagem e áudio) projetadas para execução local em dispositivos móveis, veículos e ambientes industriais com restrições de memória de até 1 GB.

Diferente da premissa convencional de que modelos pequenos são meras versões reduzidas por destilação de modelos gigantes, a engenharia de modelos de borda exige soluções arquiteturais dedicadas e estratégias de pós-treinamento focadas em tarefas específicas, latência reduzida e eliminação de instabilidades como ciclos de repetição infinita (_doom loops_).

---

## 1. Características Fundamentais e Arquitetura de Hardware

Modelos pequenos possuem três restrições operacionais determinantes: sensibilidade à latência, limitação estrita de memória RAM e capacidade reduzida de armazenamento de conhecimento enciclopédico. Em virtude disso, o design dessas redes prioriza o desempenho sintático em tarefas focadas (como extração de dados estruturados e chamadas de funções) em vez da retenção de conhecimento geral.

### 1.1 Ineficiência das Camadas de Incorporação em Modelos Destilados

Em arquiteturas convencionais destiladas — como a família **Gemma** da **Google** —, a camada de incorporação (_embedding layer_) chega a responder por 63% dos parâmetros totais no modelo **Gemma 3 270M** e por 29% no **Gemma 2.5 0.8B**. Esse efeito decorre da destilação direta a partir de modelos professores equipados com vocabulários massivos. Do ponto de vista computacional, esses parâmetros de incorporação não contribuem diretamente para a capacidade de raciocínio da rede, reduzindo a contagem efetiva de parâmetros operacionais.

### 1.2 A Arquitetura LFM 2 e Convoluções Curtas com Controle de Entrada

A família **LFM 2** da **Liquid AI** reestrutura essa proporção, dedicando mais de 90% dos parâmetros à capacidade efetiva de raciocínio. A arquitetura adota um modelo híbrido que combina Convoluções Curtas com Controle de Entrada (_Gated Short Convolutions_) e Atenção por Consulta em Grupo (**GQA**).

Em testes de perfil de desempenho em hardware alvo — como o processador _AMD Ryzen Max Plus 395_ e o smartphone _Samsung Galaxy S25 Ultra_ —, a utilização de convoluções curtas garantiu maior taxa de transferência de tokens por segundo e menor pegada de memória em comparação com mecanismos de atenção baseados em janelas deslizantes ou atenção linear.

---

## 2. Receita de Treinamento LFM 2.5 e Novas Leis de Escala

A receita do **LFM 2.5** submeteu um modelo compacto de 350 milhões de parâmetros a um volume de 28 trilhões de tokens na fase de pré-treinamento.

### 2.1 Suparação das Leis de Escala de Chinchilla

Sob a perspectiva clássica das leis de escala de **Chinchilla**, treinar um modelo de 350M de parâmetros com 28T de tokens representaria uma saturação ineficiente de poder computacional. No entanto, estudos recentes sobre leis de escala em tempo de teste e inferência em modelos de borda provam que o desempenho contínuo de modelos pequenos cresce de forma sustentada com o aumento drástico no volume de tokens de pré-treinamento, tornando a inferência em dispositivos significativamente mais barata e precisa.

Nas métricas de avaliação, o **LFM 2.5 350M** superou gerações anteriores em benchmarks de extração de dados estruturados e uso de ferramentas (como o _BFCL_ e o _IFEval_), priorizando especialização funcional em detrimento de conhecimentos genéricos em matemática ou código complexo.

---

## 3. Mitigação de Ciclos Infinitos (Doom Loops) e Alinhamento de Preferências

Um dos maiores desafios operacionais em modelos pequenos com capacidade de raciocínio é a tendência a cair em ciclos de repetição infinita (_doom loops_), onde o sistema itera indefinidamente sobre as mesmas sequências de texto sem gerar a resposta final.

### 3.1 Geração de Dados On-Policy e Otimização Direta de Preferências (DPO)

Para erradicar a repetição contínua, o processo de alinhamento utiliza amostragem com temperatura para gerar múltiplas trajetórias de resposta. Uma trajetória gerada sob temperatura zero (com alta probabilidade de entrar em ciclo infinito) é propositalmente rotulada como resposta rejeitada durante o processo de Otimização Direta de Preferências (**DPO**), ensinando o modelo a desviar de padrões repetitivos.

### 3.2 Aprendizado por Reforço com Recompensas Verificáveis (RL)

Na etapa de Aprendizado por Reforço (**RL**), aplica-se uma penalidade estrita à repetição de n-gramas associada à exigência de um resultado final verificável. 

Experimentos com o modelo **LFM 2.5 1.2B** demonstraram que a taxa de ciclos infinitos, que atingia 16% após o pré-treinamento e o ajuste fino supervisionado (**SFT**), foi reduzida a níveis próximos de zero após a aplicação combinada de **DPO** e **RL**. Em contrapartida, modelos menores treinados apenas por redução de escala convencional (como o **Qwen 3.5 0.8B**) apresentam taxas de repetição em malha fechada superiores a 50% em tarefas complexas.

---

## 4. Agentes Autônomos de Borda e Ferramentas Externas

Para superar a limitação física de memória RAM em dispositivos de borda, a estratégia da **Liquid AI** fundamenta-se no uso de ferramentas externas e agentes recursivos. Em vez de inflar a rede com conhecimento estático, o modelo de borda atua como um motor de raciocínio leve capacitado a realizar buscas na web via APIs, interagir com interpretadores Python e executar chamadas de função dinâmicas.

---

## Notas Informativas

1. **Liquid AI**: Empresa de inteligência artificial surgida do Laboratório de Ciência da Computação e Inteligência Artificial do MIT (CSAIL), dedicada à criação de modelos fundacionais líquidos e arquiteturas de redes neurais dinâmicas.
2. **Leis de Escala de Chinchilla**: Formulação empírica estabelecida por pesquisadores da **DeepMind** em 2022 que determina a proporção ideal entre o número de parâmetros de um modelo e a quantidade de tokens de treino.
3. **Gated Short Convolutions**: Mecanismo de filtragem convolucional de contexto local que substitui blocos pesados de autoatenção em transformadores por operadores de menor complexidade computacional.
</config_file>
