from database.conexao import obter_conexao


def obter_ultimo_numero():
    """Retorna o último número de etiqueta já gerado (sem alterar nada)."""
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT ultimo_numero FROM contador_etiquetas WHERE id = 1")
    linha = cursor.fetchone()
    conexao.close()
    return linha["ultimo_numero"]


def avancar_contador(quantidade):
    """
    Avança o contador em `quantidade` unidades e retorna o intervalo gerado.
    Ex: se o último número era 147 e quantidade=50, retorna (148, 197)
    e o contador passa a valer 197.
    """
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que zero.")

    conexao = obter_conexao()
    cursor = conexao.cursor()

    cursor.execute("SELECT ultimo_numero FROM contador_etiquetas WHERE id = 1")
    ultimo = cursor.fetchone()["ultimo_numero"]

    primeiro_novo = ultimo + 1
    ultimo_novo = ultimo + quantidade

    cursor.execute(
        "UPDATE contador_etiquetas SET ultimo_numero = ? WHERE id = 1",
        (ultimo_novo,)
    )
    conexao.commit()
    conexao.close()

    return primeiro_novo, ultimo_novo
