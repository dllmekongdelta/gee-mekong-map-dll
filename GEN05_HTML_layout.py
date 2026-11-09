#!/usr/bin/env python
# coding: utf-8

# In[1]:

import folium
import GEN04_mangrove_layers as ML

# ### Legend
# Three different legend dictionaries for the mangrove loss, gain, and coverage maps

# In[2]:


# -------------- Create legend for different maps --------------------
legend_dict_mangrove_LOSS = {
    "Mangrove loss (1988-1992)": ML.color_1988_1992_loss,
    "Mangrove loss (1992-1997)": ML.color_1992_1997_loss,
    "Mangrove loss (1997-2001)": ML.color_1997_2001_loss,
    "Mangrove loss (2001-2005)": ML.color_2001_2005_loss,
    "Mangrove loss (2005-2010)": ML.color_2005_2010_loss,
    "Mangrove loss (2010-2015)": ML.color_2010_2015_loss,
    "Mangrove loss (2015-2020)": ML.color_2015_2020_loss,
    "Mangrove loss (2020-2025)": ML.color_2020_2025_loss,
    "Mangrove loss (2025-2026)": ML.color_2025_2026_loss,
    "Commune boundaries": ML.color_commune,
    "Sea dikes": ML.color_sea_dike,
    "Breakwaters": ML.color_breakwater,
    "Revetments": ML.color_revetment
    }
legend_dict_mangrove_GAIN = {
    "Mangrove gain (1988-1992)": ML.color_1988_1992_gain,
    "Mangrove gain (1992-1997)": ML.color_1992_1997_gain,
    "Mangrove gain (1997-2001)": ML.color_1997_2001_gain,
    "Mangrove gain (2001-2005)": ML.color_2001_2005_gain,
    "Mangrove gain (2005-2010)": ML.color_2005_2010_gain,
    "Mangrove gain (2010-2015)": ML.color_2010_2015_gain,
    "Mangrove gain (2015-2020)": ML.color_2015_2020_gain,
    "Mangrove gain (2020-2025)": ML.color_2020_2025_gain,
    "Mangrove gain (2025-2026)": ML.color_2025_2026_gain,
    "Commune boundaries": ML.color_commune,
    "Sea dikes": ML.color_sea_dike,
    "Breakwaters": ML.color_breakwater,
    "Revetments": ML.color_revetment
}

legend_dict_mangrove_COVERAGE = {
    "Mangrove coverage": ML.color_mangrove_coverage,
    "Commune boundaries": ML.color_commune,
    "Sea dikes": ML.color_sea_dike,
    "Breakwaters": ML.color_breakwater,
    "Revetments": ML.color_revetment
}
# -------- Legend style ----------
style = {
    "position": "fixed",
    "z-index": "9999",
    "border": "2px solid grey",
    "background-color": "rgba(255, 255, 255, 0.8)",
    "border-radius": "10px",
    "padding": "5px",
    "font-size": "14px",
    "bottom": "20px",
    "right": "5px",
}

# -----------Add a custom legend to a folium map --------

def add_folium_legend(m, title, legend_dict, style=None):
    if style is None:
        style = {
            "position": "fixed",
            "z-index": "9999",
            "border": "2px solid grey",
            "background-color": "rgba(255, 255, 255, 0.8)",
            "border-radius": "10px",
            "padding": "5px",
            "font-size": "14px",
            "bottom": "20px",
            "right": "5px",
        }

    style_str = ";".join([f"{k}:{v}" for k, v in style.items()])
    legend_html = f'<div style="{style_str}">'
    legend_html += f"<b>{title}</b><br>"

    for label, color in legend_dict.items():
        legend_html += (
            f'<i style="background:{color};width:15px;height:15px;'
            f'display:inline-block;margin-right:5px;"></i>{label}<br>'
        )

    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))


# ### Page title & favicon
# folium's Map.to_html() doesn't set a <title> or favicon by default, so the
# browser tab falls back to showing the raw filename and a generic icon.

# In[2b]:


