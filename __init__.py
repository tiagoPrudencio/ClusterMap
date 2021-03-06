# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Clustering
                                 A QGIS plugin
 Receives polygon shapefile as input and applies clustering methods for the generation of choropleth maps 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-03-18
        copyright            : (C) 2020 by Prudencio T. and Maia B.
        email                : tiagoprudencio16@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Clustering class from file Clustering.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    #from .Clustering import Clustering
    from .ClusterMap import ClusterMap
    return ClusterMap(iface)
