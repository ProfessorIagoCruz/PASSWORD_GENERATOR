import tkinter as tk
import random
import string
import sqlite3
from datetime import datetime
from tkinter import ttk, messagebox

class GeradorDeSenhas:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Gerador de Senhas")
        self.janela.geometry("600x650")
        self.janela.configure(bg="#f0f0f0")

        # Conectar ao banco de dados
        self.conn = sqlite3.connect('senhas.db')
        self.criar_tabela()

        # Frame do cabeçalho
        self.header_frame = tk.Frame(self.janela, bg="#4A90E2")
        self.header_frame.pack(pady=10, fill=tk.X)

        self.header_label = tk.Label(self.header_frame, text="Gerador de Senhas", font=("Arial", 20, "bold"), bg="#4A90E2", fg="white")
        self.header_label.pack(pady=10)

        # Frame principal
        self.main_frame = tk.Frame(self.janela, bg="#f0f0f0")
        self.main_frame.pack(pady=10, padx=20)

        self.label = tk.Label(self.main_frame, text="Clique no botão para gerar uma senha:", bg="#f0f0f0", font=("Arial", 12))
        self.label.pack(pady=5)

        self.description_label = tk.Label(self.main_frame, text="Descrição:", bg="#f0f0f0", font=("Arial", 12))
        self.description_label.pack(pady=5)

        self.description_entry = tk.Entry(self.main_frame, width=40, font=("Arial", 12))
        self.description_entry.pack(pady=5)

        self.password_display = tk.Entry(self.main_frame, width=40, font=("Arial", 12))
        self.password_display.pack(pady=10)

        self.generate_button = tk.Button(self.main_frame, text="Gerar Senha", command=self.gerar_senha, bg="#5BBF8D", fg="white", font=("Arial", 12, "bold"))
        self.generate_button.pack(pady=10)

        # Campos de pesquisa
        self.search_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.search_frame.pack(pady=10)

        self.search_label_desc = tk.Label(self.search_frame, text="Pesquisar por descrição:", bg="#f0f0f0", font=("Arial", 12))
        self.search_label_desc.grid(row=0, column=0, padx=5)

        self.search_entry_desc = tk.Entry(self.search_frame, width=15, font=("Arial", 12))
        self.search_entry_desc.grid(row=0, column=1, padx=5)

        self.search_button_desc = tk.Button(self.search_frame, text="Buscar", command=self.pesquisar_por_descricao, bg="#5BBF8D", fg="white", font=("Arial", 12, "bold"))
        self.search_button_desc.grid(row=0, column=2, padx=5)

        self.search_label_date = tk.Label(self.search_frame, text="Pesquisar por data (YYYY-MM-DD):", bg="#f0f0f0", font=("Arial", 12))
        self.search_label_date.grid(row=1, column=0, padx=5)

        self.search_entry_date = tk.Entry(self.search_frame, width=15, font=("Arial", 12))
        self.search_entry_date.grid(row=1, column=1, padx=5)

        self.search_button_date = tk.Button(self.search_frame, text="Buscar", command=self.pesquisar_por_data, bg="#5BBF8D", fg="white", font=("Arial", 12, "bold"))
        self.search_button_date.grid(row=1, column=2, padx=5)

        self.history_label = tk.Label(self.main_frame, text="Histórico de Senhas:", bg="#f0f0f0", font=("Arial", 12, "bold"))
        self.history_label.pack(pady=10)

        # Frame para o histórico com Treeview
        self.history_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.history_frame.pack(pady=10)

        self.tree = ttk.Treeview(self.history_frame, columns=("ID", "Descrição", "Data", "Senha"), show='headings', height=10)
        self.tree.pack(side=tk.LEFT)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Senha", text="Senha")

        # Adicionando barra de rolagem
        self.scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.carregar_historico()

    def criar_tabela(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS senhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT,
            data_gerada TEXT,
            senha TEXT
        )''')
        self.conn.commit()

    def gerar_senha(self):
        comprimento = random.randint(10, 50)  # Comprimento aleatório entre 10 e 50
        caracteres = string.ascii_letters + string.digits + string.punctuation
        senha = ''.join(random.choice(caracteres) for _ in range(comprimento))
        self.password_display.delete(0, tk.END)
        self.password_display.insert(0, senha)

        descricao = self.description_entry.get()
        data_gerada = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        self.salvar_senha(descricao, data_gerada, senha)
        self.carregar_historico()

    def salvar_senha(self, descricao, data_gerada, senha):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO senhas (descricao, data_gerada, senha) VALUES (?, ?, ?)', 
                       (descricao, data_gerada, senha))
        self.conn.commit()

    def carregar_historico(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, descricao, data_gerada, senha FROM senhas')
        senhas = cursor.fetchall()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for senha in senhas:
            self.tree.insert("", tk.END, values=senha)

    def pesquisar_por_descricao(self):
        descricao = self.search_entry_desc.get()
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, descricao, data_gerada, senha FROM senhas WHERE descricao LIKE ?', ('%' + descricao + '%',))
        resultados = cursor.fetchall()
        self.exibir_resultados(resultados)

    def pesquisar_por_data(self):
        data = self.search_entry_date.get()
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, descricao, data_gerada, senha FROM senhas WHERE data_gerada LIKE ?', (data + '%',))
        resultados = cursor.fetchall()
        self.exibir_resultados(resultados)

    def exibir_resultados(self, resultados):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if resultados:
            for senha in resultados:
                self.tree.insert("", tk.END, values=senha)
        else:
            self.tree.insert("", tk.END, values=("Nenhum resultado encontrado.", "", "", ""))

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    janela = tk.Tk()
    app = GeradorDeSenhas(janela)
    janela.mainloop()
    
    

