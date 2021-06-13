"""Get network graph"""

import osmnx as ox
import networkx as nx

import requests
import json
from shapely.geometry import shape, Point, MultiPoint
import geopandas as gpd
import matplotlib.pyplot as plt

from . import elevation

class WalkNetwork:
    """Convenience class for walk network"""
    
    _default_save_path = 'input_data/walk_network_graph.gml.gz'
    
    _G = nx.classes.multidigraph.MultiDiGraph
    _nodes = nx.classes.reportviews.NodeView
    _edges = nx.classes.reportviews.EdgeView
    
    def __init__(self, G):
        assert type(G) == nx.classes.multidigraph.MultiDiGraph
        self._G = G
        self._nodes, self._edges = ox.graph_to_gdfs(G)
    
    @staticmethod
    def load_graph(path=_default_save_path, **kwargs):
        """Read graph from pickle `path` and return as new WalkNetwork.

        Parameters
        ----------
        path : filename or filehandle
            The filename or filehandle to read from.
        """
        G = nx.read_gpickle(path, **kwargs)
        return WalkNetwork(G)
    
    def save_graph(self, path=_default_save_path, **kwargs):
        """Write the WalkNetwork graph to `path` using pickle.

        Parameters
        ----------
        path : filename or filehandle
            The filename or filehandle to write. Files whose names end with .gz or
            .bz2 will be compressed.

        """
        nx.write_gpickle(self._G, path, **kwargs)
        
    @property
    def graph(self):
        return self._G
    
    @property
    def nodes(self):
        return self._nodes
    
    @property
    def edges(self):
        return self._edges
    
    @property
    def edge_slope(self):
        return self._edges['grade']
    
    def add_edge_speed(self):
        """
        Add walk speed to graph based on elevations using 
        gradient_adjusted_walk_speed() method
        """
        # Calculate walk speeds
        gradients = self._edges['grade']
        speeds = elevation.gradient_adjusted_walk_speed(gradients*100, max_speed=1.5, unit='m/s')
        self._edges['speed'] = speeds
        
        walk_mins = (self._edges['length'] / self._edges['speed']) / 60.0
        self._edges['walk_mins'] = walk_mins
        
        # Calculate walk speeds
        G = ox.graph_from_gdfs(self._nodes, self._edges)
        self.__init__(G)
 
    def plot_graph(self, **kwargs):
        """Convenience method to plot graph using osmnx"""
        plt = ox.plot_graph(self._G, **kwargs)
        return plt
    
    def plot_iso_bands(self,
                       iso_bands_gpd,
                       figsize=(8, 8),
                       bgcolor="#111111", 
                       color_list=None,
                       show=True, 
                       close=True):
        
        # Plot base graph
        fig, ax = plt.subplots(1, 1)

        # Plot iso bands
        if color_list is None:
            color_list = ox.plot.get_colors(n=len(iso_bands_gpd), cmap='Reds', 
                                            start=0.3, return_hex=True)

        iso_bands_gpd.plot(ax=ax, color=color_list, alpha=0.4, zorder=2)

        # plot access points
        ap = MultiPoint([a[::-1] for a in iso_bands_gpd.loc[0]['access_points']])
        ap = gpd.GeoSeries(ap)
        ap.plot(ax=ax, color='r', markersize=10)

        if show: plt.show()
        if close: plt.close()

        return fig, ax

    
    def plot_station(self,
                     access_points,
                     location_name = ""):
        iso_bands_gpd = self.iso_bands(access_points, location_name)
        fig, ax = self.plot_iso_bands(iso_bands_gpd)

        return fig, ax

        
    def iso_bands(self,
                 access_points,
                 location_name = "",
                 iso_bands_mins = [5, 10],
                 iso_edge_buffer = 25):
        """
        Return iso_bands
        """

        # Graph edge field to use for network cost 
        network_cost = 'walk_mins'

        # Ensure iso_bands_mins is a list to prevent errors 
        iso_bands_mins = [iso_bands_mins] if type(iso_bands_mins) is int else iso_bands_mins

        # Ensure centre_point is a list to prevent errors
        access_points = [access_points] if type(access_points) is tuple else access_points

        # Get nearest node to each access point. NB: Need to reverse lat/lon            
        access_nodes = []
        for ap in access_points:
            access_nodes.append(ox.nearest_nodes(self._G, *ap[::-1]))

        # Loop through bands from high to low
        iso_bands_mins.sort(reverse=True)

        iso_group = []
        for iso_band in iso_bands_mins:

            # Calculate subgraphs for each access node and return single subgraph
            # with all nodes/edges traversed 
            subgraphs = []
            for access_node in access_nodes:
                subgraphs.append(nx.ego_graph(self._G, 
                                              access_node, 
                                              radius = iso_band, 
                                              distance = network_cost))
            subgraph = nx.compose_all(subgraphs)

            # Get gdf with edges and buffer, but first having changed to projected 
            # coordinates and then back to default to ensure correct dist results
            edges = ox.graph_to_gdfs(subgraph, nodes=False)
            buffer = ox.project_gdf(edges).buffer(iso_edge_buffer)
            buffer = ox.project_gdf(buffer, to_latlong=True)

            iso_group.append({'location_name': location_name,
                              'access_points': access_points,
                              'access_nodes': access_nodes,
                              'iso_band_mins': iso_band,
                              'geometry': buffer.unary_union})

        iso_bands_gpd = gpd.GeoDataFrame(iso_group, crs=buffer.crs)

        return iso_bands_gpd



        
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

            # Buffer 2km for boundary cases
            geom.buffer(2000)
            
            local_authority_name = result["vectorQuery"]["layers"][str(statsnz_layer_code)]\
                                         ["features"][0]['properties']['TA2020_V1_00_NAME']
        except:    
            geom = None
            local_authority_name = None
    else:    
        geom = None
        local_authority_name = None
        
    return geom, local_authority_name

