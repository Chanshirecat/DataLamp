import os
import sys
from pathlib import Path
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patheffects import withStroke
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon
from shapely.ops import substring, unary_union


#CUSTOM CONFIGURATION FROM STREAMLIT ARGUMENTS
selected_palette = sys.argv[1].lower() if len(sys.argv) > 1 else "viridis"
show_state_borders = sys.argv[2].lower() == "true" if len(sys.argv) > 2 else True
show_state_labels = sys.argv[3].lower() == "true" if len(sys.argv) > 3 else True
size_preset = sys.argv[4] if len(sys.argv) > 4 else "18x12 Lamp Artboard"
dot_scale_factor = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0


#SIZE & ARTBOARD CONFIGURATION
if size_preset == "A4 Landscape (11.7 x 8.27 in)":
    PAGE_WIDTH_IN, PAGE_HEIGHT_IN = 11.7, 8.27
elif size_preset == "1080p HD (16 x 9 in)":
    PAGE_WIDTH_IN, PAGE_HEIGHT_IN = 16.0, 9.0
else:  # Default Size
    PAGE_WIDTH_IN, PAGE_HEIGHT_IN = 18.0, 12.0

PAGE_ASPECT = PAGE_WIDTH_IN / PAGE_HEIGHT_IN


#Paths
BASE_DIR = Path(__file__).resolve().parent

herd_data_path = BASE_DIR.parent / "Merged_Herd_Population_Location.csv"
us_states_path = BASE_DIR.parent / "US States" / "us-state-boundaries.geojson"
output_dir = BASE_DIR / "Output"
output_dir.mkdir(parents=True, exist_ok=True)

output_svg = output_dir / "Screen_Ready_Horse_Lamp_12x18.svg"
output_preview_png = output_dir / "Screen_Ready_Horse_Lamp_12x18_preview.png"


#Settings & Styling
INPUT_CRS = "EPSG:4326"
WEB_MERCATOR_CRS = "EPSG:3857"
WORKING_CRS = "EPSG:5070"
HERD_COORDINATE_CRS = "auto"

PALETTE_COLORS = {
    "viridis": "#D32F2F",  #Red
    "plasma": "#E65100",   #Deep Orange
    "magma": "#8E24AA",    #Purple
}

AFFECTED_RED = PALETTE_COLORS.get(selected_palette, "#D32F2F")
MAP_GRAY = "#888888"
DOT_BORDER_COLOR = "#000000"
LABEL_BLACK = "#000000"

STATE_BORDER_WIDTH = 0.75
DOT_BORDER_WIDTH = 1.25
DASH_LINE_WIDTH = 1.75

grid_spacing = 26_000
max_dot_radius_factor = 0.495 * dot_scale_factor

DASH_ON_IN = 0.18
DASH_OFF_IN = 0.22

STATE_LABEL_ANGLE = 0
MAX_LABEL_FONT_PT = 8.5
MIN_LABEL_FONT_PT = 1.6
LABEL_DOT_MARGIN_IN = 0.08

mpl.rcParams["svg.fonttype"] = "path"
mpl.rcParams["path.simplify"] = False

