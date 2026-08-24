from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QLabel, QInputDialog
)

from database.produtos import (
    adicionar_produto, listar_produtos, desativar_produto,
    reativar_produto, editar_nome_produto, excluir_produto,
    CATEGORIAS_DISPONIVEIS
)


class AbaProdutos(QWidget):
    def __init__(self):
        super().__init__()
        self._montar_layout()
        self._carregar_lista()

    def _montar_layout(self):
        layout_principal = QVBoxLayout()

        # --- Formulário de cadastro ---
        layout_formulario = QFormLayout()

        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText("Ex: Creme, Chocolate...")
        layout_formulario.addRow("Nome do produto:", self.campo_nome)

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(CATEGORIAS_DISPONIVEIS)
        layout_formulario.addRow("Categoria:", self.combo_categoria)

        layout_principal.addLayout(layout_formulario)

        botao_cadastrar = QPushButton("Cadastrar Produto")
        botao_cadastrar.clicked.connect(self._cadastrar)
        layout_principal.addWidget(botao_cadastrar)

        # --- Lista de produtos cadastrados ---
        layout_principal.addWidget(QLabel("Produtos cadastrados:"))

        self.lista_produtos = QListWidget()
        layout_principal.addWidget(self.lista_produtos)

        layout_botoes_lista = QHBoxLayout()

        botao_editar = QPushButton("Editar nome")
        botao_editar.clicked.connect(self._editar_selecionado)
        layout_botoes_lista.addWidget(botao_editar)

        botao_desativar = QPushButton("Desativar selecionado")
        botao_desativar.clicked.connect(self._desativar_selecionado)
        layout_botoes_lista.addWidget(botao_desativar)

        botao_reativar = QPushButton("Reativar selecionado")
        botao_reativar.clicked.connect(self._reativar_selecionado)
        layout_botoes_lista.addWidget(botao_reativar)

        botao_excluir = QPushButton("Excluir selecionado")
        botao_excluir.clicked.connect(self._excluir_selecionado)
        layout_botoes_lista.addWidget(botao_excluir)

        layout_principal.addLayout(layout_botoes_lista)

        self.setLayout(layout_principal)

    def _cadastrar(self):
        nome = self.campo_nome.text()
        categoria = self.combo_categoria.currentText()

        sucesso, mensagem = adicionar_produto(nome, categoria)

        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.campo_nome.clear()
            self._carregar_lista()
        else:
            QMessageBox.warning(self, "Erro ao cadastrar", mensagem)

    def _carregar_lista(self):
        """Recarrega a lista mostrando TODOS os produtos (ativos e inativos),
        deixando claro visualmente quais estão desativados."""
        self.lista_produtos.clear()
        produtos = listar_produtos(apenas_ativos=False)

        for produto in produtos:
            status = "" if produto["ativo"] else " (desativado)"
            texto = f'{produto["nome"]} — {produto["categoria"]}{status}'
            item = QListWidgetItem(texto)
            item.setData(1000, produto["id"])  # guarda o ID escondido no item
            item.setData(1001, produto["nome"])  # guarda o nome atual também
            self.lista_produtos.addItem(item)

    def _item_selecionado(self):
        item = self.lista_produtos.currentItem()
        if item is None:
            QMessageBox.warning(self, "Nada selecionado", "Selecione um produto na lista primeiro.")
            return None
        return item

    def _desativar_selecionado(self):
        item = self._item_selecionado()
        if item is None:
            return
        desativar_produto(item.data(1000))
        self._carregar_lista()

    def _reativar_selecionado(self):
        item = self._item_selecionado()
        if item is None:
            return
        reativar_produto(item.data(1000))
        self._carregar_lista()

    def _editar_selecionado(self):
        item = self._item_selecionado()
        if item is None:
            return

        produto_id = item.data(1000)
        nome_atual = item.data(1001)

        novo_nome, confirmado = QInputDialog.getText(
            self, "Editar nome do produto",
            "Novo nome:", QLineEdit.Normal, nome_atual
        )

        if not confirmado:
            return  # usuário cancelou

        sucesso, mensagem = editar_nome_produto(produto_id, novo_nome)
        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self._carregar_lista()
        else:
            QMessageBox.warning(self, "Erro ao editar", mensagem)

    def _excluir_selecionado(self):
        item = self._item_selecionado()
        if item is None:
            return

        produto_id = item.data(1000)
        nome_atual = item.data(1001)

        resposta = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Tem certeza que deseja excluir permanentemente o produto '{nome_atual}'?\n\n"
            f"Essa ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # botão padrão é "Não", pra evitar exclusão acidental
        )

        if resposta != QMessageBox.Yes:
            return

        sucesso, mensagem = excluir_produto(produto_id)
        if sucesso:
            QMessageBox.information(self, "Produto excluído", mensagem)
            self._carregar_lista()
        else:
            QMessageBox.warning(self, "Não foi possível excluir", mensagem)