import os
import requests
import rasterio
from osgeo import gdal


def linz_wellington_lidar_2013_14_dem_tile_names(x, 
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


# tiles - list of DEM tile names to download

# Specify where the DRM files are located
base_path = "/content/drive/MyDrive/Colab Notebooks/porirua-linz-lidar-dem-2013-14/"

# Specify crs of the input DEM if different from project
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

G.edges.data()