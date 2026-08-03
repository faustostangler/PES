<config_file>
# Execução de Modelos de Linguagem Compactos (TLMs) e Agentes em Dispositivos de Borda com LiteRT-LM

## Contexto e Visão Geral

Na conferência de engenharia de inteligência artificial de 2026, **Cormac Brick**, líder técnico do **Google AI Edge**, apresentou a arquitetura e as estratégias de implantação de modelos de linguagem compactos (_Tiny LLMs_ ou TLMs) em dispositivos móveis e sistemas embarcados. Utilizando o ambiente de execução **LiteRT-LM** (evolução do _TensorFlow Lite_) e a família de modelos **Gemma 4**, a palestra detalhou como viabilizar a execução local de agentes autônomos sob restrições estritas de memória RAM (abaixo de 1 GB) e latência reduzida.

A apresentação explorou os dois paradigmas concorrentes da IA móvel — inteligência artificial em nível de sistema (_System-level GenAI_) versus inteligência artificial incorporada a aplicativos (_In-app GenAI_) —, demonstrando a aplicação de decodificação restrita (_constrained decoding_) e revelação progressiva (_progressive disclosure_) para a chamada de ferramentas em dispositivos móveis.

---

## 1. Paradigmas de Inteligência Artificial em Dispositivos de Borda

A implementação de modelos de linguagem em hardware móvel divide-se em duas abordagens estruturais distintas de distribuição e uso de recursos de hardware.

### 1.1 IA em Nível de Sistema (System-level GenAI)

Modelos residentes no sistema operacional (como o _AI Core_ no _Android_ ou o _Apple Intelligence_ no _iOS_):
* **Escala de Parâmetros**: Redes neurais entre 2 e 5 bilhões de parâmetros (como as variantes **Gemma 4 E2B** e **Gemma 4 E4B**) pré-carregadas na memória RAM do dispositivo.
* **Mapeamento Efetivo de Parâmetros**: Otimização onde a tabela de incorporação por camada (_Per-Layer Embedding_ ou PLE) permanece mapeada em disco, carregando apenas as linhas estritamente necessárias para a inferência auto-regressiva e preservando a memória volátil do aparelho.

### 1.2 IA Incorporada ao Aplicativo (In-app GenAI) e Modelos Ultracompactos (TLMs)

Modelos de escopo restrito distribuídos diretamente junto com o pacote da aplicação:
* **Escala Ultracompacta**: Redes especializadas situadas entre 100 e 500 milhões de parâmetros.
* **Necessidade de Ajuste Fino (Fine-tuning)**: Modelos abaixo de 500M exigem treinamento dedicado para tarefas específicas (como transcrição de áudio, extração de entidades ou comandos de voz para ação), garantindo índices de confiabilidade de 85% a 90% em produção sem consumir a RAM do sistema.

---

## 2. A Arquitetura do Ambiente de Execução LiteRT-LM e Desempenho

O **LiteRT-LM** consolida o modelo, o tokenizador e os operadores de inferência em um único arquivo empacotado cross-platform (`.tflite` / `.pb`).

### 2.1 Suporte Multiplataforma e Otimização de Hardware

* **Portabilidade de Binários**: O mesmo pacote de modelo executa nativamente em sistemas _Android_, _iOS_, _macOS_, _Windows_, _Linux_ e sistemas embarcados.
* **Aceleração por Hardware**: Execução direta em unidades de processamento gráfico (GPU) e processadores neurais (NPU). Em placas como o _Raspberry Pi 5_, o modelo **Gemma 4 E2B** atinge 13,3 tokens por segundo via CPU, enquanto aceleradores dedicados de NPU expandem a taxa de transferência para milhares de tokens por segundo em smartphones de ponta.

---

## 3. Arquitetura de Habilidades para Agentes Móveis (Agent Skills)

A implementação de agentes autônomos em dispositivos com memória limitada exige um protocolo de carregamento sob demanda para impedir que a janela de contexto seja saturada por especificações de ferramentas.

### 3.1 Revelação Progressiva de Ferramentas (Progressive Disclosure)

Inspirado em abordagens modulares de context engineering, o **Google AI Gallery** adota uma estrutura em três camadas:
1. **Resumo Metadados**: O prompt do sistema contém apenas uma linha descritiva de cada habilidade disponível (por exemplo, consulta à _Wikipédia_, rastreamento de humor ou integração com mapas).
2. **Carregamento Condicional (`load_skill`)**: Se a intenção do usuário exigir a ferramenta, o agente aciona a função interna `load_skill` para injetar o arquivo `skill.md` correspondente na janela de contexto ativa.
3. **Execução de Scripts Locais**: O agente executa rotinas em _JavaScript_ em um ambiente isolado local ou aciona intenções nativas do sistema operacional (_Android Intents_).

### 3.2 Decodificação Restrita (Constrained Decoding)

Para evitar erros sintáticos durante o disparo de funções externas, o runtime do **LiteRT-LM** aplica uma máscara de decodificação no nível dos logits durante a fase de geração de argumentos. Essa restrição força a saída do modelo a seguir estritamente o esquema JSON predefinido para a ferramenta selecionada.

---

## Notas Informativas

1. **LiteRT-LM**: Ambiente de execução de inferência de baixa latência do Google otimizado para modelos de linguagem grandes e multimodais em dispositivos móveis e embarcados.
2. **Gemma 4 (E2B / E4B)**: Família de modelos fundacionais abertos desenvolvidos pela **Google DeepMind**, otimizados para execução local em hardware móvel e laptops de consumo.
3. **Android Intents**: Mecanismo de comunicação assíncrona do sistema operacional **Android** que permite a uma aplicação solicitar ações de outros componentes ou serviços do sistema.
</config_file>
