"""Unit tests for the network module."""

import pytest

from osmcatch import catchment
import networkx as nx
import geopandas as gpd

# Tests
class TestClassCatchment():
    
    # Fixtures
    access_point = (-41.2883327,174.7750865)
    access_points  = [(-41.2883327,174.7750865), (-41.2889303,174.7748732)] 
    dist = 100
    
    def test_get_iso_bands_single_access_point(self):
        G, iso_bands_gpd = catchment.get_iso_bands((-41.137575, 174.843478))
        assert type(G) == nx.classes.multidigraph.MultiDiGraph
        assert len(iso_bands_gpd) == 2
        assert type(iso_bands_gpd) == gpd.geodataframe.GeoDataFrame
        assert type(iso_bands_gpd['geometry']) == gpd.geoseries.GeoSeries

    def test_get_iso_bands_multiple_access_points(self):
        G, iso_bands_gpd = catchment.get_iso_bands([(-41.137575, 174.843478),(-41.13757, 174.843274)])
        assert type(G) == nx.classes.multidigraph.MultiDiGraph
        assert len(iso_bands_gpd) == 2
        assert type(iso_bands_gpd) == gpd.geodataframe.GeoDataFrame
        assert type(iso_bands_gpd['geometry']) == gpd.geoseries.GeoSeries
        
        
