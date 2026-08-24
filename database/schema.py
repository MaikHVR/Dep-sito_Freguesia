from database.conexao import obter_conexao

def criar_tabelas():
    conexao = obter_conexao()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            categoria TEXT,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            produto_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'em estoque',
            data_entrada TEXT NOT NULL,
            data_saida TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contador_etiquetas (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            ultimo_numero INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO contador_etiquetas (id, ultimo_numero)
        VALUES (1, 0)
    """)

    conexao.commit()
    conexao.close()