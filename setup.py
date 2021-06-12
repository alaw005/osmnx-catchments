import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="osmcatch",
    version="0.0.1",
    author="Adam Lawrence",
    author_email="alaw005@gmail.com",
    description="Analyse network catchments using osmnx package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alaw005/osmnx-catchments",
    project_urls={
        "Bug Tracker": "https://github.com/alaw005/osmnx-catchments/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires = [
        "osmnx>=1.1.1",
        "folium>=0.12.1",
        "scikit-learn>=0.22",
        "gdal>=3.2.0",
        "rasterio>=1.2.4",
        "shapely>=1.7.1"
    ],
    python_requires=">=3.6",
)
