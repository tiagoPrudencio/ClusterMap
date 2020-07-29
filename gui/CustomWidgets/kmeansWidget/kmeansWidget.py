from qgis.PyQt import QtWidgets, uic
from qgis.utils import iface
from qgis.core import *
from qgis.PyQt.QtCore import pyqtSlot, pyqtSignal, QSettings, Qt, QVariant
from PyQt5.QtWidgets import QMessageBox
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from ClusterMap.graph.graph import createGraph

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'kmeansWidget.ui'))

class kmeansWidget(QtWidgets.QWidget, FORM_CLASS):

	def __init__(self, parent=None):
		"""
		Initializates clusteringWidget
		"""
		super(kmeansWidget, self).__init__(parent)
		self.iface = iface
		self.parameters = dict()
		self.setupUi(self)
		self.setInitialState()

	def setInitialState(self):
		self.activeLayer()
		self.comboBox_2.addItem('Elbow Method')
		self.comboBox_2.addItem('Silhouette Method')
		self.listWidget.setSelectionMode(self.listWidget.MultiSelection)
		self.listWidget_2.setSelectionMode(self.listWidget_2.MultiSelection)

	def activeLayer(self):
		#populating the combobox
		for layer in self.iface.mapCanvas().layers():
			if isinstance(layer, QgsVectorLayer):
				self.comboBox.addItem(layer.name(),layer)


	@pyqtSlot(int)
	def on_comboBox_currentIndexChanged(self):
		self.listWidget_2.clear()
		self.listWidget.clear()
		layer = self.comboBox.currentData()
		if layer is None:
			pass
		elif layer is not None:
			attributes = [field.name() for field in layer.fields() if field.isNumeric()]
			self.listWidget.addItems(attributes)

	@pyqtSlot(bool)
	def on_toolButton_1_clicked(self):
		for i in range(self.listWidget.count()):
			item = self.listWidget.item(i)
			self.listWidget_2.addItem(item.text())
		self.listWidget.clear()

	@pyqtSlot(bool)
	def on_toolButton_2_clicked(self):
		for item in self.listWidget.selectedItems():
			self.listWidget_2.addItem(self.listWidget.takeItem(self.listWidget.row(item)))
			
	@pyqtSlot(bool)
	def on_toolButton_3_clicked(self):
		for item in self.listWidget_2.selectedItems():
			self.listWidget.addItem(self.listWidget_2.takeItem(self.listWidget_2.row(item)))

	@pyqtSlot(bool)
	def on_toolButton_4_clicked(self):
		for i in range(self.listWidget_2.count()):
			item = self.listWidget_2.item(i)
			self.listWidget.addItem(item.text())
		self.listWidget_2.clear()
   
	@pyqtSlot(bool)
	def on_toolButton_5_clicked(self):
		try:
			X = self.get_data_from_source()
			if self.comboBox_2.currentText() == 'Elbow Method':
				createGraph(X).elbowMethod()

			elif self.comboBox_2.currentText() == 'Silhouette Method':
				createGraph(X).silhouetteMethod()
		except:
			self.messsage_box = QMessageBox.warning(self,"Kmeans", 'choose at least one attribute')

	def filterNull(self,feature):
		attributes = [self.listWidget_2.item(i).text() for i in range(self.listWidget_2.count())]
		data = list()
		for attr in attributes:
			if feature[attr]  is None:
				self.parameters['id'].append(feature.id())
				data = None
				break
			else:
				data.append(feature[attr])
		return(data)

	def get_data_from_source(self):
		dataset = list()
		self.parameters['layer'] = self.comboBox.currentData()
		self.parameters['id'] = list()

		for feature in self.parameters['layer'].getFeatures():
			data = self.filterNull(feature)
			if data is not None:
				dataset.append(data)

		Standard_models = StandardScaler()
		Standard_models.fit(np.array(dataset))
		StandardX = Standard_models.transform(np.array(dataset))
		return StandardX

	def getParameters(self):
		self.parameters['dataset'] = self.get_data_from_source()
		self.parameters['attributes'] = [self.listWidget_2.item(i).text() for i in range(self.listWidget_2.count())]
		return self.parameters