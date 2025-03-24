import pandas as pd
import geopandas as gpd
from fuzzywuzzy import process

# Define file paths
herd_population_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Herd_Population.xlsx"
gdb_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\BLM Wild Horse and Burro Herd Area Polygons\data\v101\rangedata_blm_20170519.gdb"
layer_name = "BLM_National_HA_20170519"  # Ensure this is the correct layer name

# Load herd population data
df_herd_population = pd.read_excel(herd_population_path)

# Load herd location data from the GDB
gdf_herd_locations = gpd.read_file(gdb_path, layer=layer_name)

# Convert to a projected coordinate system before calculating centroids
projected_crs = "EPSG:3857"  # Web Mercator projection (meters-based)
gdf_herd_locations = gdf_herd_locations.to_crs(projected_crs)

# Now safely calculate centroids
gdf_herd_locations["longitude"] = gdf_herd_locations.geometry.centroid.x
gdf_herd_locations["latitude"] = gdf_herd_locations.geometry.centroid.y

# Convert back to WGS 84 (EPSG:4326) for correct mapping
gdf_herd_locations = gdf_herd_locations.to_crs(epsg=4326)

# Select relevant columns from location data
df_herd_locations = gdf_herd_locations[["ADMIN_ST", "HA_NAME", "HA_NO", "longitude", "latitude"]].copy()

# Function to clean herd names by removing text in parentheses
def clean_herd_name(name):
    import re
    return re.sub(r"\s*\(.*?\)", "", str(name)).strip()

# Apply cleaning to herd names in both datasets
df_herd_population["Herd Name Cleaned"] = df_herd_population["Herd Name"].apply(clean_herd_name)
df_herd_locations.loc[:, "HA_NAME Cleaned"] = df_herd_locations["HA_NAME"].apply(clean_herd_name)

# Function to find the best fuzzy match for herd names
def find_best_match(name, choices, threshold=80):
    match, score = process.extractOne(name, choices)
    return match if score >= threshold else None

# Apply fuzzy matching to align herd names
df_herd_population["Best Match Herd Name"] = df_herd_population["Herd Name Cleaned"].apply(
    lambda name: find_best_match(name, df_herd_locations["HA_NAME Cleaned"].unique())
)

# Standardize herd codes
df_herd_population["Herd Code Cleaned"] = df_herd_population["Herd Code"].astype(str).str.strip()
df_herd_locations.loc[:, "HA_NO Cleaned"] = df_herd_locations["HA_NO"].astype(str).str.strip()

# Merge using both Herd Code and fuzzy-matched Herd Name
merged_df = df_herd_population.merge(
    df_herd_locations,
    left_on=["Best Match Herd Name", "Herd Code Cleaned"],
    right_on=["HA_NAME Cleaned", "HA_NO Cleaned"],
    how="inner"
)

# Keep only necessary columns
merged_df = merged_df[[
    "State", "State Code", "Herd Name", "Herd Code",
    "Horses", "Burros", "Total Population", "latitude", "longitude"
]]

# Save merged data to a CSV file
output_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Merged_Herd_Population_Location.csv"
merged_df.to_csv(output_path, index=False)

# Print confirmation message
print(f"Merged dataset saved as {output_path}")
