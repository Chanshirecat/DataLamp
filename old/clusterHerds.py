import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import warnings
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"


warnings.filterwarnings("ignore", category=UserWarning, message="Geometry is in a geographic CRS")

# ✅ **Step 1: Load Data**
filtered_gdf_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\processed_herd_areas.geojson"
population_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Final_Cleaned_Population_Data.csv"

filtered_gdf = gpd.read_file(filtered_gdf_path)
population_data = pd.read_csv(population_data_path)

# ✅ **Step 2: Ensure Column Consistency**
if "ADMIN_ST" not in population_data.columns and "State" in population_data.columns:
    print("⚠️ 'ADMIN_ST' not found in population data. Renaming 'State' to 'ADMIN_ST'.")
    population_data.rename(columns={"State": "ADMIN_ST"}, inplace=True)

print("🔍 Unique states in `filtered_gdf`: ", filtered_gdf["ADMIN_ST"].unique())
print("🔍 Unique states in `population_data`: ", population_data["ADMIN_ST"].unique())

# ✅ **Step 3: Merge Population Data**
filtered_gdf = filtered_gdf.merge(population_data, on="ADMIN_ST", how="left")

# ✅ **Step 4: Convert CRS for Accurate Centroid Calculations**
if filtered_gdf.crs is None or filtered_gdf.crs.is_geographic:
    print("🔄 Converting CRS to projected CRS (EPSG: 3857)...")
    filtered_gdf = filtered_gdf.to_crs(epsg=3857)

# ✅ **Step 5: Clustering Function**
def cluster_by_state(gdf, default_clusters=5):
    clustered_gdf = gdf.copy()
    clustered_gdf["cluster"] = -1

    for state, state_gdf in clustered_gdf.groupby("ADMIN_ST"):
        coords = state_gdf.geometry.centroid.apply(lambda point: (point.x, point.y))
        coords = np.array(coords.tolist())

        # Adjust clusters dynamically if points are too few
        n_clusters = min(len(coords), default_clusters)
        if n_clusters < 2:
            print(f"⚠️ Not enough points to cluster for {state}, assigning all to one cluster.")
            clustered_gdf.loc[state_gdf.index, "cluster"] = 0
            continue

        # KMeans Clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        state_gdf["cluster"] = kmeans.fit_predict(coords)
        clustered_gdf.loc[state_gdf.index, "cluster"] = state_gdf["cluster"]

    return clustered_gdf


# ✅ **Step 6: Apply Clustering**
clustered_gdf = cluster_by_state(filtered_gdf, default_clusters=10)

# ✅ **Step 7: Save the Clustered Data**
output_clustered_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\clustered_herds_by_state.geojson"
clustered_gdf.to_file(output_clustered_path, driver="GeoJSON")
print(f"✅ Clustered herd data saved to: {output_clustered_path}")

# ✅ **Step 8: Plot the Clusters**
plt.figure(figsize=(10, 6))
plt.scatter(clustered_gdf.geometry.centroid.x, clustered_gdf.geometry.centroid.y,
            c=clustered_gdf["cluster"], cmap="viridis", marker="o", alpha=0.7)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Clustering of Herd Areas by State")
plt.colorbar(label="Cluster ID")
plt.show()
