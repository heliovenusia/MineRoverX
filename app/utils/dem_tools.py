from pathlib import Path
import numpy as np
import rasterio
import richdem as rd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def get_dem_path(name: str = "bolani_dem.tif") -> Path:
    
    dem_path = DATA_DIR / name
    if not dem_path.exists():
        raise FileNotFoundError(f"DEM not found at {dem_path}")
    return dem_path


def get_dem_bounds(dem_path: Path | None = None):
   
    if dem_path is None:
        dem_path = get_dem_path()

    with rasterio.open(dem_path) as src:
        b = src.bounds

    return [[b.bottom, b.left], [b.top, b.right]]


def load_dem_array(dem_path: Path | None = None):
    
    if dem_path is None:
        dem_path = get_dem_path()

    with rasterio.open(dem_path) as src:
        arr = src.read(1).astype("float32")
        profile = src.profile

    nodata = profile.get("nodata", None)
    if nodata is not None:
        arr[arr == nodata] = np.nan

    return arr, profile



def normalize(arr: np.ndarray) -> np.ndarray:
    arr = arr.astype("float32")
    # Ignore negative & NaN
    arr = np.where(np.isfinite(arr), arr, np.nan)
    arr[arr < 0] = 0
    minv = np.nanmin(arr)
    maxv = np.nanmax(arr)
    if maxv - minv == 0:
        return np.zeros_like(arr)
    return (arr - minv) / (maxv - minv)


def to_uint8(arr: np.ndarray) -> np.ndarray:
    norm = normalize(arr)
    return (norm * 255).astype("uint8")



def compute_flowacc(dem_path: Path | None = None):
    
    if dem_path is None:
        dem_path = get_dem_path()

    dem_rd = rd.LoadGDAL(str(dem_path))

    # Fill depressions
    filled = rd.FillDepressions(dem_rd, in_place=False)

    # Flow accumulation directly from filled DEM
    fa = rd.FlowAccumulation(filled, method="D8")

    fa_arr = np.array(fa, dtype="float32")

    with rasterio.open(dem_path) as src:
        profile = src.profile
    profile.update(dtype="float32", count=1, nodata=np.nan)

    return fa_arr, profile


def save_flowacc_overlay_png(
    dem_path: Path | None = None,
    png_name: str = "bolani_flowacc_overlay.png",
    cmap: str = "Blues",
    alpha: float = 0.85,
):
    
    if dem_path is None:
        dem_path = get_dem_path()

    fa_arr, profile = compute_flowacc(dem_path)

    # log scale to spread small values
    fa_vis = np.log1p(fa_arr)
    mask_valid = np.isfinite(fa_vis)
    if not np.any(mask_valid):
        raise ValueError("Flow accumulation array is empty or invalid.")

    # clip between ~60th and 99.5th percentile to emphasize channels
    lo = np.nanpercentile(fa_vis[mask_valid], 60)
    hi = np.nanpercentile(fa_vis[mask_valid], 99.5)
    if hi <= lo:
        hi = lo + 1e-3

    fa_clipped = np.clip(fa_vis, lo, hi)
    fa_norm = (fa_clipped - lo) / (hi - lo)
    fa_norm[~mask_valid] = 0.0

    # Convert to 0–255 image
    img_u8 = (fa_norm * 255).astype("uint8")

    # Apply colormap → RGBA
    cmap_obj = plt.get_cmap(cmap)
    rgba = cmap_obj(img_u8)  # (H, W, 4) in [0, 1]

    # Per-pixel alpha: only stronger flows visible
    alpha_arr = np.zeros_like(fa_norm, dtype="float32")
    alpha_arr[fa_norm > 0.25] = alpha    # moderate flow
    alpha_arr[fa_norm > 0.5] = alpha     # stronger flow
    rgba[..., 3] = alpha_arr

    png_path = DATA_DIR / png_name
    plt.imsave(png_path, rgba)

    bounds = get_dem_bounds(dem_path)
    return png_path, bounds




def compute_slope(dem_path: Path | None = None):
    
    if dem_path is None:
        dem_path = get_dem_path()

    dem_rd = rd.LoadGDAL(str(dem_path))
    slope = rd.TerrainAttribute(dem_rd, attrib="slope_degrees")
    slope_arr = np.array(slope, dtype="float32")

    with rasterio.open(dem_path) as src:
        profile = src.profile
    profile.update(dtype="float32", count=1, nodata=np.nan)

    return slope_arr, profile


def save_slope_overlay_png(
    dem_path: Path | None = None,
    png_name: str = "bolani_slope_overlay.png",
    cmap: str = "RdYlGn_r",
    alpha: float = 0.75,
):
    
    if dem_path is None:
        dem_path = get_dem_path()

    slope_arr, profile = compute_slope(dem_path)

    mask_valid = np.isfinite(slope_arr)
    if not np.any(mask_valid):
        raise ValueError("Slope array is empty or invalid.")

    # Clip slope to reasonable engineering range
    lo = np.nanpercentile(slope_arr[mask_valid], 2)
    hi = np.nanpercentile(slope_arr[mask_valid], 98)
    if hi <= lo:
        hi = lo + 1e-3

    slope_clipped = np.clip(slope_arr, lo, hi)
    slope_norm = (slope_clipped - lo) / (hi - lo)
    slope_norm[~mask_valid] = 0.0

    img_u8 = (slope_norm * 255).astype("uint8")

    cmap_obj = plt.get_cmap(cmap)
    rgba = cmap_obj(img_u8)

    # Per-pixel alpha: hide nearly-flat zones
    alpha_arr = np.zeros_like(slope_norm, dtype="float32")
    alpha_arr[slope_norm > 0.2] = alpha       # mild slopes
    alpha_arr[slope_norm > 0.6] = alpha       # steeper – same alpha for now
    rgba[..., 3] = alpha_arr

    png_path = DATA_DIR / png_name
    plt.imsave(png_path, rgba)

    bounds = get_dem_bounds(dem_path)
    return png_path, bounds
