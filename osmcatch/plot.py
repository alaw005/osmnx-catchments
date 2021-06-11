
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
import matplotlib.pyplot as plt
 
from . import catchment
 
def plot_iso_bands(G, 
                   iso_bands_gpd,
                   figsize=(8, 8),
                   bgcolor="#111111", 
                   color_list=None,
                   show=True, 
                   close=True):

    # Plot base graph
    fig, ax = ox.plot_graph(G, bgcolor="w", node_size=0, 
                            close=False, show=False, figsize=figsize)
 
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
 
 
def plot_iso_bands_folium(G, iso_bands_gpd, **kwargs):
 
    # Create folim map with base network
    map = ox.folium.plot_graph_folium(G,  
                                      color='grey', 
                                      weight=0.8, 
                                      opacity=0.4, 
                                      **kwargs) 
 
    # Add iso bands
    def style_function(feature):
        bands = iso_bands_gpd['iso_band'].unique()
        colors = ox.plot.get_colors(n=len(bands), cmap='Reds',
                                        start=0.3, return_hex=True)
        color_scale = dict(zip(bands, colors))
        return {'opacity': 0.5,
                'weight': 0,
                'fillColor': color_scale[feature['properties']['iso_band']]
                }
 
    tooltip = ox.folium.folium.GeoJsonTooltip(fields=['location_name', 'iso_band'],
                                            aliases=['Catchment', 'Walk time (mins)'])
 
    j1 = ox.folium.folium.GeoJson(data=iso_bands_gpd,
                                style_function=style_function,
                                tooltip=tooltip)
 
    j1.add_to(map)
 
    # Add access points
    aps = []
    for _, row in iso_bands_gpd.iterrows():
        aps.append(MultiPoint([p[::-1] for p in row['access_points']]))
    aps = gpd.GeoDataFrame(iso_bands_gpd[['location_name']], 
                        geometry=aps, 
                        crs=iso_bands_gpd.crs)
    j2 = ox.folium.folium.GeoJson(data=aps)
    ox.folium.folium.Popup('<b>Access point</b>: {}'.format(row['location_name'])).add_to(j2)                                
    j2.add_to(map)
    
    return map
 
 
def plot_station(location_name, access_points):
    G, iso_bands_gpd = catchment.get_iso_bands(access_points, 
                                               location_name)
    p = plot_iso_bands(G, iso_bands_gpd)
    
    