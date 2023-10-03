import logging
import traceback

from PyQt5.QtWidgets import QMessageBox


def exception_hook(exctype, value, tracebackobj):
    error_box = QMessageBox()
    tblist = traceback.extract_tb(tracebackobj)
    logmsg = f"{value}\n"
    for filename, lineno, funcname, srcline in tblist:
        logmsg += f"  File \"{filename}\", line {lineno}, in {funcname}\n    {srcline}\n"
    logging.error(logmsg)
    error_box.setText(f"{value} {tracebackobj.tb_lineno}")
    error_box.exec_()
