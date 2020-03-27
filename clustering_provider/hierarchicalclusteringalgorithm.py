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
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsField,
                       QgsVectorLayerUtils,
                       QgsFeature
                       )
from qgis import processing
from sklearn.cluster import AgglomerativeClustering
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

    INPUT = 'INPUT'
    ATTRIBUTES = 'ATTRIBUTES'
    METHOD = 'METHOD'
    METRIC = 'METRIC'
    N_CLUSTERS = 'N_CLUSTERS'
    OUTPUT = 'OUTPUT'
    
    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterField(
                self.ATTRIBUTES,
                self.tr('Attributes'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Numeric,
                allowMultiple=True
            )
        )
        self.methods = [
            'ward',
            'complete',
            'average',
            'single'
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Method'),
                options=self.methods,
                defaultValue=0
            )
        )

        self.metrics = [
            'euclidean',
            'manhattan'
        ]
        self.addParameter(
            QgsProcessingParameterEnum(
                self.METRIC,
                self.tr('Metric'),
                options=self.metrics,
                defaultValue=0
            )
        )
        
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
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        
        attributeList = self.parameterAsFields(
            parameters,
            self.ATTRIBUTES,
            context
        )
        n_clusters = self.parameterAsInt(
            parameters,
            self.N_CLUSTERS,
            context
        )
        method = self.parameterAsEnum(
            parameters,
            self.METHOD,
            context
        )
        metric = self.parameterAsEnum(
            parameters,
            self.METRIC,
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
        if method == 0 and metric == 1:
            raise QgsProcessingException(
                self.tr('Ward method does not accept manhattan metric, only euclidean')
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
        X = self.get_data_from_source(source, attributeList)
        model = AgglomerativeClustering(
            n_clusters=n_clusters,
            affinity=self.metrics[metric],
            linkage=self.methods[method]).fit(X)
        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            newFeat = QgsFeature(fields)
            for field in source.fields():
                newFeat[field.name()] = feature[field.name()]
            newFeat.setGeometry(feature.geometry())
            # Add a feature in the sink
            newFeat['cluster'] = int(model.labels_[current])
            sink.addFeature(newFeat, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))
        return {self.OUTPUT: dest_id}
    
    def get_data_from_source(self, source, attributeList):
        X = list()
        for feature in source.getFeatures():
            data = [feature[attr] for attr in attributeList]
            X.append(data)
        return np.array(X)

    
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
        return self.tr("TODO")
