#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ee, os

# --------- Activate this before pushing to GitHub --------------------
# SERVICE_ACCOUNT = os.environ.get("GEE_SERVICE_ACCOUNT")
# KEY_FILE = "key.json"   # GitHub Actions writes the secret here

# credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
# ee.Initialize(credentials)

# --------- Activate when using in VS Code --------------------
ee.Authenticate()
ee.Initialize(project="gee-mekong-map")