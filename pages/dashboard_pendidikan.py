"""
Dashboard Pendidikan - Modular Version
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import *
from src.components.layouts import render_dashboard_header, render_section_header
from src.components.cards import create_kpi_card
from src.components.filters import create_year_filter, create_multiselect_filter, create_selectbox_filter
from src.components.charts import create_line_chart, create_bar_chart
from src.utils.data_loader import load_pendidikan_data, load_geojson_data
from src.utils.pendidikan_analyzer import get_latest_period, create_trend_analysis, analyze_prevalence_category
from src.styles.main import load_pendidikan_css
from src.config.constants import PENDIDIKAN_LABEL_MAPPING
from src.utils.helpers import format_indicator_value


# Page config
st.set_page_config(
    page_title="Dashboard Pendidikan Kabupaten Malang",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
load_pendidikan_css()

# Load data
@st.cache_data
def load_data():
    return load_pendidikan_data()

@st.cache_data  
def load_geo_data():
    return load_geojson_data(GEO_DATA_PATH / "35.07_kecamatan.geojson")

# Main app
def main():
    # Load data
    df = load_data()
    geojson_kec = load_geo_data()
    
    if df.empty:
        st.error("Data pendidikan tidak dapat dimuat!")
        st.stop()

    # Sidebar filters
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h2>⚙️ Filter Data</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🗓️ **Filter Waktu & Jenjang**", expanded=True):
            years = sorted(df['tahun'].unique())
            jenjangs = sorted(df['jenjang'].unique())
            selected_year = st.selectbox("Pilih Tahun", years)
            selected_jenjang = st.selectbox("Pilih Jenjang", jenjangs)

    # Filter data
    filtered_df = df[(df['tahun'] == selected_year) & (df['jenjang'] == selected_jenjang)]
    
    if filtered_df.empty:
        st.warning(f"Tidak ada data untuk Tahun {selected_year}, Jenjang {selected_jenjang}.")
        st.stop()

    # Create ratio column
    filtered_df = filtered_df.copy()
    if 'jumlah_sekolah' in filtered_df.columns and 'jumlah_penduduk_usia_sekolah' in filtered_df.columns:
        non_zero_mask = filtered_df['jumlah_penduduk_usia_sekolah'] != 0
        filtered_df.loc[non_zero_mask, 'rasio_sekolah_penduduk'] = (
            filtered_df.loc[non_zero_mask, 'jumlah_sekolah'] / 
            filtered_df.loc[non_zero_mask, 'jumlah_penduduk_usia_sekolah']
        ) * 1000

    # Header
    render_dashboard_header(
        title="🎓 Dashboard Pendidikan Kabupaten Malang",
        subtitle=f"Analisis Data Pendidikan Tahun {selected_year} - Jenjang {selected_jenjang}",
        description="📊 Dashboard Interaktif untuk Analisis APK, APM, dan Kualitas Pendidikan"
    )

    # KPI Cards
    render_section_header("🎯 Indikator Utama Rata-rata Kabupaten")
    
    col1, col2, col3, col4 = st.columns(4)
    
    avg_apk = filtered_df['apk'].mean()
    avg_apm = filtered_df['apm'].mean() 
    avg_guru_s1 = filtered_df['persentase_guru_s1'].mean()
    avg_akreditasi = filtered_df['persentase_sekolah_akreditasi'].mean()

    with col1:
        create_kpi_card(
            title=PENDIDIKAN_LABEL_MAPPING["apk"],
            value=f"{avg_apk:.2f}%",
            icon="🎯"
        )
    with col2:
        create_kpi_card(
            title=PENDIDIKAN_LABEL_MAPPING["apm"],
            value=f"{avg_apm:.2f}%",
            icon="🧑‍🎓"
        )
    with col3:
        create_kpi_card(
            title=PENDIDIKAN_LABEL_MAPPING["persentase_guru_s1"],
            value=f"{avg_guru_s1:.2f}%",
            icon="👩‍🏫"
        )
    with col4:
        create_kpi_card(
            title=PENDIDIKAN_LABEL_MAPPING["persentase_sekolah_akreditasi"],
            value=f"{avg_akreditasi:.2f}%",
            icon="⭐"
        )

    # Map Section
    render_section_header("🗺️ Peta Sebaran Indikator per Kecamatan")
    
    all_indicator_options = {
        PENDIDIKAN_LABEL_MAPPING.get(col, col): col 
        for col in PENDIDIKAN_LABEL_MAPPING.keys() 
        if col in filtered_df.columns
    }

    if all_indicator_options:
        selected_indicator_label = st.selectbox("Pilih Indikator Peta", list(all_indicator_options.keys()))
        selected_indicator = all_indicator_options[selected_indicator_label]

        # Create choropleth map
        map_display_df = filtered_df[['kecamatan', selected_indicator]].dropna().rename(columns={"kecamatan": "kecamatan"})

        if geojson_kec and not map_display_df.empty:
            fig_map = px.choropleth_mapbox(
                map_display_df,
                geojson=geojson_kec,
                locations="kecamatan",
                featureidkey="properties.nm_kecamatan",
                color=selected_indicator,
                color_continuous_scale=["#e8e8e8", "#d1ecf2", "#2a89a6", "#62718c", "#574249", "#ad9ea5", "#e4acac", "#c85a5a", "#985356"],
                mapbox_style="carto-positron",
                zoom=8.5,
                center={"lat": -8.10, "lon": 112.65},
                opacity=1,
                labels={selected_indicator: selected_indicator_label},
                hover_name="kecamatan",
            )

            # ===== Tambahkan label kecamatan di atas polygon =====
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
                        hoverinfo='skip'
                    ))
            except Exception as e:
                st.warning(f"Could not generate map labels. Please ensure 'geopandas' is installed. Error: {e}", icon="⚠️")

            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.plotly_chart(fig_map, use_container_width=True)
            
            with col2:
                if not map_display_df.empty:
                    max_row = map_display_df.loc[map_display_df[selected_indicator].idxmax()]
                    min_row = map_display_df.loc[map_display_df[selected_indicator].idxmin()]
                    avg_value = map_display_df[selected_indicator].mean()

                    # Best/Worst performers
                    st.markdown(f"""
                    <div class="insight-box insight-box-good">
                        <h4>🏆 Best Performer</h4>
                        <p class="kecamatan-name">{max_row['kecamatan']}</p>
                        <span class="value">{format_indicator_value(selected_indicator, max_row[selected_indicator])}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="insight-box insight-box-bad">
                        <h4>⚠️ Needs Attention</h4>
                        <p class="kecamatan-name">{min_row['kecamatan']}</p>
                        <span class="value">{format_indicator_value(selected_indicator, min_row[selected_indicator])}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Summary
                    above_avg = sum(map_display_df[selected_indicator] >= avg_value)
                    below_avg = sum(map_display_df[selected_indicator] < avg_value)

                    st.markdown(f"""
                    <div style="text-align: center; font-size: 0.9rem;">
                        Rata-rata Kabupaten: <strong>{format_indicator_value(selected_indicator, avg_value)}</strong><br>
                        <hr class="custom-hr">
                        ✅ {above_avg} Kec. di atas rata-rata<br>
                        ❌ {below_avg} Kec. di bawah rata-rata
                    </div>
                    """, unsafe_allow_html=True)


    # Trend Analysis
    render_section_header(f"📈 Tren Tahunan {PENDIDIKAN_LABEL_MAPPING['apk']} & {PENDIDIKAN_LABEL_MAPPING['apm']}")
    
    kecamatan_options = ["Semua Kecamatan (Rata-rata)"] + sorted(df['kecamatan'].unique().tolist())
    selected_kec = st.selectbox("Pilih Kecamatan", kecamatan_options)

    if selected_kec == "Semua Kecamatan (Rata-rata)":
        plot_df = df[df['jenjang'] == selected_jenjang].groupby('tahun')[['apk', 'apm']].mean().reset_index()
    else:
        plot_df = df[(df['kecamatan'] == selected_kec) & (df['jenjang'] == selected_jenjang)].copy()

    # --- Pre-calculate trend variables to be used in columns and the full-width insight below ---
    latest_apk, latest_apm, prev_apk, prev_apm, gap, prev_year = (None, None, None, None, float('nan'), None)

    if not plot_df.empty:
        # Always calculate latest values and gap if possible
        latest_year_data = plot_df[plot_df['tahun'] == plot_df['tahun'].max()]
        latest_apk = latest_year_data['apk'].mean()
        latest_apm = latest_year_data['apm'].mean()
        gap = latest_apk - latest_apm

        # Calculate previous year values only if there's enough data
        unique_years = sorted(plot_df['tahun'].unique())
        if len(unique_years) > 1:
            prev_year = unique_years[-2]
            prev_data = plot_df[plot_df['tahun'] == prev_year]
            prev_apk = prev_data['apk'].mean()
            prev_apm = prev_data['apm'].mean()

    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not plot_df.empty:
            fig_line = px.line(
                plot_df, x="tahun", y=["apk", "apm"], markers=True,
                labels={c: PENDIDIKAN_LABEL_MAPPING.get(c, c) for c in plot_df.columns},
                color_discrete_map={"apk": "#004c70", "apm": "#c85a5a"}
            )
            fig_line.update_yaxes(title="Persentase")
            st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display evaluation and comparison text if trend data is available
        if prev_year is not None and prev_apk is not None:
                score = 0
                feedback = []

                if latest_apk > prev_apk:
                    score += 1
                    feedback.append("APK naik 📈")
                else:
                    feedback.append("APK turun 📉")

                if latest_apm > prev_apm:
                    score += 1
                    feedback.append("APM naik 📈")
                else:
                    feedback.append("APM turun 📉")

                if not pd.isna(gap) and gap < 20:
                    score += 1
                    feedback.append("Gap kecil 👍")
                else:
                    feedback.append("Gap besar ⚠️")

                if score == 3:
                    st.markdown('<div class="custom-alert custom-alert-success">✅ <strong>Sangat Baik:</strong> Semua indikator menunjukkan tren positif.</div>', unsafe_allow_html=True)
                elif score == 2:
                    st.markdown('<div class="custom-alert custom-alert-info">📊 <strong>Cukup Baik:</strong> Sebagian besar indikator membaik.</div>', unsafe_allow_html=True)
                elif score == 1:
                    st.markdown('<div class="custom-alert custom-alert-warning">⚠️ <strong>Perlu Perhatian:</strong> Hanya satu dari tiga kriteria positif yang terpenuhi.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="custom-alert custom-alert-error">❌ <strong>Kurang Baik:</strong> Tidak ada kriteria positif yang terpenuhi.</div>', unsafe_allow_html=True)

                st.markdown("**Detail evaluasi:** " + ", ".join(feedback))

                st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
                apk_trend = "naik 📈" if latest_apk > prev_apk else "turun 📉"
                apm_trend = "naik 📈" if latest_apm > prev_apm else "turun 📉"
                comparison_text = f"""
                ℹ️ **Dibanding tahun sebelumnya:**<br>
                - APK {apk_trend} dari {prev_apk:.2f}% → {latest_apk:.2f}%<br>
                - APM {apm_trend} dari {prev_apm:.2f}% → {latest_apm:.2f}%<br>
                - Selisih APK–APM saat ini **{gap:.2f} poin**
                """
                st.markdown(comparison_text, unsafe_allow_html=True)
        
        # Display message if only single-year data is available
        elif not pd.isna(gap):
                if gap <= 20:
                    st.markdown('<div class="custom-alert custom-alert-success">✅ <strong>Cukup Baik:</strong> Selisih APK-APM kecil.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="custom-alert custom-alert-warning">⚠️ <strong>Perlu Perhatian:</strong> Selisih APK-APM masih besar.</div>', unsafe_allow_html=True)
                st.info("Data tahun sebelumnya tidak tersedia untuk perbandingan.")
        else:
            st.info("Tidak ada data yang cukup untuk ditampilkan.")

    # --- Full-width narrative insight section ---
    if not pd.isna(gap):
        # Generate narrative insight
        narrative_insight = ""
        
        # Analisis kesenjangan (gap)
        if gap > 20:
            gap_text = f"Selisih APK-APM yang **besar ({gap:.2f} poin)** mengindikasikan perlunya perhatian pada ketepatan usia masuk sekolah dan pencegahan tinggal kelas."
        else:
            gap_text = f"Selisih APK-APM yang **kecil ({gap:.2f} poin)** menunjukkan mayoritas siswa sudah berada pada jenjang yang sesuai dengan usianya, yang merupakan sinyal positif."

        # Analisis tren (jika ada data pembanding)
        if prev_year is not None and prev_apk is not None and prev_apm is not None:
            apk_trend_text = "meningkat" if latest_apk > prev_apk else "menurun" if latest_apk < prev_apk else "stabil"
            apm_trend_text = "meningkat" if latest_apm > prev_apm else "menurun" if latest_apm < prev_apm else "stabil"
            
            narrative_insight = f"**Analisis Tren & Kesenjangan**: APK tercatat **{apk_trend_text}** sementara APM **{apm_trend_text}**. {gap_text}"
        else:
            # Fallback jika tidak ada data tren
            narrative_insight = f"**Analisis Kesenjangan**: {gap_text} (Data tren tahunan tidak tersedia untuk perbandingan)."

        # Tampilkan insight naratif
        if narrative_insight:
            st.info(narrative_insight)
    
    # Comparison Charts
    render_section_header(f"📊 Perbandingan {PENDIDIKAN_LABEL_MAPPING['apk']} & {PENDIDIKAN_LABEL_MAPPING['apm']} per Kecamatan")
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=filtered_df['kecamatan'],
        y=filtered_df['apk'],
        name=PENDIDIKAN_LABEL_MAPPING['apk'],
        marker_color="#004c70"
    ))
    fig_bar.add_trace(go.Bar(
        x=filtered_df['kecamatan'],
        y=filtered_df['apm'],
        name=PENDIDIKAN_LABEL_MAPPING['apm'],
        marker_color="#c85a5a"
    ))
    fig_bar.update_layout(barmode='group', xaxis_title="Kecamatan", yaxis_title="Persentase")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Ranking
    render_section_header("🏅 Ranking Kecamatan (5 Tertinggi & 5 Terendah)")
    
    tab_apm, tab_apk = st.tabs([
        f"Ranking {PENDIDIKAN_LABEL_MAPPING['apm']}", 
        f"Ranking {PENDIDIKAN_LABEL_MAPPING['apk']}"
    ])

    with tab_apm:
        ranked_apm = filtered_df[['kecamatan', 'apm']].dropna(subset=['apm']).sort_values(by='apm', ascending=False)
        col1, col2 = st.columns(2)
        with col1:
            top_5 = ranked_apm.head(5)
            fig_top = px.bar(
                top_5.sort_values(by='apm', ascending=True), x='apm', y='kecamatan',
                title=f"🔝 5 Kecamatan dengan {PENDIDIKAN_LABEL_MAPPING['apm']} Tertinggi",
                orientation='h', color='apm', color_continuous_scale=['#d1ecf2', '#004c70'], text='apm',
                labels={'kecamatan': 'Kecamatan', 'apm': 'APM'}
            )
            fig_top.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            # Adjust x-axis range to prevent labels from being cut off
            max_val_top = top_5['apm'].max()
            fig_top.update_layout(height=400, yaxis_title=None, xaxis_title=None, title_font_size=16, xaxis_range=[0, max_val_top * 1.15])
            st.plotly_chart(fig_top, use_container_width=True)
        with col2:
            bottom_5 = ranked_apm.tail(5)
            fig_bottom = px.bar(
                bottom_5.sort_values(by='apm', ascending=True), x='apm', y='kecamatan',
                title=f"🔻 5 Kecamatan dengan {PENDIDIKAN_LABEL_MAPPING['apm']} Terendah",
                orientation='h', color='apm', color_continuous_scale=['#e4acac', '#c85a5a'], text='apm',
                labels={'kecamatan': 'Kecamatan', 'apm': 'APM'}
            )
            fig_bottom.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            # Adjust x-axis range to prevent labels from being cut off
            max_val_bottom = bottom_5['apm'].max()
            fig_bottom.update_layout(height=400, yaxis_title=None, xaxis_title=None, title_font_size=16, xaxis_range=[0, max_val_bottom * 1.15])
            st.plotly_chart(fig_bottom, use_container_width=True)

    with tab_apk:
        ranked_apk = filtered_df[['kecamatan', 'apk']].dropna(subset=['apk']).sort_values(by='apk', ascending=False)
        col1, col2 = st.columns(2)
        with col1:
            top_5 = ranked_apk.head(5)
            fig_top = px.bar(
                top_5.sort_values(by='apk', ascending=True), x='apk', y='kecamatan',
                title=f"🔝 5 Kecamatan dengan {PENDIDIKAN_LABEL_MAPPING['apk']} Tertinggi",
                orientation='h', color='apk', color_continuous_scale=['#d1ecf2', '#004c70'], text='apk',
                labels={'kecamatan': 'Kecamatan', 'apk': 'APK'}
            )
            fig_top.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            # Adjust x-axis range to prevent labels from being cut off
            max_val_top = top_5['apk'].max()
            fig_top.update_layout(height=400, yaxis_title=None, xaxis_title=None, title_font_size=16, xaxis_range=[0, max_val_top * 1.15])
            st.plotly_chart(fig_top, use_container_width=True)
        with col2:
            bottom_5 = ranked_apk.tail(5)
            fig_bottom = px.bar(
                bottom_5.sort_values(by='apk', ascending=True), x='apk', y='kecamatan',
                title=f"🔻 5 Kecamatan dengan {PENDIDIKAN_LABEL_MAPPING['apk']} Terendah",
                orientation='h', color='apk', color_continuous_scale=['#e4acac', '#c85a5a'], text='apk',
                labels={'kecamatan': 'Kecamatan', 'apk': 'APK'}
            )
            fig_bottom.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            # Adjust x-axis range to prevent labels from being cut off
            max_val_bottom = bottom_5['apk'].max()
            fig_bottom.update_layout(height=400, yaxis_title=None, xaxis_title=None, title_font_size=16, xaxis_range=[0, max_val_bottom * 1.15])
            st.plotly_chart(fig_bottom, use_container_width=True)

    # Correlation Analysis
    render_section_header("🔗 Korelasi Antar Indikator")
    
    col1, col2 = st.columns([1, 2])

    # Calculate correlation matrix
    corr_cols = ['apk', 'apm', 'persentase_guru_s1', 'persentase_sekolah_akreditasi']
    corr = filtered_df[corr_cols].corr()

    with col1:
        st.markdown("""
        <div class="correlation-explainer">
        <h4>Memahami Korelasi</h4>
        <p>Heatmap di samping menunjukkan seberapa erat hubungan antar indikator. Nilai mendekati <strong>+1 (biru tua)</strong> berarti hubungan positif yang erat, sedangkan nilai mendekati <strong>-1 (merah tua)</strong> berarti hubungan negatif yang erat. Nilai mendekati <strong>0 (putih)</strong> berarti hampir tidak ada hubungan.</p>
        <ul>
            <li><strong>Positif (+):</strong> Jika satu indikator naik, yang lain cenderung ikut naik.</li>
            <li><strong>Negatif (-):</strong> Jika satu indikator naik, yang lain cenderung turun.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        # Find and display the strongest correlation
        def interpret_correlation(val):
            if val > 0.7: return "Hubungan Erat (+)"
            elif val > 0.3: return "Hubungan Sedang (+)"
            elif val > 0: return "Hubungan Lemah (+)"
            elif val < -0.7: return "Hubungan Erat (−)"
            elif val < -0.3: return "Hubungan Sedang (−)"
            elif val < 0: return "Hubungan Lemah (−)"
            else: return "Tidak ada hubungan"

        corr_table = []
        cols = corr.columns
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = corr.iloc[i, j]
                corr_table.append({
                    "Indikator X": PENDIDIKAN_LABEL_MAPPING.get(cols[i], cols[i]),
                    "Indikator Y": PENDIDIKAN_LABEL_MAPPING.get(cols[j], cols[j]),
                    "Nilai Korelasi": val,
                })
        
        if corr_table:
            corr_df = pd.DataFrame(corr_table)
            strongest = corr_df.iloc[corr_df['Nilai Korelasi'].abs().idxmax()]
            strongest_val = strongest['Nilai Korelasi']
            
            st.info(
                f"**Insight Utama:** Hubungan terkuat ditemukan antara **{strongest['Indikator X']}** dan **{strongest['Indikator Y']}** dengan nilai **{strongest_val:.2f}** ({interpret_correlation(strongest_val)})."
            )
    
    with col2:
        corr_renamed = corr.rename(columns=PENDIDIKAN_LABEL_MAPPING, index=PENDIDIKAN_LABEL_MAPPING)
        fig_corr = px.imshow(
            corr_renamed, text_auto='.2f', aspect="auto",
            color_continuous_scale='RdBu', color_continuous_midpoint=0,
            title="Heatmap Korelasi Antar Indikator"
        )
        fig_corr.update_xaxes(side="bottom")
        fig_corr.update_layout(title_font_size=18, coloraxis_colorbar=dict(title="Korelasi"))
        st.plotly_chart(fig_corr, use_container_width=True)

if __name__ == "__main__":
    main()