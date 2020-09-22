"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from ClusterMap.gui.CustomWidgets.hierarchicalWidget.hierarchicalWidget import hierarchicalWidget
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
		