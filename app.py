import json
import sys
import time

import pandas as pd

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QTableView, QMessageBox, QProgressBar
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

from cart_generator import generate_card
from settings import get_settings
from utils import assign_subscription_code, resolve_url
from thread_factory import Thread, ProgressWindow


class SettingsMixin:
    def save_settings(self):
        try:
            fields = {
                'base_url': self.base_url.text() or '',
                'font_size': int(self.font_size.text()) if self.font_size.text() else None,
                'space_between': int(self.space_between.text()) if self.space_between.text() else None,
                'qr_code_x': int(self.qr_code_x.text()) if self.qr_code_x.text() else None,
                'qr_code_y': int(self.qr_code_y.text()) if self.qr_code_y.text() else None,
                'box_size': int(self.box_size.text()) if self.box_size.text() else None,
            }
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter valid values.")
            return
        with open('settings.conf', 'w') as f:
            json.dump(fields, f)
        QMessageBox.information(self, "Info", "Values have been saved.")

    def load_settings(self):
        try:
            with open('settings.conf', 'r') as f:
                fields = json.load(f)
                self.base_url.setText(fields.get('base_url')) if fields.get('base_url') else '',
                self.font_size.setText(str(fields.get('font_size'))) if fields.get('font_size') else '',
                self.space_between.setText(str(fields.get('space_between'))) if fields.get('space_between') else '',
                self.qr_code_x.setText(str(fields.get('qr_code_x'))) if fields.get('qr_code_x') else '',
                self.qr_code_y.setText(str(fields.get('qr_code_y'))) if fields.get('qr_code_y') else '',
                self.box_size.setText(str(fields.get('box_size'))) if fields.get('box_size') else '',
        except FileNotFoundError:
            pass


class MainWindow(QMainWindow, SettingsMixin):
    def __init__(self):
        super().__init__()

        # settings
        self.progress_window = None
        self.label1 = QtWidgets.QLabel('Base URL')
        self.base_url = QtWidgets.QLineEdit()

        self.label2 = QtWidgets.QLabel('Font size')
        self.font_size = QtWidgets.QLineEdit()

        self.label3 = QtWidgets.QLabel('Space between')
        self.space_between = QtWidgets.QLineEdit()

        self.label4 = QtWidgets.QLabel('QR code x')
        self.qr_code_x = QtWidgets.QLineEdit()

        self.label5 = QtWidgets.QLabel('QR code y')
        self.qr_code_y = QtWidgets.QLineEdit()

        self.label6 = QtWidgets.QLabel('Box size')
        self.box_size = QtWidgets.QLineEdit()

        self.button_save_settings = QPushButton('Save', self)
        self.button_save_settings.clicked.connect(self.save_settings)

        self.button_preview_card = QPushButton('Preview', self)
        self.button_preview_card.clicked.connect(self.preview)

        settings_layout = QtWidgets.QFormLayout()
        settings_layout.addRow(self.label1, self.base_url)
        settings_layout.addRow(self.label2, self.font_size)
        settings_layout.addRow(self.label3, self.space_between)
        settings_layout.addRow(self.label4, self.qr_code_x)
        settings_layout.addRow(self.label5, self.qr_code_y)
        settings_layout.addRow(self.label6, self.box_size)
        settings_layout.addRow(self.button_save_settings)
        settings_layout.addRow(self.button_preview_card)

        self.users = None
        self.table_view = QTableView(self)
        self.table_view.setLayoutDirection(Qt.RightToLeft)

        self.model = QStandardItemModel(self.table_view)
        self.model.setHorizontalHeaderLabels(["Check", "ID", "Name"])
        self.table_view.setModel(self.model)

        self.button_open_file = QPushButton('Open File', self)
        self.button_open_file.clicked.connect(self.open_file)

        self.button_check_all = QPushButton('Check All', self)
        self.button_check_all.clicked.connect(self.check_all)

        self.button_uncheck_all = QPushButton('Uncheck All', self)
        self.button_uncheck_all.clicked.connect(self.uncheck_all)

        self.button_button_print_all = QPushButton('Print', self)
        self.button_button_print_all.clicked.connect(self.print_all)

        input_layout = QVBoxLayout()
        input_layout.addWidget(self.table_view)
        input_layout.addWidget(self.button_open_file)
        input_layout.addWidget(self.button_check_all)
        input_layout.addWidget(self.button_uncheck_all)
        input_layout.addWidget(self.button_button_print_all)

        central_widget = QtWidgets.QTabWidget()

        tab1 = QtWidgets.QWidget()
        tab1.setLayout(input_layout)
        central_widget.addTab(tab1, "Input")

        tab2 = QtWidgets.QWidget()
        tab2.setLayout(settings_layout)
        central_widget.addTab(tab2, "Settings")

        self.setCentralWidget(central_widget)

        self.load_settings()

    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                   "Excel Files (*.xlsx)", options=options)
        if file_name:
            df = pd.read_excel(file_name)
            self.model.clear()
            for index, row in df.iterrows():
                checkbox_item = QStandardItem()
                checkbox_item.setCheckState(Qt.Unchecked)
                checkbox_item.setCheckable(True)
                items = [checkbox_item, QStandardItem(str(row["id"])), QStandardItem(str(row["name"]))]
                self.model.appendRow(items)
        self.model.setHorizontalHeaderLabels(["Check", "ID", "Name"])
        self.table_view.setColumnWidth(0, 25)

    def check_all(self):
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            item.setCheckState(Qt.Checked)

    def uncheck_all(self):
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            item.setCheckState(Qt.Unchecked)

    def set_checked_items(self):
        checked_items = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.checkState() == Qt.Checked:
                id = self.model.item(row, 1).text()
                name = self.model.item(row, 2).text()
                checked_items.append([id, name])
        self.users = checked_items
        
    

    def print_all(self):
        self.set_checked_items()
        self.users = assign_subscription_code(self.users)
        self.users = resolve_url(self.users, **get_settings('base_url'))

        if self.users:
            self.progress_window = ProgressWindow('Cart Generating', 'Cart Generating')
            self.thread = Thread(self, self.progress_window)
            self.thread.set_function(generate_card, self.users, **get_settings('font_size', 'space_between',
                                                                               'qr_code_x', 'qr_code_y', 'box_size'))
            self.thread._signal.connect(self.progress_window.signal_accept)
            self.thread._signal.connect(self.close_progress_window)
            self.thread.start()
            self.progress_window.show()

    def close_progress_window(self, msg):
        if msg >= 100:
            self.progress_window.close()

    def preview(self):
        from PIL import Image
        user = ['2', 'سید محمدرضا شهرآشوب چهاردانگه اصل', 45418888, 'https://crm.hyprercaspian.com/45418888']
        card = generate_card(user, **get_settings('font_size', 'space_between', 'qr_code_x', 'qr_code_y', 'box_size'))
        img = Image.open(card)
        img.show()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
