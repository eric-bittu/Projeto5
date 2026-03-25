import pandas as pd
import matplotlib.pyplot as plt


def carregar_dados(caminho):
    df = pd.read_csv(caminho)

    # Lista de palavras que indicam que a coluna REALMENTE é uma data
    termos_data = ['date', 'at', 'scheduled', 'created', 'updated']

    for col in df.columns:
        col_lower = col.lower()
        # Só tenta converter se o nome da coluna sugerir data
        # E se NÃO for um ID (evita o erro que você teve)
        if any(termo in col_lower for termo in termos_data) and 'id' not in col_lower:
            try:
                # errors='coerce' transforma o que não é data em "NaT" (Not a Time)
                # em vez de travar o programa com erro
                df[col] = pd.to_datetime(df[col], errors='coerce')
            except:
                pass
    return df


def criar_figura(df, col_x, col_y, tipo_grafico):
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)

    try:
        # --- REGRA PARA DATA ---
        if pd.api.types.is_datetime64_any_dtype(df[col_x]):
            dados = df.groupby(df[col_x].dt.date)[col_y].sum() if pd.api.types.is_numeric_dtype(
                df[col_y]) else df.groupby(df[col_x].dt.date).size()
            dados.plot(kind='line', ax=ax, marker='o')
            ax.set_title(f"Tendência Temporal: {col_y}")

        # --- REGRA PARA IDs (storeid, customerid, id) ---
        elif 'id' in col_x.lower() or 'id' in col_y.lower():
            # Se for ID, quase sempre queremos ver a CONTAGEM (Frequência)
            # Ex: "Quais lojas (storeid) têm mais pedidos?"
            dados_plot = df[col_x].value_counts().head(10)  # Pega apenas os 10 que mais aparecem
            dados_plot.plot(kind='bar', ax=ax, color='teal')
            ax.set_title(f"Top 10 Frequência: {col_x}")
            ax.set_ylabel("Quantidade de Registros")

        # --- REGRA PARA DADOS NUMÉRICOS (Valores, Preços) ---
        elif pd.api.types.is_numeric_dtype(df[col_y]) and col_x != col_y:
            # Agrupa por categoria e soma o valor (Ex: Total por Canal de Venda)
            df.groupby(col_x)[col_y].sum().sort_values(ascending=False).head(15).plot(kind='bar', ax=ax)
            ax.set_title(f"Soma de {col_y} por {col_x}")

        # --- CASO PADRÃO (Categorias) ---
        else:
            df[col_x].value_counts().head(15).plot(kind='bar', ax=ax)
            ax.set_title(f"Distribuição de {col_x}")

        # Ajustes de layout para não cortar os IDs
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

    except Exception as e:
        ax.clear()
        ax.text(0.5, 0.5, f"Erro ao gerar gráfico:\n{e}", ha='center', va='center')

    return fig