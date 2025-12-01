#. . . . . Autor: Raquel
#. . . . . Data: 01/12/2024

import pdfplumber
import pandas as pd
import plotly.graph_objects as go

def limpar_texto(texto):
    if texto is None:
        return ""
    return texto.replace('\n', ' ').strip()

def pegar_valor_seguro_dLista_evitarIndex(linha, indice):
    try:
        return limpar_texto(linha[indice]) if indice < len(linha) else ""
    except:
        return ""

def eh_disciplina_valida(descricao):
    if not descricao:
        return False
    if descricao.lower() in ['sim', 'não', 'nao', '-', '']:
        return False
    if len(descricao) < 5:
        return False
    return True

def converter_nota(nota_str):
    if not nota_str or nota_str == '-':
        return None
    try:
        return float(nota_str.replace(',', '.'))
    except:
        return None

def classificar_nota(nota):
    if nota >= 9.0:
        return 'Excelente (9.0-10.0)'
    elif nota >= 8.0:
        return 'Ótimo (8.0-8.9)'
    elif nota >= 7.0:
        return 'Bom (7.0-7.9)'
    else:
        return 'Regular (6.0-6.9)'

def extrair_dados_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        primeira_pagina = pdf.pages[0]
        tabelas = primeira_pagina.extract_tables()
        
        dados_pessoais_tabela = tabelas[0]
        nome = limpar_texto(dados_pessoais_tabela[1][0]).replace('Nome:', '').strip()
        cpf = limpar_texto(dados_pessoais_tabela[1][2]).replace('CPF:', '').strip()
        sexo = limpar_texto(dados_pessoais_tabela[3][1]).replace('Sexo:', '').strip()
        
        dados_academicos_tabela = tabelas[1]
        matricula = limpar_texto(dados_academicos_tabela[1][0]).replace('Matrícula:', '').strip()
        situacao = limpar_texto(dados_academicos_tabela[1][1]).replace('Situação:', '').strip()
        curso = limpar_texto(dados_academicos_tabela[3][0]).replace('Curso:', '').strip()
        
        todas_disciplinas = []
        
        for num_pagina, pagina in enumerate(pdf.pages, start=1):
            tabelas_pagina = pagina.extract_tables()
            
            if num_pagina == 1:
                componentes_tabela = tabelas_pagina[2]
                for linha in componentes_tabela[3:]:
                    periodo_letivo = pegar_valor_seguro_dLista_evitarIndex(linha, 0)
                    descricao = pegar_valor_seguro_dLista_evitarIndex(linha, 3)
                    nota = pegar_valor_seguro_dLista_evitarIndex(linha, 6)
                    
                    if periodo_letivo and eh_disciplina_valida(descricao):
                        todas_disciplinas.append({
                            'periodo': periodo_letivo,
                            'disciplina': descricao,
                            'nota': nota
                        })
            else:
                if len(tabelas_pagina) > 0:
                    componentes_tabela = max(tabelas_pagina, key=len)
                    for linha in componentes_tabela:
                        periodo_letivo = pegar_valor_seguro_dLista_evitarIndex(linha, 0)
                        descricao = pegar_valor_seguro_dLista_evitarIndex(linha, 3)
                        nota = pegar_valor_seguro_dLista_evitarIndex(linha, 6)
                        
                        if periodo_letivo and '/' in periodo_letivo and eh_disciplina_valida(descricao):
                            todas_disciplinas.append({
                                'periodo': periodo_letivo,
                                'disciplina': descricao,
                                'nota': nota
                            })
    
    return {
        'dados_pessoais': {
            'nome': nome,
            'cpf': cpf,
            'sexo': sexo
        },
        'dados_academicos': {
            'matricula': matricula,
            'situacao': situacao,
            'curso': curso
        },
        'disciplinas': todas_disciplinas
    }

def processar_disciplinas(disciplinas):
    df = pd.DataFrame(disciplinas)
    df['nota_numerica'] = df['nota'].apply(converter_nota)
    df_com_notas = df[df['nota_numerica'].notna()].copy()
    df_com_notas['faixa'] = df_com_notas['nota_numerica'].apply(classificar_nota)
    
    estatisticas = {
        'total_disciplinas': len(df),
        'disciplinas_concluidas': len(df_com_notas),
        'disciplinas_cursando': len(df) - len(df_com_notas),
        'media_geral': df_com_notas['nota_numerica'].mean(),
        'maior_nota': df_com_notas['nota_numerica'].max(),
        'menor_nota': df_com_notas['nota_numerica'].min(),
        'desvio_padrao': df_com_notas['nota_numerica'].std(),
        'distribuicao': df_com_notas['faixa'].value_counts().to_dict()
    }
    
    return df, df_com_notas, estatisticas

def gerar_grafico_distribuicao(df_com_notas, media_geral):
    distribuicao = df_com_notas['faixa'].value_counts().sort_index()
    
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=distribuicao.index,
        values=distribuicao.values,
        hole=0.4,
        marker=dict(colors=['#2ecc71', '#3498db', '#f39c12', '#e74c3c']),
        textinfo='label+percent+value',
        textfont=dict(size=14)
    ))
    
    fig.update_layout(
        title=dict(
            text=f'<b>Distribuição de Notas</b><br><sub>Média Geral: {media_geral:.2f}</sub>',
            x=0.5,
            font=dict(size=24)
        ),
        annotations=[dict(
            text=f'<b>{media_geral:.2f}</b><br>Média',
            x=0.5, y=0.5,
            font=dict(size=20),
            showarrow=False
        )],
        height=500
    )
    
    return fig

def gerar_grafico_evolucao(df_com_notas, media_geral):
    media_por_periodo = df_com_notas.groupby('periodo')['nota_numerica'].mean().reset_index()
    media_por_periodo.columns = ['periodo', 'media']
    media_por_periodo = media_por_periodo.sort_values('periodo')
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=media_por_periodo['periodo'],
        y=media_por_periodo['media'],
        mode='lines+markers+text',
        line=dict(color='#3498db', width=3),
        marker=dict(size=12, color='#2ecc71'),
        text=[f'{m:.2f}' for m in media_por_periodo['media']],
        textposition='top center',
        textfont=dict(size=14)
    ))
    
    fig.add_hline(
        y=media_geral,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Média Geral: {media_geral:.2f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='<b>Evolução das Notas por Período</b>',
        xaxis_title='<b>Período Letivo</b>',
        yaxis_title='<b>Média</b>',
        yaxis=dict(range=[6.5, 10.5]),
        height=500
    )
    
    return fig

def analisar_historico(pdf_path):
    dados = extrair_dados_pdf(pdf_path)
    df, df_com_notas, estatisticas = processar_disciplinas(dados['disciplinas'])
    
    fig_distribuicao = gerar_grafico_distribuicao(df_com_notas, estatisticas['media_geral'])
    fig_evolucao = gerar_grafico_evolucao(df_com_notas, estatisticas['media_geral'])
    
    return {
        'dados_pessoais': dados['dados_pessoais'],
        'dados_academicos': dados['dados_academicos'],
        'estatisticas': estatisticas,
        'df_completo': df,
        'df_com_notas': df_com_notas,
        'graficos': {
            'distribuicao': fig_distribuicao,
            'evolucao': fig_evolucao
        }
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = r"LiriRack-pip/src_fonte/sistema - leitor de notas dados raq.pdf"
    
    print("Analisando histórico acadêmico...\n")
    resultado = analisar_historico(pdf_path)
    
    print("=" * 70)
    print("DADOS PESSOAIS")
    print("=" * 70)
    print(f"Nome: {resultado['dados_pessoais']['nome']}")
    print(f"CPF: {resultado['dados_pessoais']['cpf']}")
    print(f"Sexo: {resultado['dados_pessoais']['sexo']}")
    
    print("\n" + "=" * 70)
    print("DADOS ACADÊMICOS")
    print("=" * 70)
    print(f"Matrícula: {resultado['dados_academicos']['matricula']}")
    print(f"Situação: {resultado['dados_academicos']['situacao']}")
    print(f"Curso: {resultado['dados_academicos']['curso']}")
    
    print("\n" + "=" * 70)
    print("ESTATÍSTICAS DAS NOTAS")
    print("=" * 70)
    print(f"Total de Disciplinas: {resultado['estatisticas']['total_disciplinas']}")
    print(f"Disciplinas Concluídas: {resultado['estatisticas']['disciplinas_concluidas']}")
    print(f"Disciplinas Cursando: {resultado['estatisticas']['disciplinas_cursando']}")
    print(f"\nMédia Geral: {resultado['estatisticas']['media_geral']:.2f}")
    print(f"Maior Nota: {resultado['estatisticas']['maior_nota']:.2f}")
    print(f"Menor Nota: {resultado['estatisticas']['menor_nota']:.2f}")
    print(f"Desvio Padrão: {resultado['estatisticas']['desvio_padrao']:.2f}")
    
    print("\n" + "=" * 70)
    print("DISTRIBUIÇÃO DE NOTAS POR FAIXA")
    print("=" * 70)
    for faixa, quantidade in sorted(resultado['estatisticas']['distribuicao'].items()):
        porcentagem = (quantidade / resultado['estatisticas']['disciplinas_concluidas']) * 100
        print(f"{faixa}: {quantidade} disciplinas ({porcentagem:.1f}%)")
    
    print("\n" + "=" * 70)
    print("TODAS AS DISCIPLINAS")
    print("=" * 70)
    df_completo = resultado['df_completo']
    for _, row in df_completo.iterrows():
        if row['nota'] and row['nota'] != '-':
            print(f"{row['periodo']} | {row['disciplina']:<50} | Nota: {row['nota']}")
        else:
            print(f"{row['periodo']} | {row['disciplina']:<50} | Cursando")
    
    print("\n" + "=" * 70)
    print("GRÁFICOS")
    print("=" * 70)
    print("Gerando gráficos interativos...")
    resultado['graficos']['distribuicao'].show()
    resultado['graficos']['evolucao'].show()
    print("Gráficos abertos no navegador!")
