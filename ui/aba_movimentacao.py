from PySide6.QtCore import QEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QComboBox, QLineEdit, QLabel, QListWidget,
    QMessageBox
)

from database.produtos import listar_produtos
from database.caixas import cadastrar_caixa, remover_caixa


class AbaMovimentacao(QWidget):
    def __init__(self):
        super().__init__()
        self._montar_layout()
        self._atualizar_combo_produtos()

    def _montar_layout(self):
        layout_principal = QVBoxLayout()

        # --- Seletor de modo (topo) ---
        layout_seletor = QHBoxLayout()
        self.botao_modo_cadastro = QPushButton("Modo Cadastro")
        self.botao_modo_remocao = QPushButton("Modo Remoção")
        self.botao_modo_cadastro.setCheckable(True)
        self.botao_modo_remocao.setCheckable(True)
        self.botao_modo_cadastro.setChecked(True)
        self.botao_modo_cadastro.clicked.connect(lambda: self._trocar_modo(0))
        self.botao_modo_remocao.clicked.connect(lambda: self._trocar_modo(1))
        layout_seletor.addWidget(self.botao_modo_cadastro)
        layout_seletor.addWidget(self.botao_modo_remocao)
        layout_principal.addLayout(layout_seletor)

        # --- Páginas (Cadastro / Remoção) ---
        self.paginas = QStackedWidget()
        self.pagina_cadastro = self._criar_pagina_cadastro()
        self.pagina_remocao = self._criar_pagina_remocao()
        self.paginas.addWidget(self.pagina_cadastro)
        self.paginas.addWidget(self.pagina_remocao)
        layout_principal.addWidget(self.paginas)

        self.setLayout(layout_principal)

    def eventFilter(self, objeto, evento):
        # Sempre que o combobox de produto ganha foco (usuário vai clicar nele),
        # atualiza a lista — assim produtos cadastrados na aba Produtos aparecem
        # sem precisar reiniciar o programa. Só faz isso se não há sessão ativa,
        # pra não bagunçar uma leitura em andamento.
        if objeto is self.combo_produto_cadastro and evento.type() == QEvent.FocusIn:
            if not self.campo_leitura_cadastro.isEnabled():
                self._atualizar_combo_produtos()
        return super().eventFilter(objeto, evento)

    # ---------- Troca de modo ----------

    def _trocar_modo(self, indice):
        # Impede trocar de modo com uma sessão de leitura ativa
        if self.paginas.currentIndex() == 0 and self.campo_leitura_cadastro.isEnabled():
            QMessageBox.warning(self, "Sessão ativa", "Finalize o cadastro atual antes de trocar de modo.")
            self.botao_modo_cadastro.setChecked(True)
            self.botao_modo_remocao.setChecked(False)
            return
        if self.paginas.currentIndex() == 1 and self.campo_leitura_remocao.isEnabled():
            QMessageBox.warning(self, "Sessão ativa", "Finalize a remoção atual antes de trocar de modo.")
            self.botao_modo_remocao.setChecked(True)
            self.botao_modo_cadastro.setChecked(False)
            return

        self.paginas.setCurrentIndex(indice)
        self.botao_modo_cadastro.setChecked(indice == 0)
        self.botao_modo_remocao.setChecked(indice == 1)

    # ---------- Página de Cadastro ----------

    def _criar_pagina_cadastro(self):
        pagina = QWidget()
        layout = QVBoxLayout()

        layout_produto = QHBoxLayout()
        layout_produto.addWidget(QLabel("Produto:"))
        self.combo_produto_cadastro = QComboBox()
        self.combo_produto_cadastro.installEventFilter(self)
        layout_produto.addWidget(self.combo_produto_cadastro)
        layout.addLayout(layout_produto)

        self.botao_iniciar_cadastro = QPushButton("Iniciar Cadastro")
        self.botao_iniciar_cadastro.clicked.connect(self._iniciar_cadastro)
        layout.addWidget(self.botao_iniciar_cadastro)

        self.campo_leitura_cadastro = QLineEdit()
        self.campo_leitura_cadastro.setPlaceholderText("Aguardando leitura...")
        self.campo_leitura_cadastro.setEnabled(False)
        self.campo_leitura_cadastro.returnPressed.connect(self._processar_leitura_cadastro)
        layout.addWidget(self.campo_leitura_cadastro)

        self.label_contador_cadastro = QLabel("0 caixas cadastradas nesta sessão")
        layout.addWidget(self.label_contador_cadastro)

        self.log_cadastro = QListWidget()
        layout.addWidget(self.log_cadastro)

        self.botao_finalizar_cadastro = QPushButton("Finalizar")
        self.botao_finalizar_cadastro.setEnabled(False)
        self.botao_finalizar_cadastro.clicked.connect(self._finalizar_cadastro)
        layout.addWidget(self.botao_finalizar_cadastro)

        pagina.setLayout(layout)
        return pagina

    def _atualizar_combo_produtos(self):
        self.combo_produto_cadastro.clear()
        produtos = listar_produtos(apenas_ativos=True)
        for produto in produtos:
            # Guarda o ID junto com o texto exibido
            self.combo_produto_cadastro.addItem(produto["nome"], produto["id"])

    def _iniciar_cadastro(self):
        if self.combo_produto_cadastro.count() == 0:
            QMessageBox.warning(self, "Sem produtos", "Cadastre um produto antes de iniciar.")
            return

        self.contador_sessao_cadastro = 0
        self.log_cadastro.clear()
        self.label_contador_cadastro.setText("0 caixas cadastradas nesta sessão")

        self.combo_produto_cadastro.setEnabled(False)
        self.botao_iniciar_cadastro.setEnabled(False)
        self.campo_leitura_cadastro.setEnabled(True)
        self.botao_finalizar_cadastro.setEnabled(True)
        self.campo_leitura_cadastro.setFocus()

    def _processar_leitura_cadastro(self):
        codigo = self.campo_leitura_cadastro.text().strip()
        self.campo_leitura_cadastro.clear()
        if not codigo:
            return

        produto_id = self.combo_produto_cadastro.currentData()
        sucesso, mensagem = cadastrar_caixa(codigo, produto_id)

        if sucesso:
            self.contador_sessao_cadastro += 1
            self.label_contador_cadastro.setText(
                f"{self.contador_sessao_cadastro} caixas cadastradas nesta sessão"
            )
            self.log_cadastro.addItem(f"✓ {codigo}")
        else:
            # Erro: trava tudo até o usuário confirmar
            self.campo_leitura_cadastro.setEnabled(False)
            QMessageBox.warning(self, "Erro na leitura", mensagem)
            self.campo_leitura_cadastro.setEnabled(True)
            self.campo_leitura_cadastro.setFocus()

    def _finalizar_cadastro(self):
        self.combo_produto_cadastro.setEnabled(True)
        self.botao_iniciar_cadastro.setEnabled(True)
        self.campo_leitura_cadastro.setEnabled(False)
        self.botao_finalizar_cadastro.setEnabled(False)
        QMessageBox.information(
            self, "Sessão encerrada",
            f"Cadastro finalizado: {self.contador_sessao_cadastro} caixa(s) cadastrada(s)."
        )

    # ---------- Página de Remoção ----------

    def _criar_pagina_remocao(self):
        pagina = QWidget()
        layout = QVBoxLayout()

        self.botao_iniciar_remocao = QPushButton("Iniciar Remoção")
        self.botao_iniciar_remocao.clicked.connect(self._iniciar_remocao)
        layout.addWidget(self.botao_iniciar_remocao)

        self.campo_leitura_remocao = QLineEdit()
        self.campo_leitura_remocao.setPlaceholderText("Aguardando leitura...")
        self.campo_leitura_remocao.setEnabled(False)
        self.campo_leitura_remocao.returnPressed.connect(self._processar_leitura_remocao)
        layout.addWidget(self.campo_leitura_remocao)

        self.label_contador_remocao = QLabel("0 caixas removidas nesta sessão")
        layout.addWidget(self.label_contador_remocao)

        self.log_remocao = QListWidget()
        layout.addWidget(self.log_remocao)

        self.botao_finalizar_remocao = QPushButton("Finalizar")
        self.botao_finalizar_remocao.setEnabled(False)
        self.botao_finalizar_remocao.clicked.connect(self._finalizar_remocao)
        layout.addWidget(self.botao_finalizar_remocao)

        pagina.setLayout(layout)
        return pagina

    def _iniciar_remocao(self):
        self.contador_sessao_remocao = 0
        self.log_remocao.clear()
        self.label_contador_remocao.setText("0 caixas removidas nesta sessão")

        self.botao_iniciar_remocao.setEnabled(False)
        self.campo_leitura_remocao.setEnabled(True)
        self.botao_finalizar_remocao.setEnabled(True)
        self.campo_leitura_remocao.setFocus()

    def _processar_leitura_remocao(self):
        codigo = self.campo_leitura_remocao.text().strip()
        self.campo_leitura_remocao.clear()
        if not codigo:
            return

        sucesso, mensagem = remover_caixa(codigo)

        if sucesso:
            self.contador_sessao_remocao += 1
            self.label_contador_remocao.setText(
                f"{self.contador_sessao_remocao} caixas removidas nesta sessão"
            )
            self.log_remocao.addItem(f"✓ {codigo}")
        else:
            self.campo_leitura_remocao.setEnabled(False)
            QMessageBox.warning(self, "Erro na leitura", mensagem)
            self.campo_leitura_remocao.setEnabled(True)
            self.campo_leitura_remocao.setFocus()

    def _finalizar_remocao(self):
        self.botao_iniciar_remocao.setEnabled(True)
        self.campo_leitura_remocao.setEnabled(False)
        self.botao_finalizar_remocao.setEnabled(False)
        QMessageBox.information(
            self, "Sessão encerrada",
            f"Remoção finalizada: {self.contador_sessao_remocao} caixa(s) removida(s)."
        )