import pandas as pd

def gerar_frequencias_pitagoricas(f_fundamental=440.0):
    f_fundamental = 1.0
    notas = {'Dó': f_fundamental}
    
    # Geracao de 6 notas a partir das quintas puras (Sol, Ré, Lá, Mi, Si, Fa#)
    quintas = ['Sol', 'Ré', 'Lá', 'Mi', 'Si', 'Fa#']
    f_atual = f_fundamental
    for nome in quintas:
        f_atual = f_atual * (3.0 / 2.0)
        while f_atual >= 2.0 * f_fundamental:
            f_atual = f_atual / 2.0
        # while f_atual < f_fundamental:
        #     f_atual = f_atual * 2.0
        notas[nome] = f_atual

    # Geracao de 5 notas a partir das quartas puras (Fá, Sib, Mib, Láb, Réb)
    quartas = ['Fá', 'Sib', 'Mib', 'Láb', 'Réb']
    f_atual = f_fundamental
    for nome in quartas:
        f_atual = f_atual * 2 * (2.0 / 3.0)
        while f_atual >= 2.0 * f_fundamental:
            f_atual = f_atual / 2.0
        # while f_atual < f_fundamental:
        #     f_atual = f_atual * 2.0
        notas[nome] = f_atual

    ordem_cromatica = ['Dó', 'Réb', 'Ré', 'Mib', 'Mi', 'Fá', 'Fa#', 'Sol', 'Láb', 'Lá', 'Sib', 'Si']
    return {k: notas[k] for k in ordem_cromatica}

