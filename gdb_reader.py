import geopandas as gpd #adds the alias gdp

# path to gdb file
gdb_path = r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\BLM Wild Horse and Burro Herd Area Polygons\data\v101\rangedata_blm_20170519.gdb"

# reads gdb file to see available layers
gdf = gpd.read_file(gdb_path, driver="FileGDB")

# checks the available columns and data
print(gdf.columns)
print(gdf.head())

# gets the list of all states from the dataset
valid_states = gdf['ADMIN_ST'].unique()
print(f"Valid States: {valid_states}")

# filters by all US states in the dataset
filtered_gdf = gdf[gdf['ADMIN_ST'].isin(valid_states)]

# saves the filtered data to a new GeoJSON file for later use
filtered_gdf.to_file(r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\filtered_herds.geojson", driver="GeoJSON")
# saves the filtered data as CSV for later use
filtered_gdf.to_csv(r"D:\Users\Happi\Documents\BCC\Bachelor Thesis\DataLamp\filtered_herds.csv")
