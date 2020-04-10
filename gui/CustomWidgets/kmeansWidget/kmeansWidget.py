from qgis.PyQt import QtWidgets, uic
from qgis.utils import iface
from qgis.core import *
from qgis.PyQt.QtCore import pyqtSlot, pyqtSignal, QSettings, Qt
from PyQt5.QtWidgets import QMessageBox
import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from clustering.graph.graph import createGraph

FORM_CLASS, _ = uic.loadUiType(os.path.join(
	os.path.dirname(__file__), 'kmeansWidget.ui'))

class kmeansWidget(QtWidgets.QWidget, FORM_CLASS):

	def __init__(self, parent=None):
		"""
		Initializates clusteringWidget
		"""
		super(kmeansWidget, self).__init__(parent)
		self.iface = iface
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
		if self.comboBox.currentData()==None:
			pass
		else:
			layer = self.comboBox.currentData()
			for field in layer.fields():
				if field.isNumeric():
					self.listWidget.addItem(field.name())

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
			self.X = self.get_data_from_source()
			if self.comboBox_2.currentText() == 'Elbow Method':
				createGraph(self.X).elbowMethod()

			elif self.comboBox_2.currentText() == 'Silhouette Method':
				createGraph(self.X).silhouetteMethod()
		except:
			self.messsage_box = QMessageBox.warning(self,"Kmeans", 'choose at least one attribute')

	def get_data_from_source(self):
		X = list()
		attributeList = list()
		for i in range(self.listWidget_2.count()):
			item = self.listWidget_2.item(i)
			attributeList.append(item.text())
		source = self.comboBox.currentData()

		for feature in source.getFeatures():
			data = [feature[attr] for attr in attributeList]
			X.append(data)

		Standard_models = StandardScaler()
		Standard_models.fit(np.array(X))
		StandardX = Standard_models.transform(np.array(X))
		return StandardX

	def getParameters(self):
		Dict = {'layer':self.comboBox.currentData(),
				'attributeList': self.get_data_from_source()}
		return Dict