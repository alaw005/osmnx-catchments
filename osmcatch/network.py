"""Get network graph"""

import osmnx as ox
import networkx as nx

def trial_print(a):
    print(a)

def get_osm_walk_network(centre_point, 
                         dist=1000, 
                         snapshot_date=None, 
                         to_crs=None):
    """
    Create a graph of walking network from OSM within some distance of 
    some (lat, lng) point.
 
    Parameters
    ----------
    centre_point : tuple or list
        the [lat, lng] centre point around which to construct the graph.
    dist : int
        retain only those nodes within this many meters of the center of the
        graph.
    snapshot_date : string
        download OSM as at the date specified. Must be in the format 
        '[date:"YYYY-MM-DDTHH:MM:SSZ"]'
    to_crs : string or pyproj.CRS
        the coordinate reference system to use, e.g. 'epsg:4326', if None use 
        the osmnx default.
 
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
 
    # Calculate graph for each centre point provided and each of the custom_filter
    # tags, returning full extend of network as single graph 
    graphs = []
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
 
    #G = nx.compose_all(graphs)
 
    if not to_crs is None:
      G = ox.project_graph(G, to_crs=to_crs)
 
    return G
 