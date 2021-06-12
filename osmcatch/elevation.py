""" Return elevation data from DEM tiles """

import os
import requests
import osmnx as ox
from osgeo import gdal
import rasterio


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
    raster_crs : string or pyproj.CRS
        the coordinate reference system for the raster, default to G.graph crs. 

    Returns
    -------
    G : networkx.MultiDiGraph
        graph with node elevation, edge `grade` and `grade_abs` attributes
    """
    
    graph_crs = G.graph["crs"]
    
    # If raster_crs specified then use G.graph crs
    if raster_crs is None:
        raster_crs = graph_crs

    # Ensure graph same crs as raster for processing        
    G = ox.project_graph(G, raster_crs)

    # Process raster data
    G = ox.add_node_elevations_raster(G, raster_path)
    G = ox.add_edge_grades(G)   
        
    # Ensure graph crs set back to original
    G = ox.project_graph(G, graph_crs)

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
    if linz_api is None:
        linz_api = "69b10a1278be4d0e9a0247fdf4cfe0cc"

    # LINZ base url
    dem_index_url = "https://data.linz.govt.nz/services/query/v1/vector.json?" + \
                    "key={}&layer={}&x={}&y={}&radius={}&with_field_names=true" + \
                    "&max_results={}"
    
    # Ensure access_points is a list even when only passed a single access_point
    access_points = [access_points] if type(access_points) is tuple else access_points    

    # Query LINZ index
    tiles = []
    for ap in access_points:

        # Identify DEM tiles within range of point
        url = dem_index_url.format(linz_api, linz_layer_code, ap[1], ap[0], buffer, max_results)       
        r = requests.get(url)
        
        if r.status_code == 200:
            r_json = r.json()
            result = [i["properties"]["tile"] for i in r_json["vectorQuery"]["layers"][str(linz_layer_code)]["features"]]
        else:    
            result = []
 
        tiles.extend(result)

    # Get unique set of tiles and sort
    tiles = list(set(tiles))
    tiles.sort()

    return tiles
