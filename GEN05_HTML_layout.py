#!/usr/bin/env python
# coding: utf-8

# In[1]:

import folium
import GEN04_mangrove_layers as ML

# ### Legend
# Three different legend dictionaries for the mangrove loss, gain, and coverage maps

# In[2]:


# --------------Add Legend --------------------
legend_dict_mangrove_LOSS = {
    "Mangrove loss (1984-1992)": ML.color_1988_1992_loss,
    "Mangrove loss (1992-1997)": ML.color_1992_1997_loss,
    "Mangrove loss (1997-2001)": ML.color_1997_2001_loss,
    "Mangrove loss (2001-2005)": ML.color_2001_2005_loss,
    "Mangrove loss (2005-2010)": ML.color_2005_2010_loss,
    "Mangrove loss (2010-2015)": ML.color_2010_2015_loss,
    "Mangrove loss (2015-2020)": ML.color_2015_2020_loss,
    "Mangrove loss (2020-2025)": ML.color_2020_2024_loss 
    # "Breakwaters": color_breakwater,
    # "Seadikes": color_seadike
    }
legend_dict_mangrove_GAIN = {
    "Mangrove gain (1984-1990)": ML.color_1988_1992_gain,
    "Mangrove gain (1990-1995)": ML.color_1992_1997_gain,
    "Mangrove gain (1995-2000)": ML.color_1997_2001_gain,
    "Mangrove gain (2000-2005)": ML.color_2001_2005_gain,
    "Mangrove gain (2005-2010)": ML.color_2005_2010_gain,
    "Mangrove gain (2010-2015)": ML.color_2010_2015_gain,
    "Mangrove gain (2015-2020)": ML.color_2015_2020_gain,
    "Mangrove gain (2020-2025)": ML.color_2020_2024_gain,
}

legend_dict_mangrove_COVERAGE = {
    "Mangrove coverage": ML.color_mangrove_coverage
}

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
def add_folium_legend(m, title, legend_dict, style=None):
    """Add a custom legend to a folium map."""
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


# ### Scalebar

# In[3]:


from branca.element import MacroElement, Element
from jinja2 import Template

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


# ### North Arrow

# In[4]:


# ----------- north arrow ----------------
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
     <img src="images/Living_lab_logo_optie_1.png" height="80px" style="width:auto;">
</div>
"""

