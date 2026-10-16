#!/usr/bin/env python
# coding: utf-8

# # Shapefiles
# This file contains the link to all shapefiles, and their layout, that are added to the maps. This consists of seadikes, commune boundaries, breakwaters, wind turbines and other human activities

# ### Commune boundaries

# In[10]:
import GEN04_mangrove_layers as ML


import geopandas as gpd                # Spatial data handling (GeoDataFrames)

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


# -------------- Add breakwaters & revetments ----------------

# Two feature groups so each can be toggled independently in the layer
# control -- the shapefile's Type field distinguishes them:
#   "Kè xa bờ"  (offshore/detached breakwater)  -> breakwaters_group, yellow
#   "Kè sát bờ" (nearshore/attached revetment)   -> revetments_group,  blue
breakwaters_group = folium.FeatureGroup(name="Breakwaters", show=True)
revetments_group = folium.FeatureGroup(name="Revetments", show=True)

TYPE_BREAKWATER = "Kè xa bờ"
TYPE_REVETMENT = "Kè sát bờ"

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
# WGS84 / UTM zone 48N (EPSG:32648): no .prj sidecar either. Raw coordinates
# are in the ~470,000-700,000 / ~950,000-1,150,000 range -- UTM-scale, not
# lon/lat. An earlier version of this file guessed VN-2000/UTM48N (EPSG:3405)
# instead, which put every feature ~200m off from its true position --
# confirmed WGS84 by whoever produced the source data.
breakwaters_path = "shapefile_breakwaters/Interventions.shp"
gdf_breakwaters = gpd.read_file(breakwaters_path, encoding="utf-8")
gdf_breakwaters = gdf_breakwaters.set_crs(epsg=32648, allow_override=True).to_crs(epsg=4326)


def _breakwater_popup(row):
    # English by default (Name_EN/Type_EN/Prov_EN), matching the rest of the
    # site's UI language; the original Vietnamese Name is kept as a small
    # reference line underneath so the entry stays traceable to its source.
    year = "unknown" if pd.isna(row["Year"]) else int(row["Year"])
    return (
        f"<b>{row['Name_EN']}</b><br><br>"
        f"Type: {row['Type_EN']}<br>"
        f"Province: {row['Prov_EN']}<br>"
        f"Year built: {year}<br><br>"
        f'<span style="color:#888; font-size:11px;">{row["Name"]}</span><br><br>'
        '<a href="https://www.livinglabmekongdelta.com/breakwaters" target="_blank">'
        "For more information about breakwaters, click here.</a>"
    )


for _, row in gdf_breakwaters.iterrows():
    is_revetment = row["Type"] == TYPE_REVETMENT
    color = ML.color_revetment if is_revetment else ML.color_breakwater
    group = revetments_group if is_revetment else breakwaters_group
    folium.GeoJson(
        row.geometry.__geo_interface__,
        style_function=lambda feature, color=color: {"color": color, "weight": 5},
        popup=folium.Popup(_breakwater_popup(row), max_width=300),
    ).add_to(group)


# 

# In[13]:


# Other human activities (resort, reforestation, aquaculture, wind park, urban
# area) are built further down, in "Other human activities", because they
# share the icon/photo-gallery helpers defined with the field sites.


# ### Field sites
# Pinned survey points. To add/move a site, edit FIELD_SITES below (coordinates
# are pasted as degrees-minutes-seconds, exactly as Google Maps shows them).
# The popup shows the site name, a picture of the area and the nearest
# breakwater/revetment from Interventions.shp with its construction year --
# looked up automatically, so it stays correct when the shapefile is updated.

# In[14]:


import os
import re
from branca.element import MacroElement
from jinja2 import Template
from shapely.geometry import Point

