"""
Map components for dashboard visualization - PERBAIKI IMPORT
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from src.config.constants import KECAMATAN_COORDINATES, MAP_CENTER
from src.utils.sosial_analyzer import analyze_map_data_generic


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

def create_map_with_data(map_data, map_type, selected_years=None, height=500):
    """Create a map with different data types"""
    try:
        # Create the base map using the center coordinates from constants
        m = folium.Map(
            location=[MAP_CENTER["lat"], MAP_CENTER["lon"]],
            zoom_start=10,
            tiles='OpenStreetMap',
            width='100%',
            height=f'{height}px'
        )
        
        if map_data is not None and not map_data.empty:
            # Tentukan kolom value, unit, dan icon berdasarkan map_type
            if map_type == "Bencana Alam":
                value_col = 'Total_Bencana'
                unit = ' kejadian bencana'
                icon_base = '🌊'
                def get_disaster_icon_color(value, max_val):
                    if value == 0:
                        return 'green', 'ok'
                    elif value <= max_val * 0.3:
                        return 'lightgreen', 'info-sign'
                    elif value <= max_val * 0.6:
                        return 'orange', 'warning-sign'
                    else:
                        return 'red', 'exclamation-sign'
                        
            elif map_type == "Bantuan Sosial":
                value_col = 'Total_Penerima'
                unit = ' penerima bantuan'
                icon_base = '👥'
                def get_bantuan_icon_color(value, max_val):
                    if value == 0:
                        return 'red', 'remove'
                    elif value <= max_val * 0.3:
                        return 'orange', 'user'
                    elif value <= max_val * 0.6:
                        return 'lightblue', 'heart'
                    else:
                        return 'green', 'star'
                        
            elif map_type == "KB Performance":
                value_col = 'Growth_Rate'
                unit = '%'
                icon_base = '📈'
                def get_kb_performance_icon_color(value):
                    if value >= 2:
                        return 'green', 'thumbs-up'
                    elif value >= 0:
                        return 'lightgreen', 'arrow-up'
                    elif value >= -5:
                        return 'orange', 'minus'
                    else:
                        return 'red', 'arrow-down'
                        
            elif map_type == "Peserta KB":
                value_col = 'Total_Peserta'
                unit = ' peserta KB'
                icon_base = '👶'
                def get_peserta_kb_icon_color(value, max_val):
                    if value == 0:
                        return 'red', 'remove'
                    elif value <= max_val * 0.3:
                        return 'orange', 'user'
                    elif value <= max_val * 0.6:
                        return 'lightblue', 'heart'
                    else:
                        return 'green', 'star'
            else:
                return m
            
            if value_col not in map_data.columns:
                return m
            
            max_value = map_data[value_col].max()
            min_value = map_data[value_col].min()
            
            for _, row in map_data.iterrows():
                kecamatan = row['Kecamatan']
                value = row[value_col]
                
                coords = KECAMATAN_COORDINATES.get(kecamatan)
                if coords:
                    # Tentukan warna dan icon berdasarkan jenis data
                    if map_type == "Bencana Alam":
                        color, icon = get_disaster_icon_color(value, max_value)
                    elif map_type == "Bantuan Sosial":
                        color, icon = get_bantuan_icon_color(value, max_value)
                    elif map_type == "KB Performance":
                        color, icon = get_kb_performance_icon_color(value)
                    elif map_type == "Peserta KB":
                        color, icon = get_peserta_kb_icon_color(value, max_value)
                    
                    # Format nilai untuk popup
                    if map_type == "KB Performance":
                        formatted_value = f"{value:.2f}{unit}"
                    else:
                        formatted_value = f"{value:,.0f}{unit}"
                    
                    popup_content = f"""
                    <div style="font-family: Arial, sans-serif; min-width: 200px;">
                        <h4 style="margin: 0; color: #2c3e50;">{kecamatan}</h4>
                        <hr style="margin: 5px 0;">
                        <p style="margin: 5px 0;"><strong>{icon_base} {map_type}:</strong> {formatted_value}</p>
                    </div>
                    """
                    
                    folium.Marker(
                        location=coords,
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=f"{kecamatan}: {formatted_value}",
                        icon=folium.Icon(color=color, icon=icon)
                    ).add_to(m)
        
        return m
        
    except Exception as e:
        return None

def render_interactive_map(map_data, map_type, selected_years, height=500):
    interactive_map = create_map_with_data(map_data, map_type, selected_years, height=height)
    if not interactive_map:
        st.error("❌ Gagal memuat peta. Silakan coba lagi.")
        return None
    return st_folium(interactive_map, width='100%', height=height)

def render_map_statistics(map_data, map_type, selected_years):
    if map_data is None or map_data.empty:
        st.warning(f"⚠️ Data {map_type} tidak tersedia untuk periode yang dipilih.")
        return

    insight = analyze_map_data_generic(map_data, map_type, selected_years)

    if map_type == "KB Performance":
        avg_value = map_data['Growth_Rate'].mean()
        positive_growth = len(map_data[map_data['Growth_Rate'] > 0])
        negative_growth = len(map_data[map_data['Growth_Rate'] < 0])
        top_3 = map_data.nlargest(3, 'Growth_Rate')
        worst_3 = map_data.nsmallest(3, 'Growth_Rate')

        st.markdown(f"""
        <div class="map-stats">
            <div class="map-stat-card">
                <h4>📊 Statistik KB Performance</h4>
                <p><strong>Total Kecamatan:</strong> {len(map_data)}</p>
                <p><strong>Pertumbuhan Positif:</strong> {positive_growth} kecamatan</p>
                <p><strong>Pertumbuhan Negatif:</strong> {negative_growth} kecamatan</p>
            </div>
            <div class="map-stat-card">
                <h4>🔝 Top 3 Pertumbuhan Terbaik</h4>
                {'<br>'.join([f"• {row['Kecamatan']}: {row['Growth_Rate']:.2f}%" for _, row in top_3.iterrows()])}
            </div>
            <div class="map-stat-card">
                <h4>📈 Ringkasan Pertumbuhan</h4>
                <p><strong>Rata-rata Pertumbuhan:</strong> {avg_value:.2f}%</p>
                <p><strong>Tertinggi:</strong> {top_3.iloc[0]['Growth_Rate']:.2f}%</p>
                <p><strong>Terendah:</strong> {worst_3.iloc[0]['Growth_Rate']:.2f}%</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        value_col = map_data.columns[1]
        total_value = map_data[value_col].sum()
        avg_value = map_data[value_col].mean()
        top_3 = map_data.nlargest(3, value_col)

        if map_type == "Bencana Alam":
            unit, avg_text = "kejadian", f"{avg_value:.0f} bencana"
        elif map_type == "Bantuan Sosial":
            unit, avg_text = "penerima", f"{avg_value:.0f} orang"
        elif map_type == "Peserta KB":
            unit, avg_text = "peserta", f"{avg_value:.0f} orang"
        else:
            unit, avg_text = "nilai", f"{avg_value:.0f}"

        st.markdown(f"""
        <div class="map-stats">
            <div class="map-stat-card">
                <h4>📊 Statistik {map_type}</h4>
                <p><strong>Total Kecamatan:</strong> {len(map_data)}</p>
                <p><strong>Total {unit.title()}:</strong> {total_value:,.0f}</p>
            </div>
            <div class="map-stat-card">
                <h4>🔝 Top 3 Kecamatan</h4>
                {'<br>'.join([f"• {row['Kecamatan']}: {row[value_col]:,.0f} {unit}" for _, row in top_3.iterrows()])}
            </div>
            <div class="map-stat-card">
                <h4>📈 Ringkasan Data</h4>
                <p><strong>Rata-rata per Kecamatan:</strong> {avg_text}</p>
                <p><strong>Tertinggi:</strong> {top_3.iloc[0][value_col]:,.0f}</p>
                <p><strong>Terendah:</strong> {map_data[value_col].min():,.0f}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    icon_map = {"Bencana Alam": "🌊", "Bantuan Sosial": "👥", "KB Performance": "📈", "Peserta KB": "👶"}
    icon = icon_map.get(map_type, "📊")

    # Menambahkan jarak vertikal (margin) sebelum kotak info
    st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

    st.info(f"{icon} **Hasil Analisis {map_type}:** {insight}")

def render_map_instructions():
    st.markdown("""
    <div class="instructions">
        <h4 style="font-size: 1.1rem;">🗺️ Penjelasan Marker Peta:</h4>
        <table style="width: 100%; border: none;">
            <tr>
                <td style="width: 50%; vertical-align: top; padding-right: 20px;">
                    <p style="font-size: 1rem; margin-bottom: 6px;"><strong>🌊 Bencana Alam:</strong></p>
                    <p style="font-size: 0.9rem; line-height: 1.2; margin-bottom: 10px;">🟢 <strong>Hijau (Aman):</strong> Tidak ada bencana<br>
                    🟡 <strong>Hijau Muda (Rendah):</strong> Di bawah rata-rata<br>
                    🟠 <strong>Orange (Sedang):</strong> Di atas rata-rata<br>
                    🔴 <strong>Merah (Tinggi):</strong> Daerah rawan bencana</p>
                    <p style="font-size: 1rem; margin-bottom: 6px;"><strong>👥 Bantuan Sosial:</strong></p>
                    <p style="font-size: 0.9rem; line-height: 1.2; margin-bottom: 10px;">🔴 <strong>Merah (Tidak Ada):</strong> Tidak ada penerima<br>
                    🟠 <strong>Orange (Sedikit):</strong> Di bawah rata-rata<br>
                    🔵 <strong>Biru Muda (Sedang):</strong> Mendekati rata-rata<br>
                    🟢 <strong>Hijau (Banyak):</strong> Di atas rata-rata</p>
                </td>
                <td style="width: 50%; vertical-align: top; padding-left: 20px;">
                    <p style="font-size: 1rem; margin-bottom: 6px;"><strong>📈 KB Performance:</strong></p>
                    <p style="font-size: 0.9rem; line-height: 1.2; margin-bottom: 10px;">🟢 <strong>Hijau (Sangat Baik):</strong> Pertumbuhan ≥ 2%<br>
                    🟡 <strong>Hijau Muda (Baik):</strong> Pertumbuhan 0-2%<br>
                    🟠 <strong>Orange (Perhatian):</strong> Penurunan -5% hingga 0%<br>
                    🔴 <strong>Merah (Buruk):</strong> Penurunan > -5%</p>
                    <p style="font-size: 1rem; margin-bottom: 6px;"><strong>👶 Peserta KB:</strong></p>
                    <p style="font-size: 0.9rem; line-height: 1.2; margin-bottom: 10px;">🔴 <strong>Merah (Tidak Ada):</strong> Tidak ada peserta<br>
                    🟠 <strong>Orange (Rendah):</strong> Di bawah rata-rata<br>
                    🔵 <strong>Biru Muda (Sedang):</strong> Mendekati rata-rata<br>
                    🟢 <strong>Hijau (Tinggi):</strong> Di atas rata-rata</p>
                </td>
            </tr>
        </table>
        <p style="text-align: center; margin-top: 8px; font-style: italic; font-size: 0.9rem; color: #888;">💡 Klik marker untuk detail per kecamatan</p>
    </div>
    """, unsafe_allow_html=True)