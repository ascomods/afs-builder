from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QWidget, QFileDialog
import qtawesome as qta
from ui.views.MainWindow import Ui_MainWindow
from observed import observable_method

class MainWindowHandler(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window

    def load(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.initUi()
        self.ui.openBtn.clicked.connect(self.openAction)
    
    def initUi(self):
        # actions buttons
        self.ui.newBtn.setIcon(qta.icon('fa.file-o'))
        self.ui.openBtn.setIcon(qta.icon('fa.folder-o'))
        self.ui.importBtn.setIcon(qta.icon('fa5s.file-import'))
        self.ui.exportBtn.setIcon(qta.icon('fa5s.file-export'))
        self.ui.removeBtn.setIcon(qta.icon('mdi.delete'))
        self.ui.openNameListBtn.setIcon(qta.icon('fa.file-text-o'))
        self.ui.exportNameListBtn.setIcon(qta.icon('fa5s.file-download'))
        # select buttons
        self.ui.selectAllBtn.setIcon(qta.icon('mdi.checkbox-marked'))
        self.ui.unselectAllBtn.setIcon(qta.icon('mdi.checkbox-blank-outline'))
    
    @QtCore.pyqtSlot()
    def openAction(self):
        fd = QFileDialog()
        fd.setFileMode(QFileDialog.AnyFile)
        fd.setNameFilters(["AFS File (*.AFS)"])
        if fd.exec_():
            filename = fd.selectedFiles()
            self.notifyOpenAction(filename)

    @observable_method()
    def notifyOpenAction(self, filename):
        pass