# (name, coordinates -- DMS '9°48\'04.3"N 106°37\'43.9"E' or decimal
#  '9.80119, 106.62886', both as copied from Google Maps, kind -- key of
#  SITE_ICONS, photos -- None, one path or a list of paths (the satellite
#  snapshot is always added last), show nearest structure -- False for sites
#  with no intervention nearby)
FIELD_SITES = [
    ("Biển Tân Điền, Đồng Tháp",        '10°21\'30.5"N 106°46\'58.4"E', "site",
     ["images/sites/Tan_Dien_1.JPG", "images/sites/Tan_Dien_2.JPG", "images/sites/Tan_Dien_3.JPG"], True),
    ("Biển Cồn Lớn, Vĩnh Long",         '9°48\'04.3"N 106°37\'43.9"E',  "site",
     ["images/sites/Con_Lon_1.JPG", "images/sites/Con_Lon_2.JPG"], True),
    ("Duyên Hải, Vĩnh Long",            '9°33\'46.0"N 106°30\'18.3"E',  "site",
     ["images/sites/DuyenHai_1.JPG"], True),
    ("Trạm Thủy Văn Đại Ngãi, Cần Thơ", '9°44\'04.6"N 106°04\'27.1"E',  "station", 
     ["images/sites/Dai_Ngai_1.JPG", "images/sites/Dai_Ngai_2.JPG"], False),
    ("Vĩnh Hải, Cần Thơ",               '9°21\'13.2"N 106°09\'41.3"E',  "site",   
     ["images/sites/Vinh_Hai_1.JPG"], True),
    ("Bến Tàu Vĩnh Châu, Cần Thơ",      '9.293710892642208, 105.97646527660068', "site",
     ["images/sites/VinhChau_1.JPG", "images/sites/VinhChau_2.JPG"], True),
    ("Xã Lai Hòa, Cần Thơ",             '9.252733829491397, 105.84545999974812', "site",
     ["images/sites/Lai_Hoa_1.JPG", "images/sites/Lai_Hoa_2.JPG"], True),
    ("Resort Nhà Mát, Cà Mau",          '9.202301533249663, 105.74505836416586', "site",
      ["images/sites/Nha_Mat_1.JPG", "images/sites/Nha_Mat_2.jpeg"], True),
]

# Round badge per kind: (Font Awesome 6 glyph, background color), used by both
# FIELD_SITES and OTHER_ACTIVITIES. Glyphs: https://fontawesome.com/v6/search?ic=free
SITE_ICONS = {
    "site":          ("fa-flag",     "#c62828"),   # field survey site
    "station":       ("fa-droplet",  "#0277bd"),   # hydrological station
    "resort":        ("fa-hotel",    "#1f3f77"),
    "reforestation": ("fa-seedling", "#2e7d32"),
    "aquaculture":   ("fa-fish",     "#3a9ad9"),
    "wind":          ("fa-bolt",     "#6d6d6d"),
    "urban":         ("fa-house",    "#8e2a2a"),
}


def _site_icon(kind):
    glyph, bg = SITE_ICONS[kind]
    return folium.DivIcon(
        html=(
            f'<div style="width:28px; height:28px; border-radius:50%; background:{bg};'
            ' border:2px solid #fff; box-shadow:0 1px 4px rgba(0,0,0,.5);'
            ' display:flex; align-items:center; justify-content:center;">'
            f'<i class="fa-solid {glyph}" style="color:#fff; font-size:13px;"></i></div>'
        ),
        icon_size=(28, 28),
        icon_anchor=(14, 14),
        class_name="field-site-icon",  # replaces Leaflet's default white box
    )


def _parse_coords(coords):
    """'10°21'30.5"N 106°46'58.4"E' or '10.358472, 106.782889'
    -> (10.358472, 106.782889)"""
    parts = re.findall(r"""(\d+)°(\d+)'([\d.]+)"([NSEW])""", coords)
    if not parts:
        lat, lon = (float(v) for v in coords.split(","))
        return lat, lon
    vals = []
    for d, m, s, hemi in parts:
        v = int(d) + int(m) / 60 + float(s) / 3600
        vals.append(-v if hemi in "SW" else v)
    return vals[0], vals[1]


def _area_image_url(lat, lon, size=(400, 260), half_size=0.006):
    # Static satellite snapshot (~1.3 km wide) from Esri World Imagery -- no
    # local image file needed. Esri renders it on request, so the popup asks
    # for a small one and the lightbox for a large one.
    bbox = f"{lon - half_size},{lat - half_size * 0.65},{lon + half_size},{lat + half_size * 0.65}"
    return (
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export"
        f"?bbox={bbox}&bboxSR=4326&imageSR=3857&size={size[0]},{size[1]}&format=jpg&f=image"
    )


PHOTO_THUMB_DIR = "images/sites/thumbs"   # made by resize_site_photos.py


