---
type: concept
content:
  - computacao
  - teoria_da_informacao/codificacao
domain: teoria_da_informacao
cluster: compressao_de_dados
source: 3blue1brown/l6DKRf-fAAM
aliases: ["Prefix Code", "Código Livre de Prefixo"]
---
# Código de Prefixo

## Definição e Análise Contextual
O Código de Prefixo (ou Código Livre de Prefixo) é um sistema de codificação de tamanho variável no qual nenhuma palavra-código é prefixo de qualquer outra palavra-código válida no dicionário.

Essa restrição topológica garante decodificação unívoca instantânea sem a necessidade de caracteres delimitadores, sendo fundamental para algoritmos de compressão de dados como a Codificação de Huffman e a codificação aritmética. No problema da transmissão de comandos a um robô espacial com distribuições de probabilidade desiguais (1/2, 1/4, 1/8, 1/8), o código de prefixo ótimo atinge exatamente 1.75 bits por instrução.

## Conexões e Relações Diretas
* [[Código de Prefixo]] -> evita ambiguidades em -> [[Entropia de Shannon]]
* [[Código de Prefixo]] -> deve satisfazer a -> [[Desigualdade de Kraft-McMillan]]
* [[Claude Shannon]] -> utilizou o -> [[Código de Prefixo]] -> no -> [[1948 Teorema da Codificação Sem Ruído]]

## Matriz Causal e Atribuição Epistêmica
* **Causa / Premissa:** Eliminação de ambiguidades na leitura sequencial de fluxos binários de tamanho variável.
* **Efeito / Impacto:** Maximização da taxa de compressão aproximando o tamanho da palavra-código do conteúdo informativo do símbolo.
* **Atribuição Epistêmica:** [[Claude Shannon]] e David Huffman

## Redes de Conexão e Contexto Cruzado
* **Precursores e Ancestralidade:** Código Morse e codificação ASCII de tamanho fixo
* **Eventos Laterais e Paralelos:** Árvores binárias de busca, [[Desigualdade de Kraft-McMillan]] e representação de linguagens formais
* **Desdobramentos e Posteridade:** Aplicação em compressores modernos de texto e imagens