def set_page_meta(m, title, favicon="images/logo/icon.png"):
    m.get_root().title = title
    m.get_root().header.add_child(
        folium.Element(f'<link rel="icon" href="{favicon}" type="image/png">')
    )


# ### Basemap
# Google Hybrid = satellite imagery + road and place-name labels. Added
# directly as a tile layer: geemap's add_basemap('HYBRID') is actually Esri
# World Imagery without labels, not Google.

# In[2c]:


def add_google_hybrid(m):
    # Drop any base layer the Map already has, so Google Hybrid is the only
    # (and therefore default) basemap. Needed because the geemap version CI
    # installs (0.20, requirements.txt) always adds OpenStreetMap and ignores
    # basemap=None; newer geemap honours it. Overlays (GEE layers, shapefiles)
    # are kept -- and are normally added after this call anyway.
    for key, child in list(m._children.items()):
        if isinstance(child, folium.TileLayer) and not child.overlay:
            del m._children[key]

    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Hybrid",
        max_zoom=22,
        overlay=False,
        control=True,
    ).add_to(m)


# Google Roads = road map without satellite imagery. Optional second base layer,
# off at start; call after add_google_hybrid, which removes existing base layers.
def add_google_roads(m):
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google",
        name="Google Roads",
        max_zoom=22,
        overlay=False,
        control=True,
        show=False,
    ).add_to(m)


# ### Scalebar

# In[3]:


from branca.element import MacroElement, Element   # Low-level HTML/JS elements for Folium/Branca maps
from jinja2 import Template                        #jinja2 generates the HTML/JS template for adding the scale bar to the map.

class ScaleBar(MacroElement):
    _template = Template(u"""
        {% macro script(this, kwargs) %}
        L.control.scale({
            position: 'bottomleft',
            metric: true,
            imperial: false,
            maxWidth: 300
        }).addTo({{this._parent.get_name()}});
        {% endmacro %}
    """)

    def __init__(self, position="bottomleft", metric=True, imperial=False, max_width=300, font_size="16px"):
        super().__init__()
        self._name = "ScaleBar"
        self.position = position
        self.metric = metric
        self.imperial = imperial
        self.max_width = max_width
        self.font_size = font_size

    def render(self, **kwargs):
        super().render(**kwargs)
        # Inject CSS for larger font
        css = f"""
        <style>
        .leaflet-control-scale-line {{
            font-size: {self.font_size} !important;
            font-weight: bold;
        }}
        </style>
        """
        self.get_root().html.add_child(Element(css))


# ### Play control (time slider)
# Shows ONE year layer at a time and steps through them (play / pause, prev /
# next, slider, speed). Needed because with every year layer switched on, the
# layers stack and the map shows the union of all years, not any single year.
# Rendered as a MacroElement child of the map so its script runs after the
# tile layers it references (children render in the order they were added).

# In[3b]:


import json


