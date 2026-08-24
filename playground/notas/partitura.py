from weasyprint import HTML

def gerar_svg_partitura(notas_acorde=["Dó", "Mi", "Sol"], cifra="C"):
    posicoes_y = {
        "Dó": 100, "Réb": 95, "Ré": 95, "Mib": 90, "Mi": 90,
        "Fá": 85, "Fa#": 85, "Sol": 80, "Láb": 75, "Lá": 75,
        "Sib": 70, "Si": 70
    }
    
    acidentes = {
        "Réb": "♭", "Mib": "♭", "Láb": "♭", "Sib": "♭", "Fa#": "♯"
    }

    pulsos_x = [200, 320, 440, 560]
    elementos_acordes = []

    for i, x in enumerate(pulsos_x, start=1):
        bloco = f'<g transform="translate({x}, 0)">\n'
        for nota in notas_acorde:
            y = posicoes_y.get(nota, 100)
            if y >= 100:
                bloco += f'  <line x1="-12" y1="{y}" x2="14" y2="{y}" stroke="#1a1a1a" stroke-width="1.2"/>\n'
            bloco += f'  <ellipse cx="0" cy="{y}" rx="6.5" ry="4.5" fill="#1a1a1a" transform="rotate(-20 0 {y})"/>\n'
            if nota in acidentes:
                bloco += f'  <text x="-16" y="{y + 4}" font-size="14" font-family="serif" fill="#1a1a1a">{acidentes[nota]}</text>\n'

        y_min = min(posicoes_y.get(n, 100) for n in notas_acorde)
        y_max = max(posicoes_y.get(n, 100) for n in notas_acorde)
        y_topo = y_min - 38
        bloco += f'  <line x1="6" y1="{y_max}" x2="6" y2="{y_topo}" stroke="#1a1a1a" stroke-width="1.3"/>\n'
        bloco += f'  <text x="0" y="28" font-size="11" font-family="sans-serif" font-weight="bold" text-anchor="middle" fill="#1a2a3a">{cifra}</text>\n'
        bloco += f'  <text x="0" y="130" font-size="10" font-family="sans-serif" text-anchor="middle" fill="#4a5568">{i}º Tempo</text>\n'
        bloco += '</g>\n'
        elementos_acordes.append(bloco)

    acordes_svg_str = "".join(elementos_acordes)

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 180" width="100%" height="180">
        <g stroke="#1a1a1a" stroke-width="1.2">
            <line x1="30" y1="50" x2="670" y2="50"/>
            <line x1="30" y1="60" x2="670" y2="60"/>
            <line x1="30" y1="70" x2="670" y2="70"/>
            <line x1="30" y1="80" x2="670" y2="80"/>
            <line x1="30" y1="90" x2="670" y2="90"/>
        </g>
        <line x1="30" y1="50" x2="30" y2="90" stroke="#1a1a1a" stroke-width="2"/>
        <g transform="translate(42, 38) scale(0.042)" fill="#1a1a1a">
            <path d="M433.9 1461.4 c-29.6 -18.7 -57.4 -53.4 -67.4 -83.9 -11 -33.9 -11.5 -73.6 -2.3 -186.5 6.1 -75.3 11.8 -181.5 12.8 -236 1.7 -94.7 -0.4 -103.4 -28.5 -121.5 -61.2 -39.4 -133.5 -133.9 -154.5 -201.7 -16 -51.5 -11.3 -128.4 11.2 -185.3 46.5 -117.8 147.2 -191.5 272.2 -200.5 45.3 -3.2 100.8 12.7 137.5 39.4 69.1 50.4 104.1 138.8 91.1 230.1 -11.6 81.3 -69.2 153.2 -146.5 183 -46.7 18 -108.6 15.6 -148.9 -5.9 -19.9 -10.6 -25.6 -11 -25.6 -1.7 0 10.9 44.5 56.4 75 76.5 42 27.7 97.4 43.4 153.8 43.4 34.1 0 45.4 -3.6 77 -24.3 64.9 -42.6 101.4 -115.1 101.4 -201.5 0 -84.2 -33.7 -160.8 -94.2 -214.2 -71.2 -62.9 -168.1 -86.5 -260.7 -63.5 -122.9 30.6 -226.3 147.5 -254 286.9 -18.2 91.6 -3.8 190.5 39.8 274.6 27.3 52.6 77.4 113.8 121.2 148 40.5 31.6 42.4 35.8 38.6 85.9 -2.5 32.7 -8.2 136.2 -12.7 230 -8.4 171.7 -11.8 190.7 -32.8 184.2 -12.2 -3.7 -14.6 -15.4 -34.6 -162.7 -16.8 -124 -24.4 -153.1 -45.5 -173.8 -40.1 -39.4 -103.7 -39.8 -144.3 -0.8 -41.3 39.6 -44.5 98.7 -8.6 156.4 36.3 58.4 100.3 84.7 172.9 70.9 30.7 -5.9 49.3 -17.6 70.4 -44.3 11.2 -14.2 21.8 -25.9 23.5 -25.9 1.7 0 5.1 27.2 7.6 60.5 4.8 63.8 18.2 108.6 47 157.2 38.7 65.5 106.8 116.8 174.6 131.6 37 8 72 2.7 107.5 -16.4 56.5 -30.4 86.8 -87.8 80.7 -152.9 -5.9 -62.6 -44.2 -116 -98.3 -137 -28.9 -11.2 -75.9 -12.3 -102.8 -2.4z"/>
        </g>
        <g font-family="serif" font-weight="bold" font-size="28" fill="#1a1a1a" text-anchor="middle">
            <text x="112" y="70">4</text>
            <text x="112" y="90">4</text>
        </g>
        {acordes_svg_str}
        <line x1="662" y1="50" x2="662" y2="90" stroke="#1a1a1a" stroke-width="1.2"/>
        <line x1="667" y1="50" x2="667" y2="90" stroke="#1a1a1a" stroke-width="3.5"/>
    </svg>
    """
    return svg

def gerar_partitura_pdf(notas_acorde=["Dó", "Mi", "Sol"], cifra="C", nome_arquivo="partitura_acorde_do_maior.pdf"):
    svg_code = gerar_svg_partitura(notas_acorde, cifra)
    notas_formatadas = " - ".join(notas_acorde)
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
@page {{
    size: A4 portrait;
    margin: 20mm 20mm;
    background-color: #fcfbf9;
}}
* {{ box-sizing: border-box; }}
body {{
    margin: 0; padding: 0;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #1a1a1a;
    background-color: #fcfbf9;
}}
.header {{
    text-align: center;
    margin-bottom: 28px;
    border-bottom: 2px solid #2b3a4a;
    padding-bottom: 14px;
}}
h1 {{
    font-size: 19pt;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin: 0 0 6px 0;
    color: #1a2a3a;
}}
.subtitle {{ font-size: 11pt; color: #4a5568; margin: 0; }}
.score-card {{
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 25px 20px;
}}
.meta-info {{
    font-size: 10pt;
    color: #2d3748;
    margin-bottom: 18px;
    display: table;
    width: 100%;
}}
.meta-cell {{ display: table-cell; width: 50%; }}
.meta-right {{ text-align: right; }}
.svg-container {{ width: 100%; text-align: center; }}
</style>
</head>
<body>
<div class="header">
    <h1>ESTUDO HARMÔNICO EM PARTITURA</h1>
    <p class="subtitle">Compasso Quaternário (4/4) com Cadência em Semínimas</p>
</div>
<div class="score-card">
    <div class="meta-info">
        <div class="meta-cell"><strong>Acorde:</strong> {cifra} ({notas_formatadas})</div>
        <div class="meta-cell meta-right"><strong>Fórmula:</strong> 4/4 | <strong>Andamento:</strong> Moderato</div>
    </div>
    <div class="svg-container">
        {svg_code}
    </div>
</div>
</body>
</html>
"""
    HTML(string=html).write_pdf(nome_arquivo)

if __name__ == '__main__':
    gerar_partitura_pdf(["Dó", "Mi", "Sol"], "C", "partitura_acorde_do_maior.pdf")