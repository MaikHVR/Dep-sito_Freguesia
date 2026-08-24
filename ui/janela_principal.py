from PySide6.QtWidgets import QMainWindow, QTabWidget, QWidget, QLabel, QVBoxLayout

from ui.aba_produtos import AbaProdutos
from ui.aba_imprimir import AbaImprimirAdesivos
from ui.aba_movimentacao import AbaMovimentacao
from ui.aba_estoque import AbaEstoqueAtual
from ui.aba_relatorios import AbaRelatorios


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Estoque - Sorvetes")
        self.resize(900, 600)

        abas = QTabWidget()
        self.setCentralWidget(abas)

        abas.addTab(AbaMovimentacao(), "Movimentação")
        abas.addTab(AbaEstoqueAtual(), "Estoque Atual")
        abas.addTab(AbaProdutos(), "Produtos")
        abas.addTab(AbaImprimirAdesivos(), "Imprimir Adesivos")
        abas.addTab(AbaRelatorios(), "Relatórios")

    def _placeholder(self, nome):
        """Cria uma aba vazia temporária, só com um texto de identificação."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Aba '{nome}' — em construção"))
        widget.setLayout(layout)
        return widget