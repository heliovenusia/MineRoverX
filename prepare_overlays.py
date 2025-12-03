from app.utils.dem_tools import (
    save_flowacc_overlay_png,
    save_slope_overlay_png,
    get_dem_bounds,
    get_dem_path,
)

if __name__ == "__main__":
    dem_path = get_dem_path("bolani_dem.tif")

    fa_png, fa_bounds = save_flowacc_overlay_png(dem_path)
    slope_png, slope_bounds = save_slope_overlay_png(dem_path)

    print("Flow PNG:", fa_png)
    print("Slope PNG:", slope_png)
    print("Bounds:", fa_bounds)
