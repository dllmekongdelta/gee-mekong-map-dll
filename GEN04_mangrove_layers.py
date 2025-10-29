#!/usr/bin/env python
# coding: utf-8

# # Mangrove Layers
# This python files loads Landsat and Sentinel satellite imagery for multiple years over the defined AOI, computes NDVI for each image, and then applies a threshold to identify mangrove areas for each time period.
# The colors for the layers and the shapefiles are also defined.
# Next to this, the background satellite image is composed for the map
# 

# In[ ]:


# In[ ]:

import GEN01_GEE_Authenticate
import GEN02_AOI as aoi_def
import GEN03_helper_functions as HF

# In[ ]:


# ---------  Landsat & Sentinel collections  ------------------

# Landsat 5 for 1990, 1997
landsat1988 = HF.get_landsat_composite("LANDSAT/LT05/C02/T1_L2", 1988, aoi_def.aoi)
landsat1992 = HF.get_landsat_composite("LANDSAT/LT05/C02/T1_L2", 1992, aoi_def.aoi)
landsat1997 = HF.get_landsat_composite("LANDSAT/LT05/C02/T1_L2", 1997, aoi_def.aoi)

# Landsat 7 for 2000, 2005, 2010
landsat2001 = HF.get_landsat_composite("LANDSAT/LE07/C02/T1_L2", 2001, aoi_def.aoi)
landsat2005 = HF.get_landsat_composite("LANDSAT/LE07/C02/T1_L2", 2005, aoi_def.aoi)
landsat2010 = HF.get_landsat_composite("LANDSAT/LE07/C02/T1_L2", 2010, aoi_def.aoi)
# Landsat 8 for 2015
landsat2015 = HF.get_landsat_composite("LANDSAT/LC08/C02/T1_L2", 2015, aoi_def.aoi)
## landsat 8 for 2020 
# landsat2020 = get_landsat_composite("LANDSAT/LC08/C02/T1_L2", 2020, aoi)
## landsat9 for 2025
# landsat2025 = get_landsat_composite("LANDSAT/LC09/C02/T1_L2", 2025, aoi)

# Sentinel 2 for 2020, 2025
sentinel2020 = HF.get_sentinel_composite("COPERNICUS/S2_SR_HARMONIZED", 2020, aoi_def.aoi)
sentinel2025 = HF.get_sentinel_composite("COPERNICUS/S2_SR_HARMONIZED", 2025, aoi_def.aoi)
# sentinel2025 = HF.get_sentinel_composite("COPERNICUS/S2_SR_HARMONIZED", 2030, aoi_def.aoi)


# ----------------- NDVI (retrieve vegetation from satellite images) ---------------
landsat1988 = HF.add_ndvi(landsat1988, "L5")
landsat1992 = HF.add_ndvi(landsat1992, "L5")
landsat1997 = HF.add_ndvi(landsat1997, "L5")
landsat2001 = HF.add_ndvi(landsat2001, "L7")
landsat2005 = HF.add_ndvi(landsat2005, "L7")
landsat2010 = HF.add_ndvi(landsat2010, "L7")
landsat2015 = HF.add_ndvi(landsat2015, "L8")
sentinel2020 = HF.add_ndvi(sentinel2020, "S2")
sentinel2025 = HF.add_ndvi(sentinel2025, "S2")


# ------------- Threshold NDVI for mangroves ------------
ndvi_threshold = 0.1

#--------------  Create mangrove layers ---------------
mangrove_1988 = landsat1988.select("NDVI").gt(ndvi_threshold)
mangrove_1992 = landsat1992.select("NDVI").gt(ndvi_threshold)
mangrove_1997 = landsat1997.select("NDVI").gt(ndvi_threshold)
mangrove_2001 = landsat2001.select("NDVI").gt(ndvi_threshold)
mangrove_2005 = landsat2005.select("NDVI").gt(ndvi_threshold)
mangrove_2010 = landsat2010.select("NDVI").gt(ndvi_threshold)
mangrove_2015 = landsat2015.select("NDVI").gt(ndvi_threshold)
mangrove_2020 = sentinel2020.select("NDVI").gt(ndvi_threshold)
mangrove_2025 = sentinel2025.select("NDVI").gt(ndvi_threshold)

# --------------- Set Colors for LOSS layers and legend -------------
color_1988_1992_loss = "#2C0035" # (oldest)
color_1992_1997_loss = "#4D004B"
color_1997_2001_loss = "#810F7C"
color_2001_2005_loss = "#8856A7"
color_2005_2010_loss = "#8C96C6"
color_2010_2015_loss = "#9EBCDA"
color_2015_2020_loss = "#BFD3E6"
color_2020_2025_loss = "#E0F3F8" # (most recent)


# --------------- Set Colors for GAIN layers and legend -----------------
color_1988_1992_gain = "#e5f5f9"  # (oldest)
color_1992_1997_gain = "#ccece6"  
color_1997_2001_gain = "#99d8c9"
color_2001_2005_gain = "#66c2a4"
color_2005_2010_gain = "#41ae76"  
color_2010_2015_gain = "#238b45" 
color_2015_2020_gain = "#006d2c"  
color_2020_2025_gain = "#00441b"  # (most recent)

# --------------- Set Color for COVERAGE layers and legend -----------------
color_mangrove_coverage = "#1a9850"

# -------------- Set color for shapefile layers --------------------
color_commune = "#008B8B"
color_sea_dike = "#F18D09"
color_breakwater = "#E6EE0F" 

