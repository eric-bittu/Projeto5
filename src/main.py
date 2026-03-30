import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Configuração da Página
st.set_page_config(page_title="Dashboard de Análise de Dados", layout="wide")

st.title(" Painel de Análise Descritiva e Indicadores")
st.markdown("---")

# 1. Upload de Dados
uploaded_file = st.sidebar.file_uploader("Carregue o arquivo STOREORDER.csv", type=['csv'])

if uploaded_file is not None:
    # Carregamento com cache para não travar o site em cada clique
    @st.cache_data
    def load_data(file):
        return pd.read_csv(file)


    df = load_data(uploaded_file)

    # Configurações na Barra Lateral
    st.sidebar.header("Filtros e Ajustes")
    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
    col_alvo = st.sidebar.selectbox("Coluna para Estatística:", colunas_numericas)

    # Filtro de Outliers para "desbugar" a visualização
    remover_outliers = st.sidebar.checkbox("Remover Outliers da visualização?", value=True)

    if remover_outliers:
        q1, q3 = df[col_alvo].quantile([0.25, 0.75])
        iqr = q3 - q1
        limite = q3 + 1.5 * iqr
        df_plot = df[df[col_alvo] <= limite]
        st.sidebar.info(f"Gráficos limitados a R$ {limite:.2f}")
    else:
        df_plot = df

    # --- SEÇÃO 1: ESTATÍSTICAS (A TAREFA DA FACULDADE) ---
    st.header(f" Estatísticas Descritivas: {col_alvo}")

    with st.container():
        # Cálculos
        media = df[col_alvo].mean()
        mediana = df[col_alvo].median()
        # Tratamento para moda (pode haver mais de uma ou ser lenta)
        moda_series = df[col_alvo].mode()
        moda = moda_series[0] if not moda_series.empty else 0

        var_amostral = df[col_alvo].var()
        var_pop = df[col_alvo].var(ddof=0)
        desvio = df[col_alvo].std()

        # Layout em colunas para os Cards
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Média", f"{media:.2f}")
        m2.metric("Mediana", f"{mediana:.2f}")
        m3.metric("Moda", f"{moda:.2f}")
        m4.metric("Var. (Pop)", f"{var_pop:.2f}")
        m5.metric("Desvio Padrão", f"{desvio:.2f}")

    st.markdown("---")

    # --- SEÇÃO 2: REPRESENTAÇÕES GRÁFICAS (HISTOGRAMA E BOXPLOT) ---
    st.header(" Distribuição e Dispersão")
    g1, g2 = st.columns(2)

    with g1:
        fig_hist = px.histogram(df_plot, x=col_alvo, nbins=50, title="Histograma (Frequência)",
                                color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_hist, use_container_width=True)

    with g2:
        fig_box = px.box(df_plot, y=col_alvo, title="Boxplot (Quartis e Outliers)", points="outliers")
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")

    # --- SEÇÃO 3: INDICADORES DE NEGÓCIO (PIZZA E BARRAS) ---
    st.header(" Visão Executiva")
    i1, i2 = st.columns(2)

    with i1:
        st.subheader("Vendas por Canal")
        df_pizza = df.groupby('saleschannel')['totalamount'].sum().reset_index()
        fig_pizza = px.pie(df_pizza, values='totalamount', names='saleschannel', hole=0.4,
                           title="Faturamento por Canal")
        st.plotly_chart(fig_pizza, use_container_width=True)
        st.caption("**Legenda:** Divisão percentual do faturamento entre iFood, Site, Balcão, etc.")

    with i2:
        st.subheader("Preferência de Entrega")
        df_bar = df['ordertype'].value_counts().reset_index()
        df_bar.columns = ['Tipo', 'Qtd']
        fig_bar = px.bar(df_bar, x='Tipo', y='Qtd', color='Tipo', title="Volume de Pedidos por Tipo")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("**Legenda:** Comparação de quantidade de pedidos entre Delivery e consumo Local.")

    st.markdown("---")

    # --- SEÇÃO 4: TABELAS DE RESUMO ---
    st.header(" Detalhamento de Dados")
    t1, t2 = st.columns([2, 1])

    with t1:
        st.subheader(" Top 10 Clientes")
        top_10 = df.groupby('customerid').agg({'id': 'count', 'totalamount': 'sum'}).rename(
            columns={'id': 'Qtd Pedidos', 'totalamount': 'Total Gasto'}).sort_values('Total Gasto',
                                                                                     ascending=False).head(10)
        st.table(top_10.style.format({"Total Gasto": "R$ {:.2f}"}))
        st.caption("**Legenda:** Clientes que mais geraram receita para a loja.")

    with t2:
        st.subheader(" Resumo Financeiro")
        resumo = pd.DataFrame({
            "Descrição": ["Bruto", "Descontos", "Impostos", "Líquido"],
            "Valor": [df['subtotalamount'].sum(), df['discountamount'].sum(), df['taxamount'].sum(),
                      df['totalamount'].sum()]
        })
        st.dataframe(resumo.style.format({"Valor": "R$ {:.2f}"}), hide_index=True)
        st.caption("**Legenda:** Totalização financeira geral do período.")

else:
    st.warning("⚠️ Aguardando upload do arquivo STOREORDER.csv para gerar o relatório.")