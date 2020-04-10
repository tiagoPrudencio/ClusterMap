from clustering.gui.CustomWidgets.hierarchicalWidget.hierarchicalWidget import hierarchicalWidget
from processing.gui.wrappers import WidgetWrapper

class hierarchicalWrapper(WidgetWrapper):
	def __init__(self, *args, **kwargs):
		super(hierarchicalWrapper, self).__init__(*args, **kwargs)

	
	def createPanel(self):
		return hierarchicalWidget()

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
	