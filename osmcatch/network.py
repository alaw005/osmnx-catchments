"""Get network graph"""

import osmnx as ox
import networkx as nx

import requests
import json
from shapely.geometry import shape
import geopandas as gpd

def get_osm_walk_network(centre_point, 
                         dist=1000, 
                         snapshot_date=None, 
                         to_crs=None,
                         return_local_authority_network=False):
    """
    Create a walking network graph using OSM within specified distance of a
    (lat, lng) point.
 
    Parameters
    ----------
    centre_point : tuple or list
        the [lat, lng] centre point or list of centre points ([lat,lng], 
        [lat,lng]) around which to construct the graph.
    dist : int
        retain only those nodes within this many meters of the center of the
        graph.
    snapshot_date : string
        download OSM as at the date specified. Must be in the format 
        "YYYY-MM-DDTHH:MM:SSZ"
    to_crs : string or pyproj.CRS
        the coordinate reference system to use, e.g. 'epsg:4326', if None use 
        the osmnx default.
    return_local_authority_network : boolean
        if True then return network for local authority that first point is 
        located within instead of buffer around point
 
    Returns
    -------
    G : networkx.MultiDiGraph
    """
 
    # OSM walk network tags
    walk_highways = '["area"!~"yes"]["highway"]' + \
        '["highway"!~"motorway"]' + \
        '["highway"!~"motorway_junction"]' + \
        '["highway"!~"traffic_signals"]["highway"!~"give_way"]' + \
        '["foot"!~"no"]' + \
        '["sidewalk"!~"no|separate"]["area"!~"yes"]'
    walk_footways = '["area"!~"yes"]["footway"]'
    custom_filters = [walk_highways, walk_footways]
 
    # Configure output and set snapshot date
    config = '[out:json]' + ('' if snapshot_date is None else '[date:"' + snapshot_date + '"]')
    ox.config(overpass_settings=config)

    # Ensure centre_point is a list to prevent errors
    centre_points = [centre_point] if type(centre_point) is tuple else centre_point
 
    graphs = []
    if return_local_authority_network:
        
        # Get local authority boundary within which to return network
        geom, name = get_local_authority_boundary(centre_points[0])
        
        # Need to do multiple calls to custom_filter for OR tag criteria
        for custom_filter in custom_filters:
            try:
                G = ox.graph_from_polygon(geom.all(), 
                                        network_type="walk", 
                                        custom_filter=custom_filter, 
                                        truncate_by_edge=True,
                                        simplify=False)
            except:
                pass  # nothing to add
            else:
                graphs.append(G)            
    else:
        
        # Calculate graph for each centre point provided and each of the custom_filter
        # tags, returning full extend of network as single graph 
        for centre_point in centre_points:
            
            # Need to do multiple calls to custom_filter for OR tag criteria
            for custom_filter in custom_filters:
                try:
                    G = ox.graph_from_point(centre_point, 
                                            dist=dist, 
                                            network_type="walk", 
                                            custom_filter=custom_filter, 
                                            truncate_by_edge=True,
                                            simplify=False)
                except:
                    pass  # nothing to add
                else:
                    graphs.append(G)

    G = nx.compose_all(graphs)

    if not to_crs is None:
      G = ox.project_graph(G, to_crs=to_crs)
 
    return G
 
    
def get_local_authority_boundary(access_point,
                                    statsnz_api=None,
                                    statsnz_layer_code=104267):
    """
    Return polygon for local authority boundary, which can be used to determine
    extent of osm network to download.
    
    `geom.plot()` to plot the shape 
 
    Parameters
    ----------
    access_point : tuple
        a [lat, lng] point within the target local authority boundary.
    statsnz_api : string
        Koordinates API key to access the layer from StatsNZ.
    statsnz_layer_code : str
        The StatsNZ layer id, default is `104267` which is NZ Local Authorities
        
    Returns
    -------
    geom : geopandas.geoseries.GeoSeries
    local_authority_name : str
    """
    
    if statsnz_api is None:
        statsnz_api = 'e9dc37ccf1ef4152bb7444f61dcd2ceb'

    # StatsNZ base url
    url_template = "https://datafinder.stats.govt.nz/services/query/v1/vector.json?" + \
                   "key={}&layer={}&x={}&y={}&max_results=1&geometry=true&" + \
                   "with_field_names=true"

    
    # Query layer
    url = url_template.format(statsnz_api, statsnz_layer_code, access_point[1], access_point[0])       
    r = requests.get(url)

    if r.status_code == 200:
        result = r.json() 
        try:
            geom_str = str(result["vectorQuery"]["layers"][str(statsnz_layer_code)]\
                                 ["features"][0]["geometry"])       
            geom_shape = shape(json.loads(geom_str.replace("'", '"')))
            crs = result["vectorQuery"]["layers"][str(statsnz_layer_code)]['crs']\
                        ['properties']['name']      
            geom = gpd.GeoSeries(geom_shape, crs=crs)

            local_authority_name = result["vectorQuery"]["layers"][str(statsnz_layer_code)]\
                                         ["features"][0]['properties']['TA2020_V1_00_NAME']
        except:    
            geom = None
            local_authority_name = None
    else:    
        geom = None
        local_authority_name = None
        
    return geom, local_authority_name

