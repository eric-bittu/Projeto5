import tkinter as tk
from tkinter import filedialog, messagebox
from backend.processador import gerar_grafico


class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador de Dados")
        self.geometry("400x300")

        # Container principal
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.tela_menu = TelaMenu(parent=self.container, controller=self)
        self.tela_analise = TelaAnalise(parent=self.container, controller=self)

        self.mostrar_tela("menu")

    def mostrar_tela(self, nome_tela):
        if nome_tela == "menu":
            self.tela_analise.pack_forget()
            self.tela_menu.pack(fill="both", expand=True)
        else:
            self.tela_menu.pack_forget()
            self.tela_analise.pack(fill="both", expand=True)


class TelaMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Menu Principal", font=("Arial", 18))
        label.pack(pady=20)

        btn = tk.Button(self, text="Ir para Análise",
                        command=lambda: controller.mostrar_tela("analise"))
        btn.pack()


class TelaAnalise(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.caminho_arquivo = ""

        label = tk.Label(self, text="Tela de Análise", font=("Arial", 18))
        label.pack(pady=10)

        btn_selecionar = tk.Button(self, text="Escolher Arquivo (CSV)", command=self.selecionar_arquivo)
        btn_selecionar.pack(pady=5)

        self.lbl_arquivo = tk.Label(self, text="Nenhum arquivo selecionado", fg="gray")
        self.lbl_arquivo.pack()

        btn_gerar = tk.Button(self, text="Gerar Gráfico", command=self.executar_analise, bg="green", fg="white")
        btn_gerar.pack(pady=20)

        btn_voltar = tk.Button(self, text="Voltar ao Menu", command=lambda: controller.mostrar_tela("menu"))
        btn_voltar.pack()

    def selecionar_arquivo(self):
        self.caminho_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if self.caminho_arquivo:
            self.lbl_arquivo.config(text=self.caminho_arquivo.split('/')[-1])

    def executar_analise(self):
        if not self.caminho_arquivo:
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return
        gerar_grafico(self.caminho_arquivo)