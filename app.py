from PyQt5.QtWidgets import QApplication

from forms.login import LoginForm

if __name__ == "__main__":
    app = QApplication([])
    login_form = LoginForm()
    login_form.show()
    app.exec()
