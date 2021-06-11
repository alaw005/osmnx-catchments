""" Return elevation data from DEM tiles """

import os
import requests
import osmnx as ox
from osgeo import gdal
import rasterio


def list_tiles_linz_wellington_lidar_2013_14_dem(x, 
                                                 y, 
                                                 radius=1000,
                                                 layer=53591,
                                                 max_results=25, 
                                                 api=None):
    """
    Return list of LINZ Wellington region DEM tiles within specified radius of
    point. These then need to be manually downloaded.
 
    Parameters
    ----------
    x : decimal
        Required. Longitude of the point you want to query, in decimal degrees 
        (WGS84/EPSG:4326).
    y : decimal
        Required. Latitude of the point you want to query, in decimal degrees 
        (WGS84/EPSG:4326).
    radius : int
        radius around around point in metres for return tiles.
    layer : str
        The layer ID to get results from. Default #53591 which is LINZ 
        Wellington region DEM 1m 2013/14 
    max_results :
        Maximum number of results to return from LINZ in query
    api : string
        Your Koordinates API key to access the layer from LINZ.
 
    Returns
    -------
    tiles : list
        list of dem tile names for manual download from LINZ 
    """
    if api is None:
        api = "69b10a1278be4d0e9a0247fdf4cfe0cc"

    wellington_dem_index_url = "https://data.linz.govt.nz/services/query/v1/vector.json?key={}&layer={}&x={}&y={}&radius={}&with_field_names=true&max_results={}"
    url = wellington_dem_index_url.format(api, layer, x, y, radius, max_results)

    # Identify DEM tiles within range of point
    r = requests.get(url)
    if r.status_code == 200:
        r_json = r.json()
        tiles = [i["properties"]["tile"] for i in r_json["vectorQuery"]["layers"][str(layer)]["features"]]
    else:    
        tiles = []
 
    tiles.sort()

    return tiles


def process_elevations_raster(G, 
                              tiles,
                              base_path=None,
                              dem_crs=None):

    # Specify where the DRM files are located
    if base_path is None:
        base_path = "notebooks/input_data/porirua-linz-lidar-dem-2013-14/"

    # Specify crs of the input DEM if different from project
    if dem_crs is None:
        dem_crs = 'epsg:2193'

    # Change project projection to match DEM data
    proj_crs = ox.settings.default_crs
    G = ox.project_graph(G, dem_crs)

    # Apply elevations to graph nodes and grades to edges
    filepaths = [os.path.join(base_path, t) for t in tiles]
    G = ox.add_node_elevations_raster(G, filepaths)
    G = ox.add_edge_grades(G)

    # Project back to default project
    G = ox.project_graph(G, proj_crs)

    return G


def get_raster_tile_names_from_linz(access_points,
                                    buffer=1000,
                                    linz_api=None,
                                    linz_layer_code=53591, 
                                    max_results=25):
    """
    Return list of LINZ Wellington region DEM tiles within specified radius of
    point. These then need to be manually downloaded.
 
    Parameters
    ----------
    access_points : list 
        the (lat, lng), [(lat, lng), (lat, lng), etc] centre points around 
        which to construct the graph. In decimal degrees (WGS84/EPSG:4326).
    buffer : int
        return tiles within this many meters of each access_point, default 
        1,000m.
    linz_layer_code : str
        The LINZ layer id, default is `53591` which is Wellington region DEM 1m
        2013/14. 
    linz_api : string
        Koordinates API key to access the layer from LINZ.
    max_results :
        Maximum number of results to be returned from LINZ query, default `25`.
 
    Returns
    -------
    tiles : list
        list of dem tile names for manual download from LINZ 
    """
    
    # Ensure have linz_api, TODO: need to change to github secret
    if api is None:
        api = "69b10a1278be4d0e9a0247fdf4cfe0cc"

    # Define LINZ url
    wellington_dem_index_url = """https://data.linz.govt.nz/services/query/v1/vector.json?
                                  key={}&layer={}&x={}&y={}&radius={}&with_field_names=true
                                  &max_results={}"""
    url = wellington_dem_index_url.format(api, layer, x, y, radius, max_results)

    # Identify DEM tiles within range of point
    r = requests.get(url)
    if r.status_code == 200:
        r_json = r.json()
        tiles = [i["properties"]["tile"] for i in r_json["vectorQuery"]["layers"][str(layer)]["features"]]
    else:    
        tiles = []
 
    tiles.sort()

    return tiles


    

def add_elevations_to_graph(G, 
                          raster_path, 
                          raster_crs=None):
    """
    Use osmnx to add `elevation` and `grade` attribute to each node from local
    raster file(s).

    Parameters
    ----------
    G : networkx.MultiDiGraph
        input graph
    raster_path : string or pathlib.Path or list of strings/Paths
        path (or list of paths) to the raster file(s) to query

    Returns
    -------
    G : networkx.MultiDiGraph
        graph with node elevation, edge `grade` and `grade_abs` attributes
    """
    
    pass