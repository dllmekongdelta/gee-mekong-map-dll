# Mekong Delta Living Lab

**An Open-Air Laboratory for Coastal Protection and Nature-based Solutions**

Interactive web maps for monitoring mangrove dynamics in the Mekong Delta, Vietnam (1988–2025).

## Features

| Map      | Description                     |
| -------- | ------------------------------- |
| Coverage | Mangrove extent by year         |
| Gain     | Expansion and restoration areas |
| Loss     | Deforestation hotspots          |

Includes sea dikes, breakwaters, and commune boundaries with bilingual support (EN/VI).

## Setup

```bash
pip install -r requirements.txt
earthengine authenticate
```

Run Jupyter notebooks (`MAP01–MAP03`) to generate maps.

## Tech Stack

Google Earth Engine • Geemap • Folium • Leaflet • Bootstrap 5
