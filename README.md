Data Lamp: Visualizing Wild Horse & Burro Populations 🐎 

OVERVIEW

Data Lamp is my bachelor thesis project for my Creative Computing program at the University of Applied Sciences St. Pölten.
The project explores data physicalization through the creation of a papercraft lamp that visualizes geospatial data about Wild Horses and Burros in North America.

The lamp’s horse-shaped design incorporates laser-cut or hand-cut patterns that represent population clusters. These clusters are derived from real geospatial datasets and transformed into a visual texture applied to a 3D model in Blender.

PROJECT GOALS

- Combine data visualization and physical design to communicate environmental and animal-related data in a tangible way.
- Use Python to process, filter, and cluster geospatial datasets of wild horse and burro populations.
- Generate a cluster map for UV mapping and texturing a 3D model in Blender.
- Build 3 different printable 3D Models in Blender
- Fabricate a papercraft lamp based on the 3D model, merging digital and physical representation.

DATA PIPELINE

Input

- Datasets from the Bureau of Land Management (BLM) and related sources on wild horse and burro populations
- Filtering relevant U.S. states (only those with active populations).
- Merging multiple datasets into one unified geospatial dataset.
- Clustering population data to identify density regions using a proximity-based algorithm.

Output

- A cluster map representing merged and scaled population clusters.
- This image is then used as a material texture in Blender for UV mapping onto the 3D horse model.

TOOLS & TECHNOLOGIES  

- Python – Data processing and clustering (Libraries: pandas, geopandas, matplotlib, shapely)
- Blender – 3D modeling and UV mapping
- Pepakura Designer 6 – Unfolding 3D model for papercraft assembly
- Adobe Illustrator / Inkscape – Vector editing and refinement
