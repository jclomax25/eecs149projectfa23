"""
constants.py
define constants global for entire FRAT project

"""
# STATIC INPUTS 
# 40 fuel models
FORTY_FUEL_MODELS_TIF = "/home/johnlomax/Desktop/eecs149projectfa23/static_data/landfire_FW8smOZ84csjRPi1bY8w/LF2022_FBFM40_230_CONUS/LC22_F40_230.tif"
FORTY_FUEL_MODELS_ATTRIBUTES_CSV = "/home/johnlomax/Desktop/eecs149projectfa23/static_data/LF22_F40_230.csv"
FORTY_PROPERTIES_CSV = "/home/johnlomax/Desktop/eecs149projectfa23/static_data/40_fuel_mapping_data.csv"

# slope
SLOPE_TIF = "/home/johnlomax/Desktop/eecs149projectfa23/static_data/LF2020_SlpD_220_CONUS/LC20_SlpD_220.tif"

# aspect
ASPECT_TIF = "/home/johnlomax/Desktop/eecs149projectfa23/static_data/LF2020_Asp_220_CONUS/LC20_Asp_220.tif"

# fine fuel moisture
REF_TABLE_A = "/home/johnlomax/Desktop/eecs149projectfa23/static_data/TABLE_A_REFERENCE_FUEL_MOISTURE.csv"
REF_CORRECTION_DEC = "/home/johnlomax/Desktop/eecs149projectfa23/static_data/TABLE_D_CORRECTIONS_NOV_DEC.csv"

# DYNAMIC INPUTS 
# bounding box defined as x - longitude, y - latitue
INPUT_BOUNDS = [-122.246595, 37.881763, -122.222191, 37.864478]

# berkeley area 
BERKELEY_BOUNDS = [-122.260380, 37.876114, -122.255463, 37.873697]
CORY_TEST_POINT = [-122.257597, 37.875040]
BERKELEY_BBOX_TYPE_RESULTS = [91, 121, 102]
CORY_POINT_TYPE_RESULTS = [91]

# testing area
TESTING_BOUNDS = [-122.326024, 37.877113, -122.305323, 37.866007]
SINGLE_TESTING_POINT = [-122.305323, 37.866007]
SINGLE_GRASS_POINT = [-122.319082, 37.873181]
# extracted 40 fuel model types
TESTING_BBOX_TYPE_RESULTS = [98, 91, 121, 101, 102, 142, 122, 145, 103, 99, 183, 123, 182, 165, 188, 163]
TESTING_POINT_TYPE_RESULTS = [91]


# agreed CRS
CRS_FORTY_FUEL = "epsg:5070"
# CRS_SLOPE = "epsg:4326"