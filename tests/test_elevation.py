"""Unit tests for the elevation module."""

import pytest

from osmcatch import elevation
import networkx as nx
import geopandas as gpd

# Tests
class TestClassElevation():
    
    # Fixtures
    access_point = (-41.2883327,174.7750865)
    
    def test_list_tiles_linz_wellington_lidar_2013_14_dem(self):
        
        tiles = elevation.list_tiles_linz_wellington_lidar_2013_14_dem(x=self.access_point[1], 
                                                                       y=self.access_point[0])
        assert len(tiles) > 0
        assert 'DEM_BQ31_2013_1000_1935.tif' in tiles
