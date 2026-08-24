from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QSpinBox,
    QPushButton, QLabel, QMessageBox, QFileDialog
)

from database.contador import obter_ultimo_numero, avancar_contador
from barcode_utils.pdf_etiquetas import gerar_pdf_etiquetas


class AbaImprimirAdesivos(QWidget):
    def __init__(self):
        super().__init__()
        self._montar_layout()
        self._atualizar_label_ultimo_numero()

    def _montar_layout(self):
        layout_principal = QVBoxLayout()

        self.label_ultimo_numero = QLabel()
        layout_principal.addWidget(self.label_ultimo_numero)

        layout_formulario = QFormLayout()
        self.campo_quantidade = QSpinBox()
        self.campo_quantidade.setMinimum(1)
        self.campo_quantidade.setMaximum(1000)
        self.campo_quantidade.setValue(50)
        layout_formulario.addRow("Quantidade de etiquetas:", self.campo_quantidade)
        layout_principal.addLayout(layout_formulario)

        botao_gerar = QPushButton("Gerar PDF de Etiquetas")
        botao_gerar.clicked.connect(self._gerar_pdf)
        layout_principal.addWidget(botao_gerar)

        layout_principal.addStretch()
        self.setLayout(layout_principal)

    def _atualizar_label_ultimo_numero(self):
        ultimo = obter_ultimo_numero()
        self.label_ultimo_numero.setText(
            f"Último número gerado até agora: {ultimo}  "
            f"(próximo lote começará em {ultimo + 1})"
        )

    def _gerar_pdf(self):
        quantidade = self.campo_quantidade.value()

        # Pergunta ONDE salvar antes de mexer no contador.
        # Assim, se o usuário cancelar, nada é avançado no banco.
        caminho_arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar PDF de etiquetas",
            f"etiquetas_{quantidade}_unidades.pdf",
            "Arquivos PDF (*.pdf)"
        )

        if not caminho_arquivo:
            # Usuário cancelou a janela de salvar — não faz nada.
            return

        try:
            primeiro, ultimo = avancar_contador(quantidade)
        except ValueError as erro:
            QMessageBox.warning(self, "Erro", str(erro))
            return

        try:
            total_paginas = gerar_pdf_etiquetas(primeiro, ultimo, caminho_arquivo)
        except Exception as erro:
            QMessageBox.critical(
                self, "Erro ao gerar PDF",
                f"O contador já avançou para {ultimo}, mas o PDF falhou ao ser criado.\n"
                f"Erro: {erro}\n\n"
                f"Os números {primeiro} a {ultimo} ficarão sem etiqueta impressa."
            )
            self._atualizar_label_ultimo_numero()
            return

        QMessageBox.information(
            self, "PDF gerado com sucesso",
            f"Etiquetas de {primeiro} até {ultimo} geradas.\n"
            f"Total de páginas: {total_paginas}\n"
            f"Arquivo salvo em:\n{caminho_arquivo}"
        )
        self._atualizar_label_ultimo_numero()