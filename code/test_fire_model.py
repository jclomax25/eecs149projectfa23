"""
test_fire_modely.py

assume peripherals provide values
simulate the connection between reads and the model
call on functions to produce a final value

"""
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from read_tif_file import *
from constants import *
from fire_model import *


# PERIPHERAL INPUTS
POINT_USE = True
REV_HUMIDITY = 50 # percent form assumed
DRY_BULB = 60 # dry bulb in Farenheit!
WIND_SPEED = 5 # MPH

if POINT_USE:
    # gen single point 30m x 30m bounding box
    master_point = SINGLE_GRASS_POINT # SINGLE_TESTING_POINT
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
# print(pixelx, pixely)

# read from tif e.g. FORTY_FUEL_MODELS_TIF
raster_read = read_tif(FORTY_FUEL_MODELS_TIF,
                       lon_start,
                       lon_stop,
                       lat_start,
                       lat_stop,
                       CRS_FORTY_FUEL)

# print(raster_read)

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

# median of collection
slope_val = statistics.median(slope_unq)

# aspect access
aspect_read = read_tif(ASPECT_TIF,
                       lon_start,
                       lon_stop,
                       lat_start,
                       lat_stop,
                       CRS_FORTY_FUEL)

print("all unique aspect")
print(find_unique(aspect_read))

print("apply and fetch aspects")
aspects = []
for deg in find_unique(aspect_read):
    aspects.append(aspect_to_direction(deg))
# print(aspects)

# process vals and prep for ros input
cur_fuel_type = pick_fuel_type(unique_classification)
fuel_load = sum_fuel_load(cur_fuel_type, FORTY_PROPERTIES_CSV)
fuel_sav = sav_average(cur_fuel_type, FORTY_PROPERTIES_CSV)
fuel_depth = get_fuel_depth(cur_fuel_type, FORTY_PROPERTIES_CSV)

print('fuel load')
print(fuel_load)

print('fuel sav')
print(fuel_sav)

# try: apply relative humidity search - feed dry bulb + relative humditiy + paths to csv
fuel_moist_calc = derive_fuel_moisture(REF_TABLE_A, 
                                       REF_CORRECTION_DEC, 
                                       DRY_BULB, 
                                       REV_HUMIDITY, 
                                       'S', 4)

print('finalized moisture calc')
print(fuel_moist_calc)

print('call ros model')
ros_result = get_simple_fire_spread(fuel_load, fuel_depth, WIND_SPEED, slope_val, fuel_moist_calc / 100, fuel_sav)

print("Done - ROS print:")
print(ros_result)

print("all roth args")
print(fuel_load, fuel_depth, WIND_SPEED, slope_val, fuel_moist_calc, fuel_sav)
