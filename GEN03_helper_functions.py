#!/usr/bin/env python
# coding: utf-8

# ### Helper functions
# In the other python files, these functions are called to execute certain tasks

# ##### Satellite images
# These functions retrieve cloud-filtered Landsat or Sentinel satellite images for a specific year and AOI from Google Earth Engine, then create a composite image that is clipped to the AOI

# In[5]:
import ee

# ------------ Retrieve Landsat satellite images from GEE ----------------
def get_landsat_composite(collection_id, year, aoi):
    collection = (
        ee.ImageCollection(collection_id)
        .filterBounds(aoi)
        .filterDate(f"{year}-01-01", f"{year}-12-31")
        .filter(ee.Filter.lt("CLOUD_COVER", 30))
    )
    return collection.median().clip(aoi)

# ------------ Retrieve Sentinel satellite images from GEE ----------------
def get_sentinel_composite(collection_id, year, aoi):
    collection = (
        ee.ImageCollection(collection_id)
        .filterBounds(aoi)
        .filterDate(f"{year}-01-01", f"{year}-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    )
    return collection.median().clip(aoi)


# ##### NDVI 
# This function calculates the NDVI (Normalized Difference Vegetation Index) for a given satellite image.

# In[6]:


def add_ndvi(image, sensor):
    if sensor in ["L5", "L7"]:  # Landsat 5 or 7
        ndvi = image.normalizedDifference(["SR_B4", "SR_B3"]).rename("NDVI")
    elif sensor in ["L8", "L9"]:  # Landsat 8 or 9
        ndvi = image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
    elif sensor == "S2":  # Sentinel-2
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    else:               # error als niet bekend 
        raise ValueError("Unknown sensor type")
    return image.addBands(ndvi)

