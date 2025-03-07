import geopandas as gpd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Load the filtered data
filtered_gdf = gpd.read_file(r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\filtered_herds.geojson")

# Print the first few rows to inspect the data
print(filtered_gdf.head())


# Function to perform clustering by state
def cluster_by_state(gdf, n_clusters=5):
    clustered_gdf = gdf.copy()  # Make a copy of the GeoDataFrame to avoid modifying the original one

    # Group by state (ADMIN_ST) and perform clustering within each state
    clustered_gdf['cluster'] = -1  # Initialize cluster column with -1 (indicating no cluster yet)

    for state, state_gdf in clustered_gdf.groupby('ADMIN_ST'):
        # Get the centroids of the state herd areas
        coords = state_gdf.geometry.centroid.apply(lambda point: (point.x, point.y))
        coords = np.array(coords.tolist())

        # Perform KMeans clustering for this state
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        state_gdf['cluster'] = kmeans.fit_predict(coords)

        # Update the original GeoDataFrame with the state-specific clusters
        clustered_gdf.loc[state_gdf.index, 'cluster'] = state_gdf['cluster']

    return clustered_gdf


# Apply the clustering by state function
clustered_gdf = cluster_by_state(filtered_gdf, n_clusters=5)  # You can change n_clusters as needed

# Print the results
print(clustered_gdf[['HA_NAME', 'ADMIN_ST', 'cluster']])

# Plot the clusters using centroids
centroids = clustered_gdf.geometry.centroid

# Plot the clusters using the centroids
plt.figure(figsize=(10, 6))
plt.scatter(centroids.x, centroids.y, c=clustered_gdf['cluster'], cmap='viridis', marker='o')
plt.title("Clustering of Herd Areas by State")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.colorbar(label="Cluster")
plt.show()

# Save the clustered data to a new GeoJSON file
clustered_gdf.to_file(r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\clustered_herds_by_state.geojson",
                      driver="GeoJSON")
