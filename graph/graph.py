from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as sch
import numpy as np

class createGraph():
	def __init__(self,X,method=None):
		self.X = X
		self.method = method

	def elbowMethod (self):
		wcss = []
		
		for i in range(2, 10):
			kmeans = KMeans(n_clusters = i, init = 'k-means++', random_state = 42)
			kmeans.fit(self.X)
			wcss.append(kmeans.inertia_)
		
		acceleration = np.diff(wcss, 2)  
		acceleration_rev = acceleration[::-1]
		k = acceleration_rev.argmax()
		plt.axvline(k, color="red", linestyle="--")
		plt.plot(range(2, 10), wcss)
		plt.title('The Elbow Method')
		plt.xlabel('Number of clusters')
		plt.ylabel('Sum of squared distances')
		plt.grid(True)
		plt.show()
		
	def silhouetteMethod (self):
		range_n_clusters = [i for i in range(2,10)]
		result_avg = list()
		for n_clusters in range_n_clusters:
			clusterer = KMeans(n_clusters=n_clusters, random_state=42)
			cluster_labels = clusterer.fit_predict(self.X)
			result_avg.append(silhouette_score(self.X, cluster_labels))

		index =result_avg.index(max(result_avg))+2
		#value =max(result_avg)
		plt.plot(range(2, 10), result_avg)

		plt.title('The Silhouette Method')
		plt.xlabel('Number of clusters')
		plt.ylabel('The average silhouette_score')
		#plt.annotate('Optimal Value',xy =(index+0.2,value),
					#xytext =(index+1,value),
					#arrowprops=dict(facecolor='red',shrink = 0.05), #headwidth = 4,width =2 ,headlength =4),
					#fontsize=12,
					#horizontalalignment='left', verticalalignment='top'
					#)
		plt.axvline(index, color="red", linestyle="--")
		plt.grid(True)
		plt.show()

	def createDendrogram(self):
		dendrogram = sch.dendrogram(sch.linkage(self.X, method = self.method ))
		plt.title('Dendrogram')
		plt.xlabel('attributes')
		#plt.ylabel('metric')
		plt.show()

	#https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/