"""
Map components for dashboard visualization - PERBAIKI IMPORT
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# Import constants dengan error handling
try:
    from src.config.constants import KECAMATAN_COORDINATES, MAP_CENTER
except ImportError:
    # Fallback values if import fails
    MAP_CENTER = {"lat": -8.1, "lon": 112.6}
    KECAMATAN_COORDINATES = {
        'Dau': [-7.9167, 112.5833],
        'Pujon': [-7.8667, 112.4833],
        'Ngantang': [-7.7667, 112.4333],
        # Add more as needed...
    }

def create_folium_map(data=None, map_type="basic", zoom=10):
    """Create folium map"""
    center_lat = MAP_CENTER["lat"]
    center_lon = MAP_CENTER["lon"]
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles='OpenStreetMap'
    )
    
    if data is not None and not data.empty:
        add_markers_to_map(m, data, map_type)
    
    return m

def add_markers_to_map(map_obj, data, map_type):
    """Add markers to folium map based on data type"""
    for _, row in data.iterrows():
        kecamatan = row.get('Kecamatan', row.get('kecamatan', ''))
        coords = KECAMATAN_COORDINATES.get(kecamatan)
        
        if coords:
            # Determine marker properties based on map_type
            if map_type == "disaster":
                value = row.get('Total_Bencana', 0)
                popup_text = f"<b>{kecamatan}</b><br>Bencana: {value} kejadian"
                color = get_disaster_marker_color(value)
            elif map_type == "social":
                value = row.get('Total_Penerima', 0)
                popup_text = f"<b>{kecamatan}</b><br>Penerima: {value:,} orang"
                color = get_social_marker_color(value)
            else:
                popup_text = f"<b>{kecamatan}</b>"
                color = 'blue'
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=kecamatan,
                icon=folium.Icon(color=color)
            ).add_to(map_obj)

def get_disaster_marker_color(value):
    """Get marker color based on disaster value"""
    if value == 0:
        return 'green'
    elif value <= 5:
        return 'lightgreen'
    elif value <= 10:
        return 'orange'
    else:
        return 'red'

def get_social_marker_color(value):
    """Get marker color based on social assistance value"""
    if value == 0:
        return 'red'
    elif value <= 1000:
        return 'orange'
    elif value <= 5000:
        return 'lightblue'
    else:
        return 'green'

def create_choropleth_map(data, geojson, locations_col, color_col, title="Choropleth Map"):
    """Create choropleth map with plotly"""
    fig = px.choropleth_mapbox(
        data,
        geojson=geojson,
        locations=locations_col,
        color=color_col,
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        zoom=8,
        center={"lat": MAP_CENTER["lat"], "lon": MAP_CENTER["lon"]},
        opacity=0.7,
        title=title
    )
    
    fig.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
        height=500
    )
    
    return fig