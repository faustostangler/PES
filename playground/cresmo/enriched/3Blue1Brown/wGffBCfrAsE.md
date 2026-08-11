# O Problema da Intersecção de Cordas Aleatórias e o Paradoxo de Bertrand

## A Formulação Geométrica e a Definição de Probabilidade Uniforme

O problema da determinação do valor esperado de pontos de intersecção entre cordas aleatórias em uma circunferência integra a série de desafios de probabilidade geométrica desenvolvidos em colaboração com o **National Museum of Mathematics** (MoMath). O enigma propõe selecionar dez ou cem cordas aleatórias em um círculo e calcular o número esperado de intersecções internas geradas por essas cordas.

A definição rigorosa de uma corda aleatória exige especificar o modelo estocástico subjacente para evitar a ambiguidade conceitual célebre conhecida como **Paradoxo de Bertrand**. Formulada pelo matemático francês **Joseph Bertrand** em **1889**, essa ambiguidade demonstra que o termo distribuição uniforme para cordas varia drasticamente dependendo de o modelo considerar pontos finais uniformes na circunferência, pontos médios uniformes no disco ou distâncias radiais uniformes. No problema em questão, adota-se rigorosamente o modelo de pontos finais independentes e uniformemente distribuídos ao longo do comprimento de arco da circunferência.

## A Solução Analítica pela Linearidade da Esperança

A resolução elegante do problema prescinde de integrais complexas ao aplicar a **Linearidade da Esperança Matemática** combinada à combinatória extremal. Considerando duas cordas genéricas definidas por quatro pontos extremos distintos na circunferência, existem exatamente três maneiras distintas de emparelhar esses quatro pontos em duas cordas. Dessas três configurações topológicas possíveis, exatamente uma resulta em cordas que se cruzam no interior do círculo.

Consequentemente, a probabilidade de que qualquer par individual de cordas aleatórias se cruze é estritamente igual a um terço. Para um conjunto de $N$ cordas aleatórias, o número total de pares possíveis de cordas é dado pela combinação de $N$ tomados dois a dois. Multiplicando essa contagem pela probabilidade individual de intersecção, obtém-se a fórmula fechada do valor esperado como sendo $N$ vezes $N$ menos um dividido por seis. Para dez cordas, o valor esperado é exatamente quinze intersecções, enquanto para cem cordas, o valor esperado atinge mil seiscentas e cinquenta intersecções.

## Informações Complementares

1. **Joseph Louis François Bertrand** (1822–1900) foi um influente matemático francês cujo paradoxo da probabilidade geométrica, apresentado em sua obra de 1889 _Calcul des Probabilités_, reformulou a compreensão sobre a importância das medidas de Haar e da simetria invariante em problemas probabilísticos contínuos.

2. O **National Museum of Mathematics** (MoMath), localizado em Nova Iorque, é a principal instituição museológica norte-americana dedicada à divulgação pública e ao ensino avançado da matemática e de suas aplicações lúdicas e rigorosas.
