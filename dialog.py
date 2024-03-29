from PyQt5.QtWidgets import QMessageBox


def show_dialog(**kwargs):
    msg = QMessageBox()
    msg.setIcon(kwargs.get('icon', QMessageBox.Critical))
    msg.setText(kwargs.get('msg', ''))
    msg.setInformativeText(kwargs.get('msg_detail', ''))
    msg.setWindowTitle(kwargs.get('title', ''))
    msg.setDetailedText(kwargs.get('error', ''))
    msg.setStandardButtons(QMessageBox.Ok)

    retval = msg.exec_()  # value of pressed message box button
