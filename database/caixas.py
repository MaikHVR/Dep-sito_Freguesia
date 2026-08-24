from datetime import datetime
from database.conexao import obter_conexao


def cadastrar_caixa(codigo, produto_id):
    """Cadastra uma nova caixa (entrada). Retorna (sucesso, mensagem)."""
    codigo = codigo.strip()
    if not codigo:
        return False, "Código de barras vazio."

    conexao = obter_conexao()
    cursor = conexao.cursor()

    # Verifica se esse código já foi usado antes (em estoque ou removido)
    cursor.execute("SELECT status, data_entrada FROM caixas WHERE codigo = ?", (codigo,))
    existente = cursor.fetchone()

    if existente:
        conexao.close()
        return False, (
            f"Código '{codigo}' já está cadastrado "
            f"(status: {existente['status']}, entrada: {existente['data_entrada']})."
        )

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """INSERT INTO caixas (codigo, produto_id, status, data_entrada)
           VALUES (?, ?, 'em estoque', ?)""",
        (codigo, produto_id, agora)
    )
    conexao.commit()
    conexao.close()
    return True, f"Caixa '{codigo}' cadastrada com sucesso."


def remover_caixa(codigo):
    """Marca uma caixa como removida (saída). Retorna (sucesso, mensagem)."""
    codigo = codigo.strip()
    if not codigo:
        return False, "Código de barras vazio."

    conexao = obter_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT status FROM caixas WHERE codigo = ?", (codigo,))
    existente = cursor.fetchone()

    if not existente:
        conexao.close()
        return False, f"Código '{codigo}' não está cadastrado no sistema."

    if existente["status"] == "removido":
        conexao.close()
        return False, f"Caixa '{codigo}' já foi removida anteriormente."

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "UPDATE caixas SET status = 'removido', data_saida = ? WHERE codigo = ?",
        (agora, codigo)
    )
    conexao.commit()
    conexao.close()
    return True, f"Caixa '{codigo}' removida com sucesso."


def listar_em_estoque(produto_id=None):
    """Retorna as caixas em estoque, opcionalmente filtradas por produto."""
    conexao = obter_conexao()
    cursor = conexao.cursor()

    if produto_id:
        cursor.execute(
            """SELECT caixas.*, produtos.nome AS produto_nome
               FROM caixas
               JOIN produtos ON caixas.produto_id = produtos.id
               WHERE caixas.status = 'em estoque' AND caixas.produto_id = ?
               ORDER BY caixas.data_entrada""",
            (produto_id,)
        )
    else:
        cursor.execute(
            """SELECT caixas.*, produtos.nome AS produto_nome
               FROM caixas
               JOIN produtos ON caixas.produto_id = produtos.id
               WHERE caixas.status = 'em estoque'
               ORDER BY caixas.data_entrada"""
        )

    resultado = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return resultado