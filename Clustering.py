# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Clustering
								 A QGIS plugin
 Receives polygon shapefile as input and applies clustering methods for the generation of choropleth maps 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
							  -------------------
		begin                : 2020-03-18
		git sha              : $Format:%H$
		copyright            : (C) 2020 by Prudencio T. and Maia B.
		email                : tiagoprudencio16@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction,QFileDialog
from qgis.PyQt.QtWidgets import QToolButton, QMenu

from qgis.core import QgsProcessingAlgorithm, QgsApplication
import processing
import os.path
from .clustering_provider.clustering_provider import ClusteringProvider
import sys

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the dialog
#from .Clustering_dialog import ClusteringDialog

#import requirements
try:
	import sklearn
	import numpy
	import matplotlib
except:
	from clustering.requirements import requirements
	requirements()

class Clustering:
	"""QGIS Plugin Implementation."""

	def __init__(self,iface):
		"""Constructor.

		:param iface: An interface instance that will be passed to this class
			which provides the hook by which you can manipulate the QGIS
			application at run time.
		:type iface: QgsInterface
		"""
		# Save reference to the QGIS interface
		self.iface = iface
		# initialize plugin directory
		self.plugin_dir = os.path.dirname(__file__)
		# initialize locale
		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'Clustering_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)

			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

		# Declare instance attributes
		self.actions = []
		self.provider = ClusteringProvider()

	
	# noinspection PyMethodMayBeStatic
	def tr(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('Clustering', message)

	
	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""
		QgsApplication.processingRegistry().addProvider(self.provider)

	def unload(self):
		QgsApplication.processingRegistry().removeProvider(self.provider)
	  


		
