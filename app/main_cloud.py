import streamlit as st
from streamlit_folium import st_folium
import folium
from pathlib import Path

st.set_page_config(
    page_title="MineRoverX",
    initial_sidebar_state="expanded",
    layout="wide",
    
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# took from prepare_overlays.py ---> have to check this on Tuesday
DEM_BOUNDS = [
    [22.000138888883857, 84.99986111114623], 
    [22.500138888883924, 85.4998611111463],  
]

FLOW_PNG = DATA_DIR / "bolani_flowacc_overlay.png"
SLOPE_PNG = DATA_DIR / "bolani_slope_overlay.png"

# ───── Sidebar ─────
with st.sidebar:
    st.markdown("## MineRoverX")
    st.markdown("Test Terrain Intelligence PoC (Bolani)")

    basemap_choice = st.selectbox(
        "Basemap",
        [
            "ESRI Satellite",
            "Google Satellite",
            
        ],
        index=0,
    )

    show_flowacc = st.checkbox("Show Flow Accumulation / Drainage", value=True)
    show_slope = st.checkbox("Show Slope / Terrain Gradient", value=False)

st.markdown("### MineRoverX PoC : Terrain Intelligence Dashboard")

st.markdown(
    """
Using NASA SRTM satellite data

"""
)


st.markdown("---")

tab_map, tab_about = st.tabs(["Map View", "Home"])


with tab_map:
    st.markdown("#### Terrain Map (Bolani region)")

    # pick basemap tiles
    if basemap_choice == "ESRI Satellite":
        tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attr = "Esri World Imagery"
    else:
        tiles = "http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        attr = "Google Satellite"
    

    m = folium.Map(tiles=None)
    folium.TileLayer(tiles=tiles, attr=attr, name=basemap_choice).add_to(m)

    
    m.fit_bounds(DEM_BOUNDS)

    
    if show_flowacc and FLOW_PNG.exists():
        folium.raster_layers.ImageOverlay(
            name="Flow Accumulation",
            image=str(FLOW_PNG),
            bounds=DEM_BOUNDS,
            opacity=1.0,
            zindex=3,
        ).add_to(m)

    
    if show_slope and SLOPE_PNG.exists():
        folium.raster_layers.ImageOverlay(
            name="Slope / Gradient",
            image=str(SLOPE_PNG),
            bounds=DEM_BOUNDS,
            opacity=1.0,
            zindex=4,
        ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(m, width="100%", height=500)

