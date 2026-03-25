import tkinter as tk
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from backend.processador import carregar_dados, criar_figura

class TelaAnaliseDinamica(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.df = None
        self.canvas = None

        # --- Painel de Controle (Esquerda) ---
        self.controls = tk.Frame(self, width=200, padx=10, pady=10)
        self.controls.pack(side="left", fill="y")

        tk.Button(self.controls, text="1. Selecionar CSV", command=self.importar).pack(fill="x", pady=5)

        tk.Label(self.controls, text="Eixo X:").pack(anchor="w")
        self.cb_x = ttk.Combobox(self.controls, state="readonly")
        self.cb_x.pack(fill="x", pady=5)

        tk.Label(self.controls, text="Eixo Y:").pack(anchor="w")
        self.cb_y = ttk.Combobox(self.controls, state="readonly")
        self.cb_y.pack(fill="x", pady=5)

        tk.Label(self.controls, text="Tipo de Gráfico:").pack(anchor="w")
        self.cb_tipo = ttk.Combobox(self.controls, values=["Barras", "Linhas", "Dispersão (Scatter)"], state="readonly")
        self.cb_tipo.current(0)
        self.cb_tipo.pack(fill="x", pady=5)

        tk.Button(self.controls, text="Gerar/Atualizar Gráfico", bg="blue", fg="white",
                  command=self.plotar).pack(fill="x", pady=20)

        # --- Área do Gráfico (Direita) ---
        self.chart_frame = tk.Frame(self, bg="white")
        self.chart_frame.pack(side="right", fill="both", expand=True)

    def importar(self):
        caminho = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if caminho:
            self.df = carregar_dados(caminho)
            colunas = list(self.df.columns)
            self.cb_x['values'] = colunas
            self.cb_y['values'] = colunas
            self.cb_x.current(0)
            self.cb_y.current(0)

    def plotar(self):
        if self.df is None: return

        # Limpa o gráfico anterior se existir
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Chama o backend para gerar a figura
        fig = criar_figura(
            self.df,
            self.cb_x.get(),
            self.cb_y.get(),
            self.cb_tipo.get()
        )

        # Desenha a figura no Tkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)