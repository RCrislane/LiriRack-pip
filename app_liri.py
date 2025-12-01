import streamlit as st
from src_fonte.extrair_dados_pdf_raquel import analisar_historico
import os
import time

st.set_page_config(
    page_title="Analisador UEPB",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
/* Oculta a barra de menu do Streamlit */
.stApp > header {
    height: 100vh;
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

/* Estilo de GIF de carregamento */
.center-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding-top: 10px;
    padding-bottom: 10px;
}

.center-loading [data-testid="stAlert"] {
    max-width: 500px;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 Analisador de Histórico Acadêmico UEPB")
st.caption("Transforme seu PDF em insights visuais em segundos.")

with st.sidebar:
    st.header("⚙️ Configuração")
    st.info("Aqui você envia o arquivo e define opções futuras de análise.")
    
    st.subheader("Envio do Histórico")
    arquivo = st.file_uploader("Selecione o arquivo PDF do seu histórico acadêmico.", type=['pdf'])
    
    if not arquivo:
        st.markdown("---")
        st.info("📃 **Aguardando o envio do arquivo...**")

main_content_placeholder = st.empty()

if arquivo:
    temp_path = "temp_historico.pdf" 
    
    GIF_URL = "https://upload.wikimedia.org/wikipedia/commons/a/ad/YouTube_loading_symbol_3_%28transparent%29.gif"

    with main_content_placeholder.container():
        st.markdown('<div class="center-loading">', unsafe_allow_html=True)
        st.image(GIF_URL, width=200) 
        st.info("⏳ Analisando histórico... Por favor, aguarde o processamento.")
        st.markdown('</div>', unsafe_allow_html=True)

    
    @st.cache_data
    def analisar_historico_cache(caminho_arquivo):
        return analisar_historico(caminho_arquivo)

    try:
        with open(temp_path, "wb") as f:
            f.write(arquivo.getbuffer())
        
        time.sleep(4)

        resultado = analisar_historico_cache(temp_path)

        main_content_placeholder.empty() 
        
        if not isinstance(resultado, dict) or 'estatisticas' not in resultado or 'graficos' not in resultado:
            st.error("❌ A análise falhou. O backend não retornou a estrutura de dados esperada.")
            raise ValueError("Estrutura de resultado inválida ou ausente.") 

        st.success("✅ Análise concluída! Veja seus resultados abaixo.")    
        
        stats = resultado['estatisticas']
        charts = resultado['graficos']
        
        st.markdown("---")
        st.header("✨ Desempenho Geral") 

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Média Geral (MG)", f"{stats.get('media_geral', 0):.2f}", delta="🚀 Excelente")
        with col2:
            st.metric("Maior Nota", f"{stats.get('maior_nota', 0):.2f}", delta="🔝 Nota Máxima")
        with col3:
            st.metric("Menor Nota", f"{stats.get('menor_nota', 0):.2f}", delta="🔻 Atenção")
        with col4:
            percent_aprovacao = stats.get('percent_aprovacao', 92.5)         
            st.metric("% de Aprovação", f"{percent_aprovacao:.1f}%", delta="+2.5%")

        st.markdown("---")
        
        st.header("📈 Visualização Detalhada")
        
        tab1, tab2 = st.tabs(["📊 Distribuição", "📈 Evolução no Tempo"])    

        with tab1:
            st.subheader("Distribuição das Notas por Disciplina")
            if charts.get('distribuicao'):
                st.plotly_chart(charts['distribuicao'], use_container_width=True)
            else:
                st.warning("⚠️ O gráfico de Distribuição não pôde ser gerado ou está ausente no retorno.")
        
        with tab2:
            st.subheader("Evolução do Desempenho por Período")
            if charts.get('evolucao'):
                st.plotly_chart(charts['evolucao'], use_container_width=True)
            else:
                st.warning("⚠️ O gráfico de Evolução não pôde ser gerado ou está ausente no retorno.")

    except Exception as e:
        main_content_placeholder.empty()
        st.error(f"❌ Ocorreu um erro INESPERADO: {e}. Isso geralmente indica um problema na função de backend ou no arquivo PDF.")
        st.exception(e)       
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


else:
    with main_content_placeholder.container():
        st.info(" ←  Utilize a barra lateral à esquerda para fazer o upload do seu Histórico Acadêmico e começar a análise de desempenho.")
        st.markdown("""
            ### Funcionalidades do Aplicativo:
            - ⭐ **Visão Geral:** Métricas claras como Média Geral, Maior e Menor Nota.
            - 📊 **Visualização de Dados:** Gráficos interativos de distribuição de notas e evolução de desempenho.
            - 📚 **Organização:** Dados e gráficos dispostos em abas para uma navegação fácil e rápida.
            - 📍 **Performance:** Análise otimizada com *caching* para resultados instantâneos após o primeiro upload.
        """)