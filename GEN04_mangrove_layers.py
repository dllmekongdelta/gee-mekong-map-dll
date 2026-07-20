#!/usr/bin/env python
# coding: utf-8

# # Mangrove Layers
# This python files loads Landsat and Sentinel satellite imagery for multiple years over the defined AOI, computes NDVI for each image, and then applies a threshold to identify mangrove areas for each time period.
# The colors for the layers and the shapefiles are also defined.
# Next to this, the background satellite image is composed for the map
# 

# In[ ]:


# In[ ]:

import math

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

# Sentinel 2 for 2020, 2025, 2026
# 2026 is the current year at the time of writing, so its composite is based
# on a partial year of imagery and improves as the scheduled GitHub Actions
# runs pick up newly captured Sentinel-2 scenes throughout the year.
sentinel2020 = HF.get_sentinel_composite("COPERNICUS/S2_SR_HARMONIZED", 2020, aoi_def.aoi)
sentinel2025 = HF.get_sentinel_composite("COPERNICUS/S2_SR_HARMONIZED", 2025, aoi_def.aoi)
sentinel2026 = HF.get_sentinel_composite("COPERNICUS/S2_SR_HARMONIZED", 2026, aoi_def.aoi)

# To add a future year (e.g. 2030) once its imagery exists, repeat this same
# pattern: a sentinelYYYY composite above, an add_ndvi call below, a
# mangroveYYYY threshold below that, one new LOSS/GAIN legend color pair,
# and the matching layer entries in MAP01/MAP02/MAP03.

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
sentinel2026 = HF.add_ndvi(sentinel2026, "S2")


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
mangrove_2026 = sentinel2026.select("NDVI").gt(ndvi_threshold)

# --------------- LOSS/GAIN legend color ramps -------------------------
# Generated (not hand-picked) as single-hue OKLCH ramps with evenly spaced
# lightness steps, so classes stay both distinguishable from each other and
# legible against the white legend background as more year-classes get
# added over time. Verified against the project's palette accessibility
# checks (single hue, monotone lightness, adjacent-step lightness gap,
# light-end contrast >= 2:1) - see README.md > "Legend color ramps".
#
# To add a class (e.g. once 2030 exists): bump n_classes below by one and
# re-run the validator on the new hex list; if a check fails, widen
# l_floor/l_ceil or lower chroma slightly and re-run.
def _oklch_to_hex(lightness, chroma, hue_deg):
    hue = math.radians(hue_deg)
    a = chroma * math.cos(hue)
    b = chroma * math.sin(hue)
    l_ = lightness + 0.3963377774 * a + 0.2158037573 * b
    m_ = lightness - 0.1055613458 * a - 0.0638541728 * b
    s_ = lightness - 0.0894841775 * a - 1.2914855480 * b
    l3, m3, s3 = l_ ** 3, m_ ** 3, s_ ** 3
    r_lin = 4.0767416621 * l3 - 3.3077115913 * m3 + 0.2309699292 * s3
    g_lin = -1.2684380046 * l3 + 2.6097574011 * m3 - 0.3413193965 * s3
    b_lin = -0.0041960863 * l3 - 0.7034186147 * m3 + 1.7076147010 * s3

    def to_srgb_byte(c):
        c = min(1.0, max(0.0, c))
        c = 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
        return max(0, min(255, math.floor(c * 255 + 0.5)))

    return "#{:02X}{:02X}{:02X}".format(
        to_srgb_byte(r_lin), to_srgb_byte(g_lin), to_srgb_byte(b_lin)
    )


def _sequential_ramp(n_classes, hue_deg, chroma, l_floor, l_ceil, light_first):
    step = (l_ceil - l_floor) / (n_classes - 1)
    lightness_steps = [
        (l_ceil - i * step) if light_first else (l_floor + i * step)
        for i in range(n_classes)
    ]
    return [_oklch_to_hex(l, chroma, hue_deg) for l in lightness_steps]


# LOSS: dark (oldest) -> light (most recent), purple/magenta hue.
(
    color_1988_1992_loss, color_1992_1997_loss, color_1997_2001_loss,
    color_2001_2005_loss, color_2005_2010_loss, color_2010_2015_loss,
    color_2015_2020_loss, color_2020_2025_loss, color_2025_2026_loss,
) = _sequential_ramp(
    n_classes=9, hue_deg=320, chroma=0.09, l_floor=0.14, l_ceil=0.74, light_first=False
)

# GAIN: light (oldest) -> dark (most recent), green hue.
(
    color_1988_1992_gain, color_1992_1997_gain, color_1997_2001_gain,
    color_2001_2005_gain, color_2005_2010_gain, color_2010_2015_gain,
    color_2015_2020_gain, color_2020_2025_gain, color_2025_2026_gain,
) = _sequential_ramp(
    n_classes=9, hue_deg=150, chroma=0.15, l_floor=0.12, l_ceil=0.68, light_first=True
)

# --------------- Set Color for COVERAGE layers and legend -----------------
color_mangrove_coverage = "#1a9850"

# -------------- Set color for shapefile layers --------------------
color_commune = "#008B8B"
color_sea_dike = "#F18D09"
color_breakwater = "#E6EE0F" 

