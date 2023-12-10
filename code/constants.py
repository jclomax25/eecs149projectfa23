"""
constants.py
define constants global for entire FRAT project

"""
# path to files
LANDFIRE_DIR = "/Users/katrinasharonin/Downloads/landfire_FW8smOZ84csjRPi1bY8w"
FORTY_FUEL_MODELS_TIF = "/Users/katrinasharonin/Downloads/landfire_FW8smOZ84csjRPi1bY8w/LF2022_FBFM40_230_CONUS/LC22_F40_230.tif"

# bounding box defined as x - longitude, y - latitue
# 37.881763 (lat), -122.246595 (long) (upper left)
# 37.864478, -122.222191 (lower right)
# lon lat lon lat 
INPUT_BOUNDS = [-122.246595, 37.881763, -122.222191, 37.864478]

# TODO
# raster value mappings

# agreed CRS
crs = "EPSG:4326"