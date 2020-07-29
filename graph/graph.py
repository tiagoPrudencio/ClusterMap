from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

class createGraph():
	def __init__(self,X,method=None):
		self.X = X
		self.method = method

	def optimal_number_of_clusters(self, wcss):
		x1, y1 = 0, wcss[0]
		x2, y2 = 9, wcss[len(wcss)-1]

		distances = []
		for i in range(len(wcss)):
			x0 = i
			y0 = wcss[i]
			numerator = abs((y2-y1)*x0 - (x2-x1)*y0 + x2*y1 - y2*x1)
			denominator = ((y2 - y1)**2 + (x2 - x1)**2)**(1/2)
			distances.append(numerator/denominator)
	
		return distances.index(max(distances)) + 2


	def elbowMethod (self):
		wcss = []
		for n_clusters in range(2, 11):
			kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(self.X)
			wcss.append(kmeans.inertia_)

		k = self.optimal_number_of_clusters(wcss)

		plt.axvline(k, color="red", linestyle="--")
		plt.plot(range(2, 11), wcss)
		plt.title('The Elbow Method')
		plt.xlabel('Number of clusters')
		plt.ylabel('Sum of squared distances')
		plt.grid(True)
		plt.show()
		
	def silhouetteMethod (self):
		result_avg = list()
		for n_clusters in range(2, 11):
			kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(self.X)
			result_avg.append(silhouette_score(self.X, kmeans.labels_, metric='euclidean'))

		index =result_avg.index(max(result_avg))+2

		plt.axvline(index, color="red", linestyle="--")
		plt.plot(range(2, 11), result_avg)
		plt.title('The Silhouette Method')
		plt.xlabel('Number of clusters')
		plt.ylabel('The average silhouette_score')
		plt.grid(True)
		plt.show()