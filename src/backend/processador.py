import pandas as pd
import matplotlib.pyplot as plt

def gerar_grafico(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo) # Ou pd.read_excel
        # Exemplo: Gera um gráfico de barras das primeiras 5 linhas
        df.head().plot(kind='bar')
        plt.title(f"Análise de: {caminho_arquivo.split('/')[-1]}")
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Erro ao processar: {e}")