import logging
import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication

from exception import exception_hook
from forms.login import LoginForm

if __name__ == '__main__':
    logging.basicConfig(filename='myapp.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s (%(filename)s)')
    sys.excepthook = exception_hook
    app = QApplication([])
    window = LoginForm()
    window.setLayoutDirection(QtCore.Qt.RightToLeft)
    window.show()
    sys.exit(app.exec_())