contiguous_us_states = [
    "Alabama", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts",
    "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]

fallback_affected_states = [
    "Arizona", "California", "Colorado", "Idaho", "Montana", "Nevada",
    "New Mexico", "Oregon", "Utah", "Wyoming",
]

#Helpers
def keep_biggest_polygon(geom):
    if isinstance(geom, MultiPolygon):
        return max(geom.geoms, key=lambda g: g.area)
    return geom

def detect_herd_crs(df):
    x = df["longitude"]
    y = df["latitude"]
    looks_lon_lat = x.between(-180, 180) & y.between(-90, 90)
    looks_swapped = y.between(-180, 180) & x.between(-90, 90)
    web_limit = 20_037_508.342789244
    looks_mercator = x.between(-web_limit, web_limit) & y.between(-web_limit, web_limit)

    if looks_lon_lat.mean() >= 0.8:
        return INPUT_CRS, "normal", df.loc[looks_lon_lat].copy()
    if looks_swapped.mean() >= 0.8:
        return INPUT_CRS, "swapped", df.loc[looks_swapped].copy()
    if looks_mercator.mean() >= 0.8:
        return WEB_MERCATOR_CRS, "normal", df.loc[looks_mercator].copy()
    return INPUT_CRS, "normal", df.copy()

def make_herd_gdf(df):
    crs, order, clean_df = detect_herd_crs(df)
    if order == "swapped":
        geom = gpd.points_from_xy(clean_df["latitude"], clean_df["longitude"])
    else:
        geom = gpd.points_from_xy(clean_df["longitude"], clean_df["latitude"])
    return gpd.GeoDataFrame(clean_df, geometry=geom, crs=crs).to_crs(WORKING_CRS)

def expand_bounds(bounds):
    xmin, ymin, xmax, ymax = bounds
    width = xmax - xmin
    height = ymax - ymin
    cx = (xmin + xmax) / 2
    cy = (ymin + ymax) / 2

    if width / height < PAGE_ASPECT:
        width = height * PAGE_ASPECT
    else:
        height = width / PAGE_ASPECT

    margin = 1.09
    width *= margin
    height *= margin
    return cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2

def make_grid(bounds):
    xmin, ymin, xmax, ymax = bounds
    xs = np.arange(xmin, xmax + grid_spacing, grid_spacing)
    ys = np.arange(ymin, ymax + grid_spacing, grid_spacing)
    points = [Point(x, y) for x in xs for y in ys]
    return gpd.GeoDataFrame(geometry=points, crs=WORKING_CRS)

def line_parts(geom):
    if geom is None or geom.is_empty:
        return
    if isinstance(geom, Polygon):
        yield LineString(geom.exterior.coords)
        for ring in geom.interiors:
            yield LineString(ring.coords)
    elif isinstance(geom, MultiPolygon):
        for part in geom.geoms:
            yield from line_parts(part)
    elif isinstance(geom, LineString):
        yield geom
    elif isinstance(geom, MultiLineString):
        for part in geom.geoms:
            yield part
    else:
        if hasattr(geom, "coords"):
            yield LineString(geom.coords)
        elif hasattr(geom, "geoms"):
            for part in geom.geoms:
                yield from line_parts(part)

def make_real_dashes(geometries, plot_bounds):
    map_units_per_inch = (plot_bounds[2] - plot_bounds[0]) / PAGE_WIDTH_IN
    dash_len = DASH_ON_IN * map_units_per_inch
    gap_len = DASH_OFF_IN * map_units_per_inch

    dashes = []
    for geom in geometries:
        for line in line_parts(geom):
            dist = 0
            while dist < line.length:
                end = min(dist + dash_len, line.length)
                dash = substring(line, dist, end)
                if not dash.is_empty and dash.length > 0:
                    dashes.append(dash)
                dist += dash_len + gap_len
    return gpd.GeoDataFrame(geometry=dashes, crs=WORKING_CRS)

def draw_line(ax, geom, color, width, zorder):
    for line in line_parts(geom):
        x, y = line.xy
        ax.plot(x, y, color=color, linewidth=width, zorder=zorder, solid_capstyle="butt")

def label_box_fits(geom, center, name, font_size, plot_bounds, avoid_geom=None):
    map_units_per_pt = ((plot_bounds[2] - plot_bounds[0]) / PAGE_WIDTH_IN) / 72
    name_width = sum(0.45 if char == " " else 0.70 for char in name)
    w = name_width * font_size * map_units_per_pt * 1.25
    h = font_size * map_units_per_pt * 1.25

    angle = np.radians(STATE_LABEL_ANGLE)
    axis = np.array([np.cos(angle), np.sin(angle)])
    perp = np.array([-np.sin(angle), np.cos(angle)])
    c = np.array([center.x, center.y])

    corners = [
        (float((c + axis * (sx * w) + perp * (sy * h))[0]), float((c + axis * (sx * w) + perp * (sy * h))[1]))
        for sx, sy in [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
    ]
    label_box = Polygon(corners)

    if not geom.covers(label_box):
        return False
    if avoid_geom is not None and not avoid_geom.is_empty and label_box.intersects(avoid_geom):
        return False
    return True

def label_centers(geom):
    centers = [geom.centroid, geom.representative_point()]
    centers = [p for p in centers if geom.covers(p)]
    xmin, ymin, xmax, ymax = geom.bounds
    for x in np.linspace(xmin, xmax, 7):
        for y in np.linspace(ymin, ymax, 7):
            p = Point(x, y)
            if geom.covers(p):
                centers.append(p)
    unique = []
    for point in centers:
        if all(point.distance(old) > 1 for old in unique):
            unique.append(point)
    return unique or [geom.representative_point()]

def draw_state_label(ax, geom, name, plot_bounds, avoid_geom=None):
    name = str(name).upper()
    centers = label_centers(geom)

    for font_size in np.linspace(MAX_LABEL_FONT_PT, MIN_LABEL_FONT_PT, 36):
        for test_center in centers:
            if label_box_fits(geom, test_center, name, font_size, plot_bounds, avoid_geom):
                center = test_center
                break
        else:
            continue
        break
    else:
        font_size = MIN_LABEL_FONT_PT
        center = centers[0]

    ax.text(
        center.x, center.y, name,
        ha="center", va="center",
        fontsize=font_size, fontfamily="Arial", fontweight="bold",
        rotation=STATE_LABEL_ANGLE, rotation_mode="anchor", color=LABEL_BLACK,
        zorder=20,
        path_effects=[withStroke(linewidth=max(0.35, font_size * 0.10), foreground="white")],
    )

#Load Data & execute drawing
df = pd.read_csv(herd_data_path)
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=["latitude", "longitude"]).copy()

df["Total Population"] = pd.to_numeric(df["Total Population"], errors="coerce")
df["count"] = df["Total Population"].fillna(1).clip(lower=1)
herd = make_herd_gdf(df)

states = gpd.read_file(us_states_path)
states["name"] = states["name"].astype(str).str.strip()
states = states[states["name"].isin(contiguous_us_states)].copy().to_crs(WORKING_CRS)
states["geometry"] = states.geometry.apply(keep_biggest_polygon)

joined = gpd.sjoin(herd, states[["name", "geometry"]].rename(columns={"name": "_state_name"}), how="left", predicate="intersects")
affected_names = sorted(joined["_state_name"].dropna().unique()) or fallback_affected_states
affected = states[states["name"].isin(affected_names)].copy()

grid = make_grid(herd.total_bounds)
nearest = gpd.sjoin_nearest(herd, grid, how="left", distance_col="dist")
grid_pop = nearest.groupby("index_right")["count"].sum()

max_radius = grid_spacing * max_dot_radius_factor
sqrt_max_pop = np.sqrt(grid_pop.max())

cutouts = []
for idx, pop in grid_pop.items():
    center = grid.iloc[int(idx)].geometry
    pop_weight = np.sqrt(pop) / sqrt_max_pop
    radius = (pop_weight * max_radius) * 0.65 + (max_radius * 0.35)
    cutouts.append(center.buffer(radius, resolution=48))

cutout_gdf = gpd.GeoDataFrame(geometry=cutouts, crs=WORKING_CRS)
plot_bounds = expand_bounds(states.total_bounds)
dash_gdf = make_real_dashes(list(affected.geometry), plot_bounds)

map_units_per_inch = (plot_bounds[2] - plot_bounds[0]) / PAGE_WIDTH_IN
dot_label_margin = LABEL_DOT_MARGIN_IN * map_units_per_inch
dot_avoid_geom = unary_union(cutout_gdf.geometry).buffer(dot_label_margin)

#Draw Map Function
def draw_map(save_path, save_png=True):
    fig = plt.figure(figsize=(PAGE_WIDTH_IN, PAGE_HEIGHT_IN), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.set_xlim(plot_bounds[0], plot_bounds[2])
    ax.set_ylim(plot_bounds[1], plot_bounds[3])
    ax.set_axis_off()

    #Base State Boundaries
    state_line_width = STATE_BORDER_WIDTH if show_state_borders else 0.0
    states.boundary.plot(ax=ax, color=MAP_GRAY, linewidth=state_line_width, zorder=1)

    #Population Dots
    cutout_gdf.plot(ax=ax, facecolor="none", edgecolor=DOT_BORDER_COLOR, linewidth=DOT_BORDER_WIDTH, zorder=5)

    #Affected States Dashed Borders
    for geom in dash_gdf.geometry:
        draw_line(ax, geom, AFFECTED_RED, DASH_LINE_WIDTH, zorder=10)

    #State Name Labels
    if show_state_labels:
        for _, row in states.iterrows():
            avoid = dot_avoid_geom if row["name"] in affected_names else None
            draw_state_label(ax, row.geometry, row["name"], plot_bounds, avoid_geom=avoid)

    fig.savefig(save_path, format="svg", transparent=False, bbox_inches=None, pad_inches=0)
    if save_png:
        fig.savefig(output_preview_png, format="png", dpi=300, transparent=False, bbox_inches=None, pad_inches=0)
    plt.close(fig)

draw_map(output_svg, save_png=True)
print("Map generated successfully!")