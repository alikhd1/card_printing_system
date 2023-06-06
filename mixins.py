import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from thread_factory import ProgressWindow, Thread

from settings import settings_file

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
        with open(settings_file, 'w') as f:
            json.dump(fields, f)
        QMessageBox.information(self, "Info", "Values have been saved.")

    def load_settings(self):
        try:
            with open(settings_file, 'r') as f:
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
            print('pop')
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
            self.print_action_button.setEnabled(True)
            self.show_duplicate_users()

    def close_progress_window(self, msg):
        if msg >= 100:
            self.progress_window.close()

