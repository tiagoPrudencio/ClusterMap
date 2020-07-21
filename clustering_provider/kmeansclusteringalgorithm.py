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
from qgis.core import (QgsProcessing,
					   QgsFeatureSink,
					   QgsProcessingException,
					   QgsProcessingAlgorithm,
					   QgsProcessingParameterFeatureSource,
					   QgsProcessingParameterDefinition,
					   QgsProcessingParameterFeatureSink,
					   QgsProcessingParameterField,
					   QgsProcessingParameterNumber,
					   QgsField,
					   QgsVectorLayerUtils,
					   QgsFeature
					   )
#from qgis import processing
from sklearn.cluster import KMeans
from processing.gui.wrappers import WidgetWrapper
from clustering.gui.ProcessingUI.kmeansWrapper import kmeansWrapper
from clustering.classification.classification import classification



class KMeansClusteringAlgorithm(QgsProcessingAlgorithm):
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
			'widget_wrapper': kmeansWrapper 
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
			raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
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

		kmeans = KMeans(
			n_clusters=n_clusters,
			random_state= 0).fit(X)

		current = 0
		X_ = list()
		for feature in (features):
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
				newFeat['cluster'] = int(kmeans.labels_[current])
				current =current+1
				aux = [feature[field] for field in attr ]
				X_.append(aux)

			sink.addFeature(newFeat, QgsFeatureSink.FastInsert)

			# Update the progress bar
			feedback.setProgress(int(current * total))
 
		legends = classification(X_,kmeans.labels_,attr).decisionTree()
		feedback.pushInfo('Rules of a Decision Tree:'+'\n')
		for legend in sorted(legends):
			feedback.pushInfo(legend+'\n')
	
	   
		return {self.OUTPUT: dest_id}


	def tr(self, string):
		"""
		Returns a translatable string with the self.tr() function.
		"""
		return QCoreApplication.translate('Processing', string)

	def createInstance(self):
		return KMeansClusteringAlgorithm()

	def name(self):
		"""
		Returns the algorithm name, used for identifying the algorithm. This
		string should be fixed for the algorithm, and must not be localised.
		The name should be unique within each provider. Names should contain
		lowercase alphanumeric characters only and no spaces or other
		formatting characters.
		"""
		return 'kmeansclustering'

	def displayName(self):
		"""
		Returns the translated algorithm name, which should be used for any
		user-visible display of the algorithm name.
		"""
		return self.tr('K-Means Clustering')

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
		return self.tr("Algorithm clusters data by trying to separate samples in n groups of equal variance, minimizing a criterion known as the inertia or within-cluster sum-of-squares")

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