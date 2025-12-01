import streamlit as st
from src_fonte.extrair_dados_pdf_raquel import analisar_historico
import os

st.set_page_config(
    page_title="Analisador UEPB",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
/* Oculta a barra de menu do Streamlit */
.stApp > header {
    visibility: hidden;
}

/* Título principal (style) */
h1 {
    color: #4CAF50; /* Verde Universitário */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-weight: 700;
}

/* Estiliza os subtítulos de seção (desempenho geral e visualização detalhada) */
h2 {
    border-bottom: 2px solid #303030; /* Linha sutil de separação */
    padding-bottom: 5px;
    margin-top: 15px;
    color: #EEEEEE; 
}

/* Aumenta e centraliza o valor das métricas */
[data-testid="stMetricValue"] {
    font-size: 2.5rem;
}

/* Ajusta o separador horizontal */
hr {
    border-top: 3px solid #202020;
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 Analisador de Histórico Acadêmico UEPB")
st.caption("Transforme seu PDF em insights visuais em segundos.")

# --- 2. UPLOAD NA BARRA LATERAL (st.sidebar) ---
with st.sidebar:
    st.header("⚙️ Configuração")
    st.info("Aqui você envia o arquivo e define opções futuras de análise.")
    
    with st.spinner("Analisando histórico..."):
        resultado = analisar_historico(temp_path)
    
    if not arquivo:
        st.markdown("---")
        st.info("📃 **Aguardando o envio do arquivo...**")


# --- 3. BLOC DE ANÁLISE COM CACHING E VALIDAÇÃO ---
if arquivo:
    temp_path = "temp_historico.pdf" 
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Média Geral", f"{resultado['estatisticas']['media_geral']:.2f}")
    with col2:
        st.metric("Maior Nota", f"{resultado['estatisticas']['maior_nota']:.2f}")
    with col3:
        st.metric("Menor Nota", f"{resultado['estatisticas']['menor_nota']:.2f}")
    
    st.plotly_chart(resultado['graficos']['distribuicao'], use_container_width=True)
    st.plotly_chart(resultado['graficos']['evolucao'], use_container_width=True)