import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import json
import geopandas as gpd

# ====================
# PAGE CONFIGURATION
# ====================
st.set_page_config(
    page_title="Dashboard Pendidikan Kabupaten Malang",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================
# CUSTOM CSS
# ====================
st.markdown("""
<style>
    /* Garis custom lebih rapat */
    .custom-hr {
        border: 0;
        border-top: 1px solid #ddd;
        margin: 0.3rem 0;   /* jarak atas-bawah garis */
    }

    /* Rapikan jarak antar elemen */
    .stMarkdown, .stText, .stMetric, .stPlotlyChart, .stDataFrame {
        margin-top: 0rem;
        margin-bottom: 0.4rem;
        padding: 0rem;
    }

    /* Atur kolom agar sejajar di top */
    div[data-testid="column"] {
        vertical-align: top;
    }

    /* Header Utama */
    .main-header {
        background: linear-gradient(90deg, #62718c 0%, #2a89a6 100%, #62718c 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 { margin-bottom: 0.2rem; font-size: 2.5rem; }
    .main-header h3 { margin-bottom: 0.5rem; font-weight: 500; font-size: 1.2rem; }
    .main-header p { font-style: italic; font-size: 1rem; }

    /* Header untuk setiap seksi */
    .section-header {
        background-color: #f0f2f6;
        padding: 0.7rem 1rem;
        border-radius: 7px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-left: 5px solid #004c70; /* Aksen warna biru */
    }
    .section-header h3 {
        margin: 0;
        padding: 0;
        color: #31333F;
        font-size: 1.4rem; /* Ukuran font diperbesar */
        font-weight: 600;  /* Diberi sedikit ketebalan */
    }

    /* KPI Box Style */
    .kpi-box {
        background-color: #62718c; /* Warna abu-abu kebiruan dari palet peta */
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        height: 160px; /* Tinggi tetap untuk keseragaman */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .kpi-box:hover {
        transform: scale(1.03);
    }
    .kpi-icon {
        font-size: 2.5rem;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    .kpi-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
    }

    /* Insight Box di samping peta */
    .insight-box {
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        border-left: 5px solid;
        text-align: center;
    }
    .insight-box h4 {
        margin: 0 0 0.2rem 0;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #555;
    }
    .insight-box .kecamatan-name {
        margin: 0;
        font-size: 1.2rem;
        font-weight: 700;
        color: #333;
    }
    .insight-box .value {
        font-size: 1rem;
        font-weight: 500;
        color: #444;
    }
    .insight-box-good {
        border-color: #28a745; /* Green */
        background-color: #f0fff4; /* Light Green */
    }
    .insight-box-bad {
        border-color: #ffeeba; /* Yellow for warning */
        background-color: #fff3cd; /* Light yellow for warning */
    }

    /* Custom Alerts for Trend Section */
    .custom-alert {
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        border-radius: .375rem;
        font-size: 0.9rem;
    }
    .custom-alert-success {
        color: #004c70; /* Dark Blue */
        background-color: #eef7fa; /* Light Blue */
        border-color: #bde0eb;
    }
    .custom-alert-info {
        color: #31333F; /* Dark Gray */
        background-color: #f0f2f6; /* Light Gray */
        border-color: #d6d8db;
    }
    .custom-alert-warning {
        color: #856404;
        background-color: #fff3cd;
        border-color: #ffeeba;
    }
    .custom-alert-error {
        color: #985356; /* Darker Red from theme */
        background-color: #fff0f0; /* Light Red from theme */
        border-color: #c85a5a; /* Main Red from theme */
    }

    /* Insight Summary Box for Trend Section */
    .insight-summary-box {
        background-color: #f0f2f6; /* Light Gray */
        border: 1px solid #d6d8db;
        border-left: 5px solid #004c70; /* Blue accent */
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-top: 0.2rem; /* Jarak atas dikurangi */
    }
    .insight-summary-box ul {
        margin: 0;
        padding-left: 1.2rem;
    }
    .insight-summary-box li {
        margin-bottom: 0.5rem;
        padding-left: 0.5rem;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }

    .sidebar-header {
        background-color: #004c70;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
    }

    .sidebar-header h2 {
        margin: 0;
        font-size: 1.5rem;
    }

    [data-testid="stExpander"] summary {
        font-size: 1.1rem;
        font-weight: 600;
        color: #31333F;
    }
</style>
""", unsafe_allow_html=True)

# ====================
# LABEL MAPPING
# ====================
label_mapping = {
    "apk": "Angka Partisipasi Kasar (APK)",
    "apm": "Angka Partisipasi Murni (APM)",
    "persentase_guru_s1": "Persentase Guru S1",
    "persentase_sekolah_akreditasi": "Persentase Sekolah Terakreditasi",
    "jumlah_siswa": "Jumlah Siswa",
    "jumlah_sekolah": "Jumlah Sekolah",
    "jumlah_penduduk_usia_sekolah": "Jumlah Penduduk Usia Sekolah",
    "rasio_sekolah_penduduk": "Rasio Sekolah per 1000 Penduduk"
}

# ====================
# LOAD DATA
# ====================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        column_mapping = {
            'Tahun': 'tahun',
            'Jenjang': 'jenjang',
            'Kecamatan': 'kecamatan',
            'APK (%)': 'apk',
            'APM (%)': 'apm',
            'Persentase Guru S1': 'persentase_guru_s1',
            'Persentase Sekolah Terakreditasi': 'persentase_sekolah_akreditasi',
            'Jumlah Siswa': 'jumlah_siswa',
            'Jumlah Sekolah': 'jumlah_sekolah',
            'Jumlah Penduduk Usia Sekolah': 'jumlah_penduduk_usia_sekolah'
        }
        df = df.rename(columns=column_mapping)

        # Konversi kolom numerik
        numeric_cols = list(label_mapping.keys())
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Hapus baris kosong pada kolom inti
        core_cols = ['apk', 'apm', 'persentase_guru_s1', 'persentase_sekolah_akreditasi']
        df.dropna(subset=core_cols, inplace=True)
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan: {path}.")
        return pd.DataFrame()

file_path = "data/pendidikan/pendidikan_paud_sd_smp.csv"
df = load_data(file_path)
if df.empty:
    st.stop()

# ====================
# LOAD GEOJSON
# ====================
geojson_kec_path = "data/geo/35.07_kecamatan.geojson"
with open(geojson_kec_path, 'r', encoding='utf-8') as f:
    geojson_kec = json.load(f)

@st.cache_data
def load_geodata(path: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf.set_crs("EPSG:4326", inplace=True)
    gdf['centroid'] = gdf.geometry.centroid
    return gdf

# ====================
# SIDEBAR FILTERS
# ====================
st.sidebar.markdown("""
<div class="sidebar-header">
    <h2>⚙️ Filter Data</h2>
</div>
""", unsafe_allow_html=True)

with st.sidebar.expander("🗓️ **Filter Waktu & Jenjang**", expanded=True):
    years = sorted(df['tahun'].unique())
    jenjangs = sorted(df['jenjang'].unique())
    selected_year = st.selectbox("Pilih Tahun", years)
    selected_jenjang = st.selectbox("Pilih Jenjang", jenjangs)

filtered_df = df[(df['tahun'] == selected_year) & (df['jenjang'] == selected_jenjang)]
if filtered_df.empty:
    st.warning(f"Tidak ada data untuk Tahun {selected_year}, Jenjang {selected_jenjang}.")
    st.stop()

# Buat kolom rasio baru
filtered_df = filtered_df.copy()
if 'jumlah_sekolah' in filtered_df.columns and 'jumlah_penduduk_usia_sekolah' in filtered_df.columns:
    non_zero_mask = filtered_df['jumlah_penduduk_usia_sekolah'] != 0
    filtered_df.loc[non_zero_mask, 'rasio_sekolah_penduduk'] = (
        filtered_df.loc[non_zero_mask, 'jumlah_sekolah'] / filtered_df.loc[non_zero_mask, 'jumlah_penduduk_usia_sekolah']
    ) * 1000

# ====================
# SCORECARDS
# ====================
st.markdown(f"""
<div class="main-header">
    <h1>🎓 Dashboard Pendidikan Kabupaten Malang</h1>
    <h3>Analisis Data Pendidikan Tahun {selected_year} - Jenjang {selected_jenjang}</h3>
    <p><em>📊 Dashboard Interaktif untuk Analisis APK, APM, dan Kualitas Pendidikan</em></p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header"><h3>🎯 Indikator Utama Rata-rata Kabupaten</h3></div>', unsafe_allow_html=True)

# Tambah sedikit spasi vertikal sebelum KPI
st.markdown('<div style="margin-top: 0.5rem;"></div>', unsafe_allow_html=True)

avg_apk = filtered_df['apk'].mean()
avg_apm = filtered_df['apm'].mean()
avg_guru_s1 = filtered_df['persentase_guru_s1'].mean()
avg_akreditasi = filtered_df['persentase_sekolah_akreditasi'].mean()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-icon">🎯</div>
        <div class="kpi-title">{label_mapping["apk"]}</div>
        <div class="kpi-value">{avg_apk:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-icon">🧑‍🎓</div>
        <div class="kpi-title">{label_mapping["apm"]}</div>
        <div class="kpi-value">{avg_apm:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-icon">👩‍🏫</div>
        <div class="kpi-title">{label_mapping["persentase_guru_s1"]}</div>
        <div class="kpi-value">{avg_guru_s1:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-icon">⭐</div>
        <div class="kpi-title">{label_mapping["persentase_sekolah_akreditasi"]}</div>
        <div class="kpi-value">{avg_akreditasi:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

# ====================
# PETA INTERAKTIF + INSIGHT
# ====================
st.markdown('<div class="section-header"><h3>🗺️ Peta Sebaran Indikator per Kecamatan</h3></div>', unsafe_allow_html=True)

all_indicator_options = {label_mapping.get(col, col): col for col in label_mapping.keys() if col in filtered_df.columns}

if not all_indicator_options:
    st.warning("Tidak ada data yang dapat ditampilkan di peta untuk filter yang dipilih.")
    st.stop()

selected_indicator_label = st.selectbox("Pilih Indikator Peta", list(all_indicator_options.keys()))
selected_indicator = all_indicator_options[selected_indicator_label]

# Bungkus judul legenda agar maksimal 2 kata per baris
words = selected_indicator_label.split()
wrapped_lines = []
for i in range(0, len(words), 2):
    wrapped_lines.append(" ".join(words[i:i+2]))
wrapped_legend_title = "<br>".join(wrapped_lines)

fig_map = px.choropleth_mapbox(
    filtered_df,
    geojson=geojson_kec,
    locations="kecamatan",
    featureidkey="properties.nm_kecamatan",
    color=selected_indicator,
    color_continuous_scale=["#e8e8e8", "#d1ecf2", "#2a89a6", "#62718c", "#574249", "#ad9ea5", "#e4acac", "#c85a5a", "#985356"],
    mapbox_style="carto-positron",
    zoom=8.5,
    center={"lat": -8.10, "lon": 112.63},
    opacity=1,
    labels={selected_indicator: selected_indicator_label}
)

fig_map.update_traces(
    marker_line_width=0.8, 
    marker_line_color="black",
    text=filtered_df['kecamatan'],
    hovertemplate="<b>%{text}</b><br>" + selected_indicator_label + ": %{z}<extra></extra>"
)

fig_map.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    coloraxis_colorbar=dict(
        title=dict(
            text=wrapped_legend_title, 
            font=dict(color="black") # Pertahankan warna judul hitam
        )
    )
)

gdf = load_geodata(geojson_kec_path)
gdf = gdf.merge(filtered_df, left_on="nm_kecamatan", right_on="kecamatan")

if not gdf.empty:
    lats = [point.y for point in gdf['centroid']]
    lons = [point.x for point in gdf['centroid']]
    texts = gdf['kecamatan']

    # Layer shadow
    fig_map.add_trace(go.Scattermapbox(
        lon=[x + 0.0008 for x in lons],
        lat=[y - 0.0008 for y in lats],
        mode='text',
        text=texts,
        textfont=dict(size=8, color='black'),
        showlegend=False,
        hovertemplate=None,
        hoverinfo='none'
    ))

    # Layer utama
    fig_map.add_trace(go.Scattermapbox(
        lon=lons,
        lat=lats,
        mode='text',
        text=texts,
        textfont=dict(size=8, color='white', family="Arial Black"),
        showlegend=False,
        hovertemplate=None,
        hoverinfo='none'
    ))

# ====================
# 2 kolom: Peta & Insight
# ====================
col1, col2 = st.columns([2, 1])

with col1:
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    max_row = filtered_df.loc[filtered_df[selected_indicator].idxmax()]
    min_row = filtered_df.loc[filtered_df[selected_indicator].idxmin()]
    avg_value = filtered_df[selected_indicator].mean()

    # Best Performer
    st.markdown(f"""
    <div class="insight-box insight-box-good">
        <h4>🏆 Best Performer</h4>
        <p class="kecamatan-name">{max_row['kecamatan']}</p>
        <span class="value">{max_row[selected_indicator]:.2f}%</span>
    </div>
    """, unsafe_allow_html=True)

    # Needs Attention
    st.markdown(f"""
    <div class="insight-box insight-box-bad">
        <h4>⚠️ Needs Attention</h4>
        <p class="kecamatan-name">{min_row['kecamatan']}</p>
        <span class="value">{min_row[selected_indicator]:.2f}%</span>
    </div>
    """, unsafe_allow_html=True)

    # Summary
    st.markdown(f"""
    <div style="text-align: center; font-size: 0.9rem;">
        Rata-rata Kabupaten: <strong>{avg_value:.2f}%</strong><br>
        <hr class="custom-hr">
        ✅ {sum(filtered_df[selected_indicator] >= avg_value)} Kec. di atas rata-rata<br>
        ❌ {sum(filtered_df[selected_indicator] < avg_value)} Kec. di bawah rata-rata
    </div>
    """, unsafe_allow_html=True)


# ====================
# VISUALISASI DASAR
# ====================
st.markdown(f'<div class="section-header"><h3>📈 Tren Tahunan {label_mapping["apk"]} & {label_mapping["apm"]}</h3></div>', unsafe_allow_html=True)

kecamatan_options = ["Semua Kecamatan (Rata-rata)"] + sorted(df['kecamatan'].unique().tolist())
selected_kec = st.selectbox("Pilih Kecamatan", kecamatan_options)

if selected_kec == "Semua Kecamatan (Rata-rata)":
    plot_df = df[df['jenjang'] == selected_jenjang].groupby('tahun')[['apk', 'apm']].mean().reset_index()
    # title_chart = f"Perkembangan {label_mapping['apk']} & {label_mapping['apm']} (Rata-rata Kabupaten)"
else:
    plot_df = df[(df['kecamatan'] == selected_kec) & (df['jenjang'] == selected_jenjang)].copy()
    # title_chart = f"Perkembangan {label_mapping['apk']} & {label_mapping['apm']} - {selected_kec}"

# Hitung insight
years_sorted = sorted(plot_df['tahun'].unique())
latest_year = years_sorted[-1]
prev_year = years_sorted[-2] if len(years_sorted) >= 2 else None

latest_data = plot_df[plot_df['tahun'] == latest_year]
prev_data = plot_df[plot_df['tahun'] == prev_year] if prev_year is not None else pd.DataFrame()

latest_apk = latest_data['apk'].mean()
latest_apm = latest_data['apm'].mean()
gap = latest_apk - latest_apm

prev_apk = prev_data['apk'].mean() if not prev_data.empty else None
prev_apm = prev_data['apm'].mean() if not prev_data.empty else None

# Layout 2 kolom
col1, col2 = st.columns([2,1])

with col1:
    fig_line = px.line(
        plot_df, x="tahun", y=["apk", "apm"], markers=True,
        labels={c: label_mapping.get(c, c) for c in plot_df.columns},
        # title=title_chart,
        color_discrete_map={"apk": "#004c70", "apm": "#c85a5a"}
    )
    fig_line.update_yaxes(title="Persentase")
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if prev_year is not None and not prev_data.empty:
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

        if gap < 20:
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

    else:
        if gap <= 20:
            st.markdown('<div class="custom-alert custom-alert-success">✅ <strong>Cukup Baik:</strong> Selisih APK-APM kecil.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="custom-alert custom-alert-warning">⚠️ <strong>Perlu Perhatian:</strong> Selisih APK-APM masih besar.</div>', unsafe_allow_html=True)

    st.markdown('<hr class="custom-hr">', unsafe_allow_html=True)
    if prev_year is not None and not prev_data.empty:
        apk_trend = "naik 📈" if latest_apk > prev_apk else "turun 📉"
        apm_trend = "naik 📈" if latest_apm > prev_apm else "turun 📉"
        # Gabungkan beberapa markdown menjadi satu blok untuk merapatkan jarak
        comparison_text = f"""
        ℹ️ **Dibanding tahun sebelumnya:**<br>
        - APK {apk_trend} dari {prev_apk:.2f}% → {latest_apk:.2f}%<br>
        - APM {apm_trend} dari {prev_apm:.2f}% → {latest_apm:.2f}%<br>
        - Selisih APK–APM saat ini **{gap:.2f} poin**
        """
        st.markdown(comparison_text, unsafe_allow_html=True)
    else:
        st.info("Data tahun sebelumnya tidak tersedia untuk perbandingan.")

insight_lines = []

# Interpretasi APK
if prev_year is not None and prev_apk is not None:
    if latest_apk > prev_apk:
        insight_lines.append("- **APK meningkat** → akses/partisipasi sekolah makin luas; proporsi siswa di luar usia ideal yang masih bersekolah bisa bertambah.")
    elif latest_apk < prev_apk:
        insight_lines.append("- **APK menurun** → partisipasi sekolah berkurang; perlu perhatian pada faktor akses/retensi.")
    else:
        insight_lines.append("- **APK stabil** → partisipasi relatif tidak berubah.")
else:
    insight_lines.append("- **APK (tren tahunan)**: data pembanding tidak tersedia.")

# Interpretasi APM
if prev_year is not None and prev_apm is not None:
    if latest_apm > prev_apm:
        insight_lines.append("- **APM meningkat** → makin banyak anak usia ideal yang bersekolah sesuai jenjangnya.")
    elif latest_apm < prev_apm:
        insight_lines.append("- **APM menurun** → bertambah anak usia ideal yang belum bersekolah di jenjangnya.")
    else:
        insight_lines.append("- **APM stabil** → proporsi usia ideal bersekolah relatif sama.")
else:
    insight_lines.append("- **APM (tren tahunan)**: data pembanding tidak tersedia.")

# Interpretasi Selisih
if gap > 20:
    insight_lines.append(f"- **Selisih APK–APM besar ({gap:.2f} poin)** → banyak siswa tidak pada usia ideal (terlambat/terlalu cepat); perlu perkuat ketepatan usia masuk & pencegahan tinggal kelas.")
else:
    insight_lines.append(f"- **Selisih APK–APM kecil ({gap:.2f} poin)** → mayoritas siswa berada pada jenjang sesuai usia ideal.")


# Convert markdown list to HTML list and wrap in a styled box
html_list_items = ""
for line in insight_lines:
    clean_line = line.lstrip('- ').strip()
    # Convert markdown bold to HTML strong tag
    processed_line = clean_line.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
    html_list_items += f"<li>{processed_line}</li>"

st.markdown(f"""
<div class="insight-summary-box">
    <ul>
        {html_list_items}
    </ul>
</div>
""", unsafe_allow_html=True)

# ====================
# PERBANDINGAN PER KECAMATAN (LEBAR PENUH)
# ====================
st.markdown(f'<div class="section-header"><h3>📊 Perbandingan {label_mapping["apk"]} & {label_mapping["apm"]} per Kecamatan</h3></div>', unsafe_allow_html=True)
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    x=filtered_df['kecamatan'],
    y=filtered_df['apk'],
    name=label_mapping['apk'],
    marker_color="#004c70"
))
fig_bar.add_trace(go.Bar(
    x=filtered_df['kecamatan'],
    y=filtered_df['apm'],
    name=label_mapping['apm'],
    marker_color="#c85a5a"
))
fig_bar.update_layout(barmode='group', xaxis_title="Kecamatan", yaxis_title="Persentase")
st.plotly_chart(fig_bar, use_container_width=True)

# ====================
# RANKING
# ====================
# Create a mapping from a short label to column name for the radio button
ranking_options = { # Use short labels for the filter
    "APM": 'apm',
    "APK": 'apk'
}

# Tampilkan header seksi terlebih dahulu
st.markdown('<div class="section-header"><h3>🏅 Ranking Kecamatan (Top 5 & Bottom 5)</h3></div>', unsafe_allow_html=True)

# Add a radio button to select the indicator
selected_ranking_label = st.radio(
    "Pilih Indikator untuk Ranking", # Label ini sekarang untuk aksesibilitas (tidak terlihat)
    options=list(ranking_options.keys()),
    horizontal=True,
    label_visibility="collapsed" # Sembunyikan label karena header sudah cukup jelas
)

# Get the corresponding column name
selected_ranking_col = ranking_options[selected_ranking_label]

# Sort the dataframe based on the selected indicator
ranked = filtered_df[['kecamatan', selected_ranking_col]].sort_values(by=selected_ranking_col, ascending=False)

col1, col2 = st.columns(2)
with col1:
    st.write("🔝 Top 5")
    st.dataframe(
        ranked.head(5).rename(columns=label_mapping),
        hide_index=True,
        use_container_width=True
    )
with col2:
    st.write("🔻 Bottom 5")
    st.dataframe(
        ranked.tail(5).rename(columns=label_mapping),
        hide_index=True,
        use_container_width=True
    )

# ====================
# KORELASI
# ====================
st.markdown('<div class="section-header"><h3>🔗 Korelasi Antar Indikator</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("""
    Korelasi menunjukkan seberapa erat hubungan antar indikator:
    - **Positif (+)** → jika satu naik, yang lain cenderung ikut naik.
    - **Negatif (-)** → jika satu naik, yang lain cenderung turun.
    - Nilai mendekati **1 atau -1** berarti hubungan **sangat erat**, sedangkan mendekati **0** berarti **hampir tidak ada hubungan**.
    """)

corr = filtered_df[['apk', 'apm', 'persentase_guru_s1', 'persentase_sekolah_akreditasi']].corr()

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
    for j in range(i+1, len(cols)):
        val = corr.iloc[i,j]
        corr_table.append({
            "Indikator X": label_mapping.get(cols[i], cols[i]),
            "Indikator Y": label_mapping.get(cols[j], cols[j]),
            "Nilai Korelasi": f"{val:.2f}",
            "Interpretasi": interpret_correlation(val)
        })

# Siapkan DataFrame dan insight sebelum membuat kolom
corr_df = pd.DataFrame(corr_table)
strongest = corr_df.iloc[corr_df['Nilai Korelasi'].astype(float).abs().idxmax()]

with col2:
    st.write("📋 **Tabel Korelasi dengan Interpretasi**")
    st.dataframe(corr_df, use_container_width=True, hide_index=True)

# Tampilkan insight di bawah kedua kolom
st.markdown(
    f"- Hubungan terkuat terdapat antara **{strongest['Indikator X']}** dan **{strongest['Indikator Y']}** dengan nilai **{strongest['Nilai Korelasi']}** → {strongest['Interpretasi']}."
)

# ====================
# TABEL DETAIL
# ====================
st.markdown("---")
st.markdown('<div class="section-header"><h3>📑 Data Detail per Kecamatan</h3></div>', unsafe_allow_html=True)
st.dataframe(
    filtered_df[['kecamatan', 'apk', 'apm', 'persentase_guru_s1', 'persentase_sekolah_akreditasi']]
        .rename(columns=label_mapping)
        .sort_values(by='Angka Partisipasi Kasar (APK)', ascending=False),
    use_container_width=True
)
