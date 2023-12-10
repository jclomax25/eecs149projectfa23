"""
read_tif_file.py
given a dataset path, get the data from path and read in tif
convert lat/lon to make request on tif area

"""

# import tifffile
from osgeo import gdal, osr
from pprint import pprint
from pyproj import Proj, transform
import rasterio as rio
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
    print(px,py)
    px_pc = (px - dataset.bounds.left) / (dataset.bounds.right - dataset.bounds.left)
    py_pc = (dataset.bounds.top - py) / (dataset.bounds.top - dataset.bounds.bottom)
    # return (px_pc*dataset.width, py_pc*dataset.height)
    return (int(px_pc*dataset.width), int(py_pc*dataset.height))

def pixel_to_geo(x, y, geotransform):
    """Apply geotransform to get proper lat/lon mapping onto array."""
    lon = geotransform[0] + x * geotransform[1] + y * geotransform[2]
    lat = geotransform[3] + x * geotransform[4] + y * geotransform[5]
    return lon, lat

def geo_to_pixel(lon, lat, geotransform):
    """Apply inverse geotransform to get pixel coordinates from lat/lon."""
    det = geotransform[1] * geotransform[5] - geotransform[2] * geotransform[4]

    x = int((geotransform[1] * (lon - geotransform[0]) + geotransform[2] * (lat - geotransform[3])) / det)
    y = int((geotransform[4] * (lon - geotransform[0]) + geotransform[5] * (lat - geotransform[3])) / det)
    
    return x, y
