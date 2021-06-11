"""Unit tests for the elevation module."""

import pytest

from osmcatch import elevation, catchment
import osmnx as ox 
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

    
    def test_process_elevations_raster(self):

        G, iso_bands_gpd = catchment.get_iso_bands([(-41.137575, 174.843478),(-41.13757, 174.843274)], 'Porirua Station')
        tiles = elevation.list_tiles_linz_wellington_lidar_2013_14_dem(x=174.843274, y=-41.13757)

        G1 = elevation.process_elevations_raster(G, tiles,
                                               base_path = "notebooks/input_data/linz-porirua-lidar-1m-dem-2013-2014/")
        G2 = ox.graph_to_gdfs(G1)
        assert max(G2[1]['grade']) > 0