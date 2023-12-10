"""
constants.py
define constants global for entire FRAT project

"""
# path to files
LANDFIRE_DIR = "/Users/katrinasharonin/Downloads/landfire_FW8smOZ84csjRPi1bY8w"
FORTY_FUEL_MODELS_TIF = "/Users/katrinasharonin/Downloads/landfire_FW8smOZ84csjRPi1bY8w/LF2022_FBFM40_230_CONUS/LC22_F40_230.tif"
FORTY_FUEL_MODELS_ATTRIBUTES = "/Users/katrinasharonin/Downloads/LF22_F40_230.csv"

# bounding box defined as x - longitude, y - latitue
# 37.881763 (lat), -122.246595 (long) (upper left)
# 37.864478, -122.222191 (lower right)
# lon lat lon lat 
INPUT_BOUNDS = [-122.246595, 37.881763, -122.222191, 37.864478]

# berkeley area 
BERKELEY_BOUNDS = [-122.260380, 37.876114, -122.255463, 37.873697] 
CORY_TEST_POINT = [-122.257597, 37.875040]
BERKELEY_BBOX_TYPE_RESULTS = [91, 121, 102]
CORY_POINT_TYPE_RESULTS = [91]

# testing area
TESTING_BOUNDS = [-122.326024, 37.877113, -122.305323, 37.866007]
SINGLE_TESTING_POINT = [-122.305323, 37.866007]
# extracted 40 fuel model types
TESTING_BBOX_TYPE_RESULTS = [98, 91, 121, 101, 102, 142, 122, 145, 103, 99, 183, 123, 182, 165, 188, 163]
TESTING_POINT_TYPE_RESULTS = [91]

# TODO
# raster value mappingsv - one time dict generation/json

# agreed CRS
CRS_FORM = "epsg:5070"