def _photo_sources(label, photos, lat, lon):
    # None / one path / list of paths -> [(thumbnail, full image), ...] for
    # the existing local photos, plus the satellite snapshot last. The popup
    # shows the small thumbnail; the full image only loads in the lightbox.
    # A photo without a thumbnail in PHOTO_THUMB_DIR falls back to itself.
    # Missing files are reported, not fatal.
    if isinstance(photos, str):
        photos = [photos]
    missing = [p for p in photos or [] if not os.path.exists(p)]
    if missing:
        print(f"[{label}] photo not found, skipped: {missing}")
    pairs = []
    for p in photos or []:
        if p in missing:
            continue
        thumb = os.path.join(PHOTO_THUMB_DIR, os.path.basename(p)).replace("\\", "/")
        pairs.append((thumb if os.path.exists(thumb) else p, p))
    pairs.append((_area_image_url(lat, lon, size=(168, 124)),
                  _area_image_url(lat, lon, size=(1000, 650))))
    return pairs


def _gallery_html(sources, site_name):
    # Small thumbnails; clicking one opens the lightbox (fsOpen, defined by
    # _SiteLightbox below) on its full image, browsable with the site's others.
    # Folium popups are regular DOM, not iframes, so inline onclick works.
    html = '<div class="fs-gallery">'
    for k, (thumb, full) in enumerate(sources):
        is_sat = k == len(sources) - 1
        caption = f"{site_name} – satellite view (Esri)" if is_sat else site_name
        html += (
            f'<img class="fs-thumb" src="{thumb}" data-full="{full}" data-caption="{caption}"'
            ' onclick="fsOpen(this)">'
        )
    return html + "</div>"


class _SiteLightbox(MacroElement):
    # Page-level modal + CSS/JS for the field-site photo galleries. Added as a
    # child of sites_group, so every map that adds the group gets it -- no
    # change needed in the MAP notebooks.
    _template = Template("""
    {% macro header(this, kwargs) %}
    <style>
      .fs-gallery { display:grid; grid-template-columns:repeat(3, 84px); gap:4px; }
      .fs-thumb { width:84px; height:62px; object-fit:cover; border-radius:4px;
                  cursor:zoom-in; border:1px solid #ccc; transition:transform .15s, box-shadow .15s; }
      .fs-thumb:hover { transform:scale(1.05); box-shadow:0 2px 8px rgba(0,0,0,.35); }
      #fs-modal { position:fixed; inset:0; z-index:10000; display:flex; align-items:center;
                  justify-content:center; flex-direction:column; background:rgba(0,0,0,.85);
                  opacity:0; visibility:hidden; transition:opacity .25s, visibility .25s; }
      #fs-modal.open { opacity:1; visibility:visible; }
      #fs-modal img { max-width:90vw; max-height:80vh; border-radius:6px;
                      box-shadow:0 8px 30px rgba(0,0,0,.6); transform:scale(.92);
                      transition:transform .25s; }
      #fs-modal.open img { transform:scale(1); }
      #fs-caption { color:#eee; margin-top:10px; font:14px sans-serif; }
      .fs-btn { position:absolute; color:#fff; font:36px sans-serif; cursor:pointer;
                user-select:none; padding:10px 18px; opacity:.8; }
      .fs-btn:hover { opacity:1; }
      #fs-close { top:10px; right:14px; }
      #fs-prev { left:10px; top:50%; transform:translateY(-50%); }
      #fs-next { right:10px; top:50%; transform:translateY(-50%); }
    </style>
    {% endmacro %}

    {% macro html(this, kwargs) %}
    <div id="fs-modal" onclick="if (event.target === this) fsClose()">
      <span id="fs-close" class="fs-btn" onclick="fsClose()">&times;</span>
      <span id="fs-prev" class="fs-btn" onclick="fsStep(-1)">&#8249;</span>
      <img id="fs-img" src="">
      <span id="fs-next" class="fs-btn" onclick="fsStep(1)">&#8250;</span>
      <div id="fs-caption"></div>
    </div>
    <script>
      var fsList = [], fsIdx = 0;
      function fsShow() {
        var t = fsList[fsIdx];
        document.getElementById('fs-img').src = t.dataset.full || t.src;
        document.getElementById('fs-caption').textContent =
          t.dataset.caption + '  (' + (fsIdx + 1) + ' / ' + fsList.length + ')';
        var multi = fsList.length > 1 ? '' : 'none';
        document.getElementById('fs-prev').style.display = multi;
        document.getElementById('fs-next').style.display = multi;
      }
      function fsOpen(thumb) {
        fsList = Array.from(thumb.parentNode.querySelectorAll('.fs-thumb'));
        fsIdx = fsList.indexOf(thumb);
        fsShow();
        document.getElementById('fs-modal').classList.add('open');
      }
      function fsStep(d) { fsIdx = (fsIdx + d + fsList.length) % fsList.length; fsShow(); }
      function fsClose() { document.getElementById('fs-modal').classList.remove('open'); }
      document.addEventListener('keydown', function (e) {
        if (!document.getElementById('fs-modal').classList.contains('open')) return;
        if (e.key === 'Escape') fsClose();
        if (e.key === 'ArrowLeft') fsStep(-1);
        if (e.key === 'ArrowRight') fsStep(1);
      });
    </script>
    {% endmacro %}
    """)


