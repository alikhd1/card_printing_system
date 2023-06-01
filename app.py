import json
import sys

import pandas as pd
import requests

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QTableView, QMessageBox, QProgressBar, \
    QLabel, QLineEdit, QWidget, QDialog, QRadioButton, QHBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QVariant, QAbstractTableModel
from PyQt5.QtWidgets import QFileDialog

from api import get_user_info
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
                'error_correction': int(
                    self.error_correction.currentData()) if self.error_correction.currentData() else None,
                'api_base_url': self.api_base_url.text() or '',

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
                index = self.error_correction.findData(str(fields.get('error_correction')))
                self.error_correction.setCurrentIndex(index)
                self.api_base_url.setText(fields.get('api_base_url')) if fields.get('api_base_url') else '',
        except FileNotFoundError:
            pass


class ProcessesMixin:
    def set_checked_items(self):
        checked_items = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item.checkState() == Qt.Checked:
                id = self.model.item(row, 1).text()
                name = self.model.item(row, 2).text()
                checked_items.append({'id': id, 'name': name})
        self.users = checked_items

    def start_process(self, title, info, function, settings={}):
        self.progress_window = ProgressWindow(title, info)
        self.thread = Thread(self, self.progress_window)
        self.thread.set_function(function, self.users, **settings)
        self.thread._signal.connect(self.progress_window.signal_accept)
        self.thread._signal.connect(self.close_progress_window)
        self.thread.finished.connect(self.start_next_process)
        self.thread.start()
        self.progress_window.show()

    def start_next_process(self):
        if self.processes:
            process = self.processes.pop(0)
            self.start_process(*process)
        if not self.thread.isRunning():
            self.print_button.setEnabled(True)

    def close_progress_window(self, msg):
        if msg >= 100:
            self.progress_window.close()


class ResultTableModel(QAbstractTableModel):
    def __init__(self, data, header):
        super().__init__()
        self.data = data
        self.header = header

    def rowCount(self, parent=None):
        return len(self.data)

    def columnCount(self, parent=None):
        return len(self.header)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            item = self.data[row]
            value = item.get(self.header[col], '')
            return value
        return QVariant()


class NewTab(QWidget, ProcessesMixin):
    def __init__(self):
        super().__init__()
        self.text_input = QLineEdit()
        self.submit_button = QPushButton('جستجو')
        self.result_table = QTableView()
        self.print_button = QPushButton('چاپ کارت')

        # Create radio buttons
        self.radio_name = QRadioButton("نام خانوادگی")
        self.radio_phone_number = QRadioButton("شماره تلفن همراه")
        self.radio_sub_code = QRadioButton("کد اشتراک")
        self.radio_name.setChecked(True)

        # Put radio buttons and text input in a layout
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_name)
        radio_layout.addWidget(self.radio_phone_number)
        radio_layout.addWidget(self.radio_sub_code)

        layout = QVBoxLayout()
        layout.addLayout(radio_layout)
        layout.addWidget(self.text_input)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.result_table)
        layout.addWidget(self.print_button)
        layout.addStretch()

        self.setLayout(layout)
        self.setLayoutDirection(Qt.RightToLeft)

        self.text_input.returnPressed.connect(self.process_input)
        self.submit_button.clicked.connect(self.process_input)
        self.print_button.clicked.connect(self.process_print_button)

    def process_input(self):
        code = self.text_input.text()
        self.text_input.clear()

        search_option = None
        if self.radio_name.isChecked():
            search_option = "name"
        elif self.radio_phone_number.isChecked():
            search_option = "phone_number"
        elif self.radio_sub_code.isChecked():
            search_option = "sub_code"

        if search_option:
            data = None
            try:
                data = get_user_info(param={search_option: code})
            except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
                self.result_table.setModel(None)  # Clear the model in case of error
                QMessageBox.critical(self, "Error", f"ارتباط با سرور برقرار نمیباشد: {str(e)}")
            self.result_table.setModel(None)
            if data:
                header = ['Code', 'Nam', 'Family', 'Mobile']
                model = ResultTableModel(data, header)
                self.result_table.setModel(model)

    def process_print_button(self):
        users = []
        for index in self.result_table.selectedIndexes():
            name = f'{self.result_table.model().index(index.row(), 1).data()} {self.result_table.model().index(index.row(), 2).data()}'
            user = {'id': self.result_table.model().index(index.row(), 0).data(), 'name': name}
            users.append(user)
        self.users = users
        if self.users:
            self.print_button.setEnabled(False)
            self.processes = [
                ('Check Codes', 'Assigning Subscription Code', assign_subscription_code),
                ('Resolve Urls', 'Resolving URL', resolve_url, get_settings('base_url')),
                ('Cards', 'Generating cards', generate_card, get_settings('font_size', 'space_between',
                                                                          'qr_code_x', 'qr_code_y',
                                                                          'box_size', 'error_correction'))
            ]
            self.start_next_process()


class MainWindow(QMainWindow, SettingsMixin, ProcessesMixin):
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

        self.label7 = QtWidgets.QLabel('Error correction')
        self.error_correction = QtWidgets.QComboBox()
        self.error_correction.addItem('L', '1')
        self.error_correction.addItem('M', '0')
        self.error_correction.addItem('Q', '3')
        self.error_correction.addItem('H', '2')

        self.label8 = QtWidgets.QLabel('API Base URL')
        self.api_base_url = QtWidgets.QLineEdit()


        self.button_save_settings = QPushButton('Save', self)
        self.button_save_settings.clicked.connect(self.save_settings)

        self.button_preview_card = QPushButton('Preview', self)
        self.button_preview_card.clicked.connect(self.preview)

        settings_layout = QtWidgets.QFormLayout()
        settings_layout.addRow(self.label1, self.base_url)
        settings_layout.addRow(self.label8, self.api_base_url)
        settings_layout.addRow(self.label2, self.font_size)
        settings_layout.addRow(self.label3, self.space_between)
        settings_layout.addRow(self.label4, self.qr_code_x)
        settings_layout.addRow(self.label5, self.qr_code_y)
        settings_layout.addRow(self.label6, self.box_size)
        settings_layout.addRow(self.label7, self.error_correction)
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

        tab3 = NewTab()
        central_widget.addTab(tab3, "Users")

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

    def print_all(self):
        self.set_checked_items()
        if self.users:
            self.button_button_print_all.setEnabled(False)
            self.processes = [
                ('Check Codes', 'Assigning Subscription Code', assign_subscription_code),
                ('Resolve Urls', 'Resolving URL', resolve_url, get_settings('base_url')),
                ('Cards', 'Generating cards', generate_card, get_settings('font_size', 'space_between',
                                                                          'qr_code_x', 'qr_code_y',
                                                                          'box_size', 'error_correction'))
            ]
            self.start_next_process()

    def preview(self):
        from PIL import Image
        user = [{'id': '2', 'name': 'سید محمدرضا شهرآشوب چهاردانگه اصل', 'code': 45418888,
                 'hashed_code': '86ca44f3b21d5022', 'url': 'https://crm.hypercaspian.com/45418888'}]

        card = generate_card(user, **get_settings('font_size', 'space_between', 'qr_code_x', 'qr_code_y', 'box_size',
                                                  'error_correction'), many=False)
        img = Image.open(card)
        img.show()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
