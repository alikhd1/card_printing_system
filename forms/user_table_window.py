from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, \
    QWidget, QLabel, QMessageBox

from utils import delete_number


class UserTableWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle("مشتریان تکراری")
        self.setGeometry(100, 100, 600, 400)

        self.label = QLabel("مشتریان زیر دارای کارت میباشند", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Code"])
        self.table.setLayoutDirection(Qt.RightToLeft)

        self.button = QPushButton("حذف", self)
        self.button.clicked.connect(self.delete_users)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.table)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def setup_table(self, users):
        self.table.setRowCount(len(users))

        # Add the users to the table
        for row, user in enumerate(users):
            id_item = QTableWidgetItem(user["id"])
            name_item = QTableWidgetItem(user["name"])
            code_item = QTableWidgetItem(str(user["code"]))
            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, code_item)
        self.table.resizeColumnsToContents()

    def delete_users(self):
        selected_rows = []
        for item in self.table.selectedItems():
            if item.row() not in selected_rows:
                selected_rows.append(item.row())
        if selected_rows:
            codes = [int(self.table.item(row, 2).text()) for row in selected_rows]
            names = [self.table.item(row, 1).text() for row in selected_rows]
            message_box = QMessageBox(self)
            message_box.setIcon(QMessageBox.Question)
            message_box.setText("در صورت حذف کاربر ستاره ها نیز صفر میشوند")
            message_box.setDetailedText("\n".join(str(x) for x in names))
            message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            result = message_box.exec_()

            # If the user presses "OK", remove the selected users
            if result == QMessageBox.Ok:
                self.remove_users(codes, selected_rows)

    def remove_users(self, users, rows):
        delete_number(users)
        # TODO bug
        for row in rows:
            self.table.removeRow(row)


