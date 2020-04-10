from clustering.gui.CustomWidgets.kmeansWidget.kmeansWidget import kmeansWidget
from processing.gui.wrappers import WidgetWrapper

class kmeansWrapper(WidgetWrapper):
    def __init__(self, *args, **kwargs):
        super(kmeansWrapper, self).__init__(*args, **kwargs)

    
    def createPanel(self):
        return kmeansWidget()

    def createWidget(self):
        self.panel = self.createPanel()
        self.panel.dialogType = self.dialogType
        return self.panel
    
    def parentLayerChanged(self, layer=None):
        pass
    
    def setLayer(self, layer):
        pass
    
    def setValue(self, value):
        pass
    
    def value (self):
        return self.panel.getParameters()
        
    def postInitialize(self, wrappers):
        pass
        # for wrapper in wrappers:
        #     if wrapper.parameterDefinition().name() == self.parameterDefinition().parentLayerParameter():
        #         pass
    