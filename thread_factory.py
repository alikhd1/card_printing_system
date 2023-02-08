
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressBar, QMainWindow


class Thread(QThread):
    _signal = pyqtSignal(int)

    def __init__(self, main_window, progress_window):
        super(Thread, self).__init__()
        self.users = []
        self.main_window = main_window
        self.progress_window = progress_window

    def __del__(self):
        self.wait()

    def set_function(self, function, users: list, **kwargs):
        self.function = function
        self.users = users
        self.settings = kwargs

    def run(self):
        self.function(users=self.users, signal=self._signal, **self.settings)


class ProgressWindow(QMainWindow):
    def __init__(self, title, info):
        super(ProgressWindow, self).__init__()
        self.setWindowTitle(title)
        self.pbar = QProgressBar(self)
        self.info = QtWidgets.QLabel(info)
        self.pbar.setValue(0)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.info)
        self.vbox.addWidget(self.pbar)
        self.vbox.addStretch(1)

        central_widget = QtWidgets.QWidget(self)
        central_widget.setLayout(self.vbox)
        self.setCentralWidget(central_widget)

    def signal_accept(self, msg):
        self.pbar.setValue(int(msg))
