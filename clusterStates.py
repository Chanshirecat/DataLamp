import geopandas as gpd
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
from sklearn.cluster import KMeans
import hdbscan

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

# Paths
states_folder = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\States_Separated"
population_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Final_Cleaned_Population_Data.csv"
output_folder = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\Clustered_States"

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load population data
df_population = pd.read_csv(population_data_path)

# Function to generate cluster points inside state shape
def generate_cluster_points(state_geometry, state_population, crs):
    """Generates spaced cluster points inside state boundary, scaled by population size."""
    if pd.isna(state_population) or state_population <= 0:
        return None

    # Adjust clustering density dynamically with upper and lower limits
    num_points = min(500, max(50, int(state_population / 5)))  # Limits the density

    points = []
    minx, miny, maxx, maxy = state_geometry.bounds

    while len(points) < num_points:
        random_point = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if state_geometry.contains(random_point):  # Ensure point is inside state shape
            points.append(random_point)

    # Create GeoDataFrame
    return gpd.GeoDataFrame(geometry=points, crs=crs)

# Process each state file
for state_file in os.listdir(states_folder):
    if state_file.endswith(".geojson"):
        state_path = os.path.join(states_folder, state_file)

        # Load state boundary
        df_state = gpd.read_file(state_path)

        # Extract state name
        state_name = state_file.replace(".geojson", "")

        # Get state population from dataset
        state_population_row = df_population[df_population["State"] == state_name]
        if state_population_row.empty:
            print(f"⚠️ No population data for {state_name}, skipping...")
            continue
        state_population = state_population_row["Total Population"].values[0]

        print(f"✅ Processing {state_name} (Population: {state_population})...")

        # Get CRS from df_state
        state_crs = df_state.crs

        # Generate cluster points inside the state shape
        cluster_gdf = generate_cluster_points(df_state.geometry.iloc[0], state_population, state_crs)

        if cluster_gdf is None or len(cluster_gdf) == 0:
            print(f"⚠️ No clusters generated for {state_name}")
            continue

        print(f"🟢 Generated {len(cluster_gdf)} cluster points for {state_name}")

        # Convert points to numeric arrays
        point_coords = cluster_gdf.geometry.apply(lambda geom: [geom.x, geom.y]).tolist()

        # Apply DBSCAN first (prevents forced clustering)
        dbscan = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=3)
        cluster_labels = dbscan.fit_predict(point_coords)

        # If DBSCAN fails (i.e., assigns everything to -1), use KMeans as fallback
        if len(set(cluster_labels)) == 1:  # Only noise detected
            print(f"⚠️ DBSCAN failed for {state_name}, using KMeans fallback...")
            kmeans = KMeans(n_clusters=min(20, len(cluster_gdf)), random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(point_coords)

        cluster_gdf["Cluster_ID"] = cluster_labels

        # Avoid Overlapping Clusters: Apply force-directed jitter
        def add_jitter(coord, scale=0.02):
            """Applies slight movement to avoid overlaps."""
            return coord + np.random.uniform(-scale, scale)

        cluster_gdf["geometry"] = cluster_gdf.geometry.apply(lambda p: Point(add_jitter(p.x), add_jitter(p.y)))

        # Merge state boundary and cluster points
        cluster_gdf["type"] = "cluster"
        df_state["type"] = "boundary"
        merged_gdf = pd.concat([df_state, cluster_gdf], ignore_index=True)

        # Save clustered state for 3D use
        clustered_geojson = os.path.join(output_folder, f"{state_name}_clustered.geojson")
        merged_gdf.to_file(clustered_geojson, driver="GeoJSON")

        # Save SVG for visualization of clustering
        svg_path = os.path.join(output_folder, f"{state_name}_clustered.svg")
        fig, ax = plt.subplots(figsize=(6, 6))
        df_state.boundary.plot(ax=ax, edgecolor="black", linewidth=1.5)
        cluster_gdf.plot(ax=ax, column="Cluster_ID", cmap="tab10", legend=True, markersize=8, alpha=0.75)
        ax.set_axis_off()
        plt.savefig(svg_path, format="svg", bbox_inches="tight")
        plt.close(fig)

        print(f"✅ Clustered {state_name} saved for 3D modeling: {clustered_geojson}, {svg_path}")

print(f"✅ All clustered states saved separately in: {output_folder}")
