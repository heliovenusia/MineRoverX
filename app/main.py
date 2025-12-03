import streamlit as st
from streamlit_folium import st_folium
import folium

from utils.dem_tools import (
    DATA_DIR,
    get_dem_bounds,
    save_flowacc_overlay_png,
    save_slope_overlay_png,
)


st.set_page_config(
    page_title="MineRoverX",
    
    layout="wide",
    
)


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


tab_map, tab_home = st.tabs(["Map View","Home"])

with tab_map:
    st.markdown("#### Terrain Map (Bolani region – DEM-based overlays)")

    dem_path = DATA_DIR / "bolani_dem.tif"

    # Decide basemap tiles
    if basemap_choice == "ESRI Satellite":
        tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attr = "Esri World Imagery"
    else:
        tiles = "http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        attr = "Google Satellite"
    

    if dem_path.exists():
        bounds = get_dem_bounds(dem_path)  

        
        m = folium.Map(tiles=None)
        folium.TileLayer(
            tiles=tiles,
            attr=attr,
            name=basemap_choice,
        ).add_to(m)

       
        m.fit_bounds(bounds)

    else:
        st.error("DEM file 'data/bolani_dem.tif' not found.")
        bounds = None
        
        center_lat, center_lon = 22.1, 85.3
        m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles=tiles)

    
    folium.Marker(
        location=[22.1, 85.3],
        popup="Bolani region (approximate)",
        tooltip="Bolani (approximate)",
    ).add_to(m)

    
    if show_flowacc and dem_path.exists():
        try:
            fa_png, fa_bounds = save_flowacc_overlay_png(dem_path)
            folium.raster_layers.ImageOverlay(
                name="Flow Accumulation",
                image=str(fa_png),
                bounds=fa_bounds,
                opacity=1.0,  # alpha is encoded in PNG
                zindex=3,
            ).add_to(m)
        except Exception as e:
            st.error(f"Error generating flow accumulation overlay: {e}")

    
    if show_slope and dem_path.exists():
        try:
            slope_png, slope_bounds = save_slope_overlay_png(dem_path)
            folium.raster_layers.ImageOverlay(
                name="Slope / Gradient",
                image=str(slope_png),
                bounds=slope_bounds,
                opacity=1.0,  # alpha is encoded in PNG
                zindex=4,
            ).add_to(m)
        except Exception as e:
            st.error(f"Error generating slope overlay: {e}")

   
    folium.LayerControl().add_to(m)

    
    st_folium(m, width="100%", height=500)


