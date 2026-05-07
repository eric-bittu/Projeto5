import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from scipy import stats
import os

st.set_page_config(page_title="Análise de Regressão", layout="wide")

st.title("📈 Análise de Regressão Linear")
st.subheader("Campanhas de marketing e faturamento das lojas parceiras")
st.markdown(
    "**Pergunta central:** O volume de mensagens de campanha enviadas por uma loja "
    "tem relação com seu faturamento total?"
)
st.markdown("---")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data(show_spinner="Carregando dados…")
def carregar():
    cxo    = pd.read_csv(os.path.join(BASE_DIR, 'dados', 'CAMPAIGNxORDER.CSV'))
    orders = pd.read_csv(os.path.join(BASE_DIR, 'dados', 'STOREORDER.csv'))
    store  = pd.read_csv(os.path.join(BASE_DIR, 'dados', 'STORE.csv'))

    cxo['totalamount']    = pd.to_numeric(cxo['totalamount'],    errors='coerce').fillna(0)
    cxo['sent_at']        = pd.to_datetime(cxo['sent_at'],       errors='coerce', format='mixed', utc=True)
    cxo['order_at']       = pd.to_datetime(cxo['order_at'],      errors='coerce', format='mixed', utc=True)
    orders['totalamount'] = pd.to_numeric(orders['totalamount'], errors='coerce').fillna(0)
    orders['createdat']   = pd.to_datetime(orders['createdat'],  errors='coerce', format='mixed', utc=True)

    cxo['dias_diff'] = (cxo['order_at'] - cxo['sent_at']).dt.days
    cxo['conv_30d']  = (cxo['dias_diff'] >= 0) & (cxo['dias_diff'] <= 30)

    camp_loja = cxo.groupby('storeid').agg(
        msgs_enviadas = ('message_id',  'count'),
        conv_30d      = ('conv_30d',    'sum'),
        receita_30d   = ('totalamount', lambda x: x[cxo.loc[x.index, 'conv_30d']].sum()),
    ).reset_index()

    ord_loja = orders.groupby('storeid').agg(
        fat_total    = ('totalamount', 'sum'),
        n_pedidos    = ('id',          'count'),
        ticket_medio = ('totalamount', 'mean'),
    ).reset_index()

    df = camp_loja.merge(ord_loja, on='storeid', how='inner')
    df = df.merge(
        store[['id', 'name']].rename(columns={'id': 'storeid', 'name': 'Loja'}),
        on='storeid', how='left'
    )

    df['taxa_conv_30d'] = (df['conv_30d']    / df['msgs_enviadas'] * 100).round(2)
    df['pct_fat_camp']  = (df['receita_30d'] / df['fat_total']     * 100).round(2)
    df['roi_por_msg']   = (df['receita_30d'] / df['msgs_enviadas']).round(2)

    return df

df = carregar()

# ── Regressão ──
X      = df[['msgs_enviadas']].values
y      = df['fat_total'].values
model  = LinearRegression().fit(X, y)
y_pred = model.predict(X)

r2       = r2_score(y, y_pred)
coef     = model.coef_[0]
intc     = model.intercept_
residuos = y - y_pred

slope, intercept, r_value, p_value, std_err = stats.linregress(
    df['msgs_enviadas'].values, df['fat_total'].values
)

# ── Seção 1: Contexto ──
st.markdown("## 1. Contexto e variáveis")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
**Variável independente (X)**
> `Mensagens enviadas` — total de mensagens de campanha disparadas pela loja no período analisado.

Representa o **investimento em campanhas** de cada loja parceira.
""")
with col2:
    st.markdown("""
**Variável dependente (Y)**
> `Faturamento total` — soma de todos os pedidos realizados na loja no mesmo período.

