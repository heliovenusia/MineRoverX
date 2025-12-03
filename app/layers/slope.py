def compute_slope(dem):
    import richdem as rd
    dem_rd = rd.rdarray(dem, no_data=-9999)
    slope = rd.TerrainAttribute(dem_rd, attrib='slope_degrees')
    return slope
