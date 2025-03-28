import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from scipy.spatial import distance_matrix
import numpy as np
import os

# Pandas is used for reading and handling tabular data, GeoPandas extends it to support geospatial data
# Matplotlib is used for plotting, and Shapely is used to create Point geometries from longitude and latitude so we can map them
# SciPy is used for calculating distances between points, provides distance_matrix
# Numpy is used for numerical operations, e.g. for handling arrays and mathematical functions
# os is used for file path handling and directory creation

# File paths
herd_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Merged_Herd_Population_Location.csv"
us_states_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\US States\us-state-boundaries.geojson"
output_dir = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp"

# Load data
df = pd.read_csv(herd_data_path)
df = df.dropna(subset=["latitude", "longitude"])
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:3857"
)

# Initial attributes
# creates the geo-dataframe with the herd data, EPSG:3857 is a projected coordinate system (in meters) used for distance calculations
gdf["count"] = df["Total Population"].fillna(1)
gdf["radius"] = 30  # keep small to preserve detail

# Parameters for merging and growth
growth_step = 30
merge_threshold = 1.10
max_outer_iterations = 30

# The function uses a distance matrix to find pairs of dots that are close enough to be considered overlapping, then builds an adjacency list to represent the graph of overlapping dots
# after, it uses a breadth-first search (BFS) to find all connected clusters
def get_overlap_clusters(geo_points, threshold):
    coords = np.vstack((geo_points.geometry.x, geo_points.geometry.y)).T
    dist = distance_matrix(coords, coords)
    n = len(geo_points)
    adjacency = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            r1, r2 = geo_points.iloc[i]["radius"], geo_points.iloc[j]["radius"]
            if dist[i, j] < (r1 + r2) * threshold:
                adjacency[i].append(j)
                adjacency[j].append(i)

    visited = set()
    dot_clusters = []
    for i in range(n):
        if i not in visited:
            queue = [i]
            dot_cluster = []
            while queue:
                curr = queue.pop()
                if curr not in visited:
                    visited.add(curr)
                    dot_cluster.append(curr)
                    queue.extend(adjacency[curr])
            dot_clusters.append(dot_cluster)
    return dot_clusters

# Main iterative loop
# The outer loop iterates until either all dots are merged or the maximum number of iterations is reached
# The inner loop merges overlapping dots and grows their radius and continues until no more overlaps are found

for outer in range(max_outer_iterations):
    merged = False
    while True:
        clusters = get_overlap_clusters(gdf, merge_threshold)

        if len(clusters) == len(gdf):  # overlaps
            break

        merged = True
        merged_points, merged_counts, merged_radii = [], [], []


        for cluster in clusters:
            pts = gdf.iloc[cluster]
            total = pts["count"].sum()
            weights = pts["count"].values
            if total == 0:
                x = pts.geometry.x.mean()
                y = pts.geometry.y.mean()
            else:
                x = np.average(pts.geometry.x, weights=weights)
                y = np.average(pts.geometry.y, weights=weights)

            merged_points.append(Point(x, y))
            merged_counts.append(total)
            merged_radii.append(np.sqrt(total) * 200)

        gdf = gpd.GeoDataFrame(
            {"geometry": merged_points, "count": merged_counts, "radius": merged_radii},
            crs="EPSG:3857"
        )

    # After merging, grow
    gdf["radius"] += growth_step

    # Recheck overlaps after growth
    post_growth_clusters = get_overlap_clusters(gdf, merge_threshold)
    if len(post_growth_clusters) == len(gdf):
        print(f"Fully complete after {outer + 1} growth iterations — no overlaps remain.")
        break
    else:
        print(f"Growth iteration {outer + 1} complete — still {len(gdf)} dots")

# Final conversion and size scaling
gdf_final = gdf.to_crs("EPSG:4326") #Converts coordinates back to latitude/longitude (EPSG:4326)
sqrt_pop = np.sqrt(gdf_final["count"])
sqrt_min, sqrt_max = sqrt_pop.min(), sqrt_pop.max()
gdf_final["hole_size"] = 2 + (sqrt_pop - sqrt_min) / (sqrt_max - sqrt_min) * (20 - 2)

# borders
gdf_states = gpd.read_file(us_states_path).to_crs("EPSG:4326")
excluded = ['Alaska', 'Hawaii', 'Puerto Rico', 'American Samoa', 'Guam',
            'Commonwealth of the Northern Mariana Islands', 'United States Virgin Islands']
gdf_states = gdf_states[~gdf_states['name'].isin(excluded)]
western_states = ["Arizona", "California", "Colorado", "Idaho", "Montana", "Nevada",
                  "New Mexico", "Oregon", "Utah", "Wyoming"]
gdf_west = gdf_states[gdf_states["name"].isin(western_states)]

# Final plot
fig, ax = plt.subplots(figsize=(24, 15), facecolor="black")
ax.set_facecolor("black")
gdf_states.boundary.plot(ax=ax, color="white", linewidth=1.0, linestyle="dashed", alpha=0.8)
gdf_west.boundary.plot(ax=ax, color="red", linewidth=0.8)

gdf_final.plot(
    ax=ax,
    marker='o',
    color='white',
    linewidth=0.5,
    markersize=gdf_final["hole_size"] ** 1.5,
    alpha=1
)

ax.set_xticks([])
ax.set_yticks([])
ax.set_title("Merged Herd Population Clusters", color="white", fontsize=16)

# Export
os.makedirs(output_dir, exist_ok=True)
plt.savefig(os.path.join(output_dir, "herd_distribution_cutout_FINAL.png"), dpi=300, bbox_inches='tight', facecolor='black')
plt.savefig(os.path.join(output_dir, "herd_distribution_cutout_FINAL.svg"), format='svg', bbox_inches='tight', facecolor='black')
plt.show()