Representa o **resultado financeiro** da loja.
""")

st.markdown("---")

# ── Seção 2: Estatísticas descritivas ──
st.markdown("## 2. Estatísticas descritivas")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Lojas analisadas",      str(len(df)))
col2.metric("Média msgs enviadas",   f"{df['msgs_enviadas'].mean():,.0f}")
col3.metric("Média faturamento",     f"R$ {df['fat_total'].mean():,.2f}")
col4.metric("Correlação de Pearson", f"{r_value:.4f}")

desc = df[['msgs_enviadas', 'fat_total', 'taxa_conv_30d', 'roi_por_msg']].describe().round(2)
desc.index = ['Contagem', 'Média', 'Desvio padrão', 'Mínimo', 'Q1 (25%)', 'Mediana', 'Q3 (75%)', 'Máximo']
desc.columns = ['Msgs enviadas', 'Faturamento total (R$)', 'Taxa conv. 30d (%)', 'ROI por msg (R$)']
st.dataframe(desc, use_container_width=True)

st.markdown("---")

# ── Seção 3: Modelo ──
st.markdown("## 3. Modelo de regressão linear")

r1, r2m, r3, r4 = st.columns(4)
r1.metric("R²",               f"{r2:.4f}",        help="Proporção da variância de Y explicada por X")
r2m.metric("Coeficiente (β)", f"{coef:.4f}",       help="Variação no faturamento a cada +1 mensagem enviada")
r3.metric("Intercepto (α)",   f"R$ {intc:,.2f}")
r4.metric("p-valor",          f"{p_value:.4f}",    help="< 0.05 = coeficiente estatisticamente significativo")

st.markdown(f"""
**Equação ajustada:**
```
Faturamento total = {coef:.4f} × Mensagens enviadas + {intc:,.2f}
```
""")

st.markdown("#### Interpretação do modelo")

if p_value < 0.05:
    st.info(f"✅ O coeficiente é **estatisticamente significativo** (p={p_value:.4f} < 0.05) — a relação não é fruto do acaso.")
else:
    st.warning(f"⚠️ O coeficiente **não é estatisticamente significativo** (p={p_value:.4f} ≥ 0.05) — a relação pode ser fruto do acaso dado o tamanho da amostra.")

if r2 >= 0.7:
    qualidade = f"O modelo tem **ajuste forte** (R²={r2:.2f}): o volume de mensagens enviadas explica {r2*100:.1f}% da variação no faturamento entre as lojas."
elif r2 >= 0.3:
    qualidade = f"O modelo tem **ajuste moderado** (R²={r2:.2f}): o volume de mensagens enviadas explica {r2*100:.1f}% da variação no faturamento. Os demais {(1-r2)*100:.1f}% são influenciados por outros fatores como localização, qualidade do produto e canal de venda."
else:
    qualidade = f"O modelo tem **ajuste fraco** (R²={r2:.2f}): o volume de mensagens enviadas sozinho explica apenas {r2*100:.1f}% da variação no faturamento, sugerindo que outros fatores têm peso maior."

st.markdown(qualidade)
st.markdown(
    f"O coeficiente β={coef:.4f} indica que, **a cada mensagem adicional enviada**, "
    f"o faturamento da loja aumenta em média **R$ {coef:.2f}**. "
    f"Isso sugere que campanhas têm retorno financeiro positivo, "
    f"mas com variação considerável entre as lojas."
)

st.markdown("---")

# ── Seção 4: Gráficos ──
st.markdown("## 4. Visualizações")

# Gráfico 1: Scatter + regressão
st.markdown("### Dispersão com linha de regressão")

x_line = np.linspace(X.min(), X.max(), 200)
y_line = model.predict(x_line.reshape(-1, 1))

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df['msgs_enviadas'], y=df['fat_total'],
    mode='markers',
    text=df['Loja'],
    marker=dict(color='#22d3ee', size=10, opacity=0.8,
                line=dict(color='#0e7490', width=1)),
    name='Lojas',
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Msgs enviadas: %{x:,.0f}<br>"
        "Faturamento: R$ %{y:,.2f}<extra></extra>"
    )
))
fig1.add_trace(go.Scatter(
    x=x_line, y=y_line,
    mode='lines',
    line=dict(color='#f97316', width=2.5, dash='dash'),
    name=f'Reta ajustada  (R²={r2:.2f})'
))
fig1.update_layout(
    xaxis_title='Mensagens enviadas',
    yaxis_title='Faturamento total (R$)',
    height=500,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#555',
    legend=dict(x=0.01, y=0.99),
)
fig1.update_xaxes(gridcolor='#e5e7eb', zerolinecolor='#e5e7eb')
fig1.update_yaxes(gridcolor='#e5e7eb', zerolinecolor='#e5e7eb')
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Resíduos
st.markdown("### Análise de resíduos")
st.caption(
    "Resíduos são a diferença entre o valor real e o previsto pelo modelo. "
    "Distribuição aleatória em torno de zero indica que o modelo está bem ajustado."
)

col_g1, col_g2 = st.columns(2)

with col_g1:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=y_pred, y=residuos,
        mode='markers',
        marker=dict(color='#a78bfa', size=9, opacity=0.75),
        hovertemplate="Ŷ: R$ %{x:,.2f}<br>Resíduo: R$ %{y:,.2f}<extra></extra>"
    ))
    fig2.add_hline(y=0, line_dash='dash', line_color='#f97316', line_width=1.5)
    fig2.update_layout(
        title='Resíduos vs Valores ajustados',
        xaxis_title='Valores ajustados (Ŷ)',
        yaxis_title='Resíduos (Y − Ŷ)',
        height=360,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#555',
    )
    fig2.update_xaxes(gridcolor='#e5e7eb')
    fig2.update_yaxes(gridcolor='#e5e7eb')
    st.plotly_chart(fig2, use_container_width=True)

with col_g2:
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=residuos,
        nbinsx=10,
        marker_color='#a78bfa',
        opacity=0.8,
        name='Resíduos'
    ))
    fig3.update_layout(
        title='Distribuição dos resíduos',
        xaxis_title='Resíduo (R$)',
        yaxis_title='Frequência',
        height=360,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#555',
    )
    fig3.update_xaxes(gridcolor='#e5e7eb')
    fig3.update_yaxes(gridcolor='#e5e7eb')
    st.plotly_chart(fig3, use_container_width=True)

# Gráfico 3: ROI por loja
st.markdown("### ROI por mensagem enviada — por loja")
st.caption("Receita de campanha (30d) dividida pelo número de mensagens enviadas.")

df_roi = df[df['roi_por_msg'] > 0].sort_values('roi_por_msg', ascending=True)
fig4 = go.Figure(go.Bar(
    x=df_roi['roi_por_msg'],
    y=df_roi['Loja'],
    orientation='h',
    marker=dict(color=df_roi['roi_por_msg'], colorscale='Oranges', showscale=False),
    hovertemplate="<b>%{y}</b><br>ROI: R$ %{x:,.2f} por mensagem<extra></extra>"
))
fig4.update_layout(
    xaxis_title='ROI por mensagem enviada (R$)',
    yaxis_title='',
    height=480,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font_color='#555',
)
fig4.update_xaxes(gridcolor='#e5e7eb')
fig4.update_yaxes(gridcolor='#e5e7eb')
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── Seção 5: Conclusão ──
st.markdown("## 5. Conclusão")
st.markdown(f"""
A regressão linear entre **mensagens de campanha enviadas** e **faturamento total** das lojas
parceiras revelou uma relação positiva e estatisticamente {'significativa' if p_value < 0.05 else 'observável'}
(β={coef:.2f}, R²={r2:.2f}, p={p_value:.4f}).

