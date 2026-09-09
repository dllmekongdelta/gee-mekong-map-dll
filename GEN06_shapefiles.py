#!/usr/bin/env python
# coding: utf-8

# # Shapefiles
# This file contains the link to all shapefiles, and their layout, that are added to the maps. This consists of seadikes, commune boundaries, breakwaters, wind turbines and other human activities

# ### Commune boundaries

# In[10]:
import GEN04_mangrove_layers as ML


import geopandas as gpd                # Spatial data handling (GeoDataFrames)
import glob                            # File pattern matching (e.g., list all .tif files in a folder)

# ---- Add commune boundaries shapefile ----
commune_path = "shapefile_commune/VungNghiencuu.shp"  # path to your shapefile
# encoding="utf-8": the .dbf has no .cpg sidecar file, so GDAL/pyogrio guesses
# an encoding (cp1252/cp1258) instead of detecting it -- the guess is wrong and
# mangles every Vietnamese diacritic (e.g. "Bình An" -> "BÃ¬nh An"). The .dbf
# itself is UTF-8, confirmed by testing candidate encodings directly.
gdf_commune = gpd.read_file(commune_path, encoding="utf-8")

# Convert GeoDataFrame to GeoJSON for Folium
geojson_commune = gdf_commune.__geo_interface__

# Optional: customize style
commune_style = lambda feature: {
    # "color": "#E74176",       # Red outline
    "color": ML.color_commune,       # Almost black, administrative look
    "weight": 3,              # Line thickness
    # "fillColor": "#E74176",   # Fill color (optional)
    "fillOpacity": 0,        # Transparency
    "opacity": 1,   # 0 = fully transparent, 1 = fully opaque
    "dashArray": "5, 15"       # Ddashed line pattern 
}

# commune_style = lambda feature: {
#     "color": "#008B8B",       # Almost black, administrative look
#     "weight": 2.5,
#     "fillOpacity": 0,
#     "opacity": 0.8,
#     "dashArray": "6, 8"       # Longer dashes = calmer, less busy
# }


# ### Seadikes

# In[11]:


import folium
import pandas as pd
    # ---------------- Add Sea Dikes shapefile ------------------
sea_dikes_path = "shapefile_seadike/SeaDykes_MD_201710_EN.shp"
gdf_sea_dikes = gpd.read_file(sea_dikes_path)

# Replace 'dyke' with 'dike' in the 'Segment' and 'Type' column (case-insensitive)
gdf_sea_dikes["Segment"] = gdf_sea_dikes["Segment"].str.replace("dyke", "dike", case=False)
gdf_sea_dikes["Type"] = gdf_sea_dikes["Type"].str.replace("dyke", "dike", case=False)


sea_dikes_style = lambda feature: {
    "color": ML.color_sea_dike,   # orange
    "weight": 5,
    "fillOpacity": 0
}

# Create a FeatureGroup to hold all segments together
sea_dikes_group = folium.FeatureGroup(name="Sea Dikes")

# Loop through each row (each segment)
for _, row in gdf_sea_dikes.iterrows():
    # Skip rows where SPWs_type is None, or NaN
    if pd.isna(row["SPWs_type"]) or str(row["SPWs_type"]).strip().lower() == "none":
        continue  # <-- skip adding this segment  

    # Build a custom HTML string for the popup
    popup_html = f"""
    <b>Sea dike</b><br><br>
    <img src="images//seadike/sea_dike.jpg" width="200px"><br>
    <br>Segment: {row['Segment']}
    <br>Type: {row['Type']}
    <br>Length (m): {row['Length_m']}
    <!-- <br>SPWs Type:</b> {row['SPWs_type']} -->
    <!-- <br>L_SPWs (m):</b> {row['L_SPWs_m']}<br> --> <br>
    <a href="https://www.livinglabmekongdelta.com/seadike" target="_blank">
    For more information about sea dikes, click here</a>
    """

    # Convert this feature to GeoJSON
    geo_j = folium.GeoJson(
        data=row["geometry"].__geo_interface__,
        style_function=sea_dikes_style
    )

    # Attach the popup
    popup = folium.Popup(popup_html, max_width=350)
    popup.add_to(geo_j)

    # Add feature to the group (not directly to the map)
    geo_j.add_to(sea_dikes_group)


# ### Breakwaters

