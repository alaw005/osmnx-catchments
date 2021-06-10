# OSMnx-catchments
[![Run tests](https://github.com/alaw005/osmnx-catchments/actions/workflows/pytest.yml/badge.svg)](https://github.com/alaw005/osmnx-catchments/actions/workflows/pytest.yml)


**OSMnx-catchments** uses [**OSMnx**](https://github.com/gboeing/osmnx) to 
experiment with transport catchments. Initally considering walk catchments 
around train stations and city centre areas.

**Reference**: Boeing, G. 2017. "[OSMnx: New Methods for Acquiring, 
Constructing, Analyzing, and Visualizing Complex Street Networks]
(https://geoffboeing.com/publications/osmnx-complex-street-networks/)." 
*Computers, Environment and Urban Systems* 65, 126-139. 
doi:10.1016/j.compenvurbsys.2017.05.004


## Build package

To build on Windows need to install the following
```
pip install build[virtualenv]
```

To work on Ubuntu need to install gdal in operating system before can install
for pythong using pip
```
sudo apt-get update && sudo apt-get install python-gdal
```