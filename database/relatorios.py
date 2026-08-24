from database.conexao import obter_conexao


def resumo_estoque_atual(categoria=None):
    """
    Retorna a quantidade de caixas em estoque, agrupada por produto.
    Cada item: {produto_nome, categoria, quantidade}
    """
    conexao = obter_conexao()
    cursor = conexao.cursor()

    sql = """
        SELECT produtos.nome AS produto_nome, produtos.categoria AS categoria,
               COUNT(*) AS quantidade
        FROM caixas
        JOIN produtos ON caixas.produto_id = produtos.id
        WHERE caixas.status = 'em estoque'
    """
    parametros = []

    if categoria:
        sql += " AND produtos.categoria = ?"
        parametros.append(categoria)

    sql += " GROUP BY produtos.id ORDER BY produtos.nome"

    cursor.execute(sql, parametros)
    resultado = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return resultado


def contar_movimentacoes_por_periodo(data_inicio, data_fim, tipo, categoria=None, produto_id=None):
    """
    Conta caixas movimentadas (entradas ou saídas) num intervalo de datas,
    agrupadas por produto.

    tipo: 'entrada' (usa data_entrada) ou 'saida' (usa data_saida, só caixas removidas)
    data_inicio / data_fim: strings 'YYYY-MM-DD'
    categoria: filtro opcional ('Sorvete', 'Açaí', ou None para todos)
    produto_id: filtro opcional (None para todos)

    Retorna lista de {produto_nome, categoria, quantidade}
    """
    campo_data = "caixas.data_entrada" if tipo == "entrada" else "caixas.data_saida"

    conexao = obter_conexao()
    cursor = conexao.cursor()

    sql = f"""
        SELECT produtos.nome AS produto_nome, produtos.categoria AS categoria,
               COUNT(*) AS quantidade
        FROM caixas
        JOIN produtos ON caixas.produto_id = produtos.id
        WHERE {campo_data} IS NOT NULL
          AND date({campo_data}) BETWEEN date(?) AND date(?)
    """
    parametros = [data_inicio, data_fim]

    if tipo == "saida":
        sql += " AND caixas.status = 'removido'"

    if categoria:
        sql += " AND produtos.categoria = ?"
        parametros.append(categoria)

    if produto_id:
        sql += " AND caixas.produto_id = ?"
        parametros.append(produto_id)

    sql += " GROUP BY produtos.id ORDER BY produtos.nome"

    cursor.execute(sql, parametros)
    resultado = [dict(linha) for linha in cursor.fetchall()]
    conexao.close()
    return resultado
