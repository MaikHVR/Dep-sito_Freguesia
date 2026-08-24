from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView
)

from database.produtos import listar_produtos
from database.caixas import listar_em_estoque


class AbaEstoqueAtual(QWidget):
    def __init__(self):
        super().__init__()
        self._montar_layout()
        self._atualizar_combo_produtos()
        self._atualizar_tabela()

    def _montar_layout(self):
        layout_principal = QVBoxLayout()

        # --- Filtro ---
        layout_filtro = QHBoxLayout()
        layout_filtro.addWidget(QLabel("Filtrar por produto:"))

        self.combo_filtro_produto = QComboBox()
        self.combo_filtro_produto.currentIndexChanged.connect(self._atualizar_tabela)
        layout_filtro.addWidget(self.combo_filtro_produto)

        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self._atualizar_tudo)
        layout_filtro.addWidget(botao_atualizar)

        layout_filtro.addStretch()
        layout_principal.addLayout(layout_filtro)

        # --- Tabela ---
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Código", "Produto", "Data de Entrada"])
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout_principal.addWidget(self.tabela)

        # --- Total ---
        self.label_total = QLabel()
        layout_principal.addWidget(self.label_total)

        self.setLayout(layout_principal)

    def _atualizar_combo_produtos(self):
        # Guarda a seleção atual pra tentar restaurar depois de recarregar
        produto_selecionado_id = self.combo_filtro_produto.currentData()

        self.combo_filtro_produto.blockSignals(True)
        self.combo_filtro_produto.clear()
        self.combo_filtro_produto.addItem("Todos", None)

        for produto in listar_produtos(apenas_ativos=True):
            self.combo_filtro_produto.addItem(produto["nome"], produto["id"])

        # Tenta restaurar a seleção anterior
        indice_restaurar = self.combo_filtro_produto.findData(produto_selecionado_id)
        if indice_restaurar >= 0:
            self.combo_filtro_produto.setCurrentIndex(indice_restaurar)

        self.combo_filtro_produto.blockSignals(False)

    def _atualizar_tudo(self):
        self._atualizar_combo_produtos()
        self._atualizar_tabela()

    def _atualizar_tabela(self):
        produto_id = self.combo_filtro_produto.currentData()
        caixas = listar_em_estoque(produto_id=produto_id)

        self.tabela.setRowCount(len(caixas))
        for linha, caixa in enumerate(caixas):
            self.tabela.setItem(linha, 0, QTableWidgetItem(caixa["codigo"]))
            self.tabela.setItem(linha, 1, QTableWidgetItem(caixa["produto_nome"]))
            self.tabela.setItem(linha, 2, QTableWidgetItem(caixa["data_entrada"]))

        self.label_total.setText(f"Total em estoque: {len(caixas)} caixa(s)")