class PlayControl(MacroElement):
    _template = Template(u"""
        {% macro html(this, kwargs) %}
        <div id="{{ this.get_name() }}" style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
             z-index: 9999; background: rgba(255,255,255,0.85); border-radius: 8px; padding: 3px 10px 5px;
             box-shadow: 0 0 4px rgba(0,0,0,0.3); text-align: center; color: #111; white-space: nowrap;
             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <div style="font-size: 13px; font-weight: 600; line-height: 1.2;">{{ this.title }}
                <span class="pc-year" style="font-size: 20px; font-weight: 800; margin-left: 2px;"></span></div>
            <div style="display: flex; align-items: center; gap: 4px; justify-content: center; margin-top: 2px;">
                <button class="pc-prev" title="Previous year" style="font-size: 11px; padding: 1px 5px; cursor: pointer;">&#9198;</button>
                <button class="pc-play" title="Play / pause" style="font-size: 11px; padding: 1px 5px; cursor: pointer; min-width: 30px;">&#9654;</button>
                <button class="pc-next" title="Next year" style="font-size: 11px; padding: 1px 5px; cursor: pointer;">&#9197;</button>
                <input class="pc-slider" type="range" min="0" max="{{ this.layer_vars|length - 1 }}" step="1"
                       style="width: 140px; height: 14px; margin: 0 2px; cursor: pointer;">
                <select class="pc-speed" title="Seconds per year" style="font-size: 11px; padding: 0;">
                    <option value="800">0.8 s</option><option value="1500" selected>1.5 s</option>
                    <option value="2500">2.5 s</option>
                </select>
            </div>
        </div>
        {% endmacro %}
        {% macro script(this, kwargs) %}
        (function () {
            var map = {{ this._parent.get_name() }};
            var layers = [{% for n in this.layer_vars %}{{ n }}, {% endfor %}];
            var labels = {{ this.labels_json }};
            var box = document.getElementById('{{ this.get_name() }}');
            var yearEl = box.querySelector('.pc-year'), slider = box.querySelector('.pc-slider');
            var playBtn = box.querySelector('.pc-play'), speed = box.querySelector('.pc-speed');
            L.DomEvent.disableClickPropagation(box);
            L.DomEvent.disableScrollPropagation(box);
            var i = {{ this.start }}, timer = null;
            // Every year layer stays on the map (tiles preloaded, hidden at
            // opacity 0) and years crossfade, instead of remove/add, which
            // reloads tiles and makes the map blink between years.
            var base = layers.map(function (l) { return l.options.opacity == null ? 1 : l.options.opacity; });
            function setOp(l, op, dur, delay) {
                var c = l.getContainer && l.getContainer();
                if (c) { c.style.transition = dur ? 'opacity ' + dur + 'ms ease-in-out ' + (delay || 0) + 'ms' : 'none'; }
                l.setOpacity(op);
            }
            function show(j, dur) {
                var prev = i;
                i = (j + layers.length) % layers.length;
                layers.forEach(function (l) { if (!map.hasLayer(l)) { map.addLayer(l); } });
                dur = dur || 0;
                layers.forEach(function (l, k) {
                    if (k === i) { setOp(l, base[k], dur, 0); }
                    // old year fades out half a step later: areas present in both years stay solid
                    else if (k === prev && dur) { setOp(l, 0, dur, dur / 2); }
                    else { setOp(l, 0, 0, 0); }
                });
                yearEl.textContent = labels[i];
                slider.value = i;
            }
            function fade() { return Math.min(900, parseInt(speed.value, 10) * 0.6); }
            function stop() { if (timer) { clearInterval(timer); timer = null; } playBtn.innerHTML = '&#9654;'; }
            function play() {
                stop();
                playBtn.innerHTML = '&#10074;&#10074;';
                timer = setInterval(function () { show(i + 1, fade()); }, parseInt(speed.value, 10));
            }
            playBtn.onclick = function () { if (timer) { stop(); } else { play(); } };
            box.querySelector('.pc-prev').onclick = function () { stop(); show(i - 1, 400); };
            box.querySelector('.pc-next').onclick = function () { stop(); show(i + 1, 400); };
            slider.oninput = function () { stop(); show(parseInt(slider.value, 10), 250); };
            speed.onchange = function () { if (timer) { play(); } };
            show(i);
        })();
        {% endmacro %}
    """)

    def __init__(self, layers, labels, title="Mangrove coverage", start=None):
        super().__init__()
        self._name = "PlayControl"
        self.layer_vars = [layer.get_name() for layer in layers]
        self.labels_json = json.dumps([str(x) for x in labels])
        self.title = title
        self.start = len(layers) - 1 if start is None else start


def add_play_control(m, layer_names, labels, title="Mangrove coverage"):
    # layer_names: the names given to Map.addLayer, in time order. Looks the
    # folium tile layers up by name so callers keep using geemap's addLayer.
    by_name = {getattr(c, "layer_name", None): c for c in m._children.values()}
    missing = [n for n in layer_names if n not in by_name]
    if missing:
        raise ValueError(f"add_play_control: layers not found on map: {missing}")
    m.add_child(PlayControl([by_name[n] for n in layer_names], labels, title=title))


