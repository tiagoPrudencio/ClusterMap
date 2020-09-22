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

from sklearn import tree
import numpy as np
import collections
import statistics


class classification ():
	def __init__(self,X,Y,attr):
		self.X = X
		self.Y = Y
		self.attr = attr
		self.children_left = None
		self.children_right = None
		self.feature = None
		self.threshold = None


	def find_path(self,node_numb, path, leaf):
		path.append(node_numb)
		if node_numb == leaf:
			return True
		left = False
		right = False
		if (self.children_left[node_numb] !=-1):
			left = self.find_path(self.children_left[node_numb], path, leaf)
		if (self.children_right[node_numb] !=-1):
			right = self.find_path(self.children_right[node_numb], path, leaf)
		if left or right :
			return True
		path.remove(node_numb)
		return False


	def get_rule(self,path):
		mask = ''
		column_names = self.attr
		for index, node in enumerate(path):
			#We check if we are not in the leaf
			if index!=len(path)-1:
				# Do we go under or over the threshold ?
				if (self.children_left[node] == path[index+1]):
				 mask = mask + (str(column_names[self.feature[node]])+"<="+str(self.threshold[node])+" \t ")
				else:
					mask = mask + (str(column_names[self.feature[node]])+">"+str(self.threshold[node])+" \t ")
		# We insert the & at the right places
		mask = mask.replace("\t", "&", mask.count("\t") - 1)
		mask = mask.replace("\t", "")
		return(mask)

	def decisionTree (self):
		clf = tree.DecisionTreeClassifier(criterion= 'entropy')
		clf = clf.fit(self.X,self.Y)
		self.children_left = clf.tree_.children_left
		self.children_right = clf.tree_.children_right
		self.feature = clf.tree_.feature
		self.threshold = clf.tree_.threshold

		leave_id = clf.apply(self.X)
		paths ={}
		for leaf in np.unique(leave_id):
			path_leaf = []
			self.find_path(0, path_leaf, leaf)
			paths[leaf] = np.unique(np.sort(path_leaf))

		rules = {}
		for key in paths:
			rules[key] = self.get_rule(paths[key])

		samples = collections.defaultdict(list)
		dec_paths = clf.decision_path(self.X)
		for d, dec in enumerate(dec_paths):
			for i in range(clf.tree_.node_count):
				if dec.toarray()[0][i] == 1:
					samples[i].append(d)

		legend = dict()
		rules_tree = dict()
		for i in rules.keys():
			moda = (str(statistics.mode(clf.predict([self.X[j] for j in samples[i]]))))
			if moda in legend.keys():
				aux = legend[moda]
				legend[moda] = aux + ' OR \n' + rules[i]
				rules_tree[moda].append([rules[i],len(samples[i])])
			else:
				legend[moda] = rules[i]
				rules_tree[moda] = list()
				rules_tree[moda].append([rules[i],len(samples[i])])

		for b in rules_tree.keys():
			aux  = [i[1] for i in rules_tree[b]]
			rules_tree[b]=rules_tree[b][aux.index(max(aux))][0].rstrip()
	
		return legend, rules_tree

	
		