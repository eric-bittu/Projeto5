import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Análise Descritiva - Entrega 01", layout="wide")

st.title("📊 Projeto de Análise Descritiva")
st.markdown("---")

# 1. Upload de Dados
st.sidebar.header("Configurações")
uploaded_file = st.sidebar.file_uploader("Escolha seu arquivo CSV ou Excel", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Carregamento dos dados
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Exibição do Dataset
    st.subheader("👀 Visão Geral dos Dados")
    st.dataframe(df.head())

    # Seleção de Colunas Numéricas
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    if numeric_columns:
        col_selecionada = st.sidebar.selectbox("Selecione a coluna para analisar:", numeric_columns)

        # 2. Cálculos de Medidas de Posição e Dispersão
        st.subheader(f"📈 Estatísticas Descritivas: {col_selecionada}")

        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        # Medidas de Posição
        media = df[col_selecionada].mean()
        mediana = df[col_selecionada].median()
        moda = df[col_selecionada].mode()[0]  # Pega o primeiro valor da moda

        # Medidas de Dispersão
        variancia = df[col_selecionada].var()
        desvio_padrao = df[col_selecionada].std()

        col1.metric("Média", f"{media:.2f}")
        col2.metric("Mediana", f"{mediana:.2f}")
        col3.metric("Moda", f"{moda:.2f}")
        col4.metric("Variância", f"{variancia:.2f}")
        col5.metric("Desvio Padrão", f"{desvio_padrao:.2f}")

        st.markdown("---")

        # 3. Representações Gráficas
        st.subheader("🖼️ Visualização de Dados")

        layout_col1, layout_col2 = st.columns(2)

        with layout_col1:
            st.write("**Histograma** (Distribuição)")
            fig_hist = px.histogram(df, x=col_selecionada, nbins=30, marginal="rug",
                                    title=f"Histograma de {col_selecionada}")
            st.plotly_chart(fig_hist, use_container_width=True)

        with layout_col2:
            st.write("**Boxplot** (Identificação de Outliers)")
            fig_box = px.box(df, y=col_selecionada, title=f"Boxplot de {col_selecionada}")
            st.plotly_chart(fig_box, use_container_width=True)

    else:
        st.warning("O arquivo carregado não possui colunas numéricas para análise.")

else:
    st.info("Aguardando upload do arquivo para iniciar a análise.")