# ### North Arrow

# In[4]:


# ----------- Dunction to add North arrow ----------------
def add_north_arrow(m, position="topright", arrow_size="35px", text_size="25px"):
    arrow_css = f"""
        <div style="
            position: absolute; 
            { 'top: 10px; right: 10px;' if position=='topright' else '' }
            { 'top: 10px; left: 10px;' if position=='topleft' else '' }
            { 'bottom: 10px; right: 10px;' if position=='bottomright' else '' }
            { 'bottom: 30px; left: 10px;' if position=='bottomleft' else '' }
            z-index: 9999; 
            font-weight: bold; 
            color: black;
            text-shadow: 1px 1px 2px white;
            display: flex;
            align-items: center;
        ">
            <span style="font-size:{arrow_size}; line-height:1;">↑</span>
            <span style="font-size:{text_size}; margin-left: 4px; line-height:1;">N</span>
        </div>
    """
    m.get_root().html.add_child(folium.Element(arrow_css))


# # Logo
# This part sets the logo of the living lab on the map using HTML.

# In[5]:

# --------- Sets logo 
logo_html = """
<div style="
     position: fixed;
     top: 10px;
     left: 50px;                                /* 50px from right edge */
     z-index: 9999;
     background-color: rgba(255, 255, 255, 0.8);  /* semi-transparent white background */
     border-radius: 10px;                         /* rounded corners */
     padding: 4px 8px;                            /* smaller padding (vertical, horizontal) */
     box-shadow: 0px 0px 6px rgba(0,0,0,0.3);     /* subtle shadow */
     text-align: center;                          /* center horizontally */
     display: flex;                               /* enable vertical centering */
     align-items: center;                         /* center vertically */
     justify-content: center;                     /* center horizontally again for safety */
     height: 90px;                                /* smaller white box height */
">
     <img src="images/logo/logo-Living_lab.png" height="80px" style="width:auto;">
</div>
"""


# # Download button
# Adds a floating "download the source data" pill button over the map, for
# layers whose underlying shapefile is worth sharing (e.g. Breakwaters).
# Styled as a real call-to-action (brand gradient, icon, hover lift) rather
# than a discreet text link, so it reads as an actionable UI control instead
# of blending into the corner. Default position is bottom-right, stacked
# directly above the legend (same right-edge alignment) -- pass `bottom` per
# map to clear that map's legend height, since row count (and so legend
# height) varies: LOSS/GAIN's legends are much taller (9 interval classes +
# 3 context layers) than COVERAGE's (1 class + 3 context layers).
# Uses the fa-download glyph from Font Awesome Free 6, which folium already
# bundles on every map (verified in the generated HTML: @fortawesome/
# fontawesome-free@6.2.0/css/all.min.css) -- "fas" prefix to match the solid
# style used elsewhere on the site (index.html's "Open Full Screen" link).

# In[5b]:


def add_download_button(m, url, label, top=None, right="5px", bottom="150px", left=None):
    pos = {"top": top, "right": right, "bottom": bottom, "left": left}
    pos_css = "\n         ".join(f"{k}: {v};" for k, v in pos.items() if v is not None)
    button_html = f"""
    <div style="
         position: fixed;
         {pos_css}
         z-index: 9999;
    ">
        <a href="{url}" download style="
             display: inline-flex;
             align-items: center;
             gap: 8px;
             background: linear-gradient(135deg, #006d2c 0%, #1a9850 100%);
             color: #ffffff;
             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
             font-size: 13px;
             font-weight: 600;
             text-decoration: none;
             padding: 10px 16px;
             border-radius: 24px;
             box-shadow: 0 4px 10px rgba(0,0,0,0.3);
             transition: transform 0.15s ease, box-shadow 0.15s ease;
             white-space: nowrap;
        " onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 14px rgba(0,0,0,0.35)';"
          onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 10px rgba(0,0,0,0.3)';">
            <i class="fas fa-download"></i> {label}
        </a>
    </div>
    """
    m.get_root().html.add_child(folium.Element(button_html))

