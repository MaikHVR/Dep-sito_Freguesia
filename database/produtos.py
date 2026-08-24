from database.conexao import obter_conexao

CATEGORIAS_DISPONIVEIS = ["Sorvete", "Açaí"]


def adicionar_produto(nome, categoria):
    """Cadastra um novo produto. Retorna (sucesso, mensagem)."""
    nome = nome.strip()
    if not nome:
        return False, "O nome do produto não pode ficar vazio."

    if categoria not in CATEGORIAS_DISPONIVEIS:
        return False, f"Categoria inválida. Escolha entre: {', '.join(CATEGORIAS_DISPONIVEIS)}."

    conexao = obter_conexao()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "INSERT INTO produtos (nome, categoria, ativo) VALUES (?, ?, 1)",
            (nome, categoria)
        )
        conexao.commit()
        return True, f"Produto '{nome}' cadastrado com sucesso."
    except Exception as erro:
        if "UNIQUE constraint failed" in str(erro):
            return False, f"Já existe um produto chamado '{nome}'."
        return False, f"Erro ao cadastrar produto: {erro}"
    finally:
        conexao.close()


def editar_nome_produto(produto_id, novo_nome):
    """Altera o nome de um produto existente. Retorna (sucesso, mensagem)."""
    novo_nome = novo_nome.strip()
    if not novo_nome:
        return False, "O nome do produto não pode ficar vazio."

    conexao = obter_conexao()
    cursor = conexao.cursor()

    try:
        cursor.execute(
            "UPDATE produtos SET nome = ? WHERE id = ?",
            (novo_nome, produto_id)
        )
        conexao.commit()
        return True, f"Produto renomeado para '{novo_nome}'."
    except Exception as erro:
        if "UNIQUE constraint failed" in str(erro):
            return False, f"Já existe um produto chamado '{novo_nome}'."
        return False, f"Erro ao renomear produto: {erro}"
    finally:
        conexao.close()


def produto_possui_historico(produto_id):
    """Retorna True se existe alguma caixa (em estoque ou removida) vinculada a esse produto."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM caixas WHERE produto_id = ?", (produto_id,))
    total = cursor.fetchone()["total"]
    conexao.close()
    return total > 0


def excluir_produto(produto_id):
    """
    Exclui definitivamente um produto, mas SOMENTE se ele nunca teve
    nenhuma caixa vinculada (para não corromper o histórico).
    Retorna (sucesso, mensagem).
    """
    if produto_possui_historico(produto_id):
        return False, (
            "Este produto já tem caixas cadastradas no histórico "
            "(mesmo que removidas do estoque) e não pode ser excluído, "
            "para não perder esse registro. Use 'Desativar' em vez disso."
        )

    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conexao.commit()
    conexao.close()
    return True, "Produto excluído com sucesso."


def listar_produtos(apenas_ativos=True):
    """Retorna a lista de produtos, cada um como um dicionário."""
    conexao = obter_conexao()
    cursor = conexao.cursor()

    if apenas_ativos:
        cursor.execute("SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome")
    else:
        cursor.execute("SELECT * FROM produtos ORDER BY nome")

    produtos = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return produtos


def desativar_produto(produto_id):
    """Marca um produto como inativo (não aparece mais nas seleções, mas o histórico permanece)."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (produto_id,))
    conexao.commit()
    conexao.close()


def reativar_produto(produto_id):
    """Reverte a desativação, caso você mude de ideia."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("UPDATE produtos SET ativo = 1 WHERE id = ?", (produto_id,))
    conexao.commit()
    conexao.close()