# Horse Lamp Data Pipeline

**Bachelor Thesis**: *Physical Paper Lamps via Data Physicalization and Texture Mapping on 3D Models*  
**Subtitle**: *A Study of Wild Horse and Burro Populations in North America*  
**Author**: Nathalie Vu (CC211040)  
**Institution**: St. Pölten University of Applied Sciences — Bachelor's in Creative Computing  
**Supervisor**: Dr. Hsiang-Yun Wu

---
## Overview

This repository contains the full computational pipeline used to generate a SVG- and PNG-file from U.S. Bureau of Land Management (BLM) Wild Horse and Burro population data. The PNG file was imported as a Blender texture, UV-mapped onto a 3D horse lamp model, unfolded into pieces, printed, laser cut and built as a papercraft lamp for the thesis.

The pipeline transforms two raw government data sources, a population statistics Excel file and a geospatial GDB file, into a population-scaled dot grid map of the contiguous United States. 

Alaska, Hawaii, and U.S. island territories are intentionally excluded: including them would introduce large blank regions between the mainland and non-contiguous landmasses, reducing legibility on the fixed 18×12" artboard.

---

## Input Data

| File                                                    | Source                                                                                                                                                                        | Description                                                                                                                                                                                                                                                  |
|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `BLM-Herd-Area-and-Herd-Management-Area-Statistics.pdf` | [BLM Wild Horse & Burro Program](https://www.blm.gov/programs/wild-horse-and-burro/about/data)                                                                                | Original BLM source document. Herd Area and Herd Management Area statistics by state and individual HMA. Data as of March 1, 2024. Used as the primary source for manually compiling `Population_data.xlsx`.                                                 |
| `Population_data.xlsx`                                  | Manually compiled from the BLM PDF above                                                                                                                                      | 19-sheet Excel workbook: summary table (Sheet 1) + one sheet per state. Columns: State, Horses, Burros, Total, BLM Acres, HMA Acres, High AML. Hand-entered from the BLM PDF.                                                                                |
| `BLM-Wild-Horse-and-Burro-Herd-Area-Polygons.zip`       | [Bureau of Land Management, Geospatial Business Platform](https://gbp-blm-egis.hub.arcgis.com/datasets/BLM-EGIS::blm-natl-wild-horse-and-burro-herd-mgmt-area-polygons/about) | compressed ZIP folder containing the BLM National Herd Area GDB. Extract `data/v101/rangedata_blm_20170519.gdb/` for use in the pipeline. Original source: U.S. Department of Interior, Bureau of Land Management (BLM). Geospatial data as of May 19, 2017. |
| `us-states.geojson`                                     | [Natural Earth / US Census](https://www.census.gov/geographies/mapping-files.html)                                                                                            | U.S. state boundary polygons, used for filtering and rendering.                                                                                                                                                                                              |

### Extracting the BLM GDB
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
The GDB is nested inside the ZIP. Extract it using the following path:
---

## Script Reference

### Step 1 — `cleanPopulation.py`

**Purpose**: Cleans the BLM Excel population statistics file and extracts horse and burro counts per U.S. state.

**Input**:
- `BLM_Wild_Horse_Burro_Stats.xlsx`

**Output**:
- `cleaned_population.csv` — columns: `State`, `Horses`, `Burros`, `Total`

**Notes**: Handles non-standard government spreadsheet formatting (merged headers, mixed data types).

---

### Step 2 — `gdb_reader.py`

**Purpose**: Reads the BLM National Herd Area GDB file, computes polygon centroids, and exports all herd areas as GeoJSON.

**Input**:
- `rangedata_blm_20170519.gdb` (layer: `BLM_National_HA_20170519`)

**Output**:
- `processed_herd_areas.geojson` — herd area polygons with centroids in WGS84 (EPSG:4326)

**Notes**: Centroids are computed in EPSG:3857 (Web Mercator) for geometric accuracy, then reprojected back to EPSG:4326 for storage. Computing centroids in geographic degrees is geometrically incorrect for polygon data. Set the `GDB_PATH` variable at the top of the script to point to `data/v101/rangedata_blm_20170519.gdb/` inside the extracted ZIP.

---

### Step 3 — `mergeHerdData.py` *(canonical)*

**Purpose**: Joins the population statistics CSV with the GDB location data using fuzzy string matching and herd code matching.

**Input**:
- `cleaned_population.csv`
- `processed_herd_areas.geojson`

**Output**:
- `Merged_Herd_Population_Location.csv` — population + centroid coordinates per herd area

**Notes**: Uses Levenshtein distance-based fuzzy matching (fuzzywuzzy) because BLM's two datasets use inconsistent herd area names. Two-pass approach: name similarity match first, herd code fallback second. This is the canonical merge script — use this one, not `mergeDatasets.py`.

---

### Step 3 (alt) — `mergeDatasets.py` *(reference only)*

**Purpose**: Earlier, simpler merge of `processed_herd_areas.geojson` and the cleaned population CSV using exact state name matching.

**Status**: Superseded by `mergeHerdData.py`. Retained for reference and comparison.

---

### Step 4 — `clusterHerds.py` *(exploratory)*

**Purpose**: Applies KMeans clustering (k=10) to herd area centroids on a per-state basis to aggregate overlapping herd locations into representative points.

**Input**:
- `Merged_Herd_Population_Location.csv`

**Output**:
- Per-state clustered centroid plots (matplotlib figures)

**Notes**: Exploratory approach. KMeans was not used in the final texture because it assumes equal-sized clusters, which does not match the uneven geographic distribution of herd areas. See `clusterStates.py` for the HDBSCAN alternative.

---

### Step 4 (alt) — `clusterStates.py` *(exploratory)*

**Purpose**: Applies HDBSCAN density-based clustering (with KMeans fallback for sparse states) to herd centroids, generating per-state GeoJSON and SVG outputs.

**Input**:
- `Merged_Herd_Population_Location.csv`
- `us-states.geojson`

**Output**:
- `clustered_states/` — per-state GeoJSON and SVG files

**Notes**: Exploratory approach. HDBSCAN is more appropriate for geographic herd data than KMeans because it does not assume cluster size uniformity. Neither clustering approach was carried into the final texture design; the dot-grid encoding in `clusterStates_dots.py` was used instead.

---

### Step 5 — `clusterStates_dots.py` *(primary output script)*

**Purpose**: Generates the final population-scaled dot grid map of the contiguous United States as a laser-ready SVG and Blender-compatible PNG.

**Input**:
- `Merged_Herd_Population_Location.csv`
- `us-states.geojson`

**Output**:
- `herd_distribution_cutout_FINAL.svg` — laser-cutting file (black background, white circle cutouts, red dashed state borders)
- `herd_distribution_cutout_FINAL.png` — high-resolution raster for Blender UV mapping
- `A3_Lamp_Texture_for_Blender.jpg` — white background version for alternate use

**Key design parameters**:

| Parameter | Value | Rationale |
|---|---|---|
| Projection | EPSG:5070 (Albers Equal Area Conic) | Preserves area for contiguous US; avoids Mercator distortion |
| Grid spacing | 26,000 m | Balances dot density with legibility at 18×12" |
| Max dot radius | 0.495 × grid spacing | Prevents adjacent dots from overlapping |
| Radius scaling | `r = (√p / √p_max × r_max) × 0.65 + r_max × 0.35` | p = summed population of all herds in that grid cell; square-root compression + minimum size floor |
| Artboard | 18 × 12 inches | A3-landscape, matches laser cutter bed |
| Affected states | AZ, CA, CO, ID, MT, NV, NM, OR, UT, WY | 10 states with documented BLM herd areas |
| Border style | Red dashed, computed as line segments | SVG stroke-dasharray avoided for laser compatibility |
| Labels | Arial Bold, 1.6–8.5pt, collision-checked | Auto-scaled and tested against dot positions |

**Notes**: CRS auto-detection prevents double-reprojection if source data is already in EPSG:5070.

---

### Step 6 — `stateBoundaries.py` *(optional)*

**Purpose**: Exports individual state boundary polygons as GeoJSON, DXF, and SVG for the 10 affected U.S. states.

**Input**:
- `us-states.geojson`

**Output**:
- `state_boundaries/` — per-state GeoJSON, DXF, and SVG files

**Notes**: Used for Blender reference geometry and laser-cutting registration marks. Optional step; not required for the main texture output.

---

### Discarded — `voronoiMap.py` *(documentation only)*

**Purpose**: Attempted Voronoi tessellation approach with spatial repulsion simulation (200 iterations) and symbol-coded population markers (triangle/diamond/square/X by population range).

**Status**: Rejected. At continental U.S. scale, Voronoi cells are unbounded at map edges and extend far beyond U.S. borders, destroying geographic context. See `outputs/US_WildHorse_Voronoi_Projected.jpg` for the rejection evidence figure used in the thesis.

---

## Output Files

| File | Generated by | Description |
|---|---|---|
| `herd_distribution_cutout_FINAL.jpg` | `clusterStates_dots.py` | **Primary Blender texture**: black bg, white circles, red dashed borders |
| `A3_Lamp_Texture_for_Blender.jpg` | `clusterStates_dots.py` | White background version for laser cutting |
| `clusterStateTexture.jpg` | `clusterStates_dots.py` | Full US reference map with all state labels |
| `US_WildHorse_Voronoi_Projected.jpg` | `voronoiMap.py` | Rejected approach — included in thesis as Figure X |
| `Horse_Lamp_Topographic_V52.jpg` | earlier iteration | KDE contour line approach (discarded) |
| `Horse_Lamp_Final_V87.jpg` | earlier iteration | Symbol-coded marker approach (discarded) |

---

## Installation

```bash
# Clone or download this repository
# Then install dependencies:
pip install -r requirements.txt
```

**Windows users**: Install GDAL, Fiona, and GeoPandas via conda before pip to avoid C-extension build errors:

```bash
conda install -c conda-forge geopandas fiona pyproj
pip install -r requirements.txt
```

**Python version**: 3.10 or higher recommended.

---

## Coordinate Reference Systems Used

| CRS | EPSG | Used for |
|---|---|---|
| WGS84 Geographic | 4326 | GeoJSON storage, input data |
| Web Mercator | 3857 | Centroid calculation in `gdb_reader.py` |
| Albers Equal Area Conic (US) | 5070 | Final map projection in `clusterStates_dots.py` |

---

## Data Limitations

- BLM population statistics are from **2017** and do not reflect current herd counts.
- Population figures are sourced at the **herd area level**, not state-level aggregates. Each grid cell accumulates the population of all herd points that snap to it via nearest-neighbour join — so a grid cell near multiple small herds will show a larger dot than a cell near a single large herd of the same total. Two equal-population herds in different states produce identically sized dots. Adjacent herds that fall within the same grid cell's catchment area effectively merge into one larger dot.
- The GDB herd area polygons predate recent BLM land use plan revisions.

---

## License

Code: MIT License.  
BLM data: Public domain (U.S. federal government).  
See individual data source pages for terms of use.