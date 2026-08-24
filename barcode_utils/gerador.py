import io
import barcode
from barcode.writer import ImageWriter

PREFIXO = "FREG"


def formatar_codigo(numero):
    """
    Transforma um número inteiro no texto final do código de barras.
    Ex: 148 -> 'FREG-000148'
    """
    return f"{PREFIXO}-{numero:06d}"


def gerar_imagem_codigo_barras(texto_codigo):
    """
    Gera a imagem (PNG, em memória) de um código de barras Code128
    a partir do texto informado (ex: 'FREG-000148').
    Retorna os bytes da imagem PNG, prontos para salvar em arquivo
    ou inserir num PDF.
    """
    codigo128 = barcode.get_barcode_class("code128")
    instancia = codigo128(texto_codigo, writer=ImageWriter())

    buffer = io.BytesIO()
    instancia.write(
        buffer,
        options={
            "write_text": True,   # mostra o texto legível abaixo do código
            "module_height": 10,  # altura das barras (mm)
            "quiet_zone": 2,      # margem lateral (mm)
        },
    )
    buffer.seek(0)
    return buffer.read()
