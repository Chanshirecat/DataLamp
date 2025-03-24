import pandas as pd
import geopandas as gpd

# ✅ Step 1: Load the cleaned population data
population_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Final_Cleaned_Population_Data.csv"
df_population = pd.read_csv(population_data_path)

# ✅ Step 2: Load the herd area dataset
herd_area_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\filtered_herds.geojson"
df_herd_areas = gpd.read_file(herd_area_data_path)

# ✅ Step 3: Convert state names to uppercase for consistency
df_population["State"] = df_population["State"].str.upper()
df_herd_areas["State"] = df_herd_areas["State"].str.upper()

# ✅ Step 4: Merge datasets
df_merged = df_herd_areas.merge(df_population, on="State", how="left")

# ✅ Step 5: Fix numeric data types
import pandas as pd
import geopandas as gpd

# ✅ Step 1: Load the cleaned population data
population_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Final_Cleaned_Population_Data.csv"
df_population = pd.read_csv(population_data_path)

# ✅ Step 2: Load the herd area dataset
herd_area_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\filtered_herds.geojson"
df_herd_areas = gpd.read_file(herd_area_data_path)

# ✅ Step 3: Convert state names to uppercase for consistency
df_population["State"] = df_population["State"].str.upper()
df_herd_areas["State"] = df_herd_areas["State"].str.upper()

# ✅ Step 4: Merge datasets
df_merged = df_herd_areas.merge(df_population, on="State", how="left")

# ✅ Step 5: Fix numeric data types
df_merged["Horses"] = pd.to_numeric(df_merged["Horses"], errors="coerce").fillna(0)
df_merged["Burros"] = pd.to_numeric(df_merged["Burros"], errors="coerce").fillna(0)

# ✅ Step 6: Compute Total Animals per state
state_totals = df_merged.groupby("State")[["Horses", "Burros"]].sum().reset_index()
state_totals["Total Animals"] = state_totals["Horses"] + state_totals["Burros"]

# ✅ Step 7: Merge the total animals back into herd-level data
df_merged = df_merged.merge(state_totals[["State", "Total Animals"]], on="State", how="left")

# ✅ Step 8: Get correct state population from `df_population`
df_population_dict = df_population.set_index("State")["Total Population"].to_dict()

# ✅ Step 9: Fix population distribution (Pull correct value from dictionary)
df_merged["Total Population"] = (
    (df_merged["Horses"] + df_merged["Burros"]) / df_merged["Total Animals"]
) * df_merged["State"].map(df_population_dict)

# ✅ Step 10: Ensure valid geometries before saving
df_merged = df_merged[df_merged["geometry"].notnull() & ~df_merged["geometry"].is_empty]

# ✅ Step 11: Save the corrected dataset
merged_geojson_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\Merged_Herd_Population.geojson"
merged_csv_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\Merged_Herd_Population.csv"

df_merged.to_file(merged_geojson_path, driver="GeoJSON")
df_merged.to_csv(merged_csv_path, index=False)

# ✅ Step 12: Print confirmation and preview
print(f"✅ Corrected merge saved to:")
print(f"   - GeoJSON: {merged_geojson_path}")
print(f"   - CSV: {merged_csv_path}")

# 🚨 **Check Herd-Level Population Distribution**
print("\n🐎 Sample Herd Data (Should Show Different Population Numbers Per Herd):")
print(df_merged[["HA_NAME", "State", "Horses", "Burros", "Total Population"]].sort_values(by="Total Population", ascending=False).head(10))
