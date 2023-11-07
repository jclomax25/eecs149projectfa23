"""
preprocess_static_raster

this script is to run for all stored microSD raster datasets
raster must be converted to a friendly non-GIS library form

"""

import rasterio
import numpy as np

# set path to local file
raster_path = "your_raster.tif"
csv_name = "raster_data.csv"

# open raster
with rasterio.open(raster_path) as src:
    raster_array = src.read(1)  # 1 == firs band read

# save arr as csv file 
np.savetxt(csv_name, raster_array, delimiter=",")

# sample read - NEEDS TO FUNCTION IN MICROPY
with open(csv_name, "r") as file:
    lines = file.readlines()

# parse CSV data into a 2D list
raster_data = [list(map(float, line.strip().split(","))) for line in lines]

# access raster values by coordinates (e.g., row and column)
row = 10
col = 20
value = raster_data[row][col]

# TODO additional preprocessing for rasters e.g. CRS adjustments, grid/arr projections