O modelo explica **{r2*100:.1f}% da variação** no faturamento entre as lojas, o que indica que
campanhas de marketing têm impacto mensurável, mas que outros fatores — como canal de venda,
localização geográfica e perfil do cliente — também influenciam o resultado final.

O ROI médio por mensagem enviada é de **R$ {df['roi_por_msg'].median():.2f}** (mediana),
com forte variação entre lojas, sugerindo que a **qualidade da campanha** importa tanto
quanto o volume.

> ⚠️ **Limitação:** A conversão foi definida como pedido realizado em até 30 dias após o
> envio da mensagem. Isso é uma *correlação temporal*, não prova de causalidade direta —
> o cliente pode ter comprado independentemente da campanha.
""")

# ── Tabela ──
st.markdown("---")
with st.expander("📋 Dados completos por loja"):
    tabela = df[[
        'Loja', 'msgs_enviadas', 'conv_30d', 'taxa_conv_30d',
        'receita_30d', 'fat_total', 'pct_fat_camp', 'roi_por_msg', 'ticket_medio'
    ]].sort_values('fat_total', ascending=False).rename(columns={
        'msgs_enviadas':  'Msgs enviadas',
        'conv_30d':       'Conv. 30d',
        'taxa_conv_30d':  'Taxa conv. (%)',
        'receita_30d':    'Receita campanha (R$)',
        'fat_total':      'Faturamento total (R$)',
        'pct_fat_camp':   '% fat. via campanha',
        'roi_por_msg':    'ROI/msg (R$)',
        'ticket_medio':   'Ticket médio (R$)',
    })
    st.dataframe(
        tabela.style.format({
            'Taxa conv. (%)':         '{:.1f}%',
            'Receita campanha (R$)':  'R$ {:,.2f}',
            'Faturamento total (R$)': 'R$ {:,.2f}',
            '% fat. via campanha':    '{:.1f}%',
            'ROI/msg (R$)':           'R$ {:,.2f}',
            'Ticket médio (R$)':      'R$ {:,.2f}',
        }),
        use_container_width=True,
        hide_index=True
    )