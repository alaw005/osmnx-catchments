"""Get network graph"""

import osmnx as ox
import networkx as nx

class Catchment():
    
    access_points = []
    access_nodes = []
    

                iso_group.append({'location_name': location_name,
                              'access_points': access_points,
                              'access_nodes': access_nodes,
                              'iso_band': iso_band,
                              'geometry': buffer.unary_union})
        
        
    def get_iso_bands(location_name, 
                      access_points, 
                      iso_bands = [5, 10], 
                      walk_speed = 4.8,
                      iso_buffer = 25,
                      G=None,
                      **kwargs):
        """
        Generate iso_bands around specified access_points using OSM network.

        Parameters
        ----------
        location_name : string
            the name of the location, for reference only
        access_points : list 
            the [lat, lng] centre point around which to construct the graph.
        iso_bands : list
            default [5, 10]
        walk_speed : decimal
            default 4.8 km/h which is average walking speed (400m in 5 mins)
        iso_buffer : int
            buffer in metres used to generate isochrone around traversed 
            edges in the graph. 
        **kwargs
            kwargs passed to get_osm_walk_network() such as snapshot_date or 
            to_crs.

        Returns
        -------
        G : networkx.MultiDiGraph
        iso_bands_gpd : GeoDataFrame
        """

        network_buffer = 1.1
        network_extent = round(max(iso_bands) * 
                               (walk_speed * 1000 / 60) * network_buffer, 0)
        network_cost = 'walk_cost'

        if G is None:
            # Get graph of network 
            #G = ox.graph_from_point(access_points[0], dist=network_extent, 
            #                        network_type="walk", simplify=False)
            G = get_osm_walk_network(access_points, 
                                     dist=network_extent, 
                                     **kwargs)

        # Add walk_time to each network edge
        for u, v, k, data in G.edges(data=True, keys=True,):
            data[network_cost] = data['length'] / (walk_speed * 1000 / 60)

        # Get nearest node to each access point. NB: Need to reverse lat/lon            
        access_nodes = []
        for ap in access_points:
            access_nodes.append(ox.nearest_nodes(G, *ap[::-1]))

        # Loop through bands from high to low
        iso_bands.sort(reverse=True)

        iso_group = []
        for iso_band in iso_bands:

            # Calculate subgraphs for each access node and return single subgraph
            # withh all nodes/edges traversed 
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
