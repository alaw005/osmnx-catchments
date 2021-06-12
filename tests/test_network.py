"""Unit tests for the network module."""

import pytest

from osmcatch import network
import networkx as nx
import geopandas as gpd


# Tests
class TestClassNetwork():
    
    # Fixtures
    access_point = (-41.2883327,174.7750865)
    access_points  = [(-41.2883327,174.7750865), (-41.2889303,174.7748732)] 
    dist = 100
    
    def test_get_osm_walk_network_single_access_point_and_crs(self):
        G1 = network.get_osm_walk_network(self.access_point, self.dist, to_crs="epsg:2193")
        assert type(G1) == nx.classes.multidigraph.MultiDiGraph
        assert G1.graph['crs'] == 'epsg:2193'

    def test_get_osm_walk_network_multiple_access_points(self):
        G1 = network.get_osm_walk_network(self.access_point, self.dist)
        G2 = network.get_osm_walk_network(self.access_points, self.dist)
        assert type(G2) == nx.classes.multidigraph.MultiDiGraph
        assert G2.number_of_nodes() > G1.number_of_nodes()

    def test_get_osm_walk_network_snapshot_date_assuming_size_changes(self):
        G3 = network.get_osm_walk_network(self.access_point, self.dist, snapshot_date="2021-06-01T12:00:00Z")
        G4 = network.get_osm_walk_network(self.access_point, self.dist, snapshot_date="2020-06-01T12:00:00Z")
        assert G3.size() != G4.size()

    def test_get_local_authority_boundary(self):
        geom, tla =  network.get_local_authority_boundary(self.access_point)
        assert type(geom) == gpd.geoseries.GeoSeries
        assert tla == 'Wellington City'
        
    def test_test_get_osm_walk_network_local_authority_boundary(self):
        # TODO
        pass
