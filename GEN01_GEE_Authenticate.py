#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ee, os

# # ------- To run in Visual Studio Code (REMOVE WHEN FINAL PUSH TO GITHUB!)
# SERVICE_ACCOUNT = os.environ.get("gee-map-bot@gee-mekong-map.iam.gserviceaccount.com")
# KEY_FILE = "gee-mekong-map-2c919dd0361c.json"

# credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
# ee.Initialize(credentials)

# ------- To run on GitHub ------------------
SERVICE_ACCOUNT = os.environ.get("GEE_SERVICE_ACCOUNT")
KEY_FILE = "key.json"   # GitHub Actions writes the secret here

# credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
# ee.Initialize(credentials)

# print("✅ Earth Engine initialized with Service Account")

