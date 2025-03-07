import geopandas as gpd
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Path to GDB file
gdb_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\BLM Wild Horse and Burro Herd Area Polygons\data\v101\rangedata_blm_20170519.gdb"

# Read the GDB file and inspect available layers
gdf = gpd.read_file(gdb_path, driver="FileGDB")

# Print the available layers in the GDB
print(f"Available Layers in GDB: {gdf.keys()}")

# Let's check the columns and head of the main dataset (assuming 'gdf' is the herd areas)
print(gdf.columns)
print(gdf.head())

# Check if there is a layer with population data. For example, you may have another layer like 'herd_population'.
# If found, read the population data.
# Replace 'herd_population' with the actual layer name if you find it.
try:
    population_gdf = gpd.read_file(gdb_path, layer="herd_population", driver="FileGDB")
    print(population_gdf.columns)
    print(population_gdf.head())
except KeyError:
    print("Population data layer not found in the GDB file.")

# Filter the herd area data for all valid US states (assuming 'ADMIN_ST' contains state names)
valid_states = gdf['ADMIN_ST'].unique()
filtered_gdf = gdf[gdf['ADMIN_ST'].isin(valid_states)]

# Let's assume the population data is found in the "herd_population" layer and merged by 'Herd_ID'.
# Merge the population data with the filtered herd area data.
# Replace 'Herd_ID' and 'horse_population' with the actual column names from the population data.

# If population_gdf is available, proceed with the merge
if 'horse_population' in population_gdf.columns:
    merged_gdf = filtered_gdf.merge(population_gdf[['Herd_ID', 'horse_population']], left_on='Herd_ID', right_on='Herd_ID', how='left')
    print(merged_gdf.head())
else:
    print("Population data not available for merging.")

# If merged data is available, perform clustering based on the horse population.
# We will use KMeans to cluster the herd areas by population.
if 'horse_population' in merged_gdf.columns:
    # Extract centroids for clustering
    coords = merged_gdf.geometry.centroid.apply(lambda point: (point.x, point.y))
    coords = pd.DataFrame(coords.tolist(), columns=['x', 'y'])

    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=5)  # You can change the number of clusters as needed
    merged_gdf['cluster'] = kmeans.fit_predict(coords)

    # Visualize the clustering result
    plt.figure(figsize=(10, 8))
    plt.scatter(merged_gdf.geometry.x, merged_gdf.geometry.y, c=merged_gdf['cluster'], cmap='viridis', marker='o')
    plt.title("Clustering of Herd Areas by Horse Population")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.colorbar(label="Cluster")
    plt.show()
else:
    print("Cluster creation failed due to missing population data.")
