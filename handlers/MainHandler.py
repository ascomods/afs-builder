import ui.handlers.ViewHandler as vh

class MainHandler():
    def __init__(self, view_handler = None):
        if view_handler != None:
            self.view_handler = view_handler
        else:
            self.view_handler = vh.ViewHandler()
        self.view_handler.loadWindow('MainWindowHandler')