def compute_flow_acc(dem):
    import richdem as rd
    dem_rd = rd.rdarray(dem, no_data=-9999)
    fd = rd.FlowDirectionD8(dem_rd)
    fa = rd.FlowAccumulation(fd, method='D8')
    return fa
