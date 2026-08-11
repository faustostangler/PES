---
type: process
content:
  - ia
  - aprendizado_de_maquina/otimizacao
domain: inteligencia_artificial
cluster: treinamento_de_modelos
source: 3blue1brown/GlYgs6v2YfU
aliases: ["Knowledge Distillation", "Destilação de Modelos", "Professor-Estudante"]
---
# Destilação de Conhecimento

## Definição e Análise Contextual
A Destilação de Conhecimento é uma técnica de treinamento em aprendizado profundo na qual um modelo compacto (estudante) é treinado para replicar a distribuição de probabilidade suave de um modelo maior e mais complexo (professor).

Em vez de ser treinado apenas com rótulos discretos rígidos, o modelo estudante minimiza a **[[Entropia Cruzada]]** ou a **[[Divergência de Kullback-Leibler]]** em relação às previsões do modelo professor, absorvendo as incertezas e inter-relações entre classes.

## Conexões e Relações Diretas
* [[Destilação de Conhecimento]] -> utiliza a -> [[Entropia Cruzada]]
* [[Destilação de Conhecimento]] -> minimiza a -> [[Divergência de Kullback-Leibler]]

## Matriz Causal e Atribuição Epistêmica
* **Causa / Premissa:** Necessidade de implantar modelos de alto desempenho com baixa latência e consumo reduzido de memória em inferência.
* **Efeito / Impacto:** Compressão de parâmetros preservando a precisão preditiva do modelo maior.
* **Atribuição Epistêmica:** Geoffrey Hinton, Oriol Vinyals e Jeff Dean (2015)

## Redes de Conexão e Contexto Cruzado
* **Precursores e Ancestralidade:** Compressão de modelos de Cristian Buciluǎ (2006)
* **Eventos Laterais e Paralelos:** Quantização de pesos e poda de redes neurais (Pruning)
* **Desdobramentos e Posteridade:** Modelos de linguagem eficientes para dispositivos móveis