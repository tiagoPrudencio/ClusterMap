# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from PyQt5.QtGui import QColor
from qgis.core import (QgsProcessing,
					   QgsFeatureSink,
					   QgsProcessingException,
					   QgsProcessingAlgorithm,
					   QgsProcessingParameterFeatureSource,
					   QgsProcessingParameterFeatureSink,
					   QgsProcessingParameterField,
					   QgsProcessingParameterNumber,
					   QgsProcessingParameterDefinition,
					   QgsProcessingParameterEnum,
					   QgsField,
					   QgsVectorLayerUtils,
					   QgsFeature,
					   QgsProcessingFeedback,
					   QgsSymbol,
					   QgsRendererCategory,
					   QgsCategorizedSymbolRenderer,
					   QgsProcessingUtils
					   )
#from qgis import processing
from sklearn.cluster import AgglomerativeClustering
from processing.gui.wrappers import WidgetWrapper
from ClusterMap.gui.ProcessingUI.hierarchicalWrapper import hierarchicalWrapper
from ClusterMap.classification.classification import classification
from sklearn.metrics import  silhouette_score, silhouette_samples
import numpy as np

class HierarchicalClusteringAlgorithm(QgsProcessingAlgorithm):
	"""
	This is an example algorithm that takes a vector layer and
	creates a new identical one.

	It is meant to be used as an example of how to create your own
	algorithms and explain methods and variables used to do it. An
	algorithm like this will be available in all elements, and there
	is not need for additional work.

	All Processing algorithms should extend the QgsProcessingAlgorithm
	class.
	"""

	# Constants used to refer to parameters and outputs. They will be
	# used when calling the algorithm from another algorithm, or when
	# calling from the QGIS console.

	PARAMETERS = 'PARAMETERS'
	N_CLUSTERS = 'N_CLUSTERS'
	OUTPUT = 'OUTPUT'
	
	def initAlgorithm(self, config=None):
		"""
		Here we define the inputs and output of the algorithm, along
		with some other properties.
		"""

		# We add the input vector features source. It can have any kind of
		# geometry.
		
		slot = ParameterLayer(
			self.PARAMETERS,
			description =self.tr(''),
			)

		slot.setMetadata({
			'widget_wrapper': hierarchicalWrapper 
		})

		self.addParameter(slot)

		self.addParameter(
			QgsProcessingParameterNumber(
				self.N_CLUSTERS,
				self.tr('Number of clusters'),
				type=QgsProcessingParameterNumber.Integer,
				defaultValue=2,
				minValue=2,
				maxValue=10
			)
		)

		# We add a feature sink in which to store our processed features (this
		# usually takes the form of a newly created vector layer when the
		# algorithm is run in QGIS).
		self.addParameter(
			QgsProcessingParameterFeatureSink(
				self.OUTPUT,
				self.tr('Output layer')
			)
		)
		
	def parameterAsClustering(self, parameters, name, context):
		return parameters[name]

	def processAlgorithm(self, parameters, context, feedback):
		"""
		Here is where the processing itself takes place.
		"""

		# Retrieve the feature source and sink. The 'dest_id' variable is used
		# to uniquely identify the feature sink, and must be included in the
		# dictionary returned by the processAlgorithm function.

		param = self.parameterAsClustering(
			parameters,
			self.PARAMETERS,
			context
		)

		source = param['layer']
		method = param['method'][0]
		metric = param['metric'][0]
		X = param['dataset']
		excluded = param['id']
		attr = param['attributes']

		n_clusters = self.parameterAsInt(
			parameters,
			self.N_CLUSTERS,
			context
		)

		# If source was not found, throw an exception to indicate that the algorithm
		# encountered a fatal error. The exception text can be any string, but in this
		# case we use the pre-built invalidSourceError method to return a standard
		# helper text for when a source cannot be evaluated
		if source is None:
			raise QgsProcessingException(
				self.invalidSourceError(parameters, self.INPUT)
			)

		fields = source.fields()
		fields.append(QgsField("cluster", QVariant.Int))
		(sink, dest_id) = self.parameterAsSink(
			parameters,
			self.OUTPUT,
			context,
			fields,
			source.wkbType(),
			source.sourceCrs()
		)

		# If sink was not created, throw an exception to indicate that the algorithm
		# encountered a fatal error. The exception text can be any string, but in this
		# case we use the pre-built invalidSinkError method to return a standard
		# helper text for when a sink cannot be evaluated
		if sink is None:
			raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

		# Compute the number of steps to display within the progress bar and
		# get features from source
		total = 100.0 / source.featureCount() if source.featureCount() else 0
		features = source.getFeatures()
		#X = self.get_data_from_source(source, attributeList)
		model = AgglomerativeClustering(
			n_clusters=n_clusters,
			affinity=metric,
			linkage=method).fit(X)

		current=0
		X_ = list()
		for feature in features:
			# Stop the algorithm if cancel button has been clicked
			if feedback.isCanceled():
				break
			newFeat = QgsFeature(fields)
			for field in source.fields():
				newFeat[field.name()] = feature[field.name()]
			newFeat.setGeometry(feature.geometry())
			# Add a feature in the sink
			if feature.id() in excluded:
				pass
			else:
				newFeat['cluster'] = int(model.labels_[current])
				current =current+1
				aux = [feature[field] for field in attr ]
				X_.append(aux)
				
			sink.addFeature(newFeat, QgsFeatureSink.FastInsert)

			# Update the progress bar
			feedback.setProgress(int(current * total))

		feedback.pushInfo('\n####### THE AVERAGE SILLHOUETTE SCORE EACH CLUSTER ####### \n')
		sample_silhouette_values = silhouette_samples(X, model.labels_, metric = metric)	
		for i in range(n_clusters):
			value = np.mean(sample_silhouette_values[model.labels_ == i])
			feedback.pushInfo('Cluster ' + str(i) + ' the average silhouette_score is: '+ str(value) +'\n')

		score  = silhouette_score(X, model.labels_, metric= metric)
		feedback.pushInfo('\n####### THE AVERAGE TOTAL SILLHOUETTE SCORE ####### \n')
		feedback.pushInfo('The average total silhouette_score is: '+ str(score)+'\n')

		self.legends, self.rules_tree = classification(X_,model.labels_,attr).decisionTree()
		feedback.pushInfo('\n####### RULES OF A DECISION TREE #######'+'\n')
		for i in sorted(self.legends.keys()):
			feedback.pushInfo('class ' + i + ': ' + self.legends[i] + '\n')
		
		self.dest_id=dest_id
		return {self.OUTPUT: dest_id}

	#Create Symbol Renderer
	def postProcessAlgorithm(self, context, feedback):
		output = QgsProcessingUtils.mapLayerFromString(self.dest_id, context)
	
		my_classes = {0: list([[43,131,186,255]]),
			  1: list([[241,96,93,255]]),
			  2: list([[157,211,167,255]]),
			  3: list([[237,248,185,255]]),
			  4: list([[232,221,58,255]]),
			  5: list([[249,158,89,255]]),
			  6: list([[108,206,89,255]]),
			  7: list([[137,107,178,255]]),
			  8: list([[205,63,113,255]]),
			  9: list([[215,25,28,255]])
			  }

		rules = dict()
		for i in range(len(self.rules_tree.keys())):
			my_classes[i].append(self.rules_tree[str(i)])
			rules[i] = my_classes[i]

		categories = []
		for class_value, (symbol_property, label_text) in rules.items():

			# get default symbol for this geometry type
			symbol = QgsSymbol.defaultSymbol(output.geometryType())

			# symbol.set*(symbol_property)
			symbol.setColor(QColor(symbol_property[0],symbol_property[1],symbol_property[2],symbol_property[3]))

			# create a category with these properties
			category = QgsRendererCategory(class_value, symbol, label_text)
			categories.append(category)

		mi_rend = QgsCategorizedSymbolRenderer('cluster', categories) 
		output.setRenderer(mi_rend)
		output.triggerRepaint()
		return {self.OUTPUT: self.dest_id}
	
	def tr(self, string):
		"""
		Returns a translatable string with the self.tr() function.
		"""
		return QCoreApplication.translate('Processing', string)

	def createInstance(self):
		return HierarchicalClusteringAlgorithm()

	def name(self):
		"""
		Returns the algorithm name, used for identifying the algorithm. This
		string should be fixed for the algorithm, and must not be localised.
		The name should be unique within each provider. Names should contain
		lowercase alphanumeric characters only and no spaces or other
		formatting characters.
		"""
		return 'hierarchicalclustering'

	def displayName(self):
		"""
		Returns the translated algorithm name, which should be used for any
		user-visible display of the algorithm name.
		"""
		return self.tr('Hierarchical Clustering')

	def group(self):
		"""
		Returns the name of the group this algorithm belongs to. This string
		should be localised.
		"""
		return self.tr('Clustering Methods')

	def groupId(self):
		"""
		Returns the unique ID of the group this algorithm belongs to. This
		string should be fixed for the algorithm, and must not be localised.
		The group id should be unique within each provider. Group id should
		contain lowercase alphanumeric characters only and no spaces or other
		formatting characters.
		"""
		return 'clusteringmethods'

	def shortHelpString(self):
		"""
		Returns a localised short helper string for the algorithm. This string
		should provide a basic description about what the algorithm does and the
		parameters and outputs associated with it..
		"""
		return self.tr('Hierarchical clustering method is an algorithm that groups similar objects into groups called clusters. It starts by treating each observation as a separate cluster. Then, it repeatedly executes two steps: identify the two clusters that are closest together, and merge the two most similar clusters. This iterative process continues until all the clusters are merged together. The endpoint is a set of clusters, where each cluster is distinct from each other cluster, and the objects within each cluster are broadly similar to each other.')

class ParameterLayer(QgsProcessingParameterDefinition):

	def __init__(self, name, description='', parentLayerParameterName='INPUT'):
		super().__init__(name, description)
		self._parentLayerParameter = parentLayerParameterName

	def clone(self):
		copy = ParameterLayer(self.name(), self.description(), self._parentLayerParameter)
		return copy

	def type(self):
			return self.typeName()

	@staticmethod
	def typeName():
		return 'method_graph'
	def checkValueIsAcceptable(self, value, context=None):
		#if not isinstance(value, list):
		#   return False
		#for field_def in value:
		#    if not isinstance(field_def, dict):
		#        return False
		#    if 'name' not in field_def.keys():
		#         return False
		#    if 'type' not in field_def.keys():
		#        return False
		#    if 'expression' not in field_def.keys():
		#        return False
		return True

	def valueAsPythonString(self, value, context):
		return str(value)

	def asScriptCode(self):
		raise NotImplementedError()

	@classmethod
	def fromScriptCode(cls, name, description, isOptional, definition):
		raise NotImplementedError()

	def parentLayerParameter(self):
		return self._parentLayerParameter