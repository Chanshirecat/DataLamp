import geopandas as gpd
import pandas as pd
import fiona
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import hdbscan

# ✅ STEP 1: Ensure Correct File Path
herd_area_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\BLM Wild Horse and Burro Herd Area Polygons\data\v101\rangedata_blm_20170519.gdb"

# ✅ STEP 2: Load Correct Layer Name
layer_name = "BLM_National_HA_20170519"  # <<<< FIXED LAYER NAME

# ✅ STEP 3: Load Data from the Correct Layer
df_herd_areas = gpd.read_file(herd_area_data_path, layer=layer_name, driver="FileGDB")

# ✅ STEP 4: Check Available Columns
print("📊 Available Columns:", df_herd_areas.columns)

# ✅ STEP 5: Convert to a Projected CRS for Accurate Centroids
df_herd_areas = df_herd_areas.to_crs(epsg=3857)

# ✅ STEP 6: Compute Centroids for Clustering
df_herd_areas["Longitude"] = df_herd_areas.geometry.centroid.x
df_herd_areas["Latitude"] = df_herd_areas.geometry.centroid.y

# ✅ STEP 7: Convert Back to Geographic CRS (WGS84)
df_herd_areas = df_herd_areas.to_crs(epsg=4326)

# ✅ STEP 8: Save the Preprocessed Data
output_geojson_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\processed_herd_areas.geojson"
df_herd_areas.to_file(output_geojson_path, driver="GeoJSON")

print(f"✅ Preprocessed herd area data saved to {output_geojson_path}")

# ✅ STEP 9: Plot Herd Area Centroids
plt.figure(figsize=(10, 6))
plt.scatter(df_herd_areas["Longitude"], df_herd_areas["Latitude"], c="blue", marker="o", alpha=0.5)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Herd Area Centroids")
plt.show()
