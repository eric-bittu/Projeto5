import tkinter as tk
from frontend.interface import TelaAnaliseDinamica

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dashboard de Dados Cannoli")
    root.geometry("900x600")

    app = TelaAnaliseDinamica(root)
    app.pack(fill="both", expand=True)

    root.mainloop()