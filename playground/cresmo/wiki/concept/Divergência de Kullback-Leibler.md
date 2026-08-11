---
type: concept
content:
  - matematica
  - teoria_da_informacao/metrica
domain: teoria_da_informacao
cluster: metricas_informativas
source: 3blue1brown/GlYgs6v2YfU
aliases: ["Kullback-Leibler Divergence", "Divergência KL", "Informação Relativa"]
---
# Divergência de Kullback-Leibler

## Definição e Análise Contextual
A Divergência de Kullback-Leibler (ou Divergência KL) é uma medida assimétrica que quantifica a diferença estatística entre duas distribuições de probabilidade $P$ e $Q$.

Matematicamente, representa o número de bits adicionais desperdiçados por símbolo ao utilizar um **[[Código de Prefixo]]** otimizado para a distribuição estimada $Q$ em vez da verdadeira distribuição $P$, sendo definida como a diferença direta entre a **[[Entropia Cruzada]]** e a **[[Entropia de Shannon]]**.

## Conexões e Relações Diretas
* [[Divergência de Kullback-Leibler]] -> mede o excesso de bits em relação à -> [[Entropia de Shannon]]
* [[Divergência de Kullback-Leibler]] -> equivale à diferença entre -> [[Entropia Cruzada]] -> e -> [[Entropia de Shannon]]

## Matriz Causal e Atribuição Epistêmica
* **Causa / Premissa:** Ineficiência estrutural decorrente da discrepância entre o modelo de probabilidade assumido e a realidade estatística da fonte.
* **Efeito / Impacto:** Métrica padrão para otimização de modelos variacionais (VAEs), alinhamento RLHF e cálculo de perda em inteligência artificial.
* **Atribuição Epistêmica:** Solomon Kullback e Richard Leibler (1951)

## Redes de Conexão e Contexto Cruzado
* **Precursores e Ancestralidade:** **[[Informação de Shannon]]** e entropia relativa de Ralph Hartley
* **Eventos Laterais e Paralelos:** Teoria de decisão bayesiana e estatística de informação
* **Desdobramentos e Posteridade:** Aplicação na **[[Destilação de Conhecimento]]** e treinamento de LLMs