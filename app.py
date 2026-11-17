import os
import subprocess
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="Computational Pipeline",
    page_icon="🐴",
    layout="centered",
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "Output"
SVG_FILENAME = "Screen_Ready_Horse_Lamp_12x18.svg"
PNG_FILENAME = "Screen_Ready_Horse_Lamp_12x18_preview.png"

svg_path = OUTPUT_DIR / SVG_FILENAME
png_path = OUTPUT_DIR / PNG_FILENAME
script_path = BASE_DIR / "clusterStates_dots.py"

# Dialog Pop-Ups
@st.dialog("How the App works")
def show_info_dialog():
    st.write(
        "This pipeline automates the Data-to-Physicalization Workflow across four main stages:\n\n"
        "1. **Data Ingestion:** Ingests the 2017 Bureau of Land Management (BLM) dataset.\n"
        "2. **Data Cleaning:** Filters missing values and standardizes attributes.\n"
        "3. **Spatial Merging:** Joins tabular population data with regional boundaries.\n"
        "4. **Cartographic Mapping:** Renders proportional population dot grids and US maps."
    )

@st.dialog("About This Application")
def show_about_dialog():
    st.write(
        "**3D Data Physicalization Lamp Pipeline**\n\n"
        "Developed as part of a Bachelor thesis project in Creative Computing.\n\n"
        "The app shows the computational pipeline for the translation of complex geospatial population datasets into a 2D map of the United States, showing the Wild Horse and Burro Population in North America."
    )

# Header
header_col1, header_col2, header_col3 = st.columns([6, 1, 1])
with header_col1:
    st.title("3D Data Physicalization Lamp - Pipeline")
with header_col2:
    if st.button("ℹ️ Info", help="How the App works"):
        show_info_dialog()
with header_col3:
    if st.button("About", help="Project Background"):
        show_about_dialog()


# SIDEBAR CONTROLS
st.sidebar.header("Map Configuration")

color_palette = st.sidebar.selectbox(
    "Map Color Palette", ["Viridis (Density)", "Plasma", "Magma"]
)
canvas_size = st.sidebar.selectbox(
    "Export / Canvas Format",
    ["18x12 Lamp Artboard", "A4 Landscape (11.7 x 8.27 in)", "1080p HD (16 x 9 in)"]
)
dot_scale = st.sidebar.slider(
    "Population Dot Size Scale", min_value=0.5, max_value=2.0, value=1.0, step=0.1
)

st.sidebar.divider()
include_state_boundaries = st.sidebar.checkbox("Render US State Boundaries", value=True)
include_state_labels = st.sidebar.checkbox("Show State Names", value=True)

# Clean parameters for backend script
palette_choice = color_palette.split()[0].lower()

# Automatically execute pipeline whenever any sidebar widget changes
with st.spinner("Updating cartographic map..."):
    try:
        subprocess.run(
            [
                "python",
                str(script_path),
                palette_choice,
                str(include_state_boundaries),
                str(include_state_labels),
                canvas_size,
                str(dot_scale)
            ],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        st.error(f"Pipeline execution failed: {e.stderr}")


# MAIN INTERFACE & OUTPUT SECTION
st.success("Map updated successfully!")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Palette", value=color_palette.split()[0])
with col2:
    st.metric(label="Canvas", value=canvas_size.split()[0])
with col3:
    st.metric(label="State Labels", value="Visible" if include_state_labels else "Hidden")

st.divider()

st.subheader("Generated 2D Map Output")

# Render live preview
if os.path.exists(png_path):
    st.image(str(png_path), caption="Generated Cartographic 2D Map", width="stretch")
elif os.path.exists(svg_path):
    st.image(str(svg_path), caption="Generated Cartographic 2D Map", width="stretch")
else:
    st.info("Adjust settings in the sidebar to generate the map preview.")

# Download binary files
svg_data = b""
png_data = b""

if os.path.exists(svg_path):
    with open(svg_path, "rb") as f:
        svg_data = f.read()

if os.path.exists(png_path):
    with open(png_path, "rb") as f:
        png_data = f.read()

dl_col1, dl_col2 = st.columns(2)
with dl_col1:
    st.download_button(
        label="Download Map (.SVG)",
        data=svg_data,
        file_name=SVG_FILENAME,
        mime="image/svg+xml",
        width="stretch"
    )
with dl_col2:
    st.download_button(
        label="Download Map (.PNG)",
        data=png_data,
        file_name=PNG_FILENAME,
        mime="image/png",
        width="stretch"
    )