from PyQt5 import QtCore, QtGui, QtWidgets
from ui.views.ProgressDialog import Ui_ProgressDialog

class ProgressDialogHandler:
    def __init__(self, window):
        self.window = window

    def load(self):
        self.ui = Ui_ProgressDialog()
        self.ui.setupUi(self.window)