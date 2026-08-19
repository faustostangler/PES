import cProfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd
import pstats
import random
import time


def profiler(metodo):
  t0 = time.perf_counter()
  profiler = cProfile.Profile()
  profiler.runcall(metodo)
  stats = pstats.Stats(profiler)

  data = [
      {
          "metodo": getattr(metodo, "__name__", str(metodo)),
          "funcao": nome_func,
          "arquivo": arquivo.split("/")[-1],
          "linha": linha,
          "ncalls": nc,
          "tottime": tt,
          "cumtime": ct,
          "percall_cumtime": ct / nc if nc > 0 else 0,
      }
      for (arquivo, linha, nome_func), (cc, nc, tt, ct, _) in stats.stats.items()
  ]
  t1 = time.perf_counter()
  return pd.DataFrame(data).sort_values(by="cumtime", ascending=False).reset_index(drop=True), t1-t0


colecao = [1, 2, 3, 5, 8][::-1]
limite = max(32, len(colecao)+1)
def processar(item):
  jitter = random.uniform(0, item/1)
  time.sleep(item)
  res = item ** 2
  print(item, res)
  return res


# Padrão 1: Execução sem Retorno (Efeito Colateral)
# síncrono
def metodo_s1():
  resultados = []
  for item in colecao:
    res = processar(item)
    resultados.append(res)
  print(resultados)
  return resultados


# Padrão 1: Execução sem Retorno (Efeito Colateral)
# assíncrono
def metodo_a1(): 
  with ThreadPoolExecutor(max_workers=limite) as executor:
    resultados = (list(executor.map(processar, colecao)))
  print(resultados)
  return resultados

# Padrão 2: Coleta Ordenada de Resultados
# síncrono
def metodo_s2():
  resultados = []
  for item in colecao:
    res = processar(item)
    resultados.append(res)
  print(resultados)
  return resultados

# Padrão 2: Coleta Ordenada de Resultados
# assíncrono
def metodo_a2():
  with ThreadPoolExecutor(max_workers=limite) as executor:
    resultados = list(executor.map(processar, colecao))
  print(resultados)
  return resultados

# Padrão 3: Processamento Conforme a Conclusão (Out-of-Order)
# síncrono : impossível, porque a ordem é determinística
def metodo_s3():
  resultados = []
  for item in colecao:
    res = processar(item)
    resultados.append(res)
  print(resultados)
  return resultados


# Padrão 3: Processamento Conforme a Conclusão (Out-of-Order)
# assíncrono : impossível, porque a ordem é determinística
def metodo_a3():
  resultados = []
  with ThreadPoolExecutor(max_workers=limite) as executor:
    futures = [executor.submit(processar, item) for item in colecao]
    resultados = [future.result() for future in as_completed(futures)]
  print(resultados)
  return resultados

df_s1, tempo_s1 = profiler(metodo_s1)
df_a1, tempo_a1 = profiler(metodo_a1)
df_s2, tempo_s2 = profiler(metodo_s2)
df_a2, tempo_a2 = profiler(metodo_a2)
df_s3, tempo_s3 = profiler(metodo_s3)
df_a3, tempo_a3 = profiler(metodo_a3)

df = pd.concat([df_s1, df_a1, df_s2, df_a2, df_s3, df_a3])
df_tempo = pd.DataFrame([
  {"metodo": "metodo_s1", "tempo": tempo_s1},
  {"metodo": "metodo_a1", "tempo": tempo_a1},
  {"metodo": "metodo_s2", "tempo": tempo_s2},
  {"metodo": "metodo_a2", "tempo": tempo_a2},
  {"metodo": "metodo_s3", "tempo": tempo_s3},
  {"metodo": "metodo_a3", "tempo": tempo_a3},
])
output_path = Path(__file__).parent / "saida_profiler.csv"
df.to_csv(output_path, index=False)
print(df_tempo)


# Concorrência, Latência e Orquestração: Uma Análise do Modelo Multithreading em PythonA eficiência de um sistema computacional depende da forma como o tempo de espera é administrado pelo fluxo de controle. Em tarefas limitadas por operações de entrada e saída (E/S ou I/O-bound), como chamadas de rede, consultas a banco de dados ou pausas explícitas de temporização, a CPU permanece ociosa a maior parte do tempo.O paradigma de execução multithreading permite sobrepor esses períodos de inatividade, transformando sequências aditivas de bloqueio em processamento simultâneo.A Analogia dos Balcões de AtendimentoConsidere uma agência de correios que precisa atender cinco clientes cujos pacotes demandam tempos diferentes de conferência: 8 minutos, 5 minutos, 3 minutos, 2 minutos e 1 minuto.Modelo Síncrono (Um único atendente): O atendente processa o primeiro cliente durante 8 minutos, depois o segundo por 5 minutos, e assim sucessivamente. Os demais aguardam em fila única. O tempo total decorrido é a soma aritmética de todas as durações ($8 + 5 + 3 + 2 + 1 = 19$ minutos).Modelo Multithreading (Múltiplos atendentes em paralelo): A agência abre cinco balcões simultâneos e encaminha todos os clientes ao mesmo tempo no instante zero. O cliente com demanda de 1 minuto é liberado primeiro, seguido pelos de 2, 3, 5 e 8 minutos. O tempo total da agência é delimitado pelo cliente mais demorado (8 minutos).Essa dinâmica governa a diferença fundamental entre as abordagens analisadas nos experimentos empíricos.Os Três Padrões ArquiteturaisA manipulação concorrente em Python através do módulo concurrent.futures divide-se em três padrões fundamentais de despacho e consumo.1. Execução Síncrona SequencialNo modelo sequencial tradicional, a iteração sobre a coleção [8, 5, 3, 2, 1] força o interpretador a suspender a execução a cada elemento:Pythonresultados = []
# for item in colecao:
#     time.sleep(item)
#     res = item ** 2
#     resultados.append(res)
# O custo temporal acumula-se de forma aditiva:$$\text{Tempo Total}_{\text{síncrono}} = \sum_{i=1}^{n} t_i$$No teste determinístico com pausas fixas iguais a cada elemento, o tempo final atinge rigorosamente 19,00 segundos. A ordem de emissão dos resultados no terminal e o preenchimento do vetor de saída preservam exatamente a sequência original de iteração: [64, 25, 9, 4, 1].2. Mapeamento Concorrente com Preservação Posicional (executor.map)O método executor.map() delega o lote de tarefas para a pool de threads operárias, mantendo um iterador associado aos índices originais da coleção de entrada:Pythonwith ThreadPoolExecutor(max_workers=limite) as executor:
#     resultados = list(executor.map(processar, colecao))
# Quando a capacidade da pool atende a todos os elementos simultaneamente (limite >= 5), todas as cinco threads iniciam seus cálculos no instante zero. A conclusão das tarefas ocorre em ordem estritamente crescente de duração real (1s, 2s, 3s, 5s, 8s), como evidenciado pelos prints intermediários:Plaintext1 1
# 2 4
# 3 9
# 5 25
# 8 64
# Apesar da resolução física ocorrer fora de ordem, a função list(executor.map(...)) reconstrói o vetor final garantindo que o retorno do elemento original $8$ ocupe a primeira posição:Plaintext[64, 25, 9, 4, 1]
# O tempo total de parede colapsa para a tarefa de maior latência ($\max(8, 5, 3, 2, 1) = \mathbf{8,00\text{ s}}$).Bloqueio em Cabeça de Fila (Head-of-Line Blocking): Caso o consumidor acesse o iterador sequencialmente, o primeiro valor só será liberado após 8 segundos, ainda que os retornos dos itens 1, 2, 3 e 5 já estejam calculados e armazenados em memória nos segundos iniciais.3. Consumo por Prontidão de Conclusão (as_completed)Quando a aplicação necessita persistir dados, alimentar filas secundárias ou enviar pacotes pela rede assim que qualquer cálculo individual fica pronto, o bloqueio em cabeça de fila torna-se um gargalo indesejado.O padrão as_completed resolve essa restrição consumindo as instâncias de Future na ordem cronológica em que são finalizadas:Pythonwith ThreadPoolExecutor(max_workers=limite) as executor:
#     futures = [executor.submit(processar, item) for item in colecao]
#     resultados = [future.result() for future in as_completed(futures)]
# Nesse arranjo, o vetor de saída reflete a ordem real de resolução temporal:Plaintext[1, 4, 9, 25, 64]
# O tempo total permanece delimitado pelo caminho crítico ($\mathbf{8,00\text{ s}}$), porém a latência inicial de consumo cai de 8 segundos para apenas 1 segundo, momento em que o primeiro elemento útil já é disponibilizado para o restante da aplicação.