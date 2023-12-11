"""
test_fire_modely.py

assume peripherals provide values
simulate the connection between reads and the model
call on functions to produce a final value

"""

from read_tif_file import *
from constants import *


POINT_USE = False

if POINT_USE:
    # gen single point 30m x 30m bounding box
    master_point = CORY_TEST_POINT
    master_bounds = create_bounding_box(master_point[0], master_point[1])
else:
    # switch on bound input for reading
    master_bounds = TESTING_BOUNDS # BERKELEY_BOUNDS

lon_start = master_bounds[0]
lat_start = master_bounds[1]
lon_stop = master_bounds[2]
lat_stop = master_bounds[3]

# test prototype transform 
pixelx, pixely = image_latlon_pxpy(lat_start, lon_start, FORTY_FUEL_MODELS_TIF, CRS_FORTY_FUEL)
print(pixelx, pixely)

# read from tif e.g. FORTY_FUEL_MODELS_TIF
raster_read = read_tif(FORTY_FUEL_MODELS_TIF,
                       lon_start,
                       lon_stop,
                       lat_start,
                       lat_stop,
                       CRS_FORTY_FUEL)

print(raster_read)

# print unique vals for F40 extraction
forty_unq = find_unique(raster_read)

print("all unique FM40 nums")
print(forty_unq)

# per unique -> run classification
unique_classification = []
for u in forty_unq:
    unique_classification.append(find_FBFM40(FORTY_FUEL_MODELS_ATTRIBUTES_CSV, u))

print("associated fire models")
print(unique_classification)

# excract slope from band 2 
slope_read = read_tif(SLOPE_TIF,
                       lon_start,
                       lon_stop,
                       lat_start,
                       lat_stop,
                       CRS_FORTY_FUEL)

# print(slope_read)
slope_unq = find_unique(slope_read)

print("all unique slope")
print(slope_unq)


print("Done - Debug close")