# Interventions in metres (UTM 48N) for the nearest-structure lookup
_breakwaters_utm = gdf_breakwaters.to_crs(epsg=32648)

sites_group = folium.FeatureGroup(name="Field sites", show=True)
sites_group.add_child(_SiteLightbox())

for i, (name, coords, kind, photos, show_nearest) in enumerate(FIELD_SITES, start=1):
    lat, lon = _parse_coords(coords)
    is_dms = "°" in coords
    sources = _photo_sources(f"Field sites: Site {i}", photos, lat, lon)

    popup_html = (
        f"<b>Site {i}: {name}</b><br>"
        f'<span style="color:#888; font-size:11px;">{coords + " " if is_dms else ""}({lat:.5f}, {lon:.5f})</span><br><br>'
        f"{_gallery_html(sources, name)}<br>"
    )

    if show_nearest:
        site_utm = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(epsg=32648).iloc[0]
        dists = _breakwaters_utm.distance(site_utm)
        nearest = gdf_breakwaters.loc[dists.idxmin()]
        dist_m = dists.min()
        dist_txt = f"{dist_m:.0f} m" if dist_m < 1000 else f"{dist_m / 1000:.1f} km"
        year = "unknown" if pd.isna(nearest["Year"]) else int(nearest["Year"])
        popup_html += (
            f"<b>Nearest structure:</b> {nearest['Name_EN']}<br>"
            f"Type: {nearest['Type_EN']}<br>"
            f"Year built: {year}<br>"
            f"Distance: {dist_txt}<br><br>"
            f'<span style="color:#888; font-size:11px;">{nearest["Name"]}</span>'
        )
    else:
        popup_html += "No coastal structures nearby."

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"Site {i}: {name}",
        icon=_site_icon(kind),
    ).add_to(sites_group)


# ### Other human activities
# Same idea as FIELD_SITES: one line per point, edit freely. Coordinates were
# taken from the old shapefile_other/Shapefile11-15.shp points (which are no
# longer read). The popup shows the name, the description (HTML allowed) and
# the photo gallery; the lightbox comes with sites_group, so the MAP notebooks
# must keep adding sites_group too (they do).

# In[15]:


# (name, coordinates, kind -- key of SITE_ICONS, photos -- like FIELD_SITES,
#  description -- HTML shown under the name, "" for none)
OTHER_ACTIVITIES = [
    ("Nhà Mát resort",                  "9.205039, 105.745670", "resort", None,
     "Construction year: 2015"),
    ("Mangrove reforestation projects", "9.202535, 105.743950", "reforestation", None,
     "2000-2010: 150-200 hectares<br>"
     "2015-2020: 201 hectares<br>"
     "2019: more than 2000 mangrove trees<br><br>"
     '<a href="https://www.livinglabmekongdelta.com/mangrovereforestation" target="_blank">'
     "For more information about mangrove restoration, click here</a>"),
    ("Aquaculture",                     "9.205616, 105.714229", "aquaculture", None, ""),
    ("Wind park",                       "9.22977257587137, 105.85703141310928", "wind",
     ["images/sites/Dien_Gio_1.jpeg", "images/sites/Dien_Gio_2.jpeg"], ""),
    ("Urban area",                      "9.212384, 105.741053", "urban", None, ""),
]

Extra_group = folium.FeatureGroup(name="Other human activities", show=True)

for name, coords, kind, photos, description in OTHER_ACTIVITIES:
    lat, lon = _parse_coords(coords)
    sources = _photo_sources(f"Other activities: {name}", photos, lat, lon)

    popup_html = f"<b>{name}</b><br>"
    if description:
        popup_html += f"{description}<br>"
    popup_html += f"<br>{_gallery_html(sources, name)}"

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=name,
        icon=_site_icon(kind),
    ).add_to(Extra_group)


# In[ ]:
