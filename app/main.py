import streamlit as st
from streamlit_folium import st_folium
import folium
from pathlib import Path
import os

from utils.dem_tools import save_flowacc_overlay_png, DATA_DIR


st.set_page_config(
    page_title="MineRoverX",
    page_icon="⛏️",
    layout="wide",  
)


with st.sidebar:
    st.markdown("## MineRoverX")
    st.markdown("Terrain Intelligence for SAIL Mines - Test PoC")

    st.markdown("### View Settings")
    basemap_choice = st.selectbox(
        "Basemap",
        ["OpenStreetMap", "CartoDB Positron", "Stamen Terrain"],
        index=0,
    )
    show_flowacc = st.checkbox("Show Flow Accumulation / Drainage", value=False)
  

st.markdown("### MineRoverX : Terrain Intelligence Dashboard")

st.markdown(
    """
This is the **initial skeleton** of the MineRoverX dashboard.  
Right now it shows a dummy map; in later steps we'll add:

- Flow accumulation / drainage
- Haul-road gradient
"""
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Mine", "Bolani", "locked")
col2.metric("DEM Source", "TBD", "-")
col3.metric("Risk Hotspots", "0", "to be computed")
col4.metric("Version", "1.0")

st.markdown("---")

tab_map, tab_about = st.tabs(["Map View", "About MineRoverX"])

with tab_map:
    st.markdown("#### Terrain Map (Bolani region – DEM-based)")

   
    center_lat, center_lon = 22.1, 85.3

    if basemap_choice == "OpenStreetMap":
        tiles = "OpenStreetMap"
    elif basemap_choice == "CartoDB Positron":
        tiles = "CartoDB positron"
    else:
        tiles = "Stamen Terrain"

    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles=tiles)

   
    folium.Marker(
        location=[center_lat, center_lon],
        popup="Bolani region (approx)",
        tooltip="Bolani (approx)",
    ).add_to(m)

    
    dem_path = DATA_DIR / "bolani_dem.tif"
    if show_flowacc:
        if dem_path.exists():
            try:
                png_path, bounds = save_flowacc_overlay_png()
                folium.raster_layers.ImageOverlay(
                    name="Flow Accumulation",
                    image=str(png_path),
                    bounds=bounds,
                    opacity=1.0,
                    interactive=False,
                    cross_origin=False,
                    zindex=3,
                ).add_to(m)
                folium.LayerControl().add_to(m)
            except Exception as e:
                st.error(f"Error creating flow accumulation overlay: {e}")
        else:
            st.warning("DEM file 'data/bolani_dem.tif' not found. Flow overlay disabled.")

    st_folium(m, width="100%", height=500)

