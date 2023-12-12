# fire_main.py method for fire model run

import warnings
import random
warnings.simplefilter(action='ignore', category=FutureWarning)
from read_tif_file import *
from constants import *
from fire_model import *


def main(REV_HUMIDITY, DRY_BULB, WIND_SPEED, LAT_LON_POINT: list):
    """ 
        INPUT:
        REV_HUMIDITY: as a percent e.g. 50 (for 50%)
        DRY_BULB: Fahrenheight temperature
        WIND_SPEED: mph
        LAT_LON_POINT: [lon, latitude]]

        NOTE: EDIT CONSTANTS ACCORDING TO LOCAL SETUP!

        RETURN: 
        ROS VALUE ft / min(float)
        CLASSIFICATION (str)
    """

    assert len(LAT_LON_POINT) == 2, "Single point only, not accepting bounding box"
    master_point = LAT_LON_POINT
    master_bounds = create_bounding_box(master_point[0], master_point[1])

    lon_start = master_bounds[0]
    lat_start = master_bounds[1]
    lon_stop = master_bounds[2]
    lat_stop = master_bounds[3]

    # 40 fuel models
    raster_read = read_tif(FORTY_FUEL_MODELS_TIF,
                       lon_start,
                       lon_stop,
                       lat_start,
                       lat_stop,
                       CRS_FORTY_FUEL)
    
    # unique extraction
    forty_unq = find_unique(raster_read)
    # map to 40 models
    unique_classification = []
    for u in forty_unq:
        unique_classification.append(find_FBFM40(FORTY_FUEL_MODELS_ATTRIBUTES_CSV, u))

    # slope extraction
    slope_read = read_tif(SLOPE_TIF,
                       lon_start,
                       lon_stop,
                       lat_start,
                       lat_stop,
                       CRS_FORTY_FUEL)
    
    slope_unq = find_unique(slope_read)
    slope_val = statistics.median(slope_unq)

    # aspect access
    aspect_read = read_tif(ASPECT_TIF,
                        lon_start,
                        lon_stop,
                        lat_start,
                        lat_stop,
                        CRS_FORTY_FUEL)

    aspects = []
    for deg in find_unique(aspect_read):
        aspects.append(aspect_to_direction(deg))

    # select single aspect or assume worst case South if present, otherwise rand
    if len(aspects) == 1:
        aspect_val = aspects[0]
    elif 'S' in aspects:
        aspect_val = 'S'
    else:
        aspect_val = random.choice(aspects)


    cur_fuel_type = pick_fuel_type(unique_classification)
    fuel_load = sum_fuel_load(cur_fuel_type, FORTY_PROPERTIES_CSV)
    fuel_sav = sav_average(cur_fuel_type, FORTY_PROPERTIES_CSV)
    fuel_depth = get_fuel_depth(cur_fuel_type, FORTY_PROPERTIES_CSV)

    # fuel moisture 
    fuel_moist_calc = derive_fuel_moisture(REF_TABLE_A, 
                                       REF_CORRECTION_DEC, 
                                       DRY_BULB, 
                                       REV_HUMIDITY, 
                                       aspect_val, slope_val)
    
    # ROS ft/min - include tuple with other vals - exclude for now
    ros_result = get_simple_fire_spread(fuel_load, fuel_depth, WIND_SPEED, slope_val, fuel_moist_calc / 100, fuel_sav)
    ros_result = ros_result[0]
    # classification by str
    classification = classify_ros_value(ros_result)

    return [ros_result, classification]
