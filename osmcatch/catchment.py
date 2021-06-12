"""Get network graph"""

import osmnx as ox
import networkx as nx
import geopandas as gpd

from . import network

def get_iso_bands(access_points, 
                  location_name = "",
                  iso_bands = [5, 10], 
                  walk_speed = 4.8,
                  iso_buffer = 25,
                  snapshot_date = None):
    """
    Generate iso_bands around specified access_points using OSM network.
 
    Parameters
    ----------
    access_points : list 
        the (lat, lng), [(lat, lng), (lat, lng), etc] centre points around 
        which to construct the graph.
    location_name : string
        the name of the location, for reference only.
    iso_bands : list
        default [5, 10].
    walk_speed : decimal
        default 4.8 km/h which is average walking speed (400m in 5 mins).
    iso_buffer : int
        buffer in metres used to generate isochrone around traversed 
        edges in the graph. 
    snapshot_date : str
        date for which to extract osm data.
 
    Returns
    -------
    G : networkx.MultiDiGraph
    iso_bands_gpd : GeoDataFrame
    """

    # Config 
    network_cost = 'walk_cost'
    network_buffer = 1.1
    
    # Convert int into list if single iso_band provided 
    iso_bands = [iso_bands] if type(iso_bands) is int else iso_bands
    
    # Calculate maximum network size as crow flies 
    network_extent = round(max(iso_bands) * 
                           (walk_speed * 1000 / 60) * network_buffer, 0)
 
    # Get graph of network 
    G = network.get_osm_walk_network(access_points, 
                                     dist=network_extent,
                                     snapshot_date=snapshot_date)
    
    # Add walk_time to each network edge
    for u, v, k, data in G.edges(data=True, keys=True,):
        data[network_cost] = data['length'] / (walk_speed * 1000 / 60)

    # Ensure centre_point is a list to prevent errors
    access_points = [access_points] if type(access_points) is tuple else access_points
    
    # Get nearest node to each access point. NB: Need to reverse lat/lon            
    access_nodes = []
    for ap in access_points:
        access_nodes.append(ox.nearest_nodes(G, *ap[::-1]))
      
    # Loop through bands from high to low
    iso_bands.sort(reverse=True)


    iso_group = []
    for iso_band in iso_bands:
 
        # Calculate subgraphs for each access node and return single subgraph
        # with all nodes/edges traversed 
        subgraphs = []
        for access_node in access_nodes:
            subgraphs.append(nx.ego_graph(G, access_node, 
                                          radius = iso_band, 
                                          distance = network_cost))
        subgraph = nx.compose_all(subgraphs)
    
        # Get gdf with edges and buffer, but first having changed to projected 
        # coordinates and then back to default to ensure correct dist results
        edges = ox.graph_to_gdfs(subgraph, nodes=False)
        buffer = ox.project_gdf(edges).buffer(iso_buffer)
        buffer = ox.project_gdf(buffer, to_latlong=True)
        iso_group.append({'location_name': location_name,
                          'access_points': access_points,
                          'access_nodes': access_nodes,
                          'iso_band': iso_band,
                          'geometry': buffer.unary_union})
    
    iso_bands_gpd = gpd.GeoDataFrame(iso_group, crs=buffer.crs)
 
    return G, iso_bands_gpd