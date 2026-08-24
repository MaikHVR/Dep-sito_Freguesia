import sys
from PySide6.QtWidgets import QApplication
from ui.janela_principal import JanelaPrincipal
from database.schema import criar_tabelas

def main():
    criar_tabelas()
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())

if __name__== "__main__":
    main()