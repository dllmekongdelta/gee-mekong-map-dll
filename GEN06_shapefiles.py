#!/usr/bin/env python
# coding: utf-8

# # Shapefiles
# This file contains the link to all shapefiles, and their layout, that are added to the maps. This consists of seadikes, commune boundaries, breakwaters, wind turbines and other human activities

# ### Commune boundaries

# In[10]:


import geopandas as gpd
import GEN04_mangrove_layers as ML
import glob
# ---- Add commune boundaries shapefile ----
commune_path = "shapefile_commune/VungNghiencuu.shp"  # path to your shapefile
gdf_commune = gpd.read_file(commune_path)

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
    <br>SPWs Type:</b> {row['SPWs_type']}
    <br>L_SPWs (m):</b> {row['L_SPWs_m']}<br><br>
    <a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">
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

# Define popup text for each shapefile (order matches file order)
popup_texts_BW = [
    '<b>Detached riprap pillar breakwater</b><br><br>'
    '<img src="images/breakwaters/detached_riprap_pillar.JPG" width="200px"><br>'
    '<br>Construction year: 2019.<br>'
    'From 2016-2019, the site was protected by a bamboo fence instead of the breakwater.<br><br>'
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about breakwaters, click here.</a>', 

    '<b>Perforated dome breakwater</b><br><br>'
    '<img src="images/breakwaters/perforated_dome.JPG" width="200px"><br>'
    '<br>Construction year: 2019.<br>'
    'From 2016-2019, the site was protected by a bamboo fence instead of the breakwater.<br><br>'
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about breakwaters, click here.</a>', 

    '<b>Detached riprap pillar breakwater</b><br><br>'
    '<img src="images/breakwaters/detached_riprap_pillar.JPG" width="200px"><br>'
    '<br>Construction year: 2019.<br>'
    'From 2016-2019, the site was protected by a bamboo fence instead of the breakwater.<br><br>'
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about breakwaters, click here.</a>',

    '<b>Detached riprap pillar breakwater</b><br><br>'
    '<img src="images/breakwaters/detached_riprap_pillar.JPG" width="200px"><br>'
    '<br>Construction year: 2019.<br>'
    'From 2016-2019, the site was protected by a bamboo fence instead of the breakwater.<br><br>'
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about breakwaters, click here.</a>', 

    '<b>Detached riprap pillar breakwater</b><br><br>'
    '<img src="images/breakwaters/detached_riprap_pillar.JPG" width="200px"><br>'
    '<br>Construction year: 2019.<br>'
    'From 2016-2019, the site was protected by a bamboo fence instead of the breakwater.<br><br>'
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about breakwaters, click here.</a>', 

    '<b>Detached riprap pillar breakwater</b><br><br>'
    '<img src="images/breakwaters/detached_riprap_pillar.JPG" width="200px"><br>'
    '<br>Construction year: 2019.<br>'
    'From 2016-2019, the site was protected by a bamboo fence instead of the breakwater.<br><br>'
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about breakwaters, click here.</a>', 

    '<b>Revetment</b><br><br>'
    '<img src="images/breakwaters/revetment.jpg" width="200px"><br>'
    '<br>Construction year: 2020.<br><br>'
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about breakwaters, click here.</a>', 

    '<b>Detached riprap pillar breakwater</b><br><br>'
    '<img src="images/breakwaters/detached_riprap_pillar.JPG" width="200px"><br>'
    '<br>Construction year: 2025.<br><br>'
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about breakwaters, click here.</a>', 

]

# Loop through shapefiles in the folder
shapefiles_BW = sorted(glob.glob("shapefile_breakwaters/*.shp"))

breakwater_style = lambda feature: {
    "color": ML.color_breakwater,       # Yellow outline
    "weight": 5,              # Line thickness
}

for shp, popup_html in zip(shapefiles_BW, popup_texts_BW):
    gdf = gpd.read_file(shp)
    geojson_data = gdf.__geo_interface__

    folium.GeoJson(
        geojson_data,
        style_function=breakwater_style,
        popup=folium.Popup(popup_html, max_width=300)
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
    '<a href="https://publish.obsidian.md/livinglab/Mangrove+Living+Lab/1.+Introduction/1.1+Why+Mekong+Delta" target="_blank">For more information about mangrove restoration, click here</a>', 

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
