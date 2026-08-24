import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from barcode_utils.gerador import formatar_codigo, gerar_imagem_codigo_barras

# --- Configuração da grade de etiquetas (ajustável) ---
MARGEM = 1.0 * cm
ESPACAMENTO = 0.3 * cm
COLUNAS = 5
LINHAS = 12
ETIQUETAS_POR_PAGINA = COLUNAS * LINHAS


def gerar_pdf_etiquetas(numero_inicial, numero_final, caminho_arquivo):
    """
    Gera um PDF com uma grade de etiquetas de código de barras,
    cobrindo todos os números do intervalo [numero_inicial, numero_final].
    Cria quantas páginas forem necessárias automaticamente.
    """
    largura_pagina, altura_pagina = A4
    largura_util = largura_pagina - 2 * MARGEM
    altura_util = altura_pagina - 2 * MARGEM

    largura_etiqueta = (largura_util - (COLUNAS - 1) * ESPACAMENTO) / COLUNAS
    altura_etiqueta = (altura_util - (LINHAS - 1) * ESPACAMENTO) / LINHAS

    pdf = canvas.Canvas(caminho_arquivo, pagesize=A4)

    numeros = list(range(numero_inicial, numero_final + 1))
    posicao_na_pagina = 0

    for numero in numeros:
        # Se a página encheu, fecha e começa uma nova
        if posicao_na_pagina == ETIQUETAS_POR_PAGINA:
            pdf.showPage()
            posicao_na_pagina = 0

        coluna = posicao_na_pagina % COLUNAS
        linha = posicao_na_pagina // COLUNAS

        x = MARGEM + coluna * (largura_etiqueta + ESPACAMENTO)
        # Desenha de cima para baixo na página
        y = altura_pagina - MARGEM - altura_etiqueta - linha * (altura_etiqueta + ESPACAMENTO)

        texto_codigo = formatar_codigo(numero)
        imagem_bytes = gerar_imagem_codigo_barras(texto_codigo)
        imagem = ImageReader(io.BytesIO(imagem_bytes))

        pdf.drawImage(
            imagem, x, y,
            width=largura_etiqueta, height=altura_etiqueta,
            preserveAspectRatio=True, anchor='c'
        )

        posicao_na_pagina += 1

    pdf.save()

    total_paginas = (len(numeros) + ETIQUETAS_POR_PAGINA - 1) // ETIQUETAS_POR_PAGINA
    return total_paginas