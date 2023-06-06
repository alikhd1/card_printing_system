import requests
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

from api import login_almas_user
from forms.windows import MainWindow


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Form")
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        self.login_button.clicked.connect(self.login)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.username_input.clear()
        self.password_input.clear()

        user = None
        try:
            user = login_almas_user(username=username, password=password)
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
            QMessageBox.critical(self, "Error", f"ارتباط با سرور برقرار نمیباشد: {str(e)}")

        if user:
            self.open_application_window()

    def open_application_window(self):
        self.main_window = MainWindow()
        self.main_window.show()
        self.close()
