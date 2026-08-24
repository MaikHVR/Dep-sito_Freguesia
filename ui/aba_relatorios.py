from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QDateEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QLabel, QHeaderView, QGroupBox
)

from database.produtos import listar_produtos, CATEGORIAS_DISPONIVEIS
from database.relatorios import resumo_estoque_atual, contar_movimentacoes_por_periodo


class AbaRelatorios(QWidget):
    def __init__(self):
        super().__init__()
        self._montar_layout()
        self._atualizar_combo_produtos()
        self._atualizar_estoque_atual()

    def _montar_layout(self):
        layout_principal = QVBoxLayout()

        layout_principal.addWidget(self._criar_secao_estoque_atual())
        layout_principal.addWidget(self._criar_secao_movimentacoes())

        self.setLayout(layout_principal)

    # ---------- Seção 1: Estoque atual ----------

    def _criar_secao_estoque_atual(self):
        grupo = QGroupBox("Estoque atual (por produto)")
        layout = QVBoxLayout()

        layout_topo = QHBoxLayout()
        self.combo_categoria_estoque = QComboBox()
        self.combo_categoria_estoque.addItem("Todas as categorias", None)
        for cat in CATEGORIAS_DISPONIVEIS:
            self.combo_categoria_estoque.addItem(cat, cat)
        self.combo_categoria_estoque.currentIndexChanged.connect(self._atualizar_estoque_atual)
        layout_topo.addWidget(QLabel("Categoria:"))
        layout_topo.addWidget(self.combo_categoria_estoque)
        layout_topo.addStretch()

        botao_atualizar = QPushButton("Atualizar")
        botao_atualizar.clicked.connect(self._atualizar_estoque_atual)
        layout_topo.addWidget(botao_atualizar)

        layout.addLayout(layout_topo)

        self.tabela_estoque = QTableWidget()
        self.tabela_estoque.setColumnCount(3)
        self.tabela_estoque.setHorizontalHeaderLabels(["Produto", "Categoria", "Quantidade"])
        self.tabela_estoque.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_estoque.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_estoque.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabela_estoque.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.tabela_estoque)

        self.label_total_estoque = QLabel()
        layout.addWidget(self.label_total_estoque)

        grupo.setLayout(layout)
        return grupo

    def _atualizar_estoque_atual(self):
        categoria = self.combo_categoria_estoque.currentData()
        dados = resumo_estoque_atual(categoria=categoria)

        self.tabela_estoque.setRowCount(len(dados))
        total = 0
        for linha, item in enumerate(dados):
            self.tabela_estoque.setItem(linha, 0, QTableWidgetItem(item["produto_nome"]))
            self.tabela_estoque.setItem(linha, 1, QTableWidgetItem(item["categoria"]))
            self.tabela_estoque.setItem(linha, 2, QTableWidgetItem(str(item["quantidade"])))
            total += item["quantidade"]

        self.label_total_estoque.setText(f"Total geral em estoque: {total} caixa(s)")

    # ---------- Seção 2: Movimentações por período ----------

    def _criar_secao_movimentacoes(self):
        grupo = QGroupBox("Movimentações por período")
        layout = QVBoxLayout()

        layout_filtros = QFormLayout()

        self.combo_tipo_movimento = QComboBox()
        self.combo_tipo_movimento.addItem("Entradas", "entrada")
        self.combo_tipo_movimento.addItem("Saídas", "saida")
        layout_filtros.addRow("Tipo:", self.combo_tipo_movimento)

        self.combo_categoria_movimento = QComboBox()
        self.combo_categoria_movimento.addItem("Todas as categorias", None)
        for cat in CATEGORIAS_DISPONIVEIS:
            self.combo_categoria_movimento.addItem(cat, cat)
        layout_filtros.addRow("Categoria:", self.combo_categoria_movimento)

        self.combo_produto_movimento = QComboBox()
        layout_filtros.addRow("Produto:", self.combo_produto_movimento)

        layout_datas = QHBoxLayout()
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))
        layout_datas.addWidget(QLabel("De:"))
        layout_datas.addWidget(self.data_inicio)

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        layout_datas.addWidget(QLabel("Até:"))
        layout_datas.addWidget(self.data_fim)
        layout_filtros.addRow("Período:", layout_datas)

        layout.addLayout(layout_filtros)

        botao_gerar = QPushButton("Gerar Relatório")
        botao_gerar.clicked.connect(self._gerar_relatorio_movimentacoes)
        layout.addWidget(botao_gerar)

        self.tabela_movimentacoes = QTableWidget()
        self.tabela_movimentacoes.setColumnCount(3)
        self.tabela_movimentacoes.setHorizontalHeaderLabels(["Produto", "Categoria", "Quantidade"])
        self.tabela_movimentacoes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_movimentacoes.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_movimentacoes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabela_movimentacoes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        layout.addWidget(self.tabela_movimentacoes)

        self.label_total_movimentacoes = QLabel()
        layout.addWidget(self.label_total_movimentacoes)

        grupo.setLayout(layout)
        return grupo

    def _atualizar_combo_produtos(self):
        self.combo_produto_movimento.clear()
        self.combo_produto_movimento.addItem("Todos os produtos", None)
        for produto in listar_produtos(apenas_ativos=False):
            self.combo_produto_movimento.addItem(produto["nome"], produto["id"])

    def _gerar_relatorio_movimentacoes(self):
        tipo = self.combo_tipo_movimento.currentData()
        categoria = self.combo_categoria_movimento.currentData()
        produto_id = self.combo_produto_movimento.currentData()

        data_inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim.date().toString("yyyy-MM-dd")

        dados = contar_movimentacoes_por_periodo(
            data_inicio, data_fim, tipo,
            categoria=categoria, produto_id=produto_id
        )

        self.tabela_movimentacoes.setRowCount(len(dados))
        total = 0
        for linha, item in enumerate(dados):
            self.tabela_movimentacoes.setItem(linha, 0, QTableWidgetItem(item["produto_nome"]))
            self.tabela_movimentacoes.setItem(linha, 1, QTableWidgetItem(item["categoria"]))
            self.tabela_movimentacoes.setItem(linha, 2, QTableWidgetItem(str(item["quantidade"])))
            total += item["quantidade"]

        rotulo_tipo = "entradas" if tipo == "entrada" else "saídas"
        self.label_total_movimentacoes.setText(f"Total de {rotulo_tipo} no período: {total} caixa(s)")