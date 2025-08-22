import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import json

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

        # Konversi kolom yang relevan ke tipe data numerik
        numeric_cols = [
            'apk', 'apm', 'persentase_guru_s1', 'persentase_sekolah_akreditasi',
            'jumlah_siswa', 'jumlah_sekolah', 'jumlah_penduduk_usia_sekolah'
        ]
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Hapus baris dengan data kosong pada kolom-kolom inti
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

# ====================
# SIDEBAR FILTERS
# ====================
st.sidebar.header("📌 Filter Data")
years = sorted(df['tahun'].unique())
jenjangs = sorted(df['jenjang'].unique())
selected_year = st.sidebar.selectbox("Pilih Tahun", years)
selected_jenjang = st.sidebar.selectbox("Pilih Jenjang", jenjangs)
filtered_df = df[(df['tahun'] == selected_year) & (df['jenjang'] == selected_jenjang)]
if filtered_df.empty:
    st.warning(f"Tidak ada data untuk Tahun {selected_year}, Jenjang {selected_jenjang}.")
    st.stop()

# Buat kolom rasio baru jika data tersedia
filtered_df = filtered_df.copy() # Menghindari SettingWithCopyWarning
if 'jumlah_sekolah' in filtered_df.columns and 'jumlah_penduduk_usia_sekolah' in filtered_df.columns:
    # Menghindari pembagian dengan nol
    non_zero_mask = filtered_df['jumlah_penduduk_usia_sekolah'] != 0
    filtered_df.loc[non_zero_mask, 'rasio_sekolah_penduduk'] = \
        (filtered_df.loc[non_zero_mask, 'jumlah_sekolah'] / filtered_df.loc[non_zero_mask, 'jumlah_penduduk_usia_sekolah']) * 1000


# ====================
# SCORECARDS
# ====================
st.markdown("## 🎓 Dashboard Pendidikan Kabupaten Malang")
st.markdown(f"### Tahun {selected_year} - Jenjang {selected_jenjang}")
avg_apk = filtered_df['apk'].mean()
avg_apm = filtered_df['apm'].mean()
avg_guru_s1 = filtered_df['persentase_guru_s1'].mean()
avg_akreditasi = filtered_df['persentase_sekolah_akreditasi'].mean()

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("📈 Rata-rata APK", f"{avg_apk:.2f}%")
with col2: st.metric("📊 Rata-rata APM", f"{avg_apm:.2f}%")
with col3: st.metric("👩‍🏫 Guru S1", f"{avg_guru_s1:.2f}%")
with col4: st.metric("🏫 Akreditasi", f"{avg_akreditasi:.2f}%")

# ====================
# PETA INTERAKTIF
# ====================
st.markdown("---")
st.subheader("🗺️ Peta Interaktif Kabupaten Malang")

all_indicator_options = {
    "Jumlah Sekolah": "jumlah_sekolah",
    "Jumlah Penduduk Usia Sekolah": "jumlah_penduduk_usia_sekolah",
    "Rasio Sekolah per 1000 Penduduk": "rasio_sekolah_penduduk",
    "APK": "apk",
    "APM": "apm",
    "% Guru S1": "persentase_guru_s1",
    "% Sekolah Terakreditasi": "persentase_sekolah_akreditasi",
    "Jumlah Siswa": "jumlah_siswa"
}

available_indicators = {label: col for label, col in all_indicator_options.items() if col in filtered_df.columns}

if not available_indicators:
    st.warning("Tidak ada data yang dapat ditampilkan di peta untuk filter yang dipilih.")
    st.stop()

selected_indicator_label = st.selectbox("Pilih Indikator Peta", list(available_indicators.keys()))
selected_indicator = available_indicators[selected_indicator_label]

fig_map = px.choropleth_mapbox(
    filtered_df,
    geojson=geojson_kec,
    locations="kecamatan",
    featureidkey="properties.nm_kecamatan",
    color=selected_indicator,
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=8,
    center={"lat": -8.1, "lon": 112.6},
    opacity=0.7,
    labels={selected_indicator: selected_indicator_label}
)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)


# ====================
# VISUALISASI DASAR
# ====================
st.markdown("---")
st.markdown("### 📊 Visualisasi Data")
# Line Chart Perkembangan APK/APM
st.subheader("Perkembangan APK dan APM dari Tahun ke Tahun")
time_df = df[df['jenjang'] == selected_jenjang].groupby('tahun')[['apk', 'apm']].mean().reset_index()
fig_line = px.line(time_df, x='tahun', y=['apk', 'apm'], markers=True)
fig_line.update_yaxes(title="Persentase")
st.plotly_chart(fig_line, use_container_width=True)

# Bar Chart APK & APM per Kecamatan
st.subheader("Perbandingan APK & APM per Kecamatan")
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=filtered_df['kecamatan'], y=filtered_df['apk'], name='APK'))
fig_bar.add_trace(go.Bar(x=filtered_df['kecamatan'], y=filtered_df['apm'], name='APM'))
fig_bar.update_layout(barmode='group', xaxis_title="Kecamatan", yaxis_title="Persentase")
st.plotly_chart(fig_bar, use_container_width=True)


# ====================
# IDE TAMBAHAN
# ====================
# Ranking Top-Bottom 5
st.subheader("🏅 Ranking Kecamatan (Top 5 & Bottom 5 APM)")
ranked = filtered_df[['kecamatan','apm']].sort_values(by='apm', ascending=False)
col1, col2 = st.columns(2)
with col1:
    st.write("🔝 Top 5")
    st.dataframe(ranked.head(5))
with col2:
    st.write("🔻 Bottom 5")
    st.dataframe(ranked.tail(5))
    
# Heatmap Korelasi
st.subheader("🔗 Korelasi Antar Indikator")
corr = filtered_df[['apk', 'apm', 'persentase_guru_s1', 'persentase_sekolah_akreditasi']].corr()
fig_corr, ax = plt.subplots(figsize=(6,4))
sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
st.pyplot(fig_corr)

# Treemap Komposisi
st.subheader("🌳 Treemap Kontribusi APK per Kecamatan")
fig_tree = px.treemap(filtered_df, path=['kecamatan'], values='apk', color='apm',
                      color_continuous_scale='Viridis',
                      title="Proporsi APK & APM per Kecamatan")
st.plotly_chart(fig_tree, use_container_width=True)

# Boxplot Distribusi
st.subheader("📦 Distribusi APK dan APM")
fig_box = px.box(filtered_df.melt(id_vars="kecamatan", value_vars=["apk","apm"]),
                 x="variable", y="value", points="all", color="variable")
st.plotly_chart(fig_box, use_container_width=True)



# Gap Analysis
st.subheader("🎯 Gap Analysis APM terhadap Target 100%")
fig_gap = go.Figure()
fig_gap.add_trace(go.Bar(x=filtered_df['kecamatan'], y=filtered_df['apm'], name="Realisasi APM"))
fig_gap.add_trace(go.Scatter(x=filtered_df['kecamatan'], y=[100]*len(filtered_df),
                             mode="lines", name="Target 100%", line=dict(dash="dash", color="red")))
fig_gap.update_layout(yaxis_title="APM (%)")
st.plotly_chart(fig_gap, use_container_width=True)

# Scatter Plot
st.subheader("📈 Hubungan % Guru S1 vs APM")
fig_scatter = px.scatter(filtered_df, x="persentase_guru_s1", y="apm",
                         size="apk", color="kecamatan", hover_name="kecamatan",
                         labels={"persentase_guru_s1":"% Guru S1","apm":"APM"})
st.plotly_chart(fig_scatter, use_container_width=True)

# Time-Series per Kecamatan
st.subheader("⏳ Tren APK/APM per Kecamatan")
selected_kec = st.selectbox("Pilih Kecamatan", df['kecamatan'].unique())
kec_df = df[(df['kecamatan'] == selected_kec) & (df['jenjang'] == selected_jenjang)]
fig_kec = px.line(kec_df, x="tahun", y=["apk","apm"], markers=True,
                  title=f"Tren APK & APM - {selected_kec}")
st.plotly_chart(fig_kec, use_container_width=True)

# # Insight Otomatis
# st.subheader("💡 Insight Otomatis")
# max_apk = filtered_df.loc[filtered_df['apk'].idxmax()]
# min_apk = filtered_df.loc[filtered_df['apk'].idxmin()]
# st.markdown(
#     f"Pada tahun **{selected_year}** jenjang **{selected_jenjang}**, "
#     f"Kecamatan **{max_apk['kecamatan']}** memiliki **APK tertinggi** ({max_apk['apk']:.2f}%), "
#     f"sedangkan Kecamatan **{min_apk['kecamatan']}** memiliki **APK terendah** ({min_apk['apk']:.2f}%)."
# )

# TABEL DETAIL DATA
st.markdown("---")
st.markdown("### 📑 Data Detail per Kecamatan")
st.dataframe(
    filtered_df[['kecamatan', 'apk', 'apm', 'persentase_guru_s1', 'persentase_sekolah_akreditasi']]
        .sort_values(by='apk', ascending=False),
    use_container_width=True
)
