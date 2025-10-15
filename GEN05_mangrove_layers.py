#!/usr/bin/env python
# coding: utf-8

# # Mangrove Layers
# This python files loads Landsat and Sentinel satellite imagery for multiple years over the defined AOI, computes NDVI for each image, and then applies a threshold to identify mangrove areas for each time period.
# 
# Next to this, the background satellite image is composed for the map
# 

# In[ ]:





# In[ ]:


# get_ipython().run_line_magic('run', './GEN02_AOI.ipynb')
# get_ipython().run_line_magic('run', './GEN03_helper_functions.ipynb')
import GEN02_AOI
import GEN03_helper_functions

# In[ ]:


# ---------  Landsat & Sentinel collections  ------------------

# Landsat 5 for 1990, 1997
landsat1988 = get_landsat_composite("LANDSAT/LT05/C02/T1_L2", 1988, aoi)
landsat1992 = get_landsat_composite("LANDSAT/LT05/C02/T1_L2", 1992, aoi)
landsat1997 = get_landsat_composite("LANDSAT/LT05/C02/T1_L2", 1997, aoi)

# Landsat 7 for 2000, 2005, 2010
# landsat1995 = get_landsat_composite("LANDSAT/LE07/C02/T1_L2", 1995, aoi)
landsat2001 = get_landsat_composite("LANDSAT/LE07/C02/T1_L2", 2001, aoi)
landsat2005 = get_landsat_composite("LANDSAT/LE07/C02/T1_L2", 2005, aoi)
landsat2010 = get_landsat_composite("LANDSAT/LE07/C02/T1_L2", 2010, aoi)
# Landsat 8 for 2015
landsat2015 = get_landsat_composite("LANDSAT/LC08/C02/T1_L2", 2015, aoi)
## landsat 8 for 2020 
# landsat2020 = get_landsat_composite("LANDSAT/LC08/C02/T1_L2", 2020, aoi)
## landsat9 for 2025
# landsat2025 = get_landsat_composite("LANDSAT/LC09/C02/T1_L2", 2025, aoi)

# Sentinel 2 for 2020, 2025
sentinel2020 = get_sentinel_composite("COPERNICUS/S2_SR_HARMONIZED", 2020, aoi)
sentinel2024 = get_sentinel_composite("COPERNICUS/S2_SR_HARMONIZED", 2024, aoi)


# ----------------- NDVI ---------------
landsat1988 = add_ndvi(landsat1988, "L5")
landsat1992 = add_ndvi(landsat1992, "L5")
landsat1997 = add_ndvi(landsat1997, "L5")
landsat2001 = add_ndvi(landsat2001, "L7")
landsat2005 = add_ndvi(landsat2005, "L7")
landsat2010 = add_ndvi(landsat2010, "L7")
landsat2015 = add_ndvi(landsat2015, "L8")
sentinel2020 = add_ndvi(sentinel2020, "S2")
sentinel2024 = add_ndvi(sentinel2024, "S2")


# Threshold NDVI for mangroves
ndvi_threshold = 0.1

# Create mangrove layers
mangrove_1988 = landsat1988.select("NDVI").gt(ndvi_threshold)
mangrove_1992 = landsat1992.select("NDVI").gt(ndvi_threshold)
mangrove_1997 = landsat1997.select("NDVI").gt(ndvi_threshold)
mangrove_2001 = landsat2001.select("NDVI").gt(ndvi_threshold)
mangrove_2005 = landsat2005.select("NDVI").gt(ndvi_threshold)
mangrove_2010 = landsat2010.select("NDVI").gt(ndvi_threshold)
mangrove_2015 = landsat2015.select("NDVI").gt(ndvi_threshold)
mangrove_2020 = sentinel2020.select("NDVI").gt(ndvi_threshold)
mangrove_2024 = sentinel2024.select("NDVI").gt(ndvi_threshold)

# --------------- Set Colors for LOSS layers and legend -------------
color_1988_1992_loss = "#2C0035"  # Very dark violet-blue (oldest)
color_1992_1997_loss = "#4D004B"
color_1997_2001_loss = "#810F7C"
color_2001_2005_loss = "#8856A7"
color_2005_2010_loss = "#8C96C6"
color_2010_2015_loss = "#9EBCDA"
color_2015_2020_loss = "#BFD3E6"
color_2020_2024_loss = "#E0F3F8"  # Pale blue (most recent)


# --------------- Set Colors for GAIN layers and legend -----------------
color_1988_1992_gain = "#e5f5f9"  # very pale green (oldest)
color_1992_1997_gain = "#ccece6"  # pale green
color_1997_2001_gain = "#99d8c9"  # light green
color_2001_2005_gain = "#66c2a4"  # medium-light green
color_2005_2010_gain = "#41ae76"  # medium green
color_2010_2015_gain = "#238b45"  # strong green
color_2015_2020_gain = "#006d2c"  # dark green
color_2020_2024_gain = "#00441b"  # very dark green (most recent)

# --------------- Set Color for COVERAGE layers and legend -----------------
color_mangrove_coverage = "#1a9850"


# ### Background satellite image

# In[ ]:


import ee
# Sentinel-2 Surface Reflectance (10 m) - better resolution
sentinel = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    # .filterBounds(aoi)
    .filterDate("2024-01-01", "2024-12-31")  # pick recent year
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))  # filter clouds
    .median()
    # .clip(aoi)
)


