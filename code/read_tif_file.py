"""
read_tif_file.py
given a dataset path, get the data from path and read in tif
convert lat/lon to make request on tif area

"""

# import tifffile
from osgeo import gdal, osr

def read_tif(path: str, 
            lon_start:int,
            lon_stop: int, 
            lat_start:int,
            lat_stop: int, 
            width:int, 
            height:int):

    ds = gdal.Open(path)
    geotransform = ds.GetGeoTransform()

    # spatial reference
    srs = osr.SpatialReference()
    srs.ImportFromWkt(ds.GetProjection())
    
    x_start, y_start = geo_to_pixel(lon_start, lat_start, geotransform)
    x_stop, y_stop = geo_to_pixel(lon_stop, lat_stop, geotransform)

    raster_subset = ds.ReadAsArray(x_start,
                                   y_start, 
                                   x_stop - x_start, 
                                   y_stop - y_start)
    
    print(raster_subset)

def pixel_to_geo(x, y, geotransform):
    """ apply geotransform to get proper lat / lon mapping
        onto array
    """
    lon = geotransform[0] + x * geotransform[1] + y * geotransform[2]
    lat = geotransform[3] + x * geotransform[4] + y * geotransform[5]
    return lon, lat

def geo_to_pixel(lon, lat, geotransform):
    """ apply inverse geotransform to get pixel coordinates from lat/lon """
    det = geotransform[1] * geotransform[5] - geotransform[2] * geotransform[4]
    
    x = int((geotransform[5] * (lon - geotransform[0]) - geotransform[2] * (lat - geotransform[3])) / det)
    y = int((-geotransform[4] * (lon - geotransform[0]) + geotransform[1] * (lat - geotransform[3])) / det)
    
    return x, y