import pandas as pd

def gerar_frequencias_pitagoricas(f_fundamental=440.0):
    notas = {'Dó': f_fundamental}
    
    # Geracao de 6 notas a partir das quintas puras (Sol, Ré, Lá, Mi, Si, Fa#)
    quintas = ['Sol', 'Ré', 'Lá', 'Mi', 'Si', 'Fa#']
    f_atual = f_fundamental
    for nome in quintas:
        f_atual = f_atual * 1.5
        while f_atual >= 2.0 * f_fundamental:
            f_atual = f_atual / 2.0
        while f_atual < f_fundamental:
            f_atual = f_atual * 2.0
        notas[nome] = f_atual

    # Geracao de 5 notas a partir das quartas puras (Fá, Sib, Mib, Láb, Réb)
    quartas = ['Fá', 'Sib', 'Mib', 'Láb', 'Réb']
    f_atual = f_fundamental
    for nome in quartas:
        f_atual = f_atual * (4.0 / 3.0)
        while f_atual >= 2.0 * f_fundamental:
            f_atual = f_atual / 2.0
        while f_atual < f_fundamental:
            f_atual = f_atual * 2.0
        notas[nome] = f_atual

    ordem_cromatica = ['Dó', 'Réb', 'Ré', 'Mib', 'Mi', 'Fá', 'Fa#', 'Sol', 'Láb', 'Lá', 'Sib', 'Si']
    return {k: notas[k] for k in ordem_cromatica}

def gerar_dataframe_longo(f_fundamental=440.0):
    notas_freq = gerar_frequencias_pitagoricas(f_fundamental)
    nomes = list(notas_freq.keys())
    
    formulas_modais = {
        'Jônio / Maior': [2, 2, 1, 2, 2, 2, 1],
        'Dórico': [2, 1, 2, 2, 2, 1, 2],
        'Frígio': [1, 2, 2, 2, 1, 2, 2],
        'Lídio': [2, 2, 2, 1, 2, 2, 1],
        'Mixolídio': [2, 2, 1, 2, 2, 1, 2],
        'Eólio / Menor Natural': [2, 1, 2, 2, 1, 2, 2],
        'Lócrio': [1, 2, 2, 1, 2, 2, 2],
        'Menor Harmônica': [2, 1, 2, 2, 1, 3, 1],
        'Menor Melódica (asc.)': [2, 1, 2, 2, 2, 2, 1]
    }
    
    formulas_acordes = {
        'Acorde Maior': [2.0, 3.5],
        'Acorde Menor': [1.5, 3.5],
        'Diminuta': [1.5, 3.0],
        'Aumentada': [2.0, 4.0],
        'Suspensão por Quarta': [2.5, 3.5],
        'Suspensão por Segunda': [1.0, 3.5],
        'Sétima Maior': [2.0, 3.5, 5.5],
        'Sétima Menor': [2.0, 3.5, 5.0],
        'Sétima Diminuta': [2.0, 3.5, 4.5]
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