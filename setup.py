import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="osmcatch",
    version="0.0.2",
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
        "osmnx>=1.1.1"
    ],
    python_requires=">=3.6",
)
