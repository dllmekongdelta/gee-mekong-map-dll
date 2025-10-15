#!/usr/bin/env python
# coding: utf-8

# # Mangrove Loss: 1988 - 2024
# The code in this file creates an HTML file that visualizes the loss in mangrove forest coverage from 1988 to 2024 on an interactive Earth Engine map. It adds individual layers for each year of the mangrove extent, allowing the user to view and compare areas of mangrove loss. 

# In[ ]:


# --- Run underlying python scripts
# %run ./GEN04_HTML_layout.ipynb
import GEN04_HTML_layout


# In[10]:


import ee, os


SERVICE_ACCOUNT = "gee-map-bot@gee-mekong-map.iam.gserviceaccount.com"
KEY_FILE = "gee-mekong-map-2c919dd0361c.json"

credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
ee.Initialize(credentials, project='gee-mekong-map')

# gee-map-bot@gee-mekong-map.iam.gserviceaccount.com
# gee-mekong-map-2c919dd0361c

# SERVICE_ACCOUNT = os.environ.get("GEE_SERVICE_ACCOUNT")
# KEY_FILE = "key.json"   # GitHub Actions writes the secret here

# credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
# ee.Initialize(credentials)

# print("✅ Earth Engine initialized with Service Account")

# ee.Authenticate()
# ee.Initialize()


# In[11]:


# ------------- Packages & GEE ------------
import ee                                       # Google Earth Engine API for Python
import geemap.foliumap as geemap_folium         # Geemap module integrating Folium maps
import folium                                   # Interactive mapping library based on Leaflet.js
import geemap                                   # Toolkit for working with Google Earth Engine in Python
from geemap import cartoee                      # Module for exporting and visualizing Earth Engine maps using Matplotlib
import ipyleaflet                               # Interactive maps in Jupyter using Leaflet
import ipywidgets as widgets                    # Interactive UI controls for Jupyter notebooks
from branca.element import Element              # Low-level HTML/JS elements for Folium/Branca maps
import geopandas as gpd                         # Spatial data handling (GeoDataFrames)
import glob                                     # File pattern matching (e.g., list all .tif files in a folder)
import json                                     # JSON encoding and decoding (read/write .json files)


# In[12]:


# Mangrove loss = 2010 mangroves not present in 2015
# ------------- Calculate mangrove loss per time interval -------------
loss_1988_1992 = mangrove_1988.And(mangrove_1992.Not())
loss_1992_1997 = mangrove_1992.And(mangrove_1997.Not())
loss_1997_2001 = mangrove_1997.And(mangrove_2001.Not())
loss_2001_2005 = mangrove_2001.And(mangrove_2005.Not())
loss_2005_2010 = mangrove_2005.And(mangrove_2010.Not())
loss_2010_2015 = mangrove_2010.And(mangrove_2015.Not())
loss_2015_2020 = mangrove_2015.And(mangrove_2020.Not())
loss_2020_2024 = mangrove_2020.And(mangrove_2024.Not())


Map = geemap_folium.Map(center=[9.2, 105.75], zoom=11)

# Add Sentinel-2 as basemap (true color RGB)
Map.addLayer(
    sentinel,
    {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000},
    "Sentinel-2 (2024)"
)


# In[13]:


# ------------- Add loss layers with palette and generate tile URLs -------------
loss_layers = {
    "Mangrove loss (1988-1992)": (loss_1988_1992, color_1988_1992_loss),
    "Mangrove loss (1992-1997)": (loss_1992_1997, color_1992_1997_loss),
    "Mangrove loss (1997-2001)": (loss_1997_2001, color_1997_2001_loss),
    "Mangrove loss (2001-2005)": (loss_2001_2005, color_2001_2005_loss),
    "Mangrove loss (2005-2010)": (loss_2005_2010, color_2005_2010_loss),
    "Mangrove loss (2010-2015)": (loss_2010_2015, color_2010_2015_loss),
    "Mangrove loss (2015-2020)": (loss_2015_2020, color_2015_2020_loss),
    "Mangrove loss (2020-2024)": (loss_2020_2024, color_2020_2024_loss),
}

# -------------- Add loss maps -----------------
Map.addLayer(loss_1988_1992.updateMask(loss_1988_1992), {"palette": [color_1988_1992_loss]}, "Mangrove loss (1988-1992)")
Map.addLayer(loss_1992_1997.updateMask(loss_1992_1997), {"palette": [color_1992_1997_loss]}, "Mangrove loss (1992-1997)")
Map.addLayer(loss_1997_2001.updateMask(loss_1997_2001), {"palette": [color_1997_2001_loss]}, "Mangrove loss (1997-2001)")
Map.addLayer(loss_2001_2005.updateMask(loss_2001_2005), {"palette": [color_2001_2005_loss]}, "Mangrove loss (2001-2005)")
Map.addLayer(loss_2005_2010.updateMask(loss_2005_2010), {"palette": [color_2005_2010_loss]}, "Mangrove loss (2005-2010)")
Map.addLayer(loss_2010_2015.updateMask(loss_2010_2015), {"palette": [color_2010_2015_loss]}, "Mangrove loss (2010-2015)")
Map.addLayer(loss_2015_2020.updateMask(loss_2015_2020), {"palette": [color_2015_2020_loss]}, "Mangrove loss (2015-2020)")
Map.addLayer(loss_2020_2024.updateMask(loss_2020_2024), {"palette": [color_2020_2024_loss]}, "Mangrove loss (2020-2024)")


# In[ ]:





# In[14]:


# for name, (layer, color) in loss_layers.items():
#     vis = {"palette": [color]}
#     Map.addLayer(layer.updateMask(layer), vis, name)
#     tile_urls[name] = generate_tile_url(layer, vis)

# # Save tile URLs to JSON
# with open("tile_urls.json", "w") as f:
#     json.dump(tile_urls, f, indent=2)



# In[15]:


# ------- Add legend      --------
legend_title = "Mangrove Loss Map (1988-2024)"
add_folium_legend(Map, legend_title, legend_dict_mangrove_LOSS, style=style)

# ------- Add scalebar     -------
Map.add_child(ScaleBar(font_size="14px"))

# ------- Add north arrow --------
add_north_arrow(Map, position="bottomleft", arrow_size="35px", text_size="25px")

# ------- Add Living LAb logo -----
Map.get_root().html.add_child(folium.Element(logo_html))


# In[16]:


Map.to_html("tryout_goal_LOSS.html")

