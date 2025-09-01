"""
Dashboard Sosial - Modular Version
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import *
from src.components.layouts import render_dashboard_header, render_section_header
from src.components.charts import create_penerima_per_tahun_chart, create_bantuan_donut_chart, create_jenis_bencana_pie_chart, create_bencana_kecamatan_chart, create_kekerasan_total_yearly_chart, create_kekerasan_gender_comparison_chart, create_kekerasan_perempuan_yearly_chart, create_kekerasan_perempuan_usia_chart, create_kontrasepsi_chart, create_kb_performance_table
from src.components.cards import render_kpi_cards
from src.components.maps import render_interactive_map, render_map_statistics, render_map_instructions
from src.utils.data_loader import load_sosial_data
from src.utils.data_processor import prepare_disaster_data_for_map, prepare_bantuan_sosial_data_for_map, prepare_kb_performance_data_for_map, prepare_peserta_kb_data_for_map
from src.utils.sosial_analyzer import calculate_kpis, get_available_years, analyze_penerima_per_tahun, analyze_bantuan_donut, analyze_jenis_bencana_pie, analyze_bencana_kecamatan, analyze_kekerasan_total_yearly, analyze_kekerasan_gender_comparison, analyze_kekerasan_perempuan_yearly, analyze_kekerasan_perempuan_usia, analyze_kontrasepsi_chart, analyze_kb_performance_table
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

    # Header
    render_dashboard_header(
        title="🏛️ Dashboard Sosial Kabupaten Malang",
        subtitle="Sistem Monitoring Data Sosial 2020-2024",
        description="📊 Dashboard Interaktif untuk Analisis Data Sosial"
    )

    try:
        # Calculate KPIs
        kpis = calculate_kpis(data, selected_years)
        
        # KPI Section
        render_section_header("📊  Indikator Utama Stunting")

        render_kpi_cards([
            ("👥", "Total Penerima Bantuan", f"{kpis.get('total_penerima_bantuan', 0):,}", "Orang"),
            ("🌊", "Total Bencana", f"{kpis.get('total_bencana', 0):,}", "Kejadian"),
            ("👶", "Kekerasan Anak", f"{kpis.get('kekerasan_anak', 0):,}", "Kasus"),
            ("👩", "Kekerasan Perempuan", f"{kpis.get('kekerasan_perempuan', 0):,}", "Kasus"),
            ("👨‍👩‍👧‍👦", "Peserta KB", f"{kpis.get('peserta_kb', 0):,}", "Orang"),
        ])


        # Map Section
        render_section_header("🗺️ Peta Interaktif Indikator Sosial per Kecamatan")
        
        filter_col1, filter_col2 = st.columns([2, 3])
        
        with filter_col1:
            map_type = st.selectbox(
                "Pilih Jenis Data:",
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

        # Tentukan map_data berdasarkan map_type
            
        if map_type == "Bencana Alam":
            map_data = prepare_disaster_data_for_map(data, selected_years)
        elif map_type == "Bantuan Sosial":
            map_data = prepare_bantuan_sosial_data_for_map(data, selected_years)
        elif map_type == "KB Performance":
            map_data = prepare_kb_performance_data_for_map(data)
        elif map_type == "Peserta KB":
            map_data = prepare_peserta_kb_data_for_map(data, selected_years)
        else:
            map_data = None

        interactive_map = render_interactive_map(map_data, map_type, selected_years, height=600)

        if interactive_map:
            render_map_statistics(map_data, map_type, selected_years)
            render_map_instructions()


        # Section 1: Bantuan Sosial
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>👥 Bantuan Sosial</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_penerima_per_tahun_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                analysis = analyze_penerima_per_tahun(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Penerima per Tahun tidak tersedia")
        
        with col2:
            chart = create_bantuan_donut_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                analysis = analyze_bantuan_donut(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Bantuan tidak tersedia")
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Section 2: Bencana Alam
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>🌊 Bencana Alam</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_jenis_bencana_pie_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                analysis = analyze_jenis_bencana_pie(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Jenis Bencana tidak tersedia")
        
        with col2:
            chart = create_bencana_kecamatan_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                analysis = analyze_bencana_kecamatan(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Bencana per Kecamatan tidak tersedia")
        
        
        
        
        # Section 3: Kekerasan
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>⚠️ Kekerasan</h2>
            </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_kekerasan_total_yearly_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan total yearly
                analysis = analyze_kekerasan_total_yearly(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Total Kekerasan tidak tersedia")
        
        with col2:
            chart = create_kekerasan_gender_comparison_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan gender comparison
                analysis = analyze_kekerasan_gender_comparison(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Kekerasan berdasarkan Gender tidak tersedia")
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_kekerasan_perempuan_yearly_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan perempuan yearly
                analysis = analyze_kekerasan_perempuan_yearly(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Kekerasan Perempuan tidak tersedia")
        
        with col2:
            chart = create_kekerasan_perempuan_usia_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan perempuan usia
                analysis = analyze_kekerasan_perempuan_usia(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Kekerasan berdasarkan Usia tidak tersedia")

        # Section 4: Keluarga Berencana (KB)
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>👶 Keluarga Berencana (KB)</h2>
            </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_kontrasepsi_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kontrasepsi
                analysis = analyze_kontrasepsi_chart(data, selected_years)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Kontrasepsi tidak tersedia")
        
        with col2:
            st.markdown("#### 📈 Performa KB Kecamatan 2023-2024")
            table = create_kb_performance_table(data)
            if table is not None and not table.empty:
                st.dataframe(table, use_container_width=True, hide_index=True, height=400)
                # Analysis for KB performance table
                analysis = analyze_kb_performance_table(data)
                st.info(f"**Hasil Analisis:** {analysis}")
            else:
                st.info("📊 Data Performa KB tidak tersedia")
        
        st.markdown("</div>", unsafe_allow_html=True)


        # Display active filters info
        st.markdown("---")
        st.markdown("### 🎯 Active Filter")
        st.info(f"📅 **Tahun:** {', '.join(map(str, selected_years))}")
        
    
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan dalam memuat dashboard: {str(e)}")

if __name__ == "__main__":
    main()