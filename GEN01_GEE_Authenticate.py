#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import ee, os

# Google Earth Engine authentication.
# Mode is picked automatically, no manual editing needed:
#   - CI (GitHub Actions): GEE_SERVICE_ACCOUNT is set and key.json exists
#     (written by the workflow from the GEE_KEY secret) -> service account.
#   - Local development: neither is present -> opens a browser to sign in
#     with your own Google account against GEE_PROJECT.
# Full setup walkthrough: README.md > "Google Earth Engine setup".

SERVICE_ACCOUNT = os.environ.get("GEE_SERVICE_ACCOUNT")
KEY_FILE = "key.json"   # GitHub Actions writes the secret here
GEE_PROJECT = os.environ.get("GEE_PROJECT", "gee-mekong-map")

if SERVICE_ACCOUNT and os.path.exists(KEY_FILE):
    using_service_account = True
    credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_FILE)
    ee.Initialize(credentials)
else:
    using_service_account = False
    ee.Authenticate()
    ee.Initialize(project=GEE_PROJECT)

# Fail fast with a clear message if the credentials don't actually work,
# instead of an unrelated error surfacing later inside GEN04.
try:
    ee.Number(1).getInfo()
except Exception as exc:
    hint = (
        f"service account '{SERVICE_ACCOUNT}' (from key.json)"
        if using_service_account
        else f"project '{GEE_PROJECT}'"
    )
    raise RuntimeError(
        f"Google Earth Engine connection failed. Check that {hint} has "
        "Earth Engine access and that the Earth Engine API is enabled."
    ) from exc

identity = SERVICE_ACCOUNT if using_service_account else GEE_PROJECT
print(f"Connected to Google Earth Engine ({identity}).")