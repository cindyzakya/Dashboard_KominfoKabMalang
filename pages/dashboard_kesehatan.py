"""
Dashboard Kesehatan
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add project root to path to allow absolute imports from src
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config import *
from src.components.layouts import render_dashboard_header, render_section_header
from src.components.cards import create_kpi_card, create_white_kpi_card
from src.components.filters import create_year_filter, create_multiselect_filter
from src.utils.data_loader import load_kesehatan_data, load_geojson_data
from src.utils.data_processor import create_sorted_period_data
from src.utils.kesehatan_analyzer import get_latest_period, analyze_prevalence_category, get_latest_facilities_data, create_correlation_analysis
from src.styles.main import load_kesehatan_css

# Page config
st.set_page_config(
    page_title="Dashboard Analisis Stunting",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_kesehatan_css()

# Load data functions
@st.cache_data
def load_data():
    return load_kesehatan_data()

@st.cache_data
def load_geo_data():
    return load_geojson_data(GEO_DATA_PATH / "35.07_kecamatan.geojson")

def main():
    # Load data
    df = load_data()
    geojson_kec = load_geo_data()
    
    if df.empty:
        st.error("Data kesehatan tidak dapat dimuat!")
        st.stop()

    # Sidebar filters
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>🔍 Filter Data</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📅 **Filter Tahun**", expanded=True):
            # Year filter
            if "reset_filters" not in st.session_state:
                st.session_state.reset_filters = False
            if "reset_year_filter" not in st.session_state:
                st.session_state.reset_year_filter = False
            if "reset_kecamatan_filter" not in st.session_state:
                st.session_state.reset_kecamatan_filter = False
            
            default_checkbox_tahun = True
            default_multiselect_tahun = sorted(df['Tahun'].unique())
            
            semua_tahun = st.checkbox("Pilih Semua Tahun", value=default_checkbox_tahun, key="checkbox_tahun")
            
            if semua_tahun:
                selected_year = sorted(df['Tahun'].unique())
                st.info(f"Terpilih: {len(selected_year)} tahun")
                st.multiselect(
                    "Pilih Tahun:",
                    options=sorted(df['Tahun'].unique()),
                    default=sorted(df['Tahun'].unique()),
                    disabled=True,
                    key="multiselect_tahun"
                )
            else:
                selected_year = st.multiselect(
                    "Pilih Tahun:",
                    options=sorted(df['Tahun'].unique()),
                    default=default_multiselect_tahun,
                    key="multiselect_tahun"
                )
                if not selected_year:
                    selected_year = sorted(df['Tahun'].unique())
                    st.warning("Tidak ada tahun dipilih, menampilkan semua tahun")

        with st.expander("🏘️ **Filter Kecamatan**", expanded=True):
            default_checkbox_kecamatan = True
            default_multiselect_kecamatan = sorted(df['Kecamatan'].unique())
            
            semua_kecamatan = st.checkbox("Pilih Semua Kecamatan", value=default_checkbox_kecamatan, key="checkbox_kecamatan")
            
            if semua_kecamatan:
                selected_kecamatan = sorted(df['Kecamatan'].unique())
                st.info(f"Terpilih: {len(selected_kecamatan)} kecamatan")
                st.multiselect(
                    "Pilih Kecamatan:",
                    options=sorted(df['Kecamatan'].unique()),
                    default=sorted(df['Kecamatan'].unique()),
                    disabled=True,
                    key="multiselect_kecamatan"
                )
            else:
                selected_kecamatan = st.multiselect(
                    "Pilih Kecamatan:",
                    options=sorted(df['Kecamatan'].unique()),
                    default=sorted(df['Kecamatan'].unique())[:10],
                    key="multiselect_kecamatan"
                )
                if not selected_kecamatan:
                    selected_kecamatan = sorted(df['Kecamatan'].unique())
                    st.warning("Tidak ada kecamatan dipilih, menampilkan semua kecamatan")

    # Filter data
    filtered_df = df[
        (df['Tahun'].isin(selected_year)) &
        (df['Kecamatan'].isin(selected_kecamatan))
    ]

    if filtered_df.empty:
        st.error("Tidak ada data yang sesuai dengan filter yang dipilih. Silakan ubah filter di sidebar.")
        st.stop()

    # Get latest period
    latest_year, latest_month = get_latest_period(filtered_df)

    # Header
    render_dashboard_header(
        title="🏥 Dashboard Analisis Data Stunting",
        subtitle="Monitoring dan Evaluasi Stunting di Kabupaten Malang",
        description="📊 Dashboard Komprehensif untuk Analisis Prevalensi Stunting dan Fasilitas Kesehatan"
    )

    # KPI Section
    render_section_header("📋 Indikator Utama Stunting")

    total_stunting = filtered_df['Stunting'].sum()
    total_diukur = filtered_df['Jumlah Yang Diukur'].sum()
    avg_prevalensi = filtered_df['Prevalensi Stunting Persen'].mean()

    # Facilities data from latest period
    if latest_year and latest_month:
        latest_data = filtered_df[
            (filtered_df['Tahun'] == latest_year) & 
            (filtered_df['Bulan'] == latest_month)
        ].drop_duplicates(subset=['Kecamatan'])
        total_puskesmas = latest_data['Jumlah Puskesmas'].sum()
        total_rs = latest_data['Jumlah Rumah Sakit'].sum()
    else:
        total_puskesmas, total_rs = 0, 0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        create_kpi_card(
            title="Total Kasus Stunting", 
            value=f"{total_stunting:,}", 
            icon="👶"
        )
    with col2:
        create_kpi_card(
            title="Total Anak Diukur", 
            value=f"{total_diukur:,}", 
            icon="📏"
        )
    with col3:
        create_kpi_card(
            title="Rata-rata Prevalensi", 
            value=f"{avg_prevalensi:.2f}%", 
            icon="📊"
        )
    with col4:
        create_kpi_card(
            title="Total Puskesmas", 
            value=f"{total_puskesmas:,}", 
            icon="🏥"
        )
    with col5:
        create_kpi_card(
            title="Total Rumah Sakit", 
            value=f"{total_rs:,}", 
            icon="🏨"
            )

    # Map Section
    render_section_header("🗺️ Peta Sebaran Indikator per Kecamatan")

    # Prepare facilities data
    faskes_df = get_latest_facilities_data(filtered_df)

    all_indicator_options = {
        "Prevalensi Stunting (%)": "Prevalensi Stunting Persen",
        "Jumlah Rumah Sakit": "Jumlah Rumah Sakit",
        "Jumlah Puskesmas": "Jumlah Puskesmas",
        "Jumlah Puskesmas Pembantu": "Jumlah Puskesmas Pembantu",
        "Jumlah Klinik": "Jumlah Klinik",
        "Pos Kesehatan": "Pos Kesehatan",
        "Jumlah Pondok Bersalin Desa": "Jumlah Pondak Bersalin Desa (Polindes)",
    }

    available_indicators = {label: col for label, col in all_indicator_options.items() if col in filtered_df.columns}
    selected_indicator_label = st.selectbox("Pilih Indikator Peta", list(available_indicators.keys()))
    selected_indicator = available_indicators[selected_indicator_label]

    # Prepare map data
    if latest_year and latest_month and not faskes_df.empty:
        latest_period_data = filtered_df[
            (filtered_df['Tahun'] == latest_year) & 
            (filtered_df['Bulan'] == latest_month)
        ]
        prevalence_latest_df = latest_period_data.groupby('Kecamatan').agg({
            'Prevalensi Stunting Persen': 'mean'
        }).reset_index()

        map_data_source = pd.merge(faskes_df, prevalence_latest_df, on="Kecamatan", how="left")
    else:
        map_data_source = pd.DataFrame()

    # Display map
    col1, col2 = st.columns([2, 1])

    with col1:
        if not map_data_source.empty and selected_indicator in map_data_source.columns:
            map_display_df = map_data_source[['Kecamatan', selected_indicator]].dropna().rename(columns={"Kecamatan": "kecamatan"})

            fig_map = px.choropleth_mapbox(
                map_display_df,
                geojson=geojson_kec,
                locations="kecamatan",
                featureidkey="properties.nm_kecamatan",
                color=selected_indicator,
                color_continuous_scale=["#e8e8e8", "#d1ecf2", "#2a89a6", "#62718c", "#574249", "#ad9ea5", "#e4acac", "#c85a5a", "#985356"],
                mapbox_style="carto-positron",
                zoom=8.5,
                center={"lat": -8.1, "lon": 112.65},
                opacity=1,
                labels={selected_indicator: selected_indicator_label},
                hover_name="kecamatan",
            )

            try:
                # Load the geojson as a GeoDataFrame to calculate centroids for labels
                gdf_kec = gpd.read_file(GEO_DATA_PATH / "35.07_kecamatan.geojson")
                gdf_kec['centroid'] = gdf_kec.geometry.centroid

                # Filter the GeoDataFrame to only include kecamatans currently on the map
                label_gdf = gdf_kec[gdf_kec['nm_kecamatan'].isin(map_display_df['kecamatan'])]

                if not label_gdf.empty:
                    lats = [point.y for point in label_gdf['centroid']]
                    lons = [point.x for point in label_gdf['centroid']]
                    texts = label_gdf['nm_kecamatan']

                    # Layer shadow for text
                    fig_map.add_trace(go.Scattermapbox(
                        lon=[x + 0.0008 for x in lons],
                        lat=[y - 0.0008 for y in lats],
                        mode='text',
                        text=texts,
                        textfont=dict(size=8, color='black'),
                        showlegend=False,
                        hovertemplate=None,
                        hoverinfo='skip'
                    ))

                    # Main text layer
                    fig_map.add_trace(go.Scattermapbox(
                        lon=lons,
                        lat=lats,
                        mode='text',
                        text=texts,
                        textfont=dict(size=8, color='white', family="Arial Black"),
                        showlegend=False,
                        hovertemplate=None,
                        hoverinfo='skip'
                    ))
            except Exception as e:
                st.warning(f"Could not generate map labels. Please ensure 'geopandas' is installed. Error: {e}", icon="⚠️")

            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)

        else:
            st.warning(f"Data untuk '{selected_indicator_label}' tidak tersedia dengan filter yang dipilih saat ini.")

    with col2:
        if not map_data_source.empty and selected_indicator in map_data_source.columns:
            map_display_df = map_data_source[['Kecamatan', selected_indicator]].dropna()
            
            max_row = map_display_df.loc[map_display_df[selected_indicator].idxmax()]
            min_row = map_display_df.loc[map_display_df[selected_indicator].idxmin()]
            avg_value = map_display_df[selected_indicator].mean()

            # Best/Worst Performer
            if "Stunting" in selected_indicator_label:
                # For stunting, low value = good
                st.markdown(f"""
                <div class="insight-box insight-box-good">
                    <h4>✅ Terendah (Terbaik)</h4>
                    <p class="kecamatan-name">{min_row['Kecamatan']}</p>
                    <span class="value">{min_row[selected_indicator]:.2f}%</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="insight-box insight-box-bad">
                    <h4>⚠️ Tertinggi (Perlu Perhatian)</h4>
                    <p class="kecamatan-name">{max_row['Kecamatan']}</p>
                    <span class="value">{max_row[selected_indicator]:.2f}%</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # For facilities, high value = good
                st.markdown(f"""
                <div class="insight-box insight-box-good">
                    <h4>🏆 Tertinggi (Terbaik)</h4>
                    <p class="kecamatan-name">{max_row['Kecamatan']}</p>
                    <span class="value">{max_row[selected_indicator]:.0f} unit</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="insight-box insight-box-bad">
                    <h4>⚠️ Terendah (Perlu Perhatian)</h4>
                    <p class="kecamatan-name">{min_row['Kecamatan']}</p>
                    <span class="value">{min_row[selected_indicator]:.0f} unit</span>
                </div>
                """, unsafe_allow_html=True)

            # Summary
            above_avg = sum(map_display_df[selected_indicator] >= avg_value)
            below_avg = sum(map_display_df[selected_indicator] < avg_value)
            
            if "Stunting" in selected_indicator_label:
                st.markdown(f"""
                <div style="text-align: center; font-size: 0.9rem;">
                    Rata-rata Kabupaten: <strong>{avg_value:.2f}%</strong><br>
                    <hr class="custom-hr">
                    ✅ {below_avg} Kec. di bawah rata-rata<br>
                    ❌ {above_avg} Kec. di atas rata-rata
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; font-size: 0.9rem;">
                    Rata-rata Kabupaten: <strong>{avg_value:.1f} unit</strong><br>
                    <hr class="custom-hr">
                    ✅ {above_avg} Kec. di atas rata-rata<br>
                    ❌ {below_avg} Kec. di bawah rata-rata
                </div>
                """, unsafe_allow_html=True)

    # Trend Analysis
    render_section_header("📈 Tren Stunting dari Waktu ke Waktu")

    tab1, tab2 = st.tabs(["Tren Tahunan", "Tren per Kecamatan"])

    with tab1:
        trend_type_general = st.selectbox(
            "Pilih Jenis Tren:",
            options=["Per Tahun", "Per Periode"],
            key="general_trend_type"
        )

        if trend_type_general == "Per Tahun":
            # Yearly trend
            yearly_trend = filtered_df.groupby('Tahun').agg({
                'Prevalensi Stunting Persen': ['mean', 'std'],
                'Stunting': 'sum',
                'Jumlah Yang Diukur': 'sum'
            }).reset_index()
            
            yearly_trend.columns = ['Tahun', 'Prevalensi_Mean', 'Prevalensi_Std', 'Total_Stunting', 'Total_Diukur']
            yearly_trend['Prevalensi_Std'] = yearly_trend['Prevalensi_Std'].fillna(0)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig_trend = go.Figure()
                
                fig_trend.add_trace(go.Scatter(
                    x=yearly_trend['Tahun'],
                    y=yearly_trend['Prevalensi_Mean'],
                    mode='lines+markers',
                    name='Prevalensi',
                    line=dict(width=4, color='#2a89a6'),
                    marker=dict(size=12),
                ))
                
                fig_trend.update_layout(
                    title='Tren Stunting per Tahun',
                    xaxis_title="Tahun",
                    yaxis_title="Persentase Stunting (%)",
                    height=500
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if len(yearly_trend) > 1:
                    trend_change = yearly_trend.iloc[-1]['Prevalensi_Mean'] - yearly_trend.iloc[0]['Prevalensi_Mean']
                    best_year = yearly_trend.loc[yearly_trend['Prevalensi_Mean'].idxmin(), 'Tahun']
                    worst_year = yearly_trend.loc[yearly_trend['Prevalensi_Mean'].idxmax(), 'Tahun']
                    best_prev = yearly_trend['Prevalensi_Mean'].min()
                    worst_prev = yearly_trend['Prevalensi_Mean'].max()
                    
                    if abs(trend_change) < 1:
                        st.markdown('<div class="custom-alert custom-alert-info">📊 <strong>Stabil:</strong> Perubahan minimal dalam periode observasi.</div>', unsafe_allow_html=True)
                    elif trend_change < 0:
                        st.markdown('<div class="custom-alert custom-alert-success">✅ <strong>Membaik:</strong> Terjadi penurunan stunting yang positif.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="custom-alert custom-alert-warning">⚠️ <strong>Perlu Perhatian:</strong> Terjadi peningkatan stunting.</div>', unsafe_allow_html=True)

                    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
                    comparison_text = f"""
                    ℹ️ **Detail Perkembangan:**<br>
                    - Perubahan: {trend_change:+.1f}% ({yearly_trend.iloc[0]['Tahun']} → {yearly_trend.iloc[-1]['Tahun']})<br>
                    - Tahun terbaik: **{best_year}** ({best_prev:.1f}%)<br>
                    - Tahun terburuk: **{worst_year}** ({worst_prev:.1f}%)
                    """
                    st.markdown(comparison_text, unsafe_allow_html=True)
                else:
                    st.info("Data hanya tersedia untuk satu tahun.")
        
        elif trend_type_general == "Per Periode":
            # Monthly trend
            monthly_map = {
                'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 'Mei': 5, 'Juni': 6,
                'Juli': 7, 'Agustus': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
            }
            
            period_trend = filtered_df.copy()
            period_trend['month_num'] = period_trend['Bulan'].map(monthly_map)
            period_trend = period_trend.sort_values(['Tahun', 'month_num'])
            
            period_trend_agg = period_trend.groupby(['Tahun', 'Bulan', 'month_num']).agg({
                'Prevalensi Stunting Persen': 'mean'
            }).reset_index()
            
            period_trend_agg['Periode'] = period_trend_agg['Tahun'].astype(str) + '-' + period_trend_agg['Bulan'].str.slice(0, 3)
            
            col1, col2 = st.columns([2, 1])

            with col1:
                fig_period_trend = go.Figure()
                
                fig_period_trend.add_trace(go.Scatter(
                    x=period_trend_agg['Periode'],
                    y=period_trend_agg['Prevalensi Stunting Persen'],
                    mode='lines+markers',
                    name='Prevalensi per Periode',
                    line=dict(width=3, color='#2a89a6'),
                    marker=dict(size=8),
                ))
                
                fig_period_trend.update_layout(
                    title='Tren Stunting per Periode (Bulan)',
                    xaxis_title="Periode",
                    yaxis_title="Persentase Stunting (%)",
                    height=500,
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig_period_trend, use_container_width=True)

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if len(period_trend_agg) > 1:
                    trend_change = period_trend_agg.iloc[-1]['Prevalensi Stunting Persen'] - period_trend_agg.iloc[0]['Prevalensi Stunting Persen']
                    best_period_row = period_trend_agg.loc[period_trend_agg['Prevalensi Stunting Persen'].idxmin()]
                    worst_period_row = period_trend_agg.loc[period_trend_agg['Prevalensi Stunting Persen'].idxmax()]
                    
                    if abs(trend_change) < 0.5:
                        st.markdown('<div class="custom-alert custom-alert-info">📊 <strong>Stabil:</strong> Perubahan minimal dari awal hingga akhir periode.</div>', unsafe_allow_html=True)
                    elif trend_change < 0:
                        st.markdown('<div class="custom-alert custom-alert-success">✅ <strong>Membaik:</strong> Terjadi penurunan stunting secara keseluruhan.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="custom-alert custom-alert-warning">⚠️ <strong>Perlu Perhatian:</strong> Terjadi peningkatan stunting secara keseluruhan.</div>', unsafe_allow_html=True)

                    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
                    comparison_text = f"""
                    ℹ️ **Detail Perkembangan per Periode:**<br>
                    - Perubahan: {trend_change:+.1f}% ({period_trend_agg.iloc[0]['Periode']} → {period_trend_agg.iloc[-1]['Periode']})<br>
                    - Periode terbaik: **{best_period_row['Periode']}** ({best_period_row['Prevalensi Stunting Persen']:.1f}%)<br>
                    - Periode terburuk: **{worst_period_row['Periode']}** ({worst_period_row['Prevalensi Stunting Persen']:.1f}%)
                    """
                    st.markdown(comparison_text, unsafe_allow_html=True)
                else:
                    st.info("Data hanya tersedia untuk satu periode.")
        

    with tab2:
        # Single district trend
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            trend_type_kec = st.selectbox(
                "Jenis Tren:",
                options=["Per Tahun", "Per Periode"],
                key="kec_trend_type"
            )
        
        with col_filter2:
            available_kecamatan_single = sorted(df['Kecamatan'].unique())
            selected_kecamatan_single = st.selectbox(
                "Pilih Satu Kecamatan:",
                options=available_kecamatan_single,
                key="single_kecamatan_filter"
            )
        
        single_kec_df = df[df['Kecamatan'] == selected_kecamatan_single]
        
        if not single_kec_df.empty:
            if trend_type_kec == "Per Tahun":
                yearly_single_trend = single_kec_df.groupby('Tahun').agg({
                    'Prevalensi Stunting Persen': 'mean',
                    'Stunting': 'sum',
                    'Jumlah Yang Diukur': 'sum'
                }).reset_index()
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig_single = go.Figure()
                    
                    fig_single.add_trace(go.Scatter(
                        x=yearly_single_trend['Tahun'],
                        y=yearly_single_trend['Prevalensi Stunting Persen'],
                        mode='lines+markers',
                        name=f'{selected_kecamatan_single}',
                        line=dict(width=4, color='#c85a5a'),
                        marker=dict(size=12),
                    ))
                    
                    fig_single.update_layout(
                        title=f'Tren Stunting per Tahun - {selected_kecamatan_single}',
                        xaxis_title="Tahun",
                        yaxis_title="Persentase Stunting (%)",
                        height=500
                    )
                    
                    st.plotly_chart(fig_single, use_container_width=True)

                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if len(yearly_single_trend) > 1:
                        single_trend_change = yearly_single_trend.iloc[-1]['Prevalensi Stunting Persen'] - yearly_single_trend.iloc[0]['Prevalensi Stunting Persen']
                        
                        if single_trend_change < -1:
                            st.markdown('<div class="custom-alert custom-alert-success">✅ <strong>Tren Membaik:</strong> Penurunan signifikan.</div>', unsafe_allow_html=True)
                        elif single_trend_change > 1:
                            st.markdown('<div class="custom-alert custom-alert-error">❌ <strong>Tren Memburuk:</strong> Peningkatan signifikan.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="custom-alert custom-alert-info">📊 <strong>Tren Stabil:</strong> Perubahan minimal.</div>', unsafe_allow_html=True)
                    else:
                        st.info("Data hanya tersedia untuk satu tahun.")
            
            elif trend_type_kec == "Per Periode":
                monthly_map = {
                    'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 'Mei': 5, 'Juni': 6,
                    'Juli': 7, 'Agustus': 8, 'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
                }

                single_kec_df_sorted = create_sorted_period_data(single_kec_df.copy())
            
                period_single_trend = single_kec_df_sorted.groupby(['Tahun', 'Bulan', 'Periode', 'Month_Num']).agg({
                    'Prevalensi Stunting Persen': 'mean',
                    'Stunting': 'sum',
                    'Jumlah Yang Diukur': 'sum',
                }).reset_index()
                
                period_single_trend = period_single_trend.sort_values(['Tahun', 'Month_Num']).reset_index(drop=True)
                
                col1, col2 = st.columns([2, 1])

                with col1:
                    fig_single_period = go.Figure()
                    
                    fig_single_period.add_trace(go.Scatter(
                        x=period_single_trend['Periode'],
                        y=period_single_trend['Prevalensi Stunting Persen'],
                        mode='lines+markers',
                        name=f'{selected_kecamatan_single}',
                        line=dict(width=3, color='#c85a5a'),
                        marker=dict(size=8),
                    ))
                    
                    fig_single_period.update_layout(
                        title=f'Tren Stunting per Periode - {selected_kecamatan_single}',
                        xaxis_title="Periode",
                        yaxis_title="Persentase Stunting (%)",
                        height=500,
                        xaxis=dict(
                            categoryorder='array',
                            categoryarray=period_single_trend['Periode'].tolist()
                        )
                    )
                    
                    st.plotly_chart(fig_single_period, use_container_width=True)

                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if len(period_single_trend) > 1:
                        highest_period_single = period_single_trend.loc[period_single_trend['Prevalensi Stunting Persen'].idxmax(), 'Periode']
                        lowest_period_single = period_single_trend.loc[period_single_trend['Prevalensi Stunting Persen'].idxmin(), 'Periode']
                        highest_prev_single = period_single_trend['Prevalensi Stunting Persen'].max()
                        lowest_prev_single = period_single_trend['Prevalensi Stunting Persen'].min()
                        range_period_single = highest_prev_single - lowest_prev_single
                        
                        if range_period_single > 5:
                            st.markdown('', unsafe_allow_html=True)
                        elif range_period_single > 2:
                            st.markdown('<div class="custom-alert custom-alert-info">📊 <strong>Variasi Sedang:</strong> Fluktuasi normal antar periode.</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="custom-alert custom-alert-success">✅ <strong>Konsisten:</strong> Variasi minimal antar periode.</div>', unsafe_allow_html=True)

                        st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
                        comparison_text = f"""
                        ℹ️ **Detail untuk {selected_kecamatan_single}:**<br>
                        - Rentang variasi: **{range_period_single:.1f}%**<br>
                        - Periode terbaik: **{lowest_period_single}** ({lowest_prev_single:.1f}%)<br>
                        - Periode terburuk: **{highest_period_single}** ({highest_prev_single:.1f}%)
                        """
                        st.markdown(comparison_text, unsafe_allow_html=True)
                    else:
                        st.info("Data hanya tersedia untuk satu periode.")

                    

    # Regional Comparison
    render_section_header("🗺️ Perbandingan Antar Wilayah")

    if latest_year and latest_month:
        distribution_df = filtered_df[
            (filtered_df['Tahun'] == latest_year) & 
            (filtered_df['Bulan'] == latest_month)
        ]
    else:
        distribution_df = filtered_df

    col1, col2 = st.columns(2)

    with col1:
        # Top 10 highest stunting
        top_kecamatan = distribution_df.groupby('Kecamatan').agg({
            'Prevalensi Stunting Persen': 'mean',
            'Stunting': 'sum'
        }).reset_index().sort_values('Prevalensi Stunting Persen', ascending=False).head(10)
        
        fig_top = px.bar(
            top_kecamatan,
            x='Prevalensi Stunting Persen',
            y='Kecamatan',
            title='10 Kecamatan dengan Stunting Tertinggi',
            orientation='h',
            color='Prevalensi Stunting Persen',
            color_continuous_scale='Reds',
            text='Prevalensi Stunting Persen'
        )
        fig_top.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_top.update_layout(height=500)
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        bottom_kecamatan = distribution_df.groupby('Kecamatan').agg({
            'Prevalensi Stunting Persen': 'mean',
            'Stunting': 'sum'
        }).reset_index().sort_values('Prevalensi Stunting Persen', ascending=True).head(10)
        
        fig_bottom = px.bar(
            bottom_kecamatan,
            x='Prevalensi Stunting Persen',
            y='Kecamatan',
            title='10 Kecamatan dengan Stunting Terendah',
            orientation='h',
            color='Prevalensi Stunting Persen',
            color_continuous_scale='Blues',
            text='Prevalensi Stunting Persen'
        )
        fig_bottom.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_bottom.update_layout(height=500)
        st.plotly_chart(fig_bottom, use_container_width=True)

    # Analysis
    highest_kec = top_kecamatan.iloc[0]['Kecamatan']
    highest_prev = top_kecamatan.iloc[0]['Prevalensi Stunting Persen']
    highest_cases = top_kecamatan.iloc[0]['Stunting']

    lowest_kec = bottom_kecamatan.iloc[0]['Kecamatan']
    lowest_prev = bottom_kecamatan.iloc[0]['Prevalensi Stunting Persen']
    lowest_cases = bottom_kecamatan.iloc[0]['Stunting']

    gap = highest_prev - lowest_prev

    st.info(f"**Variasi Antar Wilayah**: Terdapat perbedaan {gap:.1f}% antara kecamatan dengan angka stunting tertinggi (**{highest_kec}**: {highest_prev:.1f}% atau {highest_cases:,} kasus) dan terendah (**{lowest_kec}**: {lowest_prev:.1f}% atau {lowest_cases:,} kasus). Hal ini menunjukkan adanya variasi kondisi stunting antar wilayah.")

    # Category distribution
    avg_prevalensi_kecamatan = distribution_df.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().reset_index()
    avg_prevalensi_kecamatan['Kategori'] = avg_prevalensi_kecamatan['Prevalensi Stunting Persen'].apply(analyze_prevalence_category)
    kategori_counts = avg_prevalensi_kecamatan['Kategori'].value_counts()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='font-size: 18px; font-weight: bold;'>Distribusi Kecamatan Berdasarkan Kategori</h3>", unsafe_allow_html=True)
        
        pie_colors = ["#2a89a6", "#c85a5a", "#d1ecf2"]

        fig_pie = px.pie(
            values=kategori_counts.values,
            names=kategori_counts.index,
            color=kategori_counts.index,
            color_discrete_sequence=pie_colors[:len(kategori_counts)] 
        )
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("<h3 style='font-size: 18px; font-weight: bold;'>Daftar Kecamatan per Kategori</h3>", unsafe_allow_html=True)
        for kategori in kategori_counts.index:
            kecamatan_list = avg_prevalensi_kecamatan[avg_prevalensi_kecamatan['Kategori'] == kategori]['Kecamatan'].tolist()
            st.write(f"**{kategori}**: {', '.join(kecamatan_list[:15])}" + ("..." if len(kecamatan_list) > 15 else ""))

    # Change Analysis
    render_section_header("📈📉 Perubahan Stunting Antar Waktu")

    if filtered_df['Tahun'].nunique() > 1:
        perubahan_df = filtered_df.groupby(['Kecamatan', 'Tahun'])['Prevalensi Stunting Persen'].mean().reset_index()
        tahun_awal, tahun_akhir = perubahan_df['Tahun'].min(), perubahan_df['Tahun'].max()

        perubahan_pivot = perubahan_df.pivot(index='Kecamatan', columns='Tahun', values='Prevalensi Stunting Persen').reset_index()
        perubahan_pivot = perubahan_pivot.dropna()
        
        if len(perubahan_pivot.columns) >= 3:
            perubahan_pivot['Perubahan'] = perubahan_pivot[tahun_akhir] - perubahan_pivot[tahun_awal]
            perubahan_pivot['Perubahan_Persen'] = (perubahan_pivot['Perubahan'] / perubahan_pivot[tahun_awal]) * 100

            col_header1, col_header2 = st.columns([3, 1])

            with col_header2:
                sort_option = st.selectbox(
                    "🔧 Lihat berdasarkan:",
                    options=[
                        "📉 Penurunan Terbesar",
                        "📈 Peningkatan Terbesar",
                    ],
                    index=0
                )

            # Sort based on selection
            if sort_option == "📉 Penurunan Terbesar":
                sorted_data = perubahan_pivot.sort_values('Perubahan').head(15)
                chart_title = f"Kecamatan dengan Penurunan Stunting Terbesar ({tahun_awal} → {tahun_akhir})"
                chart_color = 'Reds'
            elif sort_option == "📈 Peningkatan Terbesar":
                sorted_data = perubahan_pivot.sort_values('Perubahan', ascending=False).head(15)
                chart_title = f"Kecamatan dengan Peningkatan Stunting Terbesar ({tahun_awal} → {tahun_akhir})"
                chart_color = 'Greens_r'

            col1, col2 = st.columns(2)
            
            with col1:
                fig_change = px.bar(
                    sorted_data.head(10), 
                    x='Perubahan', 
                    y='Kecamatan', 
                    orientation='h',
                    color='Perubahan',
                    color_continuous_scale=chart_color,
                    text='Perubahan',
                    title=chart_title
                )
                fig_change.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig_change.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_change, use_container_width=True)

            with col2:
                display_data = sorted_data[['Kecamatan', tahun_awal, tahun_akhir, 'Perubahan', 'Perubahan_Persen']].copy()
                display_data.columns = ['Kecamatan', f'{tahun_awal} (%)', f'{tahun_akhir} (%)', 'Selisih (%)', 'Perubahan (%)']
                
                st.dataframe(display_data, column_config={
                    f'{tahun_awal} (%)': st.column_config.NumberColumn(format='%.2f'),
                    f'{tahun_akhir} (%)': st.column_config.NumberColumn(format='%.2f'),
                    'Selisih (%)': st.column_config.NumberColumn(format='%.2f'),
                    'Perubahan (%)': st.column_config.NumberColumn(format='%.1f')
                }, hide_index=True, height=400)
                
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            perbaikan_count = len(perubahan_pivot[perubahan_pivot['Perubahan'] < 0])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{perbaikan_count}</div>
                <div class="metric-label">Kecamatan Menurun</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            memburuk_count = len(perubahan_pivot[perubahan_pivot['Perubahan'] > 0])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{memburuk_count}</div>
                <div class="metric-label">Kecamatan Meningkat</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_change = perubahan_pivot['Perubahan'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_change:.2f}%</div>
                <div class="metric-label">Rata-rata Perubahan</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            best_performer = perubahan_pivot.sort_values('Perubahan').iloc[0]['Kecamatan']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="font-size: 1.2rem;">{best_performer}</div>
                <div class="metric-label">Penurunan Terbesar</div>
            </div>
            """, unsafe_allow_html=True)

        # Analisis perubahan
        improvement_rate = (perbaikan_count / len(perubahan_pivot)) * 100
        best_change = perubahan_pivot['Perubahan'].min()
        worst_change = perubahan_pivot['Perubahan'].max()
        worst_performer = perubahan_pivot.sort_values('Perubahan', ascending=False).iloc[0]['Kecamatan']
        
        st.info(f"**Ringkasan Perubahan**: Dari periode {tahun_awal} ke {tahun_akhir}, {improvement_rate:.0f}% kecamatan ({perbaikan_count} kecamatan) mengalami penurunan stunting, sementara {100-improvement_rate:.0f}% mengalami peningkatan. Penurunan terbesar terjadi di **{best_performer}** ({abs(best_change):.1f}%), sedangkan peningkatan terbesar di **{worst_performer}** ({worst_change:.1f}%). Rata-rata perubahan secara keseluruhan adalah {avg_change:+.1f}%.")

    # Correlation Analysis
    render_section_header("🔬 Hubungan Stunting dengan Fasilitas Kesehatan")

    if latest_year and latest_month:
        latest_period_data_for_corr = filtered_df[
            (filtered_df['Tahun'] == latest_year) & 
            (filtered_df['Bulan'] == latest_month)
        ]
        prevalensi_df = latest_period_data_for_corr.groupby('Kecamatan').agg({
            'Prevalensi Stunting Persen': 'mean'
        }).reset_index()
    else:
        prevalensi_df = filtered_df.groupby('Kecamatan').agg({'Prevalensi Stunting Persen': 'mean'}).reset_index()
        st.info("Analisis menggunakan rata-rata dari seluruh periode yang dipilih.")

    # Merge prevalence and facilities data
    analysis_df = pd.merge(prevalensi_df, faskes_df, on='Kecamatan', how='inner')

    if not analysis_df.empty and len(analysis_df) > 1:
        # Calculate total facilities per district
        facility_cols = [col for col in faskes_df.columns if col != 'Kecamatan']
        analysis_df['Total Faskes'] = analysis_df[facility_cols].sum(axis=1)

        # Sort by prevalence from high to low
        display_kecamatan = analysis_df.sort_values('Prevalensi Stunting Persen', ascending=False)

        # Reshape data for side-by-side visualization
        plot_data = []
        for _, row in display_kecamatan.iterrows():
            plot_data.append({
                'Kecamatan': row['Kecamatan'],
                'Metrik': 'Persentase Stunting (%)',
                'Nilai': row['Prevalensi Stunting Persen']
            })
            plot_data.append({
                'Kecamatan': row['Kecamatan'],
                'Metrik': 'Jumlah Fasilitas Kesehatan',
                'Nilai': row['Total Faskes']
            })
        
        plot_df = pd.DataFrame(plot_data)
        
        # Create side-by-side chart
        fig_faskes_comp = px.bar(
            plot_df,
            x='Kecamatan',
            y='Nilai',
            color='Metrik',
            barmode='group',
            title=f'Perbandingan Stunting vs Fasilitas Kesehatan - {len(display_kecamatan)} Kecamatan',
            text='Nilai',
            color_discrete_map={
                'Persentase Stunting (%)': '#c85a5a',
                'Jumlah Fasilitas Kesehatan': '#2a89a6'
            }
        )
        
        fig_faskes_comp.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_faskes_comp.update_layout(
            height=600,
            yaxis_title='Nilai',
            xaxis_title='Kecamatan',
            xaxis={'tickangle': 45}
        )
        
        st.plotly_chart(fig_faskes_comp, use_container_width=True)

        # Correlation analysis
        correlation = analysis_df['Prevalensi Stunting Persen'].corr(analysis_df['Total Faskes'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if correlation < -0.3:
                delta_text = "Hubungan Negatif"
            elif correlation > 0.3:
                delta_text = "Hubungan Positif"
            else:
                delta_text = "Hubungan Lemah"
            
            create_white_kpi_card(
                value=f"{correlation:.2f}",
                title=f"Korelasi ({delta_text})"
            )
        
        with col2:
            # Best performer
            faskes_tinggi_prev_rendah = analysis_df[
                (analysis_df['Total Faskes'] >= analysis_df['Total Faskes'].quantile(0.7)) & 
                (analysis_df['Prevalensi Stunting Persen'] <= analysis_df['Prevalensi Stunting Persen'].quantile(0.3))
            ].sort_values('Prevalensi Stunting Persen')
            
            if not faskes_tinggi_prev_rendah.empty:
                best_kecamatan = faskes_tinggi_prev_rendah.iloc[0]['Kecamatan']
                best_prevalensi = faskes_tinggi_prev_rendah.iloc[0]['Prevalensi Stunting Persen']
                best_faskes = faskes_tinggi_prev_rendah.iloc[0]['Total Faskes']
            else:
                best_row = analysis_df.nsmallest(1, 'Prevalensi Stunting Persen').iloc[0]
                best_kecamatan = best_row['Kecamatan']
                best_prevalensi = best_row['Prevalensi Stunting Persen']
                best_faskes = best_row['Total Faskes']
            
            create_white_kpi_card(
                value=best_kecamatan,
                title="Kondisi Terbaik",
                description=f"{best_faskes:.0f} faskes, {best_prevalensi:.1f}% stunting"
            )
        
        with col3:
            # Challenge area
            faskes_rendah_prev_tinggi = analysis_df[
                (analysis_df['Total Faskes'] <= analysis_df['Total Faskes'].quantile(0.3)) & 
                (analysis_df['Prevalensi Stunting Persen'] >= analysis_df['Prevalensi Stunting Persen'].quantile(0.7))
            ].sort_values('Prevalensi Stunting Persen', ascending=False)
            
            if not faskes_rendah_prev_tinggi.empty:
                challenge_kecamatan = faskes_rendah_prev_tinggi.iloc[0]['Kecamatan']
                challenge_prevalensi = faskes_rendah_prev_tinggi.iloc[0]['Prevalensi Stunting Persen']
                challenge_faskes = faskes_rendah_prev_tinggi.iloc[0]['Total Faskes']
            else:
                challenge_row = analysis_df.nlargest(1, 'Prevalensi Stunting Persen').iloc[0]
                challenge_kecamatan = challenge_row['Kecamatan']
                challenge_prevalensi = challenge_row['Prevalensi Stunting Persen']
                challenge_faskes = challenge_row['Total Faskes']
            
            create_white_kpi_card(
                value=challenge_kecamatan,
                title="Perlu Perhatian",
                description=f"{challenge_faskes:.0f} faskes, {challenge_prevalensi:.1f}% stunting"
            )

    # Analisis menggunakan fungsi utility
    avg_faskes = analysis_df['Total Faskes'].mean()
    high_faskes_low_prev = len(faskes_tinggi_prev_rendah)
    low_faskes_high_prev = len(faskes_rendah_prev_tinggi)
    
    st.info(create_correlation_analysis(correlation, avg_faskes, high_faskes_low_prev, low_faskes_high_prev))

    # Stunting Composition
    render_section_header("📊 Komposisi Jenis Stunting")

    composition_df = filtered_df.groupby('Tahun').agg({
        'Pendek': 'sum',
        'Sangat Pendek': 'sum'
    }).reset_index()

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=composition_df['Tahun'], 
        y=composition_df['Pendek'], 
        name='Pendek',
        text=composition_df['Pendek'],
        textposition='inside',
        marker_color='#2a89a6'
    ))
    fig_comp.add_trace(go.Bar(
        x=composition_df['Tahun'], 
        y=composition_df['Sangat Pendek'], 
        name='Sangat Pendek',
        text=composition_df['Sangat Pendek'],
        textposition='inside',
        marker_color='#c85a5a'
    ))
    fig_comp.update_layout(
        barmode='stack', 
        title='Komposisi Kasus Stunting: Pendek vs Sangat Pendek', 
        xaxis_title='Tahun', 
        yaxis_title='Jumlah Kasus', 
        height=500
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # Composition analysis
    total_pendek = composition_df['Pendek'].sum()
    total_sangat_pendek = composition_df['Sangat Pendek'].sum()
    total_stunting_comp = total_pendek + total_sangat_pendek
    pct_sangat_pendek = (total_sangat_pendek / total_stunting_comp * 100) if total_stunting_comp > 0 else 0

    if len(composition_df) > 1:
        latest_year_comp = composition_df.iloc[-1]
        earliest_year_comp = composition_df.iloc[0]
        
        latest_total = latest_year_comp['Pendek'] + latest_year_comp['Sangat Pendek']
        earliest_total = earliest_year_comp['Pendek'] + earliest_year_comp['Sangat Pendek']
        
        latest_pct_severe = (latest_year_comp['Sangat Pendek'] / latest_total) * 100 if latest_total > 0 else 0
        earliest_pct_severe = (earliest_year_comp['Sangat Pendek'] / earliest_total) * 100 if earliest_total > 0 else 0
        severity_trend = latest_pct_severe - earliest_pct_severe
        
        st.info(f"**Komposisi Stunting**: Dari total {total_stunting_comp:,} kasus stunting, {pct_sangat_pendek:.0f}% ({total_sangat_pendek:,} kasus) termasuk kategori 'Sangat Pendek' dan {100-pct_sangat_pendek:.0f}% ({total_pendek:,} kasus) kategori 'Pendek'. Dari periode {earliest_year_comp['Tahun']} ke {latest_year_comp['Tahun']}, proporsi kasus 'Sangat Pendek' mengalami {'peningkatan' if severity_trend > 0 else 'penurunan'} sebesar {abs(severity_trend):.1f}%.")
    else:
        st.info(f"**Komposisi Stunting**: Dari total {total_stunting_comp:,} kasus stunting, {pct_sangat_pendek:.0f}% ({total_sangat_pendek:,} kasus) termasuk kategori 'Sangat Pendek' yang memerlukan penanganan intensif, sementara {100-pct_sangat_pendek:.0f}% ({total_pendek:,} kasus) masuk kategori 'Pendek' yang dapat ditangani dengan intervensi preventif.")

if __name__ == "__main__":
    main()