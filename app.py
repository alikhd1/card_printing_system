from PyQt5.QtWidgets import QApplication

from forms.login import LoginForm

if __name__ == "__main__":
    app = QApplication([])
    window = LoginForm()
    window.show()
    app.exec_()
