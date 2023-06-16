import sys
from PyQt5 import QtGui, QtWidgets
from ui.handlers.MainWindowHandler import MainWindowHandler
from ui.handlers.ProgressDialogHandler import ProgressDialogHandler

class ViewHandler():
    observers = {}

    def init(self, callbacks = None):
        if callbacks != None:
            for function, params in callbacks.items():
                eval(function)(params)

    def resetWindow(self):
        if hasattr(self, 'window'):
            self.window.close()
        self.window = QtWidgets.QMainWindow()
    
    def disableElements(self, elements):
        for elt in elements:
            eval(f"self.window_handler.ui.{elt}").setEnabled(False)

    def enableElements(self, elements):
        for elt in elements:
            eval(f"self.window_handler.ui.{elt}").setEnabled(True)
    
    def addObservers(self, observers):
        self.observers = {**self.observers, **observers}

    def attachObservers(self):
        for window_class, functions in self.observers.items():
            for function, observer in functions.items():
                if self.window_handler.__class__.__name__ == window_class:
                    eval(f"self.window_handler.{function}").add_observer(observer, identify_observed=True)

    def addEntries(self, listModel, entries):
        for entry in entries:
            eval(f"self.window_handler.{listModel}").appendRow(QtGui.QStandardItem(entry))
        self.window_handler.ui.statusbar.showMessage(f"{len(entries)} entries found")
    
    def loadWindow(self, handler_class, callbacks = None):
        if hasattr(self, 'window'):
            self.parent = self.window
            self.window = QtWidgets.QMainWindow(self.parent)
        else:
            self.window = QtWidgets.QMainWindow()
        self.window_handler = eval(handler_class)(self.window)
        self.attachObservers()
        self.window_handler.load()
        self.window.setWindowTitle("AFS Builder - by Ascomods")
        if callbacks != None:
            for function, params in callbacks.items():
                eval(function)(params)
        self.window.show()
    
    def showMessageDialog(self, message, type = 'information', title = ''):
        """
        Possible types : 'information', 'warning', 'critical', 'question'
        """
        if title == '':
            title = type.title()
        res = eval(f"QtWidgets.QMessageBox.{type}")(None, title, message)
        if type == 'question':
            return res == QtWidgets.QMessageBox.Yes
        return False
    
    def setStatusBarMessage(self, message):
        self.window_handler.ui.statusbar.showMessage(message)
    
    def openFileDialog(self, type = 'file', title = 'Open', filter = ''):
        if type == 'folder':
            method = "getExistingDirectory"
        elif type == 'save-file':
            method = "getSaveFileName"
        else:
            method = "getOpenFileName"
        if type != 'folder':
            return eval(f"QFileDialog.{method}")(self.window, title, filter=filter)
        else:
            return eval(f"QFileDialog.{method}")(self.window, title)

# class ViewHandler():
#     resources = {
#         'icon': './ui/resources/db.ico'
#     }

#     def __init__(self):
#         self.app = QtWidgets.QApplication([])
#         self.resetWindow()
#         self.main_window = MainWindowHandler(self.window)
#         self.main_window.load()
#         self.window.show()
#         self.main_window.notifyOpenAction.add_observer(self.AFSOpenAction, identify_observed=True)
#         sys.exit(self.app.exec_())

#     def resetWindow(self):
#         if hasattr(self, 'window'):
#             self.window.close()
#         self.window = QtWidgets.QMainWindow()
#         self.window.setWindowIcon(QtGui.QIcon(self.resources['icon']))

#     def AFSOpenAction(self, observed, args):
#         print(args)
#         #self.resetWindow()
#         #self.progress_dialog = ProgressDialogHandler(self.window)
#         #self.progress_dialog.load()
#         #self.window.setWindowTitle("Loading...")
#         #self.progress_dialog.ui.progressBar.setProperty("value", 40)
#         #self.window.show()
#         #self.ShowAction()

#     def ShowAction(self):
#         self.resetWindow()
#         self.window.setWindowTitle("AFS Unpacker - test.afs")
#         self.window.show()