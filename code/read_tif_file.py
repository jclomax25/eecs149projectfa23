"""
read_tif_file.py
given a dataset path, get the data from path and read in tif
convert lat/lon to make request on tif area

"""

import math
import csv
import rasterio as rio
from osgeo import gdal, osr
from pyproj import Proj, transform
from constants import *

def read_tif(path: str, 
            lon_start:int,
            lon_stop: int, 
            lat_start:int,
            lat_stop: int,
            crs:str):

    ds = gdal.Open(path)
    geotransform = ds.GetGeoTransform()

    # spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    
    # TODO: reduce overhead by chaning rio vs GDAL reading
    x_start, y_start = image_latlon_pxpy(lat_start, lon_start, path, crs)
    x_stop, y_stop = image_latlon_pxpy(lat_stop, lon_stop, path, crs)

    # due to crs issues, enhance pixel sampling zone
    if x_start == x_stop:
        x_stop += 1
    if y_start == y_stop:
        y_stop += 1

    raster_subset = ds.ReadAsArray(x_start,
                                   y_start, 
                                   x_stop - x_start, 
                                   y_stop - y_start)
    
    print(raster_subset)

    return raster_subset

def image_latlon_pxpy(latitude, longitude, path, crs_form):
    """ apply lat lon to proper pixel x and y form, use known projections
        NOTE needs casting which may impact accuracy
    """
    dataset = rio.open(path, crs=crs_form)
    coords = transform(Proj(init='epsg:4326'), Proj(init=crs_form), longitude, latitude)
    px, py = coords[0], coords[1]
    # print(px,py)
    px_pc = (px - dataset.bounds.left) / (dataset.bounds.right - dataset.bounds.left)
    py_pc = (dataset.bounds.top - py) / (dataset.bounds.top - dataset.bounds.bottom)
    
    # return (px_pc*dataset.width, py_pc*dataset.height)
    # print(px_pc*dataset.width)
    # print(py_pc*dataset.height)

    return (int(px_pc*dataset.width), int(py_pc*dataset.height))


def create_bounding_box(lat, lon):
    """ with a single lat lon, return an approx 30m x 30m bbox
        Length in km of 1° of latitude = always 111.32 km == 111320 m  / 30 ~= 3711 
        1 deg / 3711 ~= 0.00026946914 vds 0.00015 standard recommended 
        Length in km of 1° of longitude = 40075 km * cos( latitude ) / 360
    """

    # approximate distance covered by 0.0003 degrees at the equator, ~30 m
    delta =  0.00015 # 0.00026946914 # 0.00015
    
    delta_lat = delta
    delta_lon = delta / abs(math.cos(math.radians(lat)))  # correct for dist variation

    upper_left_lat = lat + delta_lat
    upper_left_lon = lon - delta_lon
    lower_right_lat = lat - delta_lat
    lower_right_lon = lon + delta_lon
    
    # mapping distorted
    return [lower_right_lat, lower_right_lon, upper_left_lat, upper_left_lon]

def find_FBFM40(csv_file: str, search_value: int):
    """ identify corresponding fuel model from tif array vals
    """
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['VALUE']) == search_value:
                return row['FBFM40']

    return None

def find_unique(input_arr):
    """ helper to identify unique vals
    """
    all_unique = []
    for sub_list in input_arr:
        setit = set(sub_list)
        setit = list(setit)
        for item in setit:
            if item not in all_unique:
                all_unique.append(item)
    
    return all_unique


# def pixel_to_geo(x, y, geotransform):
#     """Apply geotransform to get proper lat/lon mapping onto array."""
#     lon = geotransform[0] + x * geotransform[1] + y * geotransform[2]
#     lat = geotransform[3] + x * geotransform[4] + y * geotransform[5]
#     return lon, lat

# def geo_to_pixel(lon, lat, geotransform):
#     """Apply inverse geotransform to get pixel coordinates from lat/lon."""
#     det = geotransform[1] * geotransform[5] - geotransform[2] * geotransform[4]

#     x = int((geotransform[1] * (lon - geotransform[0]) + geotransform[2] * (lat - geotransform[3])) / det)
#     y = int((geotransform[4] * (lon - geotransform[0]) + geotransform[5] * (lat - geotransform[3])) / det)
    
#     return x, y
