---
type: concept
content:
  - matematica
  - teoria_da_informacao/desigualdade
domain: teoria_da_informacao
cluster: compressao_de_dados
source: 3blue1brown/7L_eTem1SQ4
aliases: ["Kraft Inequality", "Desigualdade de Kraft", "Kraft-McMillan Inequality"]
---
# Desigualdade de Kraft-McMillan

## Definição e Análise Contextual
A Desigualdade de Kraft-McMillan é um teorema fundamental na teoria da codificação que estabelece a condição necessária e suficiente para a existência de um **[[Código de Prefixo]]** (ou código univocamente decodificável) para um dado conjunto de comprimentos de palavras-código.

Matematicamente, sobre um alfabeto binário, a desigualdade é expressa como $\sum 2^{-l_i} \le 1$, onde $l_i$ representa o comprimento da $i$-ésima palavra-código. Quando a alocação de comprimentos é perfeitamente proporcional aos logaritmos inversos das probabilidades das mensagens, a soma satura exatamente em um.

## Conexões e Relações Diretas
* [[Desigualdade de Kraft-McMillan]] -> garante a existência de um -> [[Código de Prefixo]]
* [[Desigualdade de Kraft-McMillan]] -> fundamenta o limite da -> [[Entropia de Shannon]]

## Matriz Causal e Atribuição Epistêmica
* **Causa / Premissa:** Restrição topológica da estrutura de árvores binárias onde ramificações não podem se sobrepor.
* **Efeito / Impacto:** Prova matemática da impossibilidade de criar um código de prefixo com comprimentos médios inferiores à entropia da fonte.
* **Atribuição Epistêmica:** Leon Kraft (1949) e Brockway McMillan (1956)

## Redes de Conexão e Contexto Cruzado
* **Precursores e Ancestralidade:** Árvores de decisão binárias
* **Eventos Laterais e Paralelos:** Codificação de Huffman e Codificação Aritmética
* **Desdobramentos e Posteridade:** Prova de optimalidade no **[[1948 Teorema da Codificação Sem Ruído]]**