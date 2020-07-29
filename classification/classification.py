from sklearn import tree
import numpy as np
import collections
import statistics

'''
import tempfile
import os
r = export_text(decision_tree,feature_names=attr)
 with tempfile.TemporaryFile(suffix=".png",delete=False) as tmpfile:
			plt.figure()
			tree.plot_tree(decision_tree,feature_names=attr)
			plt.savefig(tmpfile, format="png") # File position is at the end of the file.
			tmpfile.seek(0) # Rewind the file. (0: the beginning of the file)
			tfName = tmpfile.name
			os.startfile(tfName)
			tmpfile.close()
		feedback.pushInfo('Rules of a Decision Tree:'+'\n'+r )
'''
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

		legend = list()
		for i in rules.keys():
			rules_ = dict()
			moda = (str(statistics.mode(clf.predict([self.X[j] for j in samples[i]]))))
			legend.append('class '+moda+' : ' +rules[i])
	
		return legend

	
		