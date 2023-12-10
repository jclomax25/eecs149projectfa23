"""
test_fire_modely.py

assume peripherals provide values
simulate the connection between reads and the model
call on functions to produce a final value

"""

from read_tif_file import *
from constants import *


POINT_USE = True

if POINT_USE:
    # gen single point 30m x 30m bounding box
    master_point = CORY_TEST_POINT
    master_bounds = create_bounding_box(master_point[0], master_point[1])
else:
    # switch on bound input for reading
    master_bounds = BERKELEY_BOUNDS # TESTING_BOUNDS

lon_start = master_bounds[0]
lat_start = master_bounds[1]
lon_stop = master_bounds[2]
lat_stop = master_bounds[3]

# test prototype transform 
pixelx, pixely = image_latlon_pxpy(lat_start, lon_start, FORTY_FUEL_MODELS_TIF, CRS_FORM)
print(pixelx, pixely)

# read from tif e.g. FORTY_FUEL_MODELS_TIF
raster_read = read_tif(FORTY_FUEL_MODELS_TIF,
                       lon_start,
                       lon_stop,
                       lat_start,
                       lat_stop,
                       CRS_FORM)

print(raster_read)

# print unique vals for F40 extraction
all_unique = []
for sub_list in raster_read:
    setit = set(sub_list)
    setit = list(setit)
    for item in setit:
        if item not in all_unique:
            all_unique.append(item)

print(all_unique)
print("Done - Debug close")