# In[12]:


# -------------- Add breakwaters ----------------

# Create one feature group for all breakwaters
breakwaters_group = folium.FeatureGroup(name="Breakwaters", show=True)

# Single consolidated shapefile (85 real interventions with Name/Type/Year
# attributes) replaces the old Shapefile1.shp..Shapefile8.shp placeholders,
# which carried no usable attributes and were paired 1:1 by file order with
# 8 hardcoded generic English popup strings that didn't actually describe
# the digitized features. Popups are now built per-feature from the real
# attribute data instead.
#
# encoding="utf-8": no .cpg sidecar next to the .dbf, so GDAL/pyogrio guesses
# an encoding and mangles the Vietnamese diacritics in the Name field -- same
# failure mode as shapefile_commune (see README > "Legend color ramps").
#
# VN-2000 / UTM zone 48N (EPSG:3405): no .prj sidecar either. Raw coordinates
# are in the ~470,000-700,000 / ~950,000-1,150,000 range -- UTM-scale, not
# lon/lat -- consistent with VN-2000 UTM48N, the standard projection for
# Vietnamese government coastal-engineering GIS deliverables (this dataset
# references official programs like DPNSTW/SP-RCC). WGS84 UTM48N (EPSG:32648)
# reprojects to within ~200m of the same spot -- immaterial for a reference
# line layer, but revisit this assumption if the true source CRS is known.
breakwaters_path = "shapefile_breakwaters/Interventions.shp"
gdf_breakwaters = gpd.read_file(breakwaters_path, encoding="utf-8")
gdf_breakwaters = gdf_breakwaters.set_crs(epsg=3405, allow_override=True).to_crs(epsg=4326)

breakwater_style = lambda feature: {
    "color": ML.color_breakwater,       # Yellow outline
    "weight": 5,              # Line thickness
}


def _breakwater_popup(row):
    year = "chưa rõ" if pd.isna(row["Year"]) else int(row["Year"])
    return (
        f"<b>{row['Name']}</b><br><br>"
        f"Loại công trình: {row['Type']}<br>"
        f"Năm xây dựng: {year}<br><br>"
        '<a href="https://www.livinglabmekongdelta.com/breakwaters" target="_blank">'
        "For more information about breakwaters, click here.</a>"
    )


for _, row in gdf_breakwaters.iterrows():
    folium.GeoJson(
        row.geometry.__geo_interface__,
        style_function=breakwater_style,
        popup=folium.Popup(_breakwater_popup(row), max_width=300),
    ).add_to(breakwaters_group)


# 

# In[13]:


# -------------- Add more human activities ----------------------------
Extra_group = folium.FeatureGroup(name="Other human activities", show=True)

# Loop through shapefiles in the folder 
shapefiles_extra = sorted(glob.glob("shapefile_other/*.shp"))

# Define popup text for each shapefile (order matches file order)
popup_texts_extra = [   
    '<b>Nhà Mát resort</b>'
    '<br>Construction year: 2015<br>', 

    '<b>Mangrove reforestation projects</b>'
    '<br>2000-2010: 150-200 hectares'
    '<br>2015-2020: 201 hectares'
    '<br>2019: more than 2000 mangrove trees<br><br>'
    '<a href="https://www.livinglabmekongdelta.com/mangrovereforestation" target="_blank">For more information about mangrove restoration, click here</a>', 

    '<b>Aquaculture</b>', 

    '<b>Wind park</b>', 

    '<b>Urban area</b>'   
]

# Define matching icons (Font Awesome 4.7 icons supported by Folium)
icons_extra = [
    ("hotel", "darkblue"),   # For resort
    ("seedling", "green"),    # For mangrove reforestation
    ("fish", "lightblue"),    # For aquaculture
    ("bolt", "lightgray"),    # For windmill farm
    ("house", "darkred")     # For urban area
]

for shp, popup_html, (icon_name, icon_color) in zip(shapefiles_extra, popup_texts_extra, icons_extra):
    gdf = gpd.read_file(shp)

    # Extract the single point geometry
    point = gdf.geometry.iloc[0]

    if point.geom_type == "Point":
        lon, lat = point.x, point.y

        # Add marker with popup and appropriate icon
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(icon=icon_name, prefix="fa", color=icon_color)
        ).add_to(Extra_group)



# In[ ]:
