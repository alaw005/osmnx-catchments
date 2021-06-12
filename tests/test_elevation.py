"""Unit tests for the elevation module."""

import pytest

from osmcatch import elevation, catchment
import osmnx as ox 
import networkx as nx
import geopandas as gpd
from pathlib import Path

# Tests
class TestClassElevation():
    
    # Fixtures
    access_points = ([(-41.137575, 174.843478), (-41.13757, 174.843274), (-41.142401,174.858625)])
    tiles = list(Path("tests/test_data").glob("DEM*.tif"))
    
    def test_add_elevations_to_graph(self):
        
        G, iso_bands_gpd = catchment.get_iso_bands(self.access_points, 'Test access points', [5])

        G1 = elevation.add_elevations_to_graph(G=G, 
                                               raster_path=self.tiles, 
                                               raster_crs='epsg:2193')
        G2 = ox.graph_to_gdfs(G1)

        assert max(G2[1]['grade']) > 0
        
    def test_get_raster_tile_names_from_linz(self):
      
        tiles = elevation.get_raster_tile_names_from_linz(self.access_points,200)
        
        assert len(tiles) > 0
        assert 'DEM_BP31_2013_1000_4748.tif' in tiles
        