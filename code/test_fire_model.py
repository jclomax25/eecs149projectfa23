"""
test_fire_modely.py

assume peripherals provide values
simulate the connection between reads and the model
call on functions to produce a final value

"""

from read_tif_file import *
from constants import *

lon_start = INPUT_BOUNDS[0]
lat_start = INPUT_BOUNDS[1]
lon_stop = INPUT_BOUNDS[2]
lat_stop = INPUT_BOUNDS[3]

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

# call function with inputs

# classify the danger into categories 

# finish