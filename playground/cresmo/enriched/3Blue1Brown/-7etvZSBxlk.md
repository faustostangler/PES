# A Medição Experimental da Entropia da Linguagem e a Redundância do Inglês

## A Evolução dos Experimentos Preditivos de Shannon

A determinação da compressibilidade fundamental da linguagem natural exigiu ultrapassar a simples análise estatística de frequência de símbolos isolados. Nas fases iniciais de sua pesquisa no final da década de **1940**, **Claude Shannon** tentou calcular as probabilidades de ocorrência de novos caracteres tabulando sequências curtas conhecidas como _n-grams_. No entanto, esse método puramente estatístico revelou-se ineficaz para janelas de contexto amplas, nas quais combinações inéditas de texto nunca ocorriam nos corpora literários analisados, embora o contexto longo torne a linguagem humana substancialmente mais previsível e compressível.

Para contornar essa limitação de dados brutos, Shannon desenvolveu experimentos preditivos utilizando a capacidade cognitiva humana como modelo probabilístico subjacente. Em um primeiro experimento informal com sua esposa, **Betty Shannon**, ele solicitava a adivinhação sequencial de cada letra de um texto impresso. Os acertos eram substituídos por traços no texto reduzido, demonstrando qualitativamente que a previsibilidade estrutural permitia eliminar redundâncias sem perda de conteúdo informativo, desde que um sistema preditivo equivalente estivesse disponível para a decodificação.

## O Estudo de 1950 e o Limite de Um Bit por Caractere

Em seu trabalho seminal de **1951** intitulado _Prediction and Entropy of Printed English_ (cujos experimentos foram desenhados em **1950**), Shannon aprimorou o método experimental ao entrevistar grupos de sujeitos humanos. Em vez de registrar apenas o acerto ou erro, Shannon anotava rigorosamente o número de tentativas necessárias para que o sujeito adivinhasse a letra seguinte correta. Mapeando a distribuição estatística do número de palpites para probabilidades implícitas de ocorrência, ele formulou o cálculo formal da **taxa de entropia** para processos estocásticos de linguagem.

Os resultados revelaram que, dispondo de uma janela de contexto de pelo menos cem caracteres anteriores, o inglês impresso possui uma entropia de aproximadamente um bit por caractere. Essa taxa reduzida evidencia uma redundância linguística superior a setenta e cinco por cento. Sete décadas após as investigações de Shannon, a compressão computacional prática que se aproxima desse limite ideal deixou de ser uma simples sonda da inteligência humana para se tornar a base da engenharia de redes neurais e Grandes Modelos de Linguagem, onde a minimização da **entropia cruzada** equivale à construção de compressores de dados ótimos.

## Informações Complementares

1. **Mary Elizabeth Moore Shannon** (conhecida como Betty Shannon, 1916–2017) foi uma matemática e pesquisadora norte-americana que colaborou com seu marido Claude Shannon em diversos experimentos práticos e na construção de dispositivos automatizados na Bell Labs.

2. A **taxa de entropia** de um processo estocástico representa o limite assintótico da quantidade média de informação emitida por símbolo à medida que o comprimento do contexto tende ao infinito.
