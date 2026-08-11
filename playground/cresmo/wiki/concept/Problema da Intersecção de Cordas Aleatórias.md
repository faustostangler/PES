---
type: concept
content:
  - matematica
  - probabilidade/geometria
domain: probabilidade_geometrica
cluster: geometria_estocastica
source: 3blue1brown/wGffBCfrAsE
aliases: ["Random Chords Intersection Problem", "Problema das Cordas Aleatórias"]
---
# Problema da Intersecção de Cordas Aleatórias

## Definição e Análise Contextual
O Problema da Intersecção de Cordas Aleatórias é um problema de probabilidade geométrica que pergunta qual o valor esperado de intersecções internas geradas por $N$ cordas aleatórias em um círculo.

Utilizando o modelo de pontos finais uniformemente distribuídos na circunferência, a probabilidade de que dois pares genéricos de cordas se cruzem é de 1/3, resultando em um valor esperado exatamente igual a $\frac{N(N-1)}{6}$ por **[[Linearidade da Esperança Matemática]]**.

## Conexões e Relações Diretas
* [[Problema da Intersecção de Cordas Aleatórias]] -> resolve-se com a -> [[Linearidade da Esperança Matemática]]
* [[Problema da Intersecção de Cordas Aleatórias]] -> evita o -> [[Paradoxo de Bertrand]]
* [[National Museum of Mathematics]] -> promoveu o desafio do -> [[Problema da Intersecção de Cordas Aleatórias]]

## Matriz Causal e Atribuição Epistêmica
* **Causa / Premissa:** Análise combinatória de 4 pontos discretos em um círculo produzindo 3 emparelhamentos possíveis.
* **Efeito / Impacto:** Solução de forma fechada $E[X] = 15$ para $N=10$ e $E[X] = 1650$ para $N=100$.
* **Atribuição Epistêmica:** [[3Blue1Brown]] / [[National Museum of Mathematics]]

## Redes de Conexão e Contexto Cruzado
* **Precursores e Ancestralidade:** **[[Paradoxo de Bertrand]]**
* **Eventos Laterais e Paralelos:** Problemas de interseção de segmentos em geometria computacional
* **Desdobramentos e Posteridade:** Teoria de grafos aleatórios e geometria estocástica