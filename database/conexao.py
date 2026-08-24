import sqlite3

CAMINHO_BANCO = "estoque.db"

def obter_conexao():
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao