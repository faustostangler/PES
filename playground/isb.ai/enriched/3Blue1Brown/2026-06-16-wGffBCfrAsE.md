<config_file>
# O Problema da Interseção de Cordas Aleatórias em um Círculo

## A Definição do Modelo Geométrico e o Paradoxo de Bertrand

O enigma de **geometria estocástica** analisa o comportamento de segmentos de reta que conectam dois pontos dispostos na circunferência de um círculo, conhecidos tecnicamente como cordas geométricas. A especificação precisa da distribuição probabilística é fundamental nesse contexto para evitar ambiguidades conceituais associadas ao célebre **Paradoxo de Bertrand**.

Para definir uma corda aleatória sem ambiguidade, selecionam-se dois pontos de forma independente e uniforme ao longo do perímetro do círculo. Isso significa que a probabilidade de um ponto pertencer a um determinado arco é estritamente proporcional ao comprimento desse arco. A união desses dois pontos sorteados por um segmento retilíneo define a corda. O desafio consiste em calcular o valor esperado do número total de pontos de interseção formados no interior do círculo quando se desenham dez ou cem cordas aleatórias independentes.

## A Probabilidade Pairwise e o Cálculo da Expectativa

A determinação do número médio de interseções baseia-se na análise combinatória aplicada a cada par de cordas. Para qualquer par de cordas selecionado, existem quatro pontos de extremidade dispostos na circunferência. Considerando esses quatro pontos em ordem ao longo da borda, existem exatamente três maneiras distintas de emparelhá-los em duas cordas.

Dentre os três emparelhamentos possíveis, apenas um resulta no cruzamento das duas cordas no interior do círculo, enquanto os outros dois arranjos produzem cordas que não se interseptam. Como os pontos são escolhidos de forma uniforme e independente, cada uma das três combinações possui uma probabilidade exatamente igual a um terço. Pela propriedade da **linearidade da expectativa**, o número total de interseções esperadas equivale a um terço do número total de combinações de pares de cordas. Para dez cordas, o número esperado é de quinze interseções; para cem cordas, a média eleva-se para mil seiscentas e cinquenta interseções.

## Informações Complementares

O **Paradoxo de Bertrand**, formulado em 1889 pelo matemático francês **Joseph Bertrand**, demonstra que a probabilidade em problemas de geometria estocástica depende criticamente do método utilizado para definir a aleatoriedade. Dependendo se a escolha da corda é feita sorteando extremidades na circunferência, a direção de um raio perpendicular ou a posição do ponto médio no disco interior, a probabilidade de uma corda ser maior que o lado de um triângulo equilátero inscrito varia entre meio, um terço e um quarto. A resolução moderna dessa aparente contradição exige a especificação rigorosa da medida de invariância geométrica adotada pelo experimento.
</config_file>
