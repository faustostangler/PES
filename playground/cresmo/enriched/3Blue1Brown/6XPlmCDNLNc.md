# O Enigma dos 64 Cubos de Açúcar e o Princípio das Gavetas de Dirichlet

## A Formulação da Olimpíada Britânica de Matemática e a Discretização Espacial

O problema dos sessenta e quatro cubos de açúcar origina-se de uma questão da **Olimpíada Britânica de Matemática de 2024** (_British Mathematical Olympiad_), apresentada na série de desafios mensais do **National Museum of Mathematics** (MoMath). O enigma considera um bloco cúbico tridimensional composto por sessenta e quatro posições discretas arranjadas em uma grade de quatro por quatro por quatro. Cada cubo individual é colorido arbitrariamente com uma de três cores disponíveis: branco, azul ou castanho.

O desafio matemático consiste em provar rigorosamente que, independentemente da distribuição de cores atribuída às sessenta e quatro posições, é sempre inevitável encontrar seis pares distintos de cubos (totalizando doze cubos individuais distintos) que compartilhem a mesma cor exata e cujos centros guardem distâncias euclidianas rigorosamente idênticas entre si.

## A Aplicação do Princípio do Pombal e a Combinatória Extremal

A demonstração da inevitabilidade estrutural desse padrão baseia-se na aplicação combinada do **Princípio das Gavetas de Dirichlet** (ou Princípio do Pombal) e da **Combinatória Extremal**. Pela versão generalizada do princípio das gavetas, ao partição dos sessenta e quatro cubos em apenas três classes de cores, pelo menos uma das cores deve conter no mínimo vinte e dois cubos.

Com vinte e dois cubos da mesma cor, o número total de pares distintos de centros de cubos que podem ser formados é dado pela combinação de vinte e dois tomados dois a dois, resultando em duzentas e trinta e uma conexões aos pares. Em uma grade tridimensional discreta de quatro por quatro por quatro, o número de distâncias quadráticas inteiras possíveis entre quaisquer dois pontos é estritamente limitado. Aplicando novamente o Princípio das Gavetas de Dirichlet sobre o conjunto das duzentas e trinta e uma conexões distribuídas entre as poucas distâncias geométricas permitidas na grade, garante-se que pelo menos uma distância específica deve se repetir em múltiplos pares disjuntos, demonstrando a existência inescapável de seis pares disjuntos da mesma cor com distâncias equivalentes.

## Informações Complementares

1. A **Olimpíada Britânica de Matemática** (_British Mathematical Olympiad_ - BMO) é a competição nacional de matemática de alto nível para estudantes do ensino secundário no Reino Unido, organizada pela _United Kingdom Mathematics Trust_ (UKMT).

2. **Peter Gustav Lejeune Dirichlet** (1805–1859) formalizou o Princípio das Gavetas de Dirichlet em 1834 sob o nome de _Schubfachprinzip_, estabelecendo uma das ferramentas mais profundas e versáteis da combinatória extremal moderna.
