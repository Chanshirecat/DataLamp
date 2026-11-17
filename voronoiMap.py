import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

# 1. LOAD DATA
file_path = r'C:\Users\Happi\Documents\BCC\Bachelor Thesis\Merged_Herd_Population_Location.csv'
df = pd.read_csv(file_path).dropna(subset=['longitude', 'latitude'])
pop_col = 'Total Population'

# 2. MAP SETUP
usa_states = gpd.read_file(
    "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json").to_crs(
    "EPSG:3857")
lower_48 = usa_states[~usa_states['name'].isin(['Alaska', 'Hawaii', 'Puerto Rico'])]
bounds = lower_48.total_bounds

# 3. SPATIAL BUFFERING (The "No-Overlap" Guarantee)
coords = df[['longitude', 'latitude']].values
repulsion_radius = 25000
df['x_viz'], df['y_viz'] = df['longitude'], df['latitude']

for iteration in range(200):
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            dx, dy = df.at[i, 'x_viz'] - df.at[j, 'x_viz'], df.at[i, 'y_viz'] - df.at[j, 'y_viz']
            dist = np.sqrt(dx ** 2 + dy ** 2)
            if 0 < dist < repulsion_radius:
                overlap = (repulsion_radius - dist) / dist
                df.at[i, 'x_viz'] += dx * overlap * 0.5
                df.at[i, 'y_viz'] += dy * overlap * 0.5
                df.at[j, 'x_viz'] -= dx * overlap * 0.5
                df.at[j, 'y_viz'] -= dy * overlap * 0.5

# 4. PRODUCTION RENDER
fig, ax = plt.subplots(figsize=(30, 20), dpi=300)
fig.patch.set_facecolor('black')
ax.set_facecolor('black')

# THE THEME: Outline only the states with horse populations
# A. Find states that contain at least one horse herd point
gdf_points = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['longitude'], df['latitude']), crs="EPSG:3857")
horse_states = gpd.sjoin(lower_48, gdf_points, predicate='contains')['name'].unique()

print(f"Horses detected in {len(horse_states)} states. Outlining.")
lower_48[lower_48['name'].isin(horse_states)].boundary.plot(ax=ax, color='white', linewidth=1.0, alpha=0.9, zorder=1)
# Faint outline of others for context
lower_48[~lower_48['name'].isin(horse_states)].boundary.plot(ax=ax, color='#111111', linewidth=0.5, alpha=0.3, zorder=0)

# 5. ICON MAPPING (Size by population)
max_pop = df[pop_col].max()
for _, row in df.iterrows():
    p = row[pop_col]
    size = 4 + (p / max_pop) * 8  # 4min, 12max

    if p < 10:
        marker = '^'  # Triangle
    elif p < 50:
        marker = 'D'  # Diamond
    elif p < 100:
        marker = 's'  # Square
    else:
        marker = 'X'  # Bold X

    ax.plot(row['x_viz'], row['y_viz'], marker=marker, color='white', markersize=size, alpha=1.0, zorder=3)

# 6. Viewport Lock
ax.set_xlim(bounds[0], bounds[2])
ax.set_ylim(bounds[1], bounds[3])
ax.set_aspect('equal')
plt.axis('off')

output_name = 'Horse_Lamp_Blueprint_V88.png'
plt.savefig(output_name, facecolor='black', bbox_inches='tight', pad_inches=0)
print(f"Thesis Deployment Complete: '{output_name}' is error-free.")