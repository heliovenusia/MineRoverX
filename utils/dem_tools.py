import rasterio
import numpy as np
import richdem as rd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_dem(dem_name: str = "bolani_dem.tif") -> tuple:
    dem_path = DATA_DIR / dem_name
    if not dem_path.exists():
        raise FileNotFoundError(f"DEM not found at {dem_path}")
    
    ds = rasterio.open(dem_path)
    arr = ds.read(1).astype("float32")
    # Optional: mask no-data
    arr[arr == ds.nodata] = np.nan
    return ds, arr

def compute_flow_accumulation(dem_name: str = "bolani_dem.tif", cache: bool = True):
    
    dem_path = DATA_DIR / dem_name
    if not dem_path.exists():
        raise FileNotFoundError(f"DEM not found at {dem_path}")
    
    # Cached output path
    fa_tif = DATA_DIR / "bolani_flowacc.tif"

    if cache and fa_tif.exists():
        with rasterio.open(fa_tif) as src:
            fa_arr = src.read(1).astype("float32")
            profile = src.profile
        return fa_arr, profile

    dem_rd = rd.LoadGDAL(str(dem_path))
    filled = rd.FillDepressions(dem_rd, in_place=False)
    flowdir = rd.FlowDirD8(filled)
    flowacc = rd.FlowAccumulation(flowdir, method='D8')

    fa_arr = np.array(flowacc, dtype="float32")

    with rasterio.open(dem_path) as src:
        profile = src.profile
    profile.update(dtype="float32", count=1, nodata=np.nan)

    with rasterio.open(fa_tif, "w", **profile) as dst:
        dst.write(fa_arr, 1)

    return fa_arr, profile

def normalize_for_overlay(arr: np.ndarray, clip_percent: float = 99.0) -> np.ndarray:
    
    arr = arr.copy()
    mask = np.isfinite(arr)
    if not np.any(mask):
        return np.zeros_like(arr, dtype="uint8")

    vals = arr[mask]
    upper = np.percentile(vals, clip_percent)
    lower = np.percentile(vals, 1.0)

    arr[~mask] = lower
    arr = np.clip(arr, lower, upper)
    arr = (arr - lower) / (upper - lower + 1e-6)
    img = (arr * 255).astype("uint8")
    return img


import matplotlib.pyplot as plt

def save_flowacc_overlay_png(
    png_name: str = "bolani_flowacc_overlay.png",
    cmap: str = "Blues",
    alpha: float = 0.6,
) -> tuple:
    
    fa_arr, profile = compute_flow_accumulation()
    img = normalize_for_overlay(fa_arr)

   
    cmap_obj = plt.get_cmap(cmap)
    rgba = cmap_obj(img)  
    rgba[..., 3] = alpha  

    png_path = DATA_DIR / png_name

    
    plt.imsave(png_path, rgba)

   
    transform = profile["transform"]
    height, width = fa_arr.shape

    west = transform.c
    north = transform.f
    east = west + transform.a * width
    south = north + transform.e * height  

    bounds = [[south, west], [north, east]]
    return png_path, bounds

