import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# Caminho base: pasta onde main.py está localizado
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'dados')

# ──────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Cannoli — Plataforma de Campanhas",
    page_icon="🍕",
    layout="wide",
)

# ──────────────────────────────────────────────
# CSS GLOBAL
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1,h2,h3,h4 { font-family: 'Syne', sans-serif; }

/* Fundo geral */
.stApp { background: #0e0f14; color: #e8e6e1; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #16181f !important;
    border-right: 1px solid #2a2d3a;
}

/* Cards de métricas */
[data-testid="metric-container"] {
    background: #1c1e27;
    border: 1px solid #2a2d3a;
    border-radius: 12px;
    padding: 16px 20px !important;
}
[data-testid="stMetricValue"] { color: #f97316; font-family: 'Syne', sans-serif; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #8b8fa8; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .08em; }
[data-testid="stMetricDelta"] { color: #22d3ee !important; }

/* Tabs */
[data-baseweb="tab-list"] { background: #1c1e27; border-radius: 10px; gap: 4px; padding: 4px; }
[data-baseweb="tab"] { color: #8b8fa8 !important; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: .85rem; }
[aria-selected="true"] { background: #f97316 !important; color: #fff !important; }

/* Botões */
.stButton > button {
    background: #f97316;
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    padding: 10px 24px;
    transition: all .2s;
}
.stButton > button:hover { background: #ea6a0a; transform: translateY(-1px); }

/* Inputs */
.stTextInput > div > div > input {
    background: #1c1e27 !important;
    border: 1px solid #2a2d3a !important;
    color: #e8e6e1 !important;
    border-radius: 8px !important;
}
.stSelectbox > div > div {
    background: #1c1e27 !important;
    border: 1px solid #2a2d3a !important;
    border-radius: 8px !important;
    color: #e8e6e1 !important;
}

/* Dividers */
hr { border-color: #2a2d3a; }

/* Tabelas */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* Alertas */
.stAlert { border-radius: 10px; }

/* Badge chip */
.chip {
    display: inline-block;
    background: #f9731620;
    color: #f97316;
    border: 1px solid #f9731640;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: .75rem;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    letter-spacing: .06em;
}
.chip-blue {
    background: #22d3ee20;
    color: #22d3ee;
    border-color: #22d3ee40;
}

/* Login card */
.login-wrap {
    max-width: 420px;
    margin: 60px auto 0;
    background: #1c1e27;
    border: 1px solid #2a2d3a;
    border-radius: 20px;
    padding: 44px 40px 36px;
}
.login-logo {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #f97316;
    text-align: center;
    margin-bottom: 6px;
}
.login-sub {
    text-align: center;
    color: #8b8fa8;
    font-size: .85rem;
    margin-bottom: 28px;
}

/* Section header */
.sec-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #e8e6e1;
    margin-bottom: 4px;
}
.sec-sub { color: #8b8fa8; font-size: .82rem; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DADOS COM CACHE
# ──────────────────────────────────────────────
@st.cache_data(show_spinner="Carregando dados…")
def load_all():
    store     = pd.read_csv(os.path.join(DATA_DIR, 'STORE.csv'))
    orders    = pd.read_csv(os.path.join(DATA_DIR, 'STOREORDER.csv'))
    campaign  = pd.read_csv(os.path.join(DATA_DIR, 'CAMPAIGN.CSV'))
    cxo       = pd.read_csv(os.path.join(DATA_DIR, 'CAMPAIGNxORDER.CSV'))
    customer  = pd.read_csv(os.path.join(DATA_DIR, 'CUSTOMER.CSV'))
    addr      = pd.read_csv(os.path.join(DATA_DIR, 'CUSTOMERADDRESS.CSV'))

    # Normaliza tipos
    orders['totalamount']   = pd.to_numeric(orders['totalamount'],   errors='coerce').fillna(0)
    orders['subtotalamount']= pd.to_numeric(orders['subtotalamount'],errors='coerce').fillna(0)
    orders['discountamount']= pd.to_numeric(orders['discountamount'],errors='coerce').fillna(0)
    orders['taxamount']     = pd.to_numeric(orders['taxamount'],     errors='coerce').fillna(0)
    orders['createdat']     = pd.to_datetime(orders['createdat'],    errors='coerce', utc=True)

    cxo['totalamount']      = pd.to_numeric(cxo['totalamount'],      errors='coerce').fillna(0)
    cxo['sent_at']          = pd.to_datetime(cxo['sent_at'],         errors='coerce', utc=True)
    cxo['order_at']         = pd.to_datetime(cxo['order_at'],        errors='coerce', utc=True)

    campaign['createdat']   = pd.to_datetime(campaign['createdat'],  errors='coerce', utc=True)

    return store, orders, campaign, cxo, customer, addr

store_df, orders_df, campaign_df, cxo_df, customer_df, addr_df = load_all()

# ──────────────────────────────────────────────
# ESTADO DE SESSÃO
# ──────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None          # 'cannoli' | 'store'
    st.session_state.store_id = None
    st.session_state.store_name = None

# ──────────────────────────────────────────────
# TELA DE LOGIN
# ──────────────────────────────────────────────
def tela_login():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-logo">🍕 Cannoli</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Plataforma de Campanhas & Analytics</div>', unsafe_allow_html=True)

    tipo = st.radio("Entrar como:", ["Cannoli (Admin)", "Empresa Parceira"], horizontal=True, label_visibility="collapsed")

    if tipo == "Cannoli (Admin)":
        user = st.text_input("Usuário", placeholder="admin")
        pwd  = st.text_input("Senha",   type="password", placeholder="••••••")
        if st.button("Entrar", use_container_width=True):
            if user == "admin" and pwd == "cannoli123":
                st.session_state.logged_in = True
                st.session_state.role = "cannoli"
                st.rerun()
            else:
                st.error("Credenciais inválidas. (admin / cannoli123)")
    else:
        stores_with_data = store_df[store_df['id'].isin(orders_df['storeid'].unique())].sort_values('name')
        store_names = stores_with_data['name'].tolist()
        chosen = st.selectbox("Selecione sua empresa", store_names)
        pwd    = st.text_input("Senha", type="password", placeholder="••••••")
        if st.button("Entrar", use_container_width=True):
            # Senha demo = nome da loja em minúsculas sem espaços
            expected = chosen.lower().replace(" ", "")
            if pwd == expected or pwd == "demo123":
                row = stores_with_data[stores_with_data['name'] == chosen].iloc[0]
                st.session_state.logged_in  = True
                st.session_state.role       = "store"
                st.session_state.store_id   = row['id']
                st.session_state.store_name = row['name']
                st.rerun()
            else:
                st.error("Senha incorreta. Use 'demo123' para demonstração.")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#444;font-size:.75rem;margin-top:24px'>Cannoli Food Technology © 2025</p>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# HELPERS GRÁFICOS
# ──────────────────────────────────────────────
PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#8b8fa8',
    font_family='DM Sans',
    colorway=['#f97316','#22d3ee','#a78bfa','#34d399','#fb7185','#fbbf24'],
    xaxis=dict(gridcolor='#2a2d3a', linecolor='#2a2d3a'),
    yaxis=dict(gridcolor='#2a2d3a', linecolor='#2a2d3a'),
)

def apply_theme(fig):
    fig.update_layout(**PLOTLY_THEME)
    return fig

def fmt_brl(v): return f"R$ {v:,.2f}"

# ──────────────────────────────────────────────
# DASHBOARD CANNOLI (ADMIN)
# ──────────────────────────────────────────────
def dashboard_cannoli():
    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### 🍕 Cannoli Admin")
        st.markdown('<span class="chip">Super Admin</span>', unsafe_allow_html=True)
        st.markdown("---")

        # Filtro de lojas
        all_stores = store_df[store_df['id'].isin(orders_df['storeid'].unique())].sort_values('name')
        sel_stores = st.multiselect(
            "Filtrar Lojas",
            options=all_stores['id'].tolist(),
            format_func=lambda x: all_stores.set_index('id').loc[x,'name'],
            default=[],
            placeholder="Todas as lojas"
        )

        # Filtro de período
        min_d = orders_df['createdat'].min().date()
        max_d = orders_df['createdat'].max().date()
        date_range = st.date_input("Período", value=(min_d, max_d), min_value=min_d, max_value=max_d)

        st.markdown("---")
        if st.button("🚪 Sair"):
            for k in ['logged_in','role','store_id','store_name']:
                st.session_state[k] = None if k != 'logged_in' else False
            st.rerun()

    # Aplica filtros
    ord_f = orders_df.copy()
    cxo_f = cxo_df.copy()
    camp_f = campaign_df.copy()

    if len(date_range) == 2:
        start = pd.Timestamp(date_range[0], tz='UTC')
        end   = pd.Timestamp(date_range[1], tz='UTC')
        ord_f  = ord_f[(ord_f['createdat'] >= start) & (ord_f['createdat'] <= end)]
        cxo_f  = cxo_f[(cxo_f['order_at'] >= start) & (cxo_f['order_at'] <= end)]

    if sel_stores:
        ord_f  = ord_f[ord_f['storeid'].isin(sel_stores)]
        cxo_f  = cxo_f[cxo_f['storeid'].isin(sel_stores)]
        camp_f = camp_f[camp_f['storeid'].isin(sel_stores)]

    # Pedidos atribuídos a campanhas (status 2 = convertido)
    cxo_conv = cxo_f[cxo_f['status'] == 2].drop_duplicates('order_id')

    # ── Header ──
    st.markdown("## 🍕 Cannoli — Visão Geral da Plataforma")
    st.markdown("---")

    # ── KPIs ──
    total_rev    = ord_f['totalamount'].sum()
    camp_rev     = cxo_conv['totalamount'].sum()
    attr_pct     = (camp_rev / total_rev * 100) if total_rev > 0 else 0
    n_stores     = ord_f['storeid'].nunique()
    n_campaigns  = camp_f['segmentid'].nunique()
    conv_orders  = cxo_conv['order_id'].nunique()

    row1 = st.columns(3)
    row1[0].metric("💰 Faturamento Total",      fmt_brl(total_rev))
    row1[1].metric("📣 Receita por Campanha",   fmt_brl(camp_rev))
    row1[2].metric("🎯 Atribuição",  f"{attr_pct:.1f}%", help="% do faturamento originado de campanhas")
    row2 = st.columns(3)
    row2[0].metric("🏪 Lojas Ativas",           str(n_stores))
    row2[1].metric("📨 Campanhas",              str(n_campaigns))
    row2[2].metric("🛒 Pedidos Convertidos",    str(conv_orders))

    st.markdown("---")

    tabs = st.tabs(["📊 Visão Geral", "📣 Campanhas", "🏪 Lojas", "👥 Clientes"])

    # ──────────────────── TAB 1: VISÃO GERAL ────────────────────
    with tabs[0]:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="sec-header">Faturamento Mensal</div>', unsafe_allow_html=True)
            ord_f['mes'] = ord_f['createdat'].dt.to_period('M').astype(str)
            monthly = ord_f.groupby('mes')['totalamount'].sum().reset_index()
            monthly.columns = ['Mês','Faturamento']
            fig = px.bar(monthly, x='Mês', y='Faturamento', title='')
            apply_theme(fig)
            fig.update_traces(marker_color='#f97316', marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="sec-header">Canais de Venda</div>', unsafe_allow_html=True)
            ch = ord_f.groupby('saleschannel')['totalamount'].sum().reset_index()
            fig2 = px.pie(ch, values='totalamount', names='saleschannel', hole=0.45, title='')
            apply_theme(fig2)
            fig2.update_traces(textfont_color='#fff')
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="sec-header">Tipo de Pedido</div>', unsafe_allow_html=True)
            ot = ord_f['ordertype'].value_counts().reset_index()
            ot.columns = ['Tipo','Qtd']
            fig3 = px.bar(ot, x='Tipo', y='Qtd', title='', color='Tipo')
            apply_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown('<div class="sec-header">Pedidos: Orgânico vs Campanha</div>', unsafe_allow_html=True)
            campaign_order_ids = set(cxo_conv['order_id'].dropna())
            ord_f['origem'] = ord_f['id'].apply(lambda x: 'Campanha' if x in campaign_order_ids else 'Orgânico')
            orig = ord_f.groupby('origem')['totalamount'].sum().reset_index()
            fig4 = px.pie(orig, values='totalamount', names='origem', hole=0.45, title='',
                          color='origem', color_discrete_map={'Campanha':'#f97316','Orgânico':'#22d3ee'})
            apply_theme(fig4)
            fig4.update_traces(textfont_color='#fff')
            st.plotly_chart(fig4, use_container_width=True)

    # ──────────────────── TAB 2: CAMPANHAS ────────────────────
    with tabs[1]:
        st.markdown('<div class="sec-header">Performance de Campanhas por Loja</div>', unsafe_allow_html=True)

        # Merge campanha com conversões
        # Renomeia storeid da campaign para evitar conflito com storeid do cxo
        camp_perf = cxo_f.merge(
            campaign_df[['segmentid','name','storeid']].rename(
                columns={'segmentid':'campaignid','name':'camp_name','storeid':'camp_storeid'}),
            on='campaignid', how='left'
        )
        # Prioriza storeid do cxo; se nulo, usa o da campanha
        camp_perf['_sid'] = camp_perf['storeid'].combine_first(camp_perf['camp_storeid'])
        camp_perf = camp_perf.merge(
            store_df[['id','name']].rename(columns={'id':'_sid','name':'store_name'}),
            on='_sid', how='left'
        )

        conv_by_camp = camp_perf[camp_perf['status']==2].groupby(['camp_name','store_name']).agg(
            Conversoes=('order_id','nunique'),
            Receita=('totalamount','sum')
        ).reset_index().sort_values('Receita', ascending=False).head(20)

        fig5 = px.bar(conv_by_camp, x='Receita', y='camp_name', orientation='h',
                      color='store_name', title='Top 20 Campanhas por Receita Convertida')
        apply_theme(fig5)
        fig5.update_layout(yaxis_title='', xaxis_title='Receita (R$)', legend_title='Loja', height=520)
        st.plotly_chart(fig5, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="sec-header">Funil de Campanha</div>', unsafe_allow_html=True)
            total_sent   = len(cxo_f)
            total_conv   = len(cxo_f[cxo_f['status']==2])
            funnel_data  = pd.DataFrame({'Etapa':['Mensagens Enviadas','Pedidos Convertidos'],
                                          'Qtd':[total_sent, total_conv]})
            fig6 = px.funnel(funnel_data, x='Qtd', y='Etapa', title='')
            apply_theme(fig6)
            st.plotly_chart(fig6, use_container_width=True)
            taxa = total_conv/total_sent*100 if total_sent else 0
            st.metric("Taxa de Conversão Global", f"{taxa:.2f}%")

        with col_b:
            st.markdown('<div class="sec-header">Campanhas por Tipo</div>', unsafe_allow_html=True)
            type_map = {1:'SMS/Push',2:'Email',3:'WhatsApp'}
            camp_f2 = camp_f.copy()
            camp_f2['tipo_str'] = camp_f2['type'].map(type_map).fillna('Outro')
            ct = camp_f2['tipo_str'].value_counts().reset_index()
            ct.columns = ['Tipo','Qtd']
            fig7 = px.pie(ct, values='Qtd', names='Tipo', hole=0.45, title='')
            apply_theme(fig7)
            fig7.update_traces(textfont_color='#fff')
            st.plotly_chart(fig7, use_container_width=True)

    # ──────────────────── TAB 3: LOJAS ────────────────────
    with tabs[2]:
        st.markdown('<div class="sec-header">Ranking de Lojas</div>', unsafe_allow_html=True)

        store_rank = ord_f.merge(store_df[['id','name']].rename(columns={'id':'storeid','name':'store_name'}),
                                  on='storeid', how='left')
        store_rank = store_rank.groupby('store_name').agg(
            Pedidos=('id','count'),
            Faturamento=('totalamount','sum'),
            TicketMedio=('totalamount','mean')
        ).sort_values('Faturamento', ascending=False).reset_index()

        # Adiciona coluna de pedidos de campanha por loja
        camp_by_store = cxo_conv.groupby('storeid')['order_id'].nunique().reset_index()
        camp_by_store.columns = ['storeid','PedidosCampanha']
        store_rank = store_rank.merge(
            store_df[['id','name']].rename(columns={'id':'storeid','name':'store_name'}),
            on='store_name', how='left'
        ).merge(camp_by_store, on='storeid', how='left')
        store_rank['PedidosCampanha'] = store_rank['PedidosCampanha'].fillna(0).astype(int)
        store_rank['%Campanha'] = (store_rank['PedidosCampanha'] / store_rank['Pedidos'] * 100).round(1)

        fig8 = px.bar(store_rank.head(20), x='store_name', y='Faturamento', title='Top 20 Lojas por Faturamento',
                      color='%Campanha', color_continuous_scale='Oranges')
        apply_theme(fig8)
        fig8.update_layout(xaxis_title='', coloraxis_colorbar_title='% Campanha')
        fig8.update_xaxes(tickangle=-35)
        st.plotly_chart(fig8, use_container_width=True)

        st.markdown('<div class="sec-header">Tabela Detalhada</div>', unsafe_allow_html=True)
        display = store_rank[['store_name','Pedidos','Faturamento','TicketMedio','PedidosCampanha','%Campanha']].head(30)
        display = display.rename(columns={'store_name':'Loja','TicketMedio':'Ticket Médio'})
        st.dataframe(
            display.style.format({'Faturamento':'R$ {:.2f}','Ticket Médio':'R$ {:.2f}','%Campanha':'{:.1f}%'}),
            use_container_width=True, hide_index=True
        )

    # ──────────────────── TAB 4: CLIENTES ────────────────────
    with tabs[3]:
        st.markdown('<div class="sec-header">Top 15 Clientes (Receita)</div>', unsafe_allow_html=True)

        top_cust = ord_f.groupby('customerid').agg(
            Pedidos=('id','count'),
            Receita=('totalamount','sum')
        ).sort_values('Receita', ascending=False).head(15).reset_index()
        top_cust = top_cust.merge(
            customer_df[['id','name']].rename(columns={'id':'customerid','name':'Cliente'}),
            on='customerid', how='left'
        )
        top_cust['Cliente'] = top_cust['Cliente'].fillna(top_cust['customerid'].str[:8] + '…')

        fig9 = px.bar(top_cust, x='Cliente', y='Receita', title='', color='Pedidos',
                      color_continuous_scale='Oranges')
        apply_theme(fig9)
        fig9.update_layout(xaxis_title='', coloraxis_colorbar_title='Pedidos')
        fig9.update_xaxes(tickangle=-30)
        st.plotly_chart(fig9, use_container_width=True)

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown('<div class="sec-header">Distribuição de Gênero</div>', unsafe_allow_html=True)
            gen = customer_df['gender'].value_counts().reset_index()
            gen.columns = ['Gênero','Qtd']
            gen['Gênero'] = gen['Gênero'].map({'M':'Masculino','F':'Feminino'}).fillna('Não informado')
            fig10 = px.pie(gen, values='Qtd', names='Gênero', hole=0.45, title='')
            apply_theme(fig10)
            fig10.update_traces(textfont_color='#fff')
            st.plotly_chart(fig10, use_container_width=True)

        with col_d:
            st.markdown('<div class="sec-header">Clientes por Estado</div>', unsafe_allow_html=True)
            state = addr_df['state'].value_counts().head(10).reset_index()
            state.columns = ['Estado','Qtd']
            fig11 = px.bar(state, x='Estado', y='Qtd', title='', color='Qtd',
                           color_continuous_scale='Oranges')
            apply_theme(fig11)
            fig11.update_layout(showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig11, use_container_width=True)


# ──────────────────────────────────────────────
# DASHBOARD EMPRESA PARCEIRA
# ──────────────────────────────────────────────
def dashboard_store(store_id: str, store_name: str):
    # Filtra dados da loja
    ord_s  = orders_df[orders_df['storeid'] == store_id].copy()
    camp_s = campaign_df[campaign_df['storeid'] == store_id].copy()
    cxo_s  = cxo_df[cxo_df['storeid'] == store_id].copy()
    cxo_s_conv = cxo_s[cxo_s['status'] == 2].drop_duplicates('order_id')

    # Marca pedidos de campanha
    camp_order_ids = set(cxo_s_conv['order_id'].dropna())
    ord_s['origem'] = ord_s['id'].apply(lambda x: 'Campanha' if x in camp_order_ids else 'Orgânico')

    # ── Sidebar ──
    with st.sidebar:
        st.markdown(f"### 🏪 {store_name}")
        st.markdown('<span class="chip chip-blue">Empresa Parceira</span>', unsafe_allow_html=True)
        st.markdown("---")

        min_d = ord_s['createdat'].min().date() if len(ord_s) else pd.Timestamp.today().date()
        max_d = ord_s['createdat'].max().date() if len(ord_s) else pd.Timestamp.today().date()
        date_range = st.date_input("Período", value=(min_d, max_d), min_value=min_d, max_value=max_d)

        st.markdown("---")
        if st.button("🚪 Sair"):
            for k in ['logged_in','role','store_id','store_name']:
                st.session_state[k] = None if k != 'logged_in' else False
            st.rerun()

    if len(date_range) == 2:
        start = pd.Timestamp(date_range[0], tz='UTC')
        end   = pd.Timestamp(date_range[1], tz='UTC')
        ord_s  = ord_s[(ord_s['createdat'] >= start) & (ord_s['createdat'] <= end)]
        cxo_s_conv = cxo_s_conv[(cxo_s_conv['order_at'] >= start) & (cxo_s_conv['order_at'] <= end)]

    # ── Header ──
    st.markdown(f"## 🏪 {store_name}")
    st.markdown("---")

    # ── KPIs ──
    total_rev   = ord_s['totalamount'].sum()
    camp_rev    = cxo_s_conv['totalamount'].sum()
    attr_pct    = (camp_rev / total_rev * 100) if total_rev > 0 else 0
    n_orders    = len(ord_s)
    n_campaigns = camp_s['segmentid'].nunique()
    ticket      = ord_s['totalamount'].mean() if n_orders else 0

    row1 = st.columns(3)
    row1[0].metric("💰 Faturamento Total",      fmt_brl(total_rev))
    row1[1].metric("📣 Receita por Campanha",   fmt_brl(camp_rev))
    row1[2].metric("🎯 Atribuição",  f"{attr_pct:.1f}%")
    row2 = st.columns(3)
    row2[0].metric("🛒 Pedidos",                str(n_orders))
    row2[1].metric("📨 Campanhas",              str(n_campaigns))
    row2[2].metric("🧾 Ticket Médio",      fmt_brl(ticket))

    st.markdown("---")

    tabs = st.tabs(["📊 Vendas", "📣 Minhas Campanhas", "👥 Meus Clientes"])

    # ──────────────────── TAB 1: VENDAS ────────────────────
    with tabs[0]:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="sec-header">Faturamento Mensal</div>', unsafe_allow_html=True)
            ord_s['mes'] = ord_s['createdat'].dt.to_period('M').astype(str)
            monthly = ord_s.groupby(['mes','origem'])['totalamount'].sum().reset_index()
            fig = px.bar(monthly, x='mes', y='totalamount', color='origem', barmode='stack',
                         color_discrete_map={'Campanha':'#f97316','Orgânico':'#22d3ee'}, title='')
            apply_theme(fig)
            fig.update_layout(xaxis_title='', yaxis_title='R$', legend_title='Origem')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="sec-header">Canal de Venda</div>', unsafe_allow_html=True)
            ch = ord_s.groupby('saleschannel')['totalamount'].sum().reset_index()
            fig2 = px.pie(ch, values='totalamount', names='saleschannel', hole=0.45, title='')
            apply_theme(fig2)
            fig2.update_traces(textfont_color='#fff')
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="sec-header">Tipo de Pedido</div>', unsafe_allow_html=True)
            ot = ord_s['ordertype'].value_counts().reset_index()
            ot.columns = ['Tipo','Qtd']
            fig3 = px.bar(ot, x='Tipo', y='Qtd', color='Tipo', title='')
            apply_theme(fig3)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown('<div class="sec-header">Resumo Financeiro</div>', unsafe_allow_html=True)
            resumo = pd.DataFrame({
                "Descrição": ["Subtotal", "Descontos", "Impostos", "Líquido"],
                "Valor": [ord_s['subtotalamount'].sum(), ord_s['discountamount'].sum(),
                          ord_s['taxamount'].sum(), ord_s['totalamount'].sum()]
            })
            # Adiciona linha de campanha
            extra = pd.DataFrame({"Descrição": ["↳ via Campanha"], "Valor": [camp_rev]})
            resumo = pd.concat([resumo, extra], ignore_index=True)
            st.dataframe(resumo.style.format({"Valor": "R$ {:.2f}"}), hide_index=True, use_container_width=True)

    # ──────────────────── TAB 2: CAMPANHAS ────────────────────
    with tabs[1]:
        if len(camp_s) == 0:
            st.info("Nenhuma campanha encontrada para esta loja.")
        else:
            st.markdown('<div class="sec-header">Campanhas Criadas</div>', unsafe_allow_html=True)

            # Junta campanha com conversões
            camp_detail = camp_s.merge(
                cxo_s.groupby('campaignid').agg(
                    Enviadas=('message_id','count'),
                    Convertidas=('order_id', lambda x: x[cxo_s.loc[x.index,'status']==2].nunique()),
                    ReceitaConv=('totalamount', lambda x: x[cxo_s.loc[x.index,'status']==2].sum())
                ).reset_index(),
                left_on='segmentid', right_on='campaignid', how='left'
            )
            camp_detail['Enviadas']    = camp_detail['Enviadas'].fillna(0).astype(int)
            camp_detail['Convertidas'] = camp_detail['Convertidas'].fillna(0).astype(int)
            camp_detail['ReceitaConv'] = camp_detail['ReceitaConv'].fillna(0)
            camp_detail['TaxaConv%']   = (camp_detail['Convertidas'] / camp_detail['Enviadas'] * 100).fillna(0).round(1)

            # Status map
            status_map = {1:'Rascunho',2:'Encerrada',4:'Ativa',5:'Pausada',7:'Agendada'}
            camp_detail['Status'] = camp_detail['statusend'].map(status_map).fillna('?')

            col_a, col_b = st.columns(2)
            with col_a:
                fig_c1 = px.bar(camp_detail.sort_values('ReceitaConv', ascending=False).head(15),
                                x='name', y='ReceitaConv', title='Top Campanhas (Receita Convertida)',
                                color='TaxaConv%', color_continuous_scale='Oranges')
                apply_theme(fig_c1)
                fig_c1.update_layout(xaxis_title='', yaxis_title='R$')
                fig_c1.update_xaxes(tickangle=-35)
                st.plotly_chart(fig_c1, use_container_width=True)

            with col_b:
                fig_c2 = px.scatter(camp_detail, x='Enviadas', y='Convertidas', size='ReceitaConv',
                                    color='Status', hover_name='name',
                                    title='Envios vs Conversões (tamanho = receita)',
                                    size_max=40)
                apply_theme(fig_c2)
                st.plotly_chart(fig_c2, use_container_width=True)

            st.markdown('<div class="sec-header">Tabela de Campanhas</div>', unsafe_allow_html=True)
            show_cols = ['name','Status','Enviadas','Convertidas','TaxaConv%','ReceitaConv']
            st.dataframe(
                camp_detail[show_cols].rename(columns={
                    'name':'Campanha','ReceitaConv':'Receita Convertida'
                }).sort_values('Receita Convertida', ascending=False).style.format({
                    'Receita Convertida':'R$ {:.2f}','TaxaConv%':'{:.1f}%'
                }),
                use_container_width=True, hide_index=True
            )

    # ──────────────────── TAB 3: CLIENTES ────────────────────
    with tabs[2]:
        st.markdown('<div class="sec-header">Top 10 Clientes da Loja</div>', unsafe_allow_html=True)

        top_cust = ord_s.groupby('customerid').agg(
            Pedidos=('id','count'),
            Receita=('totalamount','sum'),
            ViaCampanha=('origem', lambda x: (x=='Campanha').sum())
        ).sort_values('Receita', ascending=False).head(10).reset_index()

        top_cust = top_cust.merge(
            customer_df[['id','name']].rename(columns={'id':'customerid','name':'Cliente'}),
            on='customerid', how='left'
        )
        top_cust['Cliente'] = top_cust['Cliente'].fillna(top_cust['customerid'].str[:8] + '…')

        fig_t = px.bar(top_cust, x='Cliente', y='Receita', color='ViaCampanha',
                       color_continuous_scale='Oranges', title='')
        apply_theme(fig_t)
        fig_t.update_layout(coloraxis_colorbar_title='Pedidos via\nCampanha')
        fig_t.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_t, use_container_width=True)

        st.dataframe(
            top_cust[['Cliente','Pedidos','Receita','ViaCampanha']].style.format({
                'Receita':'R$ {:.2f}'
            }),
            use_container_width=True, hide_index=True
        )


# ──────────────────────────────────────────────
# ROTEADOR PRINCIPAL
# ──────────────────────────────────────────────
if not st.session_state.logged_in:
    tela_login()
elif st.session_state.role == 'cannoli':
    dashboard_cannoli()
elif st.session_state.role == 'store':
    dashboard_store(st.session_state.store_id, st.session_state.store_name)