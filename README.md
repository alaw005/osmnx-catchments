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

## Run tests

Run the following in Python terminal from project root directory  to execute 
tests.

```
pytest
```

## Build package

To build on Windows need to install the following
```
pip install build[virtualenv]
```

Can run using Docker base image here 
[jupyter-gdal](https://hub.docker.com/repository/docker/alaw005/jupyter-gdal)