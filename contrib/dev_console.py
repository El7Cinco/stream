# http://www.pythoncentral.io/embed-interactive-python-interpreter-console/

from code import InteractiveConsole
from imp import new_module
 
class dev_console(InteractiveConsole):
 
    def __init__(self, parent=None, names=None):
        names = names or {}
        names['main'] = parent
        names['console'] = self
        InteractiveConsole.__init__(self, names)
        self.superspace = new_module('superspace')
 
    def enter(self, source):
        source = self.preprocess(source)
        self.runcode(source)
 
    @staticmethod
    def preprocess(source):
        return source
 
#code.interact()