def gerar_dataframe_longo(f_fundamental=440.0):
    notas_freq = gerar_frequencias_pitagoricas(f_fundamental)
    nomes = list(notas_freq.keys())
    
    formulas_modais = {
        # Modos da Escala Maior (Diatônicos)
        'Jônio / Maior': [2, 2, 1, 2, 2, 2, 1],
        'Dórico': [2, 1, 2, 2, 2, 1, 2],
        'Frígio': [1, 2, 2, 2, 1, 2, 2],
        'Lídio': [2, 2, 2, 1, 2, 2, 1],
        'Mixolídio': [2, 2, 1, 2, 2, 1, 2],
        'Eólio / Menor Natural': [2, 1, 2, 2, 1, 2, 2],
        'Lócrio': [1, 2, 2, 1, 2, 2, 2],

        # Modos da Escala Menor Harmônica
        'Menor Harmônica': [2, 1, 2, 2, 1, 3, 1],
        'Lócrio 6M / Lócrio 13': [1, 2, 2, 1, 3, 1, 2],
        'Jônio #5': [2, 2, 1, 3, 1, 2, 1],
        'Dórico #4 / Dórico #11': [1, 2, 3, 1, 2, 1, 2],
        'Frígio Maior / Frígio Dominante': [1, 3, 1, 2, 1, 2, 2],
        'Lídio #2': [3, 1, 2, 1, 2, 2, 1],
        'Ultralócrio / Diminuto b4': [1, 2, 1, 2, 2, 1, 3],

        # Modos da Escala Menor Melódica (ascendente)
        'Menor Melódica (asc.)': [2, 1, 2, 2, 2, 2, 1],
        'Dórico b2 / Dórico b9': [1, 2, 2, 2, 2, 1, 2],
        'Lídio Aumentado / Lídio #5': [2, 2, 2, 2, 1, 2, 1],
        'Lídio Dominante / Lídio b7': [2, 2, 2, 1, 2, 1, 2],
        'Mixolídio b6 / Mixolídio b13': [2, 2, 1, 2, 1, 2, 2],
        'Lócrio 9M / Lócrio #2': [1, 2, 2, 1, 2, 2, 2],
        'Superlócrio / Modo Alterado': [1, 2, 1, 2, 2, 2, 2],

        # Escalas Simétricas e Sintéticas
        'Tons Inteiros / Hexafônica': [2, 2, 2, 2, 2, 2],
        'Diminuta (Tom-Semitom)': [2, 1, 2, 1, 2, 1, 2, 1],
        'Dominante Diminuta (Semitom-Tom)': [1, 2, 1, 2, 1, 2, 1, 2],

        # Escalas Pentatônicas e Blues
        'Pentatônica Maior': [2, 2, 3, 2, 3],
        'Pentatônica Menor': [3, 2, 2, 3, 2],
        'Blues': [3, 2, 1, 1, 3, 2],

        # Escalas Bebop
        'Bebop Maior': [2, 2, 1, 2, 1, 1, 2, 1],
        'Bebop Dominante': [2, 2, 1, 2, 2, 1, 1, 1],
        'Bebop Menor': [2, 1, 1, 1, 2, 2, 1, 2]
    }

    formulas_acordes = {
        # Tríades Fundamentais
        'Acorde Maior': [2.0, 3.5],
        'Acorde Menor': [1.5, 3.5],
        'Diminuta': [1.5, 3.0],
        'Aumentada': [2.0, 4.0],
        'Suspensão por Quarta': [2.5, 3.5],
        'Suspensão por Segunda': [1.0, 3.5],

        # Acordes com Sexta
        'Maior com Sexta': [2.0, 3.5, 4.5],
        'Menor com Sexta': [1.5, 3.5, 4.5],

        # Tétrades Fundamentais
        'Maior com Sétima Maior': [2.0, 3.5, 5.5],
        'Dominante (Sétima Menor)': [2.0, 3.5, 5.0],
        'Menor com Sétima': [1.5, 3.5, 5.0],
        'Menor com Sétima Maior': [1.5, 3.5, 5.5],
        'Meio-Diminuta (Menor com Sétima e Quinta Diminuta)': [1.5, 3.0, 5.0],
        'Diminuta Completa (Sétima Diminuta)': [1.5, 3.0, 4.5],
        'Aumentada com Sétima Maior': [2.0, 4.0, 5.5],
        'Aumentada com Sétima Menor': [2.0, 4.0, 5.0],
        'Dominante com Quinta Diminuta': [2.0, 3.0, 5.0],
        'Dominante Suspenso': [2.5, 3.5, 5.0],

        # Acordes Estendidos (Extensões Diatônicas)
        'Maior com Nona': [2.0, 3.5, 5.5, 7.0],
        'Dominante com Nona': [2.0, 3.5, 5.0, 7.0],
        'Menor com Nona': [1.5, 3.5, 5.0, 7.0],
        'Maior com Décima Primeira': [2.0, 3.5, 5.5, 7.0, 8.5],
        'Dominante com Décima Primeira': [2.0, 3.5, 5.0, 7.0, 8.5],
        'Menor com Décima Primeira': [1.5, 3.5, 5.0, 7.0, 8.5],
        'Maior com Décima Terceira': [2.0, 3.5, 5.5, 7.0, 8.5, 10.5],
        'Dominante com Décima Terceira': [2.0, 3.5, 5.0, 7.0, 8.5, 10.5],
        'Menor com Décima Terceira': [1.5, 3.5, 5.0, 7.0, 8.5, 10.5],

        # Acordes Dominantes Alterados
        'Dominante com Nona Menor': [2.0, 3.5, 5.0, 6.5],
        'Dominante com Nona Aumentada': [2.0, 3.5, 5.0, 7.5],
        'Dominante com Décima Primeira Aumentada': [2.0, 3.5, 5.0, 7.0, 9.0],
        'Dominante com Décima Terceira Menor': [2.0, 3.5, 5.0, 7.0, 10.0]
    }

    
    graus_rotulos = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    registros = []

    for tom in nomes:
        idx_base = nomes.index(tom)
        for modo, passos in formulas_modais.items():
            escala = []
            idx = idx_base
            for step in [0] + passos[:-1]:
                idx = (idx + step) % 12
                escala.append(nomes[idx])
            
            for i, tonica_grau in enumerate(escala):
                grau_label = graus_rotulos[i]
                idx_g = nomes.index(tonica_grau)
                
                for nome_acorde, distancias in formulas_acordes.items():
                    vozes = [tonica_grau]
                    for d in distancias:
                        semitons = int(round(d * 2))
                        idx_voz = (idx_g + semitons) % 12
                        vozes.append(nomes[idx_voz])
                    
                    registros.append({
                        'Tônica Fundamental': tom,
                        'Frequência Fundamental (Hz)': round(notas_freq[tom], 2),
                        'Modo': modo,
                        'Grau': grau_label,
                        'Nota do Grau': tonica_grau,
                        'Frequência do Grau (Hz)': round(notas_freq[tonica_grau], 2),
                        'Tipo de Acorde': nome_acorde,
                        'Notas do Acorde': ' '.join(vozes)
                    })
                
    return pd.DataFrame(registros)

if __name__ == '__main__':
    # f0 = float(input('Digite a frequência fundamental para Dó (padrão 440): ') or 440.0)
    f0 = 440.0
    df_longo = gerar_dataframe_longo(f0)
    
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print(df_longo.info())
    print(df_longo.head(20).to_string())
    
    df_longo.to_csv('sistema_harmonica_longo.csv', index=False, encoding='utf-8-sig')