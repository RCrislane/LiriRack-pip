import streamlit as st
from src_fonte.extrair_dados_pdf_raquel import analisar_historico

st.title("< Analisador de Histórico Acadêmico UEPB >")

arquivo = st.file_uploader("Envie seu histórico acadêmico", type=['pdf'])

if arquivo:
    temp_path = "temp_historico.pdf"
    with open(temp_path, "wb") as f:
        f.write(arquivo.getbuffer())
    
    with st.spinner("Analisando histórico..."):
        resultado = analisar_historico(temp_path)
    
    st.success("[OK] Análise concluída!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Média Geral", f"{resultado['estatisticas']['media_geral']:.2f}")
    with col2:
        st.metric("Maior Nota", f"{resultado['estatisticas']['maior_nota']:.2f}")
    with col3:
        st.metric("Menor Nota", f"{resultado['estatisticas']['menor_nota']:.2f}")
    
    st.plotly_chart(resultado['graficos']['distribuicao'], use_container_width=True)
    st.plotly_chart(resultado['graficos']['evolucao'], use_container_width=True)