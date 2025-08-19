import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Stunting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load data
@st.cache_data
def load_data():
    """
    Memuat dan membersihkan data stunting dari file CSV.
    Kolom 'Prevalensi Stunting' dibersihkan dari karakter non-numerik
    dan dikonversi menjadi tipe float untuk kalkulasi yang lebih tangguh.
    """
    df = pd.read_csv("data/kesehatan/kesehatan_stunting.csv")
    # Membersihkan kolom 'Prevalensi Stunting' secara lebih tangguh
    # Mengambil angka pertama yang ditemukan (misal: '5.4% %' akan menjadi 5.4)
    df['Prevalensi Stunting Persen'] = pd.to_numeric(df['Prevalensi Stunting'].astype(str).str.extract(r'(\d+\.?\d*)')[0], errors='coerce')
    # Hapus baris yang gagal dikonversi untuk menjaga integritas data
    df.dropna(subset=['Prevalensi Stunting Persen'], inplace=True)
    return df

df = load_data()

# =================== TITLE ===================
st.title("📊 Dashboard Analisis Data Stunting")
st.markdown("Dashboard interaktif untuk analisis data stunting di berbagai kecamatan di Kabupaten Malang.")
st.markdown("---")

# =================== FILTER ===================
st.header("🔍 Filter Data")
st.write("Gunakan filter di bawah ini untuk menampilkan data yang lebih spesifik.")
col1, col2 = st.columns(2)

with col1:
    selected_year = st.multiselect(
        "Pilih Tahun:",
        options=sorted(df['Tahun'].unique()),
        default=sorted(df['Tahun'].unique())
    )

with col2:
    selected_kecamatan = st.multiselect(
        "Pilih Kecamatan:",
        options=sorted(df['Kecamatan'].unique()),
        default=sorted(df['Kecamatan'].unique())[:10]
    )

# Filter dataframe berdasarkan input pengguna dan tangani jika filter kosong
if not selected_year or not selected_kecamatan:
    st.warning("Silakan pilih minimal satu tahun dan satu kecamatan untuk menampilkan data.")
    st.stop() # Menghentikan eksekusi jika filter kosong

filtered_df = df[
    (df['Tahun'].isin(selected_year)) & 
    (df['Kecamatan'].isin(selected_kecamatan))
]

# =================== RINGKASAN UTAMA ===================
st.header("📋 Ringkasan Utama")
st.caption(f"Data berdasarkan pilihan tahun {', '.join(map(str, selected_year))} dan {len(selected_kecamatan)} kecamatan terpilih.")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Kasus Stunting", f"{filtered_df['Stunting'].sum():,}")

with col2:
    st.metric("Total Anak Diukur", f"{filtered_df['Jumlah Yang Diukur'].sum():,}")

with col3:
    st.metric("Rata-rata Prevalensi", f"{filtered_df['Prevalensi Stunting Persen'].mean():.2f}%")

st.markdown("---")

# =================== TREN ===================
st.header("📈 Analisis Tren dan Perbandingan")
col_trend, col_monthly = st.columns(2)

with col_trend:
    # Tren prevalensi stunting per tahun
    yearly_trend = filtered_df.groupby('Tahun')['Prevalensi Stunting Persen'].mean().reset_index()
    fig_trend = px.line(
        yearly_trend,
        x='Tahun',
        y='Prevalensi Stunting Persen',
        title='Tren Rata-rata Prevalensi per Tahun',
        markers=True,
        labels={'Tahun': 'Tahun', 'Prevalensi Stunting Persen': 'Rata-rata Prevalensi (%)'}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_monthly:
    # Perbandingan prevalensi antara Februari dan Agustus
    monthly_comparison = filtered_df.groupby(['Tahun', 'Bulan'])['Prevalensi Stunting Persen'].mean().reset_index()
    fig_monthly = px.bar(
        monthly_comparison,
        x='Tahun',
        y='Prevalensi Stunting Persen',
        color='Bulan',
        barmode='group',
        title='Perbandingan Prevalensi: Februari vs Agustus',
        labels={'Tahun': 'Tahun', 'Prevalensi Stunting Persen': 'Rata-rata Prevalensi (%)'}
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

st.markdown("---")

# =================== TOP 10 KECAMATAN ===================
st.header("🏆 Analisis Wilayah dan Distribusi Data")
col_top, col_dist = st.columns(2)

with col_top:
    # Menyederhanakan kode untuk top 10 dan mengurutkan agar bar terpanjang di atas
    top_kecamatan = filtered_df.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().nlargest(10).sort_values(ascending=True)
    fig_top = px.bar(
        top_kecamatan,
        x=top_kecamatan.values,
        y=top_kecamatan.index,
        orientation='h',
        title="Top 10 Kecamatan dengan Prevalensi Tertinggi",
        color=top_kecamatan.values,
        color_continuous_scale='Reds',
        labels={'y': 'Kecamatan', 'x': 'Rata-rata Prevalensi (%)'}
    )
    st.plotly_chart(fig_top, use_container_width=True)

with col_dist:
    # Distribusi prevalensi stunting
    fig_hist = px.histogram(
        filtered_df,
        x='Prevalensi Stunting Persen',
        nbins=30,
        title='Distribusi Frekuensi Prevalensi Stunting',
        labels={'Prevalensi Stunting Persen': 'Prevalensi Stunting (%)'}
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# =================== REKOMENDASI ===================
st.header("🎯 Rekomendasi dan Insights (Berdasarkan Filter)")

# Kalkulasi insight dinamis berdasarkan data yang difilter
kecamatan_prevalence = filtered_df.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean()
avg_prev = kecamatan_prevalence.mean()
worst_kec = kecamatan_prevalence.idxmax()
best_kec = kecamatan_prevalence.idxmin()

st.info(f"""
Berdasarkan data yang Anda filter:
- Rata-rata prevalensi stunting adalah **{avg_prev:.2f}%**.
- Kecamatan dengan prevalensi **tertinggi** adalah **{worst_kec}** ({kecamatan_prevalence.max():.2f}%).
- Kecamatan dengan prevalensi **terendah** adalah **{best_kec}** ({kecamatan_prevalence.min():.2f}%).
""")

st.subheader("📋 Rencana Aksi yang Disarankan")
st.write(f"""
1. **Fokus Intervensi**: Prioritaskan sumber daya dan program intervensi di **Kecamatan {worst_kec}** dan wilayah lain dengan prevalensi di atas rata-rata.
2. **Studi Kasus**: Pelajari praktik baik (best practices) dari **Kecamatan {best_kec}** untuk diterapkan di wilayah lain.
3. **Peningkatan Edukasi**: Tingkatkan edukasi gizi dan pemantauan pertumbuhan anak secara intensif di kecamatan-kecamatan prioritas.
""")

# =================== PETA GEOGRAFIS ===================
st.markdown("---")
st.header("🗺️ Peta Sebaran Prevalensi Stunting")
st.caption("Peta ini menunjukkan rata-rata prevalensi stunting di kecamatan yang Anda pilih. Warna yang lebih gelap menandakan prevalensi yang lebih tinggi.")

# Membuat path yang robust ke file GeoJSON, relatif terhadap lokasi script ini.
# Ini memastikan file akan ditemukan tidak peduli dari direktori mana script dijalankan.
SCRIPT_DIR = Path(__file__).parent
# Menggunakan path absolut secara langsung untuk debugging
GEOJSON_PATH = r"c:\Users\rosar\Documents\PKL\Dashboard_KominfoKabMalang\data\geo\35.07_kecamatan.geojson"

# Load geojson peta kecamatan
try:
    # Menggunakan path absolut yang sudah kita buat, dengan encoding utf-8
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    # Hitung rata-rata prevalensi per kecamatan untuk data yang difilter
    geo_data = filtered_df.groupby("Kecamatan")["Prevalensi Stunting Persen"].mean().reset_index()

    # 2. Menyamakan format nama kecamatan (Title Case) agar cocok dengan GeoJSON
    #    Contoh: 'DONOMULYO' di CSV menjadi 'Donomulyo' agar cocok dengan 'nm_kecamatan' di GeoJSON
    geo_data['Kecamatan'] = geo_data['Kecamatan'].str.title()

    # Bikin choropleth map yang interaktif
    fig_map = px.choropleth_mapbox(
        geo_data,
        geojson=geojson,
        locations="Kecamatan",
        featureidkey="properties.nm_kecamatan",  # 3. Menyesuaikan dengan key di file 35.07_kecamatan.geojson
        color="Prevalensi Stunting Persen",
        color_continuous_scale="Reds",
        mapbox_style="carto-positron", # Style peta dasar yang bersih
        zoom=8.5, # Level zoom awal
        center={"lat": -8.1689, "lon": 112.6197}, # Titik tengah peta (Kab. Malang)
        opacity=0.6,
        labels={'Prevalensi Stunting Persen': 'Prevalensi (%)'},
        hover_name="Kecamatan" # Menampilkan nama kecamatan saat di-hover
    )
    fig_map.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox_accesstoken=st.secrets.get("MAPBOX_TOKEN") # Opsional: untuk performa lebih baik
    )
    st.plotly_chart(fig_map, use_container_width=True)

except FileNotFoundError:
    st.error(f"File GeoJSON tidak ditemukan. Script mencari file di path: '{GEOJSON_PATH}'. Pastikan file '35.07_kecamatan.geojson' ada di dalam folder 'data/geo' di dalam direktori proyek Anda.")
except Exception as e:
    st.error(f"Terjadi kesalahan saat membuat peta: {e}")

# =================== FOOTER ===================
st.markdown("---")
st.markdown("**📊 Dashboard Analisis Stunting** | Sederhana, ringkas, dan mudah dipahami.")
