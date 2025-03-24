import geopandas as gpd
import pandas as pd
import os
import matplotlib.pyplot as plt

# Paths to datasets
geojson_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\US States\us-state-boundaries.geojson"
population_data_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\Final_Cleaned_Population_Data.csv"
output_folder = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\States_Separated"

# Ensure the output directory exists
os.makedirs(output_folder, exist_ok=True)

# State name to abbreviation mapping
state_abbreviations = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND",
    "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

# Load US state boundaries
df_states = gpd.read_file(geojson_path)
print(f"✅ Loaded {len(df_states)} states from GeoJSON.")

# Load population data
df_population = pd.read_csv(population_data_path)
print(f"✅ Loaded population data for {len(df_population)} states.")

# Convert full state names to abbreviations
df_states["State_Abbrev"] = df_states["name"].map(state_abbreviations)

# Keep only the 10 states that have wild horse & burro populations
relevant_states = df_population["State"].unique()
df_states = df_states[df_states["State_Abbrev"].isin(relevant_states)]
print(f"✅ Filtered to {len(df_states)} relevant states.")

# Rename to match population dataset
df_states = df_states.rename(columns={"State_Abbrev": "State"})
df_merged = df_states.merge(df_population, on="State", how="left")
print(f"✅ Merged dataset now has {len(df_merged)} states.")

# Ensure all geometries are valid before exporting
df_merged = df_merged[df_merged["geometry"].notnull() & ~df_merged["geometry"].is_empty]

# Save each state separately
if len(df_merged) == 0:
    print("⚠️ No valid states to save. Check dataset filtering.")
else:
    for _, row in df_merged.iterrows():
        state_name = row["State"]
        state_gdf = gpd.GeoDataFrame([row], crs=df_merged.crs)

        # Define file paths
        geojson_path = os.path.join(output_folder, f"{state_name}.geojson")
        dxf_path = os.path.join(output_folder, f"{state_name}.dxf")
        svg_path = os.path.join(output_folder, f"{state_name}.svg")

        # Save each state separately
        state_gdf.to_file(geojson_path, driver="GeoJSON")

        # **Fix DXF Export: Convert geometries before saving**
        try:
            state_gdf[["geometry"]].to_file(dxf_path, driver="DXF")
            print(f"✅ Saved DXF: {dxf_path}")
        except Exception as e:
            print(f"⚠️ Could not save DXF for {state_name}: {e}")

        # **Fix SVG Export Using Matplotlib Instead**
        fig, ax = plt.subplots(figsize=(5, 5))
        state_gdf.boundary.plot(ax=ax, edgecolor="black")
        ax.set_axis_off()  # Remove background axes
        plt.savefig(svg_path, format="svg", bbox_inches="tight")  # Save as SVG
        plt.close(fig)  # Close figure to free memory
        print(f"✅ Saved SVG: {svg_path}")

print(f"✅ All relevant states saved separately in: {output_folder}")
