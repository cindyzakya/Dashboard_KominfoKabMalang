"""
Dashboard Sosial - Modular Version
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import *
from src.components.layouts import render_dashboard_header, render_section_header
from src.components.cards import create_kpi_card
from src.components.filters import create_year_filter
from src.components.maps import create_folium_map, add_markers_to_map
from src.utils.data_loader import load_sosial_data
from src.utils.sosial_analyzer import calculate_kpis, get_available_years
from src.utils.data_processor import clean_numeric_columns, extract_rupiah_value
from src.styles.main import load_sosial_css
from src.config.constants import JENIS_BENCANA_MAPPING, KECAMATAN_COORDINATES

# Page config
st.set_page_config(
    page_title="Dashboard Sosial Kabupaten Malang",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_sosial_css()

# Load data
@st.cache_data
def load_data():
    return load_sosial_data()

# Chart creation functions
def create_penerima_per_tahun_chart(data, selected_years):
    """Create recipients per year chart"""
    try:
        if 'Bantuan Sosial' not in data:
            return None
        
        df = data['Bantuan Sosial'].copy()
        
        tahun_col = None
        penerima_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'tahun' in col_lower:
                tahun_col = col
            elif 'penerima' in col_lower:
                penerima_col = col
        
        if not all([tahun_col, penerima_col]):
            return None
        
        if "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        yearly_data = df.groupby(tahun_col)[penerima_col].agg(['sum', 'mean']).reset_index()
        yearly_data.columns = [tahun_col, 'Total_Penerima', 'Rata_rata_Penerima']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=yearly_data[tahun_col],
            y=yearly_data['Total_Penerima'],
            name='Total Penerima',
            marker_color='#3498db',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=yearly_data[tahun_col],
            y=yearly_data['Rata_rata_Penerima'],
            mode='lines+markers',
            name='Rata-rata Penerima',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Rata-rata dan Jumlah Penerima per Tahun',
            xaxis_title='Tahun',
            yaxis=dict(title='Total Penerima', side='left'),
            yaxis2=dict(title='Rata-rata Penerima', side='right', overlaying='y'),
            height=400,
            legend=dict(x=0, y=1)
        )
        
        return fig
        
    except Exception as e:
        return None

def create_bantuan_donut_chart(data, selected_years):
    """Create social assistance donut chart"""
    try:
        if 'Bantuan Sosial' not in data:
            return None
        
        df = data['Bantuan Sosial'].copy()
        
        program_col = None
        penerima_col = None
        tahun_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'program' in col_lower and 'type' in col_lower:
                program_col = col
            elif 'penerima' in col_lower:
                penerima_col = col
            elif 'tahun' in col_lower:
                tahun_col = col
        
        if not all([program_col, penerima_col]):
            return None
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        chart_data = df.groupby(program_col)[penerima_col].sum().reset_index()
        
        fig = px.pie(
            chart_data,
            values=penerima_col,
            names=program_col,
            title="Distribusi Penerima Bantuan per Program",
            hole=0.4,
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<br>Persentase: %{percent}<br><extra></extra>'
        )
        
        fig.update_layout(height=400)
        return fig
        
    except Exception as e:
        return None

def create_jenis_bencana_pie_chart(data, selected_years):
    """Create disaster type pie chart"""
    try:
        if 'Jenis Bencana' not in data:
            return None
        
        df = data['Jenis Bencana'].copy()
        
        if 'Jenis_Bencana_Nama' in df.columns:
            jenis_col = 'Jenis_Bencana_Nama'
        else:
            if 'Jenis_Bencana' in df.columns:
                df['Jenis_Bencana_Display'] = df['Jenis_Bencana'].astype(str).str.replace('_', ' ').str.title()
                jenis_col = 'Jenis_Bencana_Display'
            else:
                return None
        
        jumlah_col = None
        for col in df.columns:
            if 'jumlah' in col.lower() and df[col].dtype in ['int64', 'float64']:
                jumlah_col = col
                break
        
        if not jumlah_col:
            return None
        
        tahun_col = None
        for col in df.columns:
            if 'tahun' in col.lower():
                tahun_col = col
                break
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df_filtered = df[df[tahun_col].isin(selected_years)]
        else:
            df_filtered = df
        
        if df_filtered.empty:
            return None
        
        chart_data = df_filtered.groupby(jenis_col)[jumlah_col].sum().reset_index()
        chart_data = chart_data[chart_data[jumlah_col] > 0]
        
        if chart_data.empty:
            return None
        
        fig = px.pie(
            chart_data,
            values=jumlah_col,
            names=jenis_col,
            title="Distribusi Jenis Bencana",
            color_discrete_sequence=[
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
            ]
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<br><extra></extra>'
        )
        
        fig.update_layout(height=500)
        return fig
        
    except Exception as e:
        return None

def create_year_chips(available_years, key):
    """Create chip-style year selection"""
    
    if f"selected_years_{key}" not in st.session_state:
        st.session_state[f"selected_years_{key}"] = ["Semua Tahun"]
    
    st.markdown("**📅 Select the Year:**")
    
    # Display selected chips
    if st.session_state[f"selected_years_{key}"]:
        chips_html = '<div class="year-selection-area">'
        for year in st.session_state[f"selected_years_{key}"]:
            chips_html += f'<span class="year-chip selected">{year} ✕</span>'
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="year-selection-area"><em style="color: #ccc;">No years selected</em></div>', unsafe_allow_html=True)
    
    # Available Years section
    st.markdown("**Available Years:**")
    
    # Semua Tahun and Clear All buttons
    col1, col2 = st.columns(2)
    
    with col1:
        semua_tahun_selected = "Semua Tahun" in st.session_state[f"selected_years_{key}"]
        button_text = "✅ Semua Tahun" if semua_tahun_selected else "📋 Semua Tahun"
        if st.button(button_text, key=f"all_years_{key}", use_container_width=True):
            if not semua_tahun_selected:
                st.session_state[f"selected_years_{key}"] = ["Semua Tahun"]
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All", key=f"clear_all_{key}", use_container_width=True):
            st.session_state[f"selected_years_{key}"] = []
            st.rerun()
    
    # Individual Years section
    st.markdown("**Individual Years:**")
    
    cols = st.columns(2)
    
    for i, year in enumerate(available_years):
        col_idx = i % 2
        with cols[col_idx]:
            is_selected = year in st.session_state[f"selected_years_{key}"]
            button_text = f"✅ {year}" if is_selected else f"📅 {year}"
            
            if st.button(button_text, key=f"year_{year}_{key}", use_container_width=True):
                current_selection = st.session_state[f"selected_years_{key}"].copy()
                
                if "Semua Tahun" in current_selection:
                    current_selection.remove("Semua Tahun")
                
                if year in current_selection:
                    current_selection.remove(year)
                else:
                    current_selection.append(year)
                
                if not current_selection:
                    current_selection = ["Semua Tahun"]
                
                st.session_state[f"selected_years_{key}"] = sorted(current_selection, key=lambda x: x if x == "Semua Tahun" else int(x))
                st.rerun()
    
    return st.session_state[f"selected_years_{key}"]

def main():
    # Load data
    with st.spinner("📊 Loading data..."):
        data = load_data()
    
    if not data:
        st.error("❌ Tidak ada data yang berhasil dimuat!")
        return

    # Get available years
    available_years = get_available_years(data)
    
    if not available_years:
        available_years = [2020, 2021, 2022, 2023, 2024]

    # Sidebar filters
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-filter">
            <h3>🔍 Please Filter Here:</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="filter-section">
        """, unsafe_allow_html=True)
        
        selected_years = create_year_chips(available_years, "main")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <h4 style="color: white; margin: 0;">📋 Main Menu</h4>
        </div>
        """, unsafe_allow_html=True)

    # Header
    render_dashboard_header(
        title="🏛️ Dashboard Sosial Kabupaten Malang",
        subtitle="Sistem Monitoring Data Sosial 2020-2024",
        description="📊 Dashboard Interaktif untuk Analisis Data Sosial"
    )

    try:
        # Calculate KPIs
        kpis = calculate_kpis(data, selected_years)
        
        # Display KPIs
        st.markdown("""
        <div class="kpi-section">
            <h3>📊 Indikator Utama Sosial</h3>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            value = int(kpis.get('total_penerima_bantuan', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👥 Total Penerima Bantuan</h4>
                <h2>{value:,}</h2>
                <p>{value} Orang</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            value = int(kpis.get('total_bencana', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>🌊 Total Bencana</h4>
                <h2>{value:,}</h2>
                <p>{value} Kejadian</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            value = int(kpis.get('kekerasan_anak', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👶 Kekerasan Anak</h4>
                <h2>{value:,}</h2>
                <p>{value} Kasus</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            value = int(kpis.get('kekerasan_perempuan', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👩 Kekerasan Perempuan</h4>
                <h2>{value:,}</h2>
                <p>{value} Kasus</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            value = int(kpis.get('peserta_kb', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👶 Peserta KB</h4>
                <h2>{value:,}</h2>
                <p>{value} Orang</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Interactive Map Section
        st.markdown("""
        <div class="map-container">
            <div class="map-header">
                <h2>🗺️ PETA INTERAKTIF KABUPATEN MALANG</h2>
                <p><em>Visualisasi data sosial per kecamatan berdasarkan berbagai indikator</em></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Map filter
        st.markdown("""
        <div class="map-filter-container">
            <h4 class="map-filter-header">🎯 Pilih Jenis Data untuk Visualisasi Peta</h4>
        """, unsafe_allow_html=True)
        
        filter_col1, filter_col2 = st.columns([2, 3])
        
        with filter_col1:
            map_type = st.selectbox(
                "📊 Jenis Data:",
                ["Bencana Alam", "Bantuan Sosial", "KB Performance", "Peserta KB"],
                key="map_type_selector",
                help="Pilih jenis data yang ingin ditampilkan pada peta"
            )
        
        with filter_col2:
            if map_type == "Bencana Alam":
                info_text = "🌊 Menampilkan tingkat kerawanan bencana per kecamatan berdasarkan data historis"
                filter_applied = "📅 Filter tahun aktif"
            elif map_type == "Bantuan Sosial":
                info_text = "👥 Menampilkan distribusi penerima bantuan sosial per kecamatan"
                filter_applied = "📅 Filter tahun aktif"
            elif map_type == "KB Performance":
                info_text = "📈 Menampilkan tingkat pertumbuhan program KB tahun 2024 vs 2023"
                filter_applied = "📊 Data perbandingan 2023-2024"
            elif map_type == "Peserta KB":
                info_text = "👶 Menampilkan jumlah peserta program Keluarga Berencana per kecamatan"
                filter_applied = "📅 Filter tahun aktif"
            
            st.markdown(f"""
            <div class="filter-info-box">
                <strong>ℹ️ Informasi:</strong><br>
                {info_text}<br>
                <strong>🔧 Status Filter:</strong> {filter_applied}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Create simple folium map (placeholder for now)
        center_lat = -8.0710
        center_lon = 112.6333
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles='OpenStreetMap',
            width='100%',
            height='500px'
        )
        
        # Display map
        map_data_result = st_folium(m, width='100%', height=500)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 1: Bantuan Sosial
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>👥 BANTUAN SOSIAL</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_penerima_per_tahun_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.markdown(f"""
                <div class="chart-explanation">
                    📊 <strong>Hasil Analisis:</strong> Grafik menunjukkan tren penerima bantuan sosial per tahun dengan perbandingan total dan rata-rata penerima.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Penerima per Tahun tidak tersedia")
        
        with col2:
            chart = create_bantuan_donut_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.markdown(f"""
                <div class="chart-explanation">
                    🍩 <strong>Hasil Analisis:</strong> Distribusi penerima bantuan menunjukkan proporsi setiap program bantuan sosial.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Bantuan tidak tersedia")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 2: Bencana Alam
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>🌊 BENCANA ALAM</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_jenis_bencana_pie_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.markdown(f"""
                <div class="chart-explanation">
                    🥧 <strong>Hasil Analisis:</strong> Distribusi jenis bencana menunjukkan tipe bencana yang paling sering terjadi di Kabupaten Malang.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Jenis Bencana tidak tersedia")
        
        with col2:
            st.info("📊 Chart bencana per kecamatan akan ditambahkan")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Display active filters info
        st.markdown("---")
        st.markdown("### 🎯 Active Filter")
        st.info(f"📅 **Tahun:** {', '.join(map(str, selected_years))}")
        
        # Footer
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        ---
        <div style='text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 10px;'>
            <p><strong>📊 Dashboard Sosial Kabupaten Malang</strong></p>
            <p><strong>🔗 Data Source:</strong> Local CSV Files | <strong>🕒 Generated:</strong> {current_time}</p>
            <p><strong>💡 Insight:</strong> Dashboard ini menyediakan visualisasi data sosial untuk mendukung pengambilan keputusan (Periode 2020-2024)</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan dalam memuat dashboard: {str(e)}")

if __name__ == "__main__":
    main()