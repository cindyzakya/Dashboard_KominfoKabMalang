import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Analisis Stunting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/kesehatan/kesehatan_stunting.csv")
    # Membersihkan kolom Prevalensi Stunting
    df['Prevalensi Stunting Persen'] = df['Prevalensi Stunting'].str.replace('%', '').str.replace(' ', '').str.replace('%%', '').astype(float)
    return df

df = load_data()

geojson_kec_path = "data/geo/35.07_kecamatan.geojson"
with open(geojson_kec_path, 'r', encoding='utf-8') as f:
    geojson_kec = json.load(f)

# =================== UTILITY FUNCTIONS ===================
def get_latest_period(df_to_check):
    """Mencari tahun dan bulan terakhir dari dataframe yang diberikan."""
    if df_to_check.empty:
        return None, None

    month_order = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                   'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    latest_year = df_to_check['Tahun'].max()
    latest_year_data = df_to_check[df_to_check['Tahun'] == latest_year]
    available_months = latest_year_data['Bulan'].unique()

    latest_month = None
    for month in reversed(month_order):
        if month in available_months:
            latest_month = month
            break
    
    return latest_year, latest_month

def get_month_mapping():
    """Return mapping bulan ke angka untuk sorting"""
    return {
        'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4, 
        'Mei': 5, 'Juni': 6, 'Juli': 7, 'Agustus': 8, 
        'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
    }

def create_sorted_period_data(df):
    """Buat data periode yang sudah diurutkan dengan benar"""
    month_mapping = get_month_mapping()
    df['Month_Num'] = df['Bulan'].map(month_mapping)
    df['Periode'] = df['Tahun'].astype(str) + '-' + df['Bulan']
    
    return df.sort_values(['Tahun', 'Month_Num']).reset_index(drop=True)

def analyze_prevalence_category(prevalensi):
    """Klasifikasi prevalensi stunting"""
    if prevalensi < 5:
        return "Rendah (< 5%)"
    elif prevalensi < 10:
        return "Sedang (5-10%)"
    elif prevalensi < 20:
        return "Tinggi (10-20%)"
    else:
        return "Sangat Tinggi (> 20%)"

def get_latest_facilities_data(data):
    """Ambil data fasilitas dari periode terakhir"""
    if data.empty:
        return pd.DataFrame()

    month_order = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                   'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    latest_year = data['Tahun'].max()
    latest_year_data = data[data['Tahun'] == latest_year]
    
    latest_month = None
    for month in reversed(month_order):
        if month in latest_year_data['Bulan'].unique():
            latest_month = month
            break
    
    if not latest_month:
        return pd.DataFrame()

    latest_period_df = latest_year_data[latest_year_data['Bulan'] == latest_month]

    # Kolom yang dihitung per kecamatan (ambil nilai unik)
    per_kecamatan_cols = ['Jumlah Rumah Sakit', 'Jumlah Puskesmas', 'Jumlah Puskesmas Pembantu']
    # Kolom yang dihitung per unit kerja (dijumlahkan)
    per_unit_kerja_cols = ['Jumlah Klinik', 'Pos Kesehatan', 'Jumlah Pondak Bersalin Desa (Polindes)']

    # Filter kolom yang benar-benar ada di dataframe
    per_kecamatan_cols = [col for col in per_kecamatan_cols if col in latest_period_df.columns]
    per_unit_kerja_cols = [col for col in per_unit_kerja_cols if col in latest_period_df.columns]

    # Proses faskes per kecamatan
    faskes_kec_df = latest_period_df[['Kecamatan'] + per_kecamatan_cols].drop_duplicates(subset=['Kecamatan']).reset_index(drop=True)

    # Proses faskes per unit kerja
    faskes_unit_df = latest_period_df.groupby('Kecamatan')[per_unit_kerja_cols].sum().reset_index()

    # Gabungkan keduanya
    final_faskes_df = pd.merge(faskes_kec_df, faskes_unit_df, on='Kecamatan', how='outer').fillna(0)
    return final_faskes_df

def create_trend_analysis(trend_data, period_type="tahun"):
    """Generate analisis tren berdasarkan data"""
    if len(trend_data) <= 1:
        return "Data tidak cukup untuk analisis tren."
    
    if period_type == "tahun":
        trend_change = trend_data.iloc[-1]['Prevalensi_Mean'] - trend_data.iloc[0]['Prevalensi_Mean']
        best_period = trend_data.loc[trend_data['Prevalensi_Mean'].idxmin(), 'Tahun']
        worst_period = trend_data.loc[trend_data['Prevalensi_Mean'].idxmax(), 'Tahun']
        best_prev = trend_data['Prevalensi_Mean'].min()
        worst_prev = trend_data['Prevalensi_Mean'].max()
        
        if abs(trend_change) < 1:
            return f"📊 **Perkembangan**: Angka stunting relatif stabil dari tahun {trend_data.iloc[0]['Tahun']} ke {trend_data.iloc[-1]['Tahun']} dengan perubahan {abs(trend_change):.1f}%. Angka terendah tercatat pada tahun {best_period} ({best_prev:.1f}%) dan tertinggi pada tahun {worst_period} ({worst_prev:.1f}%)."
        elif trend_change < 0:
            return f"📊 **Perkembangan**: Terjadi penurunan angka stunting sebesar {abs(trend_change):.1f}% dari tahun {trend_data.iloc[0]['Tahun']} ke {trend_data.iloc[-1]['Tahun']}. Angka terendah tercatat pada tahun {best_period} ({best_prev:.1f}%)."
        else:
            return f"📊 **Perkembangan**: Terjadi peningkatan angka stunting sebesar {trend_change:.1f}% dari tahun {trend_data.iloc[0]['Tahun']} ke {trend_data.iloc[-1]['Tahun']}. Angka tertinggi tercatat pada tahun {worst_period} ({worst_prev:.1f}%)."
    
    else:  # periode bulanan
        highest_period = trend_data.loc[trend_data['Prevalensi_Mean'].idxmax(), 'Periode']
        lowest_period = trend_data.loc[trend_data['Prevalensi_Mean'].idxmin(), 'Periode']
        highest_prev = trend_data['Prevalensi_Mean'].max()
        lowest_prev = trend_data['Prevalensi_Mean'].min()
        range_prev = highest_prev - lowest_prev
        
        if range_prev > 5:
            return f"**Variasi Bulanan**: Terdapat variasi yang cukup besar antar periode dengan selisih {range_prev:.1f}%. Angka tertinggi terjadi pada periode **{highest_period}** ({highest_prev:.1f}%) dan terendah pada **{lowest_period}** ({lowest_prev:.1f}%)."
        elif range_prev > 2:
            return f"**Variasi Bulanan**: Terjadi fluktuasi sedang antar periode dengan selisih {range_prev:.1f}%. Periode tertinggi: **{highest_period}** ({highest_prev:.1f}%), terendah: **{lowest_period}** ({lowest_prev:.1f}%)."
        else:
            return f"**Variasi Bulanan**: Angka stunting menunjukkan konsistensi yang baik antar periode dengan selisih hanya {range_prev:.1f}%. Periode terendah: **{lowest_period}** ({lowest_prev:.1f}%)."

def create_correlation_analysis(correlation, avg_faskes, high_faskes_low_prev, low_faskes_high_prev):
    """Generate analisis korelasi"""
    if correlation < -0.4:
        return f"**Hubungan Negatif Kuat**: Data menunjukkan korelasi negatif yang kuat ({correlation:.2f}) antara jumlah fasilitas kesehatan dan tingkat stunting. Rata-rata terdapat {avg_faskes:.1f} fasilitas per kecamatan. {high_faskes_low_prev} kecamatan menunjukkan pola fasilitas banyak dengan stunting rendah."
    elif correlation < -0.2:
        return f"**Hubungan Negatif Sedang**: Terdapat korelasi negatif sedang ({correlation:.2f}) yang menunjukkan adanya hubungan antara fasilitas kesehatan dan tingkat stunting. {high_faskes_low_prev} kecamatan menunjukkan kondisi optimal dengan fasilitas memadai dan stunting rendah."
    elif correlation > 0.2:
        return f"**Hubungan Positif**: Data menunjukkan korelasi positif ({correlation:.2f}), dimana wilayah dengan fasilitas kesehatan lebih banyak cenderung memiliki tingkat stunting yang lebih tinggi. {low_faskes_high_prev} kecamatan memiliki fasilitas terbatas namun stunting tinggi."
    else:
        return f"**Hubungan Lemah**: Korelasi yang lemah ({correlation:.2f}) menunjukkan bahwa faktor selain jumlah fasilitas kesehatan mungkin lebih berpengaruh terhadap tingkat stunting. {low_faskes_high_prev} kecamatan memiliki kondisi yang memerlukan perhatian khusus."

def create_map_analysis(selected_indicator_label, max_kecamatan, max_value, min_kecamatan, min_value, mean_value, above_avg, below_avg, difference_ratio):
    """Generate analisis peta sebaran"""
    if "Persentase" in selected_indicator_label or "Stunting" in selected_indicator_label:
        return f"**Sebaran {selected_indicator_label}**: Nilai tertinggi terdapat di **{max_kecamatan}** ({max_value:.1f}%) dan terendah di **{min_kecamatan}** ({min_value:.1f}%). Rata-rata wilayah adalah {mean_value:.1f}% dengan {above_avg} kecamatan berada di atas rata-rata dan {below_avg} kecamatan di bawah rata-rata. Rasio perbedaan antara tertinggi dan terendah adalah {difference_ratio:.1f} kali."
    else:
        return f"**Sebaran {selected_indicator_label}**: Jumlah tertinggi terdapat di **{max_kecamatan}** ({max_value:.0f} unit) dan terendah di **{min_kecamatan}** ({min_value:.0f} unit). Rata-rata adalah {mean_value:.1f} unit per kecamatan dengan {above_avg} kecamatan berada di atas rata-rata dan {below_avg} kecamatan di bawah rata-rata."

# =================== SIDEBAR FILTERS ===================
with st.sidebar:
    st.header("🔍 Filter Data")
    
    # Initialize filter states if not exists
    if "reset_filters" not in st.session_state:
        st.session_state.reset_filters = False
    if "reset_year_filter" not in st.session_state:
        st.session_state.reset_year_filter = False
    if "reset_kecamatan_filter" not in st.session_state:
        st.session_state.reset_kecamatan_filter = False
    
    # Filter Tahun
    st.subheader("Tahun")
    
    # Set default values based on reset state
    default_checkbox_tahun = True if st.session_state.reset_filters or st.session_state.reset_year_filter else True
    default_multiselect_tahun = sorted(df['Tahun'].unique())
    
    semua_tahun = st.checkbox("Pilih Semua Tahun", value=default_checkbox_tahun, key="checkbox_tahun")
    
    if semua_tahun:
        selected_year = sorted(df['Tahun'].unique())
        st.info(f"Terpilih: {len(selected_year)} tahun")
        # Disable multiselect when all years are selected
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
        # Jika tidak ada tahun yang dipilih, default ke semua tahun
        if not selected_year:
            selected_year = sorted(df['Tahun'].unique())
            st.warning("Tidak ada tahun dipilih, menampilkan semua tahun")
    
    # Reset flag after rerun
    if st.session_state.reset_year_filter:
        st.session_state.reset_year_filter = False
    
    # Filter Kecamatan
    st.subheader("Kecamatan")
    
    # Set default values based on reset state
    default_checkbox_kecamatan = True if st.session_state.reset_filters or st.session_state.reset_kecamatan_filter else True
    default_multiselect_kecamatan = sorted(df['Kecamatan'].unique())
    
    semua_kecamatan = st.checkbox("Pilih Semua Kecamatan", value=default_checkbox_kecamatan, key="checkbox_kecamatan")
    
    if semua_kecamatan:
        selected_kecamatan = sorted(df['Kecamatan'].unique())
        st.info(f"Terpilih: {len(selected_kecamatan)} kecamatan")
        # Disable multiselect when all kecamatan are selected
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
            default=default_multiselect_kecamatan if st.session_state.reset_filters or st.session_state.reset_kecamatan_filter else sorted(df['Kecamatan'].unique())[:10],
            key="multiselect_kecamatan"
        )
        # Jika tidak ada kecamatan yang dipilih, default ke semua kecamatan
        if not selected_kecamatan:
            selected_kecamatan = sorted(df['Kecamatan'].unique())
            st.warning("Tidak ada kecamatan dipilih, menampilkan semua kecamatan")
    
    # Reset flag after rerun
    if st.session_state.reset_kecamatan_filter:
        st.session_state.reset_kecamatan_filter = False
    
    # Reset flag after rerun
    if st.session_state.reset_filters:
        st.session_state.reset_filters = False

# Filter data berdasarkan seleksi
filtered_df = df[
    (df['Tahun'].isin(selected_year)) &
    (df['Kecamatan'].isin(selected_kecamatan))
]

# Title dan Header
st.title("📊 Dashboard Analisis Data Stunting")
st.markdown("Dashboard komprehensif untuk analisis data stunting di berbagai kecamatan")

# Cek apakah ada data setelah filtering
if filtered_df.empty:
    st.error("Tidak ada data yang sesuai dengan filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

# Info filter aktif
st.markdown("---")

# =================== METRICS UTAMA ===================
st.header("📋 Ringkasan Utama")

latest_year, latest_month = get_latest_period(filtered_df)

# Data stunting dari semua periode yang difilter
total_stunting = filtered_df['Stunting'].sum()
total_diukur = filtered_df['Jumlah Yang Diukur'].sum()
avg_prevalensi = filtered_df['Prevalensi Stunting Persen'].mean()

# Data fasilitas dari periode terakhir saja - AMBIL KECAMATAN UNIK SAJA
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
    st.metric("Total Kasus Stunting", f"{total_stunting:,}")

with col2:
    st.metric("Total Anak Diukur", f"{total_diukur:,}")

with col3:
    st.metric("Rata-rata Prevalensi", f"{avg_prevalensi:.2f}%")

with col4:
    st.metric("Total Puskesmas", f"{total_puskesmas:,}")
    if latest_month:
        st.caption(f"Data per {latest_month} {latest_year}")

with col5:
    st.metric("Total Rumah Sakit", f"{total_rs:,}")
    if latest_month:
        st.caption(f"Data per {latest_month} {latest_year}")

# Analisis menggunakan fungsi utility

st.markdown("---")

# Siapkan data fasilitas kesehatan untuk peta dan analisis korelasi
faskes_df = get_latest_facilities_data(filtered_df)

st.header("🗺️ Peta Sebaran")

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

selected_indicator_label = st.selectbox("Pilih indikator untuk ditampilkan:", list(available_indicators.keys()))
selected_indicator = available_indicators[selected_indicator_label]

# Data untuk peta
if 'latest_year' in locals() and 'latest_month' in locals() and not faskes_df.empty:
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

if not map_data_source.empty and selected_indicator in map_data_source.columns:
    map_display_df = map_data_source[['Kecamatan', selected_indicator]].dropna()

    fig_map = px.choropleth_mapbox(
        map_display_df,
        geojson=geojson_kec,
        locations="Kecamatan",
        featureidkey="properties.nm_kecamatan",
        color=selected_indicator,
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        zoom=8,
        center={"lat": -8.1, "lon": 112.6},
        opacity=0.7,
        labels={selected_indicator: selected_indicator_label},
        hover_name="Kecamatan",
    )

    # Tentukan format hovertemplate untuk menampilkan nilai dengan benar
    if "Prevalensi Stunting (%)" in selected_indicator_label:
        template_value = '%{z:.2f}%'
    else:
        template_value = '%{z:,.0f}' # Gunakan koma untuk ribuan pada data non-persen

    fig_map.update_traces(hovertemplate=f'<b>%{{location}}</b><br>{selected_indicator_label}: {template_value}<extra></extra>')

    fig_map.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        title=f"Sebaran {selected_indicator_label} per Kecamatan (Data: {latest_month} {latest_year})"
    )
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Analisis menggunakan fungsi utility
    max_value = map_display_df[selected_indicator].max()
    min_value = map_display_df[selected_indicator].min()
    mean_value = map_display_df[selected_indicator].mean()
    
    max_kecamatan = map_display_df[map_display_df[selected_indicator] == max_value]['Kecamatan'].iloc[0]
    min_kecamatan = map_display_df[map_display_df[selected_indicator] == min_value]['Kecamatan'].iloc[0]
    
    above_avg = len(map_display_df[map_display_df[selected_indicator] > mean_value])
    below_avg = len(map_display_df[map_display_df[selected_indicator] < mean_value])
    
    difference_ratio = max_value / min_value if min_value > 0 else float('inf')
    
    st.info(create_map_analysis(selected_indicator_label, max_kecamatan, max_value, min_kecamatan, min_value, mean_value, above_avg, below_avg, difference_ratio))
        
else:
    st.warning(f"Data untuk '{selected_indicator_label}' tidak tersedia dengan filter yang dipilih saat ini.")

st.markdown("---")

# =================== ANALISIS TREN YANG LEBIH EFEKTIF ===================
st.header("📈 Tren Stunting dari Waktu ke Waktu")

# Buat tabs untuk organisasi yang lebih baik
tab1, tab2 = st.tabs(["Tren Tahunan", "Tren per Kecamatan"])

with tab1:
    # Filter jenis tren saja (menggunakan data dari sidebar filter)
    trend_type_general = st.selectbox(
        "Pilih Jenis Tren:",
        options=["Per Tahun", "Per Periode"],
        key="general_trend_type"
    )

    
    if trend_type_general == "Per Tahun":
        # Tren Tahunan (menggunakan filtered_df dari sidebar)
        yearly_trend = filtered_df.groupby('Tahun').agg({
            'Prevalensi Stunting Persen': ['mean', 'std'],
            'Stunting': 'sum',
            'Jumlah Yang Diukur': 'sum'
        }).reset_index()
        
        yearly_trend.columns = ['Tahun', 'Prevalensi_Mean', 'Prevalensi_Std', 'Total_Stunting', 'Total_Diukur']
        yearly_trend['Prevalensi_Std'] = yearly_trend['Prevalensi_Std'].fillna(0)
        
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=yearly_trend['Tahun'],
            y=yearly_trend['Prevalensi_Mean'],
            mode='lines+markers',
            name='Prevalensi',
            line=dict(width=4, color='#1f77b4'),
            marker=dict(size=12),
            hovertemplate='<b>Prevalensi</b><br>Tahun: %{x}<br>Prevalensi: %{y:.2f}%<br>Total Kasus: %{customdata[0]:,}<br>Total Diukur: %{customdata[1]:,}<extra></extra>',
            customdata=yearly_trend[['Total_Stunting', 'Total_Diukur']].values
        ))
        
        fig_trend.update_layout(
            title='Tren Stunting per Tahun',
            xaxis_title="Tahun",
            yaxis_title="Persentase Stunting (%)",
            height=500,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Analisis tren tahunan
        if len(yearly_trend) > 1:
            trend_change = yearly_trend.iloc[-1]['Prevalensi_Mean'] - yearly_trend.iloc[0]['Prevalensi_Mean']
            best_year = yearly_trend.loc[yearly_trend['Prevalensi_Mean'].idxmin(), 'Tahun']
            worst_year = yearly_trend.loc[yearly_trend['Prevalensi_Mean'].idxmax(), 'Tahun']
            best_prev = yearly_trend['Prevalensi_Mean'].min()
            worst_prev = yearly_trend['Prevalensi_Mean'].max()
            
            if abs(trend_change) < 1:
                st.info(f"**Perkembangan**: Angka stunting relatif stabil dari tahun {yearly_trend.iloc[0]['Tahun']} ke {yearly_trend.iloc[-1]['Tahun']} dengan perubahan {abs(trend_change):.1f}%. Angka terendah tercatat pada tahun {best_year} ({best_prev:.1f}%) dan tertinggi pada tahun {worst_year} ({worst_prev:.1f}%).")
            elif trend_change < 0:
                st.success(f"**Perkembangan Positif**: Terjadi penurunan angka stunting sebesar {abs(trend_change):.1f}% dari tahun {yearly_trend.iloc[0]['Tahun']} ke {yearly_trend.iloc[-1]['Tahun']}. Angka terendah tercatat pada tahun {best_year} ({best_prev:.1f}%).")
            else:
                st.warning(f"**Perlu Perhatian**: Terjadi peningkatan angka stunting sebesar {trend_change:.1f}% dari tahun {yearly_trend.iloc[0]['Tahun']} ke {yearly_trend.iloc[-1]['Tahun']}. Angka tertinggi tercatat pada tahun {worst_year} ({worst_prev:.1f}%).")
        else:
            st.info("Data hanya tersedia untuk satu tahun.")
    
    else:  # Per Periode
        # Sorting periode yang benar
        filtered_df_sorted = create_sorted_period_data(filtered_df.copy())
        
        period_trend = filtered_df_sorted.groupby(['Tahun', 'Bulan', 'Periode', 'Month_Num']).agg({
            'Prevalensi Stunting Persen': ['mean', 'std'],
            'Stunting': 'sum',
            'Jumlah Yang Diukur': 'sum'
        }).reset_index()
        
        period_trend.columns = ['Tahun', 'Bulan', 'Periode', 'Month_Num', 'Prevalensi_Mean', 'Prevalensi_Std', 'Total_Stunting', 'Total_Diukur']
        period_trend['Prevalensi_Std'] = period_trend['Prevalensi_Std'].fillna(0)
        period_trend = period_trend.sort_values(['Tahun', 'Month_Num']).reset_index(drop=True)
        
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=period_trend['Periode'],
            y=period_trend['Prevalensi_Mean'],
            mode='lines+markers',
            name='Prevalensi',
            line=dict(width=4, color='#2E8B57'),
            marker=dict(size=10),
            hovertemplate='<b>Prevalensi</b><br>Periode: %{x}<br>Prevalensi: %{y:.2f}%<br>Total Kasus: %{customdata[0]:,}<br>Total Diukur: %{customdata[1]:,}<extra></extra>',
            customdata=period_trend[['Total_Stunting', 'Total_Diukur']].values
        ))
        
        fig_trend.update_layout(
            title='Tren Stunting per Periode',
            xaxis_title="Periode (Tahun-Bulan)",
            yaxis_title="Persentase Stunting (%)",
            height=500,
            hovermode='x unified',
            xaxis=dict(
                categoryorder='array',
                categoryarray=period_trend['Periode'].tolist()
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Analisis tren periodik
        if len(period_trend) > 1:
            highest_period = period_trend.loc[period_trend['Prevalensi_Mean'].idxmax(), 'Periode']
            lowest_period = period_trend.loc[period_trend['Prevalensi_Mean'].idxmin(), 'Periode']
            highest_prev = period_trend['Prevalensi_Mean'].max()
            lowest_prev = period_trend['Prevalensi_Mean'].min()
            range_prev = highest_prev - lowest_prev
            
            if range_prev > 5:
                st.warning(f"**Variasi Tinggi**: Terdapat variasi yang cukup besar antar periode dengan selisih {range_prev:.1f}%. Angka tertinggi terjadi pada periode **{highest_period}** ({highest_prev:.1f}%) dan terendah pada **{lowest_period}** ({lowest_prev:.1f}%).")
            elif range_prev > 2:
                st.info(f"**Variasi Sedang**: Terjadi fluktuasi sedang antar periode dengan selisih {range_prev:.1f}%. Periode tertinggi: **{highest_period}** ({highest_prev:.1f}%), terendah: **{lowest_period}** ({lowest_prev:.1f}%).")
            else:
                st.success(f"**Konsisten**: Angka stunting menunjukkan konsistensi yang baik antar periode dengan selisih hanya {range_prev:.1f}%. Periode terendah: **{lowest_period}** ({lowest_prev:.1f}%).")
        else:
            st.info("Data hanya tersedia untuk satu periode.")

with tab2:
    
    # Filter lokal untuk tab kecamatan (hanya periode dan 1 kecamatan)
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # Filter jenis tren (hanya periode - per tahun/per bulan)
        trend_type_kec = st.selectbox(
            "Jenis Tren:",
            options=["Per Tahun", "Per Periode"],
            key="kec_trend_type"
        )
    
    with col_filter2:
        # Filter kecamatan tunggal
        available_kecamatan_single = sorted(df['Kecamatan'].unique())
        selected_kecamatan_single = st.selectbox(
            "Pilih Satu Kecamatan:",
            options=available_kecamatan_single,
            key="single_kecamatan_filter"
        )
    
    # Filter data berdasarkan kecamatan tunggal yang dipilih (gunakan semua tahun yang tersedia)
    single_kec_df = df[df['Kecamatan'] == selected_kecamatan_single]
    
    if single_kec_df.empty:
        st.error("Tidak ada data untuk kecamatan yang dipilih.")
    else:
        available_years_single = sorted(single_kec_df['Tahun'].unique())
        
        if trend_type_kec == "Per Tahun":
            # Tren tahunan untuk kecamatan tunggal
            yearly_single_trend = single_kec_df.groupby('Tahun').agg({
                'Prevalensi Stunting Persen': 'mean',
                'Stunting': 'sum',
                'Jumlah Yang Diukur': 'sum'
            }).reset_index()
            
            fig_single = go.Figure()
            
            fig_single.add_trace(go.Scatter(
                x=yearly_single_trend['Tahun'],
                y=yearly_single_trend['Prevalensi Stunting Persen'],
                mode='lines+markers',
                name=f'{selected_kecamatan_single}',
                line=dict(width=4, color='#e74c3c'),
                marker=dict(size=12),
                hovertemplate=f'<b>{selected_kecamatan_single}</b><br>Tahun: %{{x}}<br>Prevalensi: %{{y:.2f}}%<br>Total Kasus: %{{customdata[0]:,}}<br>Total Diukur: %{{customdata[1]:,}}<extra></extra>',
                customdata=yearly_single_trend[['Stunting', 'Jumlah Yang Diukur']].values
            ))
            
            fig_single.update_layout(
                title=f'Tren Stunting per Tahun - {selected_kecamatan_single}',
                xaxis_title="Tahun",
                yaxis_title="Persentase Stunting (%)",
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_single, use_container_width=True)
            
            # Analisis tren untuk kecamatan tunggal
            if len(yearly_single_trend) > 1:
                single_trend_change = yearly_single_trend.iloc[-1]['Prevalensi Stunting Persen'] - yearly_single_trend.iloc[0]['Prevalensi Stunting Persen']
                best_year_single = yearly_single_trend.loc[yearly_single_trend['Prevalensi Stunting Persen'].idxmin(), 'Tahun']
                worst_year_single = yearly_single_trend.loc[yearly_single_trend['Prevalensi Stunting Persen'].idxmax(), 'Tahun']
                best_prev_single = yearly_single_trend['Prevalensi Stunting Persen'].min()
                worst_prev_single = yearly_single_trend['Prevalensi Stunting Persen'].max()
                range_single = worst_prev_single - best_prev_single
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if single_trend_change < -1:
                        st.success(f"**Tren Membaik**\nTurun {abs(single_trend_change):.1f}%")
                    elif single_trend_change > 1:
                        st.error(f"**Tren Memburuk**\nNaik {single_trend_change:.1f}%")
                    else:
                        st.info(f"**Tren Stabil**\nPerubahan {single_trend_change:+.1f}%")
                
                with col2:
                    st.metric("Tahun Terbaik", f"{best_year_single}", f"{best_prev_single:.1f}%")
                
                with col3:
                    st.metric("Tahun Terburuk", f"{worst_year_single}", f"{worst_prev_single:.1f}%")
                
                # Insight untuk kecamatan tunggal
                if range_single > 5:
                    st.warning(f"**Fluktuasi Tinggi**: Kecamatan **{selected_kecamatan_single}** mengalami fluktuasi besar dengan rentang {range_single:.1f}% antara tahun terbaik dan terburuk.")
                elif range_single > 2:
                    st.info(f"**Fluktuasi Sedang**: Terdapat variasi {range_single:.1f}% dalam periode yang diamati. Kondisi cukup stabil dengan beberapa fluktuasi.")
                else:
                    st.success(f"**Konsisten**: Kecamatan **{selected_kecamatan_single}** menunjukkan konsistensi yang baik dengan rentang hanya {range_single:.1f}%.")
            else:
                st.info("Data hanya tersedia untuk satu tahun.")
        
        else:  # Per Periode
            # Sorting periode yang benar untuk kecamatan tunggal
            single_kec_df_sorted = create_sorted_period_data(single_kec_df.copy())
            
            period_single_trend = single_kec_df_sorted.groupby(['Tahun', 'Bulan', 'Periode', 'Month_Num']).agg({
                'Prevalensi Stunting Persen': 'mean',
                'Stunting': 'sum',
                'Jumlah Yang Diukur': 'sum'
            }).reset_index()
            
            period_single_trend = period_single_trend.sort_values(['Tahun', 'Month_Num']).reset_index(drop=True)
            
            fig_single_period = go.Figure()
            
            fig_single_period.add_trace(go.Scatter(
                x=period_single_trend['Periode'],
                y=period_single_trend['Prevalensi Stunting Persen'],
                mode='lines+markers',
                name=f'{selected_kecamatan_single}',
                line=dict(width=4, color='#9b59b6'),
                marker=dict(size=10),
                hovertemplate=f'<b>{selected_kecamatan_single}</b><br>Periode: %{{x}}<br>Prevalensi: %{{y:.2f}}%<br>Total Kasus: %{{customdata[0]:,}}<br>Total Diukur: %{{customdata[1]:,}}<extra></extra>',
                customdata=period_single_trend[['Stunting', 'Jumlah Yang Diukur']].values
            ))
            
            fig_single_period.update_layout(
                title=f'Tren Stunting per Periode - {selected_kecamatan_single}',
                xaxis_title="Periode (Tahun-Bulan)",
                yaxis_title="Persentase Stunting (%)",
                height=500,
                hovermode='x unified',
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=period_single_trend['Periode'].tolist()
                )
            )
            
            st.plotly_chart(fig_single_period, use_container_width=True)
            
            # Analisis tren periodik untuk kecamatan tunggal
            if len(period_single_trend) > 1:
                highest_period_single = period_single_trend.loc[period_single_trend['Prevalensi Stunting Persen'].idxmax(), 'Periode']
                lowest_period_single = period_single_trend.loc[period_single_trend['Prevalensi Stunting Persen'].idxmin(), 'Periode']
                highest_prev_single = period_single_trend['Prevalensi Stunting Persen'].max()
                lowest_prev_single = period_single_trend['Prevalensi Stunting Persen'].min()
                range_period_single = highest_prev_single - lowest_prev_single
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Periode Terbaik", lowest_period_single, f"{lowest_prev_single:.1f}%")
                
                with col2:
                    st.metric("Periode Terburuk", highest_period_single, f"{highest_prev_single:.1f}%")
                
                with col3:
                    st.metric("Rentang Variasi", f"{range_period_single:.1f}%", "Antar Periode")
                
                # Analisis pola musiman untuk kecamatan tunggal
                monthly_avg_single = period_single_trend.groupby('Bulan')['Prevalensi Stunting Persen'].mean()
                month_order = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                               'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
                monthly_avg_single = monthly_avg_single.reindex([month for month in month_order if month in monthly_avg_single.index])
                
                if len(monthly_avg_single) > 1:
                    best_month_single = monthly_avg_single.idxmin()
                    worst_month_single = monthly_avg_single.idxmax()
                    seasonal_range_single = monthly_avg_single.max() - monthly_avg_single.min()
                    
                    if seasonal_range_single > 3:
                        st.warning(f"**Pola Musiman Kuat**: Kecamatan **{selected_kecamatan_single}** menunjukkan variasi musiman yang signifikan (rentang {seasonal_range_single:.1f}%). Bulan terbaik: **{best_month_single}**, terburuk: **{worst_month_single}**.")
                    elif seasonal_range_single > 1:
                        st.info(f"**Pola Musiman Sedang**: Terdapat variasi musiman dengan rentang {seasonal_range_single:.1f}%. Bulan terbaik: **{best_month_single}**, terburuk: **{worst_month_single}**.")
                    else:
                        st.success(f"**Konsisten Sepanjang Tahun**: Kecamatan **{selected_kecamatan_single}** menunjukkan konsistensi yang baik sepanjang tahun dengan variasi minimal ({seasonal_range_single:.1f}%).")
            else:
                st.info("Data hanya tersedia untuk satu periode.")

st.markdown("---")

st.header("🗺️ Perbandingan Antar Wilayah")

# Data untuk distribusi diambil dari periode terakhir untuk konsistensi dengan peta dan korelasi
if 'latest_year' in locals() and 'latest_month' in locals() and latest_month is not None:
    distribution_df = filtered_df[
        (filtered_df['Tahun'] == latest_year) & 
        (filtered_df['Bulan'] == latest_month)
    ]
    
else:
    distribution_df = filtered_df # Fallback jika periode terakhir tidak ditemukan
    

col1, col2 = st.columns(2)

with col1:
    # Kecamatan dengan prevalensi tertinggi
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

# Analisis distribusi menggunakan data yang sudah dihitung
highest_kec = top_kecamatan.iloc[0]['Kecamatan']
highest_prev = top_kecamatan.iloc[0]['Prevalensi Stunting Persen']
highest_cases = top_kecamatan.iloc[0]['Stunting']

lowest_kec = bottom_kecamatan.iloc[0]['Kecamatan']
lowest_prev = bottom_kecamatan.iloc[0]['Prevalensi Stunting Persen']
lowest_cases = bottom_kecamatan.iloc[0]['Stunting']

gap = highest_prev - lowest_prev

st.info(f"**Variasi Antar Wilayah**: Terdapat perbedaan {gap:.1f}% antara kecamatan dengan angka stunting tertinggi (**{highest_kec}**: {highest_prev:.1f}% atau {highest_cases:,} kasus) dan terendah (**{lowest_kec}**: {lowest_prev:.1f}% atau {lowest_cases:,} kasus). Hal ini menunjukkan adanya variasi kondisi stunting antar wilayah.")

avg_prevalensi_kecamatan = distribution_df.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().reset_index()

# Gunakan fungsi utility untuk klasifikasi
avg_prevalensi_kecamatan['Kategori'] = avg_prevalensi_kecamatan['Prevalensi Stunting Persen'].apply(analyze_prevalence_category)

kategori_counts = avg_prevalensi_kecamatan['Kategori'].value_counts()

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='font-size: 18px; font-weight: bold;'>Distribusi Kecamatan Berdasarkan Kategori</h3>", unsafe_allow_html=True)
    fig_pie = px.pie(
        values=kategori_counts.values,
        names=kategori_counts.index,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("<h3 style='font-size: 18px; font-weight: bold;'>Daftar Kecamatan per Kategori</h3>", unsafe_allow_html=True)
    for kategori in kategori_counts.index:
        kecamatan_list = avg_prevalensi_kecamatan[avg_prevalensi_kecamatan['Kategori'] == kategori]['Kecamatan'].tolist()
        st.write(f"**{kategori}**: {', '.join(kecamatan_list[:15])}" + ("..." if len(kecamatan_list) > 15 else ""))

# Analisis kategori
total_kecamatan = len(avg_prevalensi_kecamatan)
high_categories = ['Tinggi (10-20%)', 'Sangat Tinggi (> 20%)']
high_count = sum([kategori_counts.get(cat, 0) for cat in high_categories])
high_pct = (high_count / total_kecamatan) * 100

low_count = kategori_counts.get('Rendah (< 5%)', 0)
medium_count = kategori_counts.get('Sedang (5-10%)', 0)

st.info(f"**Distribusi Kategori**: Dari {total_kecamatan} kecamatan, {low_count} ({low_count/total_kecamatan*100:.0f}%) berada dalam kategori rendah, {medium_count} ({medium_count/total_kecamatan*100:.0f}%) kategori sedang, dan {high_count} ({high_pct:.0f}%) dalam kategori tinggi. Distribusi ini memberikan gambaran kondisi stunting di wilayah yang diamati.")

st.markdown("---")

# =================== RANKING PERUBAHAN PREVALENSI ===================
col_header1, col_header2 = st.columns([3, 1])

with col_header1:
    st.header("📈📉 Perubahan Stunting Antar Waktu")

with col_header2:
    sort_option = st.selectbox(
        "🔧 Lihat berdasarkan:",
        options=[
            "📉 Penurunan Terbesar",
            "📈 Peningkatan Terbesar",
        ],
        index=0,
        help="Pilih untuk melihat kecamatan dengan perubahan terbesar"
    )

if filtered_df['Tahun'].nunique() > 1:
    perubahan_df = filtered_df.groupby(['Kecamatan', 'Tahun'])['Prevalensi Stunting Persen'].mean().reset_index()
    tahun_awal, tahun_akhir = perubahan_df['Tahun'].min(), perubahan_df['Tahun'].max()

    perubahan_pivot = perubahan_df.pivot(index='Kecamatan', columns='Tahun', values='Prevalensi Stunting Persen').reset_index()
    perubahan_pivot = perubahan_pivot.dropna()
    
    if len(perubahan_pivot.columns) >= 3:
        perubahan_pivot['Perubahan'] = perubahan_pivot[tahun_akhir] - perubahan_pivot[tahun_awal]
        perubahan_pivot['Perubahan_Persen'] = (perubahan_pivot['Perubahan'] / perubahan_pivot[tahun_awal]) * 100

        # Sorting berdasarkan pilihan user
        if sort_option == "📉 Penurunan Terbesar":
            sorted_data = perubahan_pivot.sort_values('Perubahan').head(15)
            chart_title = f"Kecamatan dengan Penurunan Stunting Terbesar ({tahun_awal} → {tahun_akhir})"
            chart_color = 'Greens_r'
        elif sort_option == "📈 Peningkatan Terbesar":
            sorted_data = perubahan_pivot.sort_values('Perubahan', ascending=False).head(15)
            chart_title = f"Kecamatan dengan Peningkatan Stunting Terbesar ({tahun_awal} → {tahun_akhir})"
            chart_color = 'Reds'

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
            st.metric("Kecamatan Menurun", perbaikan_count, delta=f"{perbaikan_count/len(perubahan_pivot)*100:.0f}% dari total")
        
        with col2:
            memburuk_count = len(perubahan_pivot[perubahan_pivot['Perubahan'] > 0])
            st.metric("Kecamatan Meningkat", memburuk_count, delta=f"{memburuk_count/len(perubahan_pivot)*100:.0f}% dari total")
        
        with col3:
            avg_change = perubahan_pivot['Perubahan'].mean()
            st.metric("Rata-rata Perubahan", f"{avg_change:.2f}%", delta="Negatif = Menurun")
        
        with col4:
            best_performer = perubahan_pivot.sort_values('Perubahan').iloc[0]['Kecamatan']
            worst_performer = perubahan_pivot.sort_values('Perubahan', ascending=False).iloc[0]['Kecamatan']
            st.metric("Penurunan Terbesar", best_performer)
            st.metric("Peningkatan Terbesar", worst_performer)

        # Analisis perubahan
        improvement_rate = (perbaikan_count / len(perubahan_pivot)) * 100
        best_change = perubahan_pivot['Perubahan'].min()
        worst_change = perubahan_pivot['Perubahan'].max()
        
        st.info(f"**Ringkasan Perubahan**: Dari periode {tahun_awal} ke {tahun_akhir}, {improvement_rate:.0f}% kecamatan ({perbaikan_count} kecamatan) mengalami penurunan stunting, sementara {100-improvement_rate:.0f}% mengalami peningkatan. Penurunan terbesar terjadi di **{best_performer}** ({abs(best_change):.1f}%), sedangkan peningkatan terbesar di **{worst_performer}** ({worst_change:.1f}%). Rata-rata perubahan secara keseluruhan adalah {avg_change:+.1f}%.")

        # Detail perubahan
        with st.expander("Detail Analisis Perubahan"):
            col1, col2 = st.columns(2)
            
            top_improve = perubahan_pivot.sort_values('Perubahan').head(3)
            top_worsen = perubahan_pivot.sort_values('Perubahan', ascending=False).head(3)
            
            with col1:
                st.markdown("**📉 Kecamatan dengan Penurunan Signifikan:**")
                for i, (_, row) in enumerate(top_improve.iterrows(), 1):
                    st.success(f"{i}. **{row['Kecamatan']}**: Turun {abs(row['Perubahan']):.1f}%")

            with col2:
                st.markdown("**📈 Kecamatan dengan Peningkatan Signifikan:**")
                for i, (_, row) in enumerate(top_worsen.iterrows(), 1):
                    st.error(f"{i}. **{row['Kecamatan']}**: Naik {row['Perubahan']:.1f}%")
                
    else:
        st.info("Data tidak mencukupi untuk analisis perubahan (memerlukan data minimal 2 tahun untuk kecamatan yang sama).")
else:
    st.info("Data hanya tersedia untuk satu tahun, sehingga analisis perubahan tidak dapat dilakukan.")

st.markdown("---")

# =================== ANALISIS KORELASI & KOMPOSISI ===================
st.header("🔬 Hubungan Stunting dengan Fasilitas Kesehatan")

if 'latest_year' in locals() and 'latest_month' in locals() and latest_month is not None:
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

# Merge data prevalensi dan fasilitas
analysis_df = pd.merge(prevalensi_df, faskes_df, on='Kecamatan', how='inner')

if not analysis_df.empty and len(analysis_df) > 1:
    # Hitung total fasilitas kesehatan per kecamatan
    facility_cols = [col for col in faskes_df.columns if col != 'Kecamatan']
    analysis_df['Total Faskes'] = analysis_df[facility_cols].sum(axis=1)

    # Urutkan berdasarkan prevalensi dari tinggi ke rendah
    display_kecamatan = analysis_df.sort_values('Prevalensi Stunting Persen', ascending=False)

    # Reshape data untuk visualisasi side-by-side
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
    
    # Buat grafik side-by-side per kecamatan
    fig_faskes_comp = px.bar(
        plot_df,
        x='Kecamatan',
        y='Nilai',
        color='Metrik',
        barmode='group',
        title=f'Perbandingan Stunting vs Fasilitas Kesehatan - {len(display_kecamatan)} Kecamatan',
        text='Nilai',
        color_discrete_map={
            'Persentase Stunting (%)': '#FF6B6B',
            'Jumlah Fasilitas Kesehatan': '#4ECDC4'
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

    # Analisis korelasi
    correlation = analysis_df['Prevalensi Stunting Persen'].corr(analysis_df['Total Faskes'])
    
    # Identifikasi kecamatan untuk metrics
    faskes_rendah_prev_tinggi = analysis_df[
        (analysis_df['Total Faskes'] <= analysis_df['Total Faskes'].quantile(0.3)) & 
        (analysis_df['Prevalensi Stunting Persen'] >= analysis_df['Prevalensi Stunting Persen'].quantile(0.7))
    ].sort_values('Prevalensi Stunting Persen', ascending=False)
        
    faskes_tinggi_prev_rendah = analysis_df[
        (analysis_df['Total Faskes'] >= analysis_df['Total Faskes'].quantile(0.7)) & 
        (analysis_df['Prevalensi Stunting Persen'] <= analysis_df['Prevalensi Stunting Persen'].quantile(0.3))
    ].sort_values('Prevalensi Stunting Persen')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if correlation < -0.3:
            delta_text = "Hubungan Negatif"
        elif correlation > 0.3:
            delta_text = "Hubungan Positif"
        else:
            delta_text = "Hubungan Lemah"
        st.metric("Korelasi", f"{correlation:.2f}", delta=delta_text)
    
    with col2:
        if not faskes_tinggi_prev_rendah.empty:
            best_kecamatan = faskes_tinggi_prev_rendah.iloc[0]['Kecamatan']
            best_prevalensi = faskes_tinggi_prev_rendah.iloc[0]['Prevalensi Stunting Persen']
            best_faskes = faskes_tinggi_prev_rendah.iloc[0]['Total Faskes']
            delta_text = f"{best_faskes:.0f} faskes, {best_prevalensi:.1f}% stunting"
        else:
            best_row = analysis_df.nsmallest(1, 'Prevalensi Stunting Persen').iloc[0]
            best_kecamatan = best_row['Kecamatan']
            delta_text = f"{best_row['Total Faskes']:.0f} faskes, {best_row['Prevalensi Stunting Persen']:.1f}% stunting"
        
        st.metric("Kondisi Terbaik", best_kecamatan, delta=delta_text)
    
    with col3:
        if not faskes_rendah_prev_tinggi.empty:
            challenge_kecamatan = faskes_rendah_prev_tinggi.iloc[0]['Kecamatan']
            challenge_prevalensi = faskes_rendah_prev_tinggi.iloc[0]['Prevalensi Stunting Persen']
            challenge_faskes = faskes_rendah_prev_tinggi.iloc[0]['Total Faskes']
            delta_text = f"{challenge_faskes:.0f} faskes, {challenge_prevalensi:.1f}% stunting"
        else:
            challenge_row = analysis_df.nlargest(1, 'Prevalensi Stunting Persen').iloc[0]
            challenge_kecamatan = challenge_row['Kecamatan']
            delta_text = f"{challenge_row['Total Faskes']:.0f} faskes, {challenge_row['Prevalensi Stunting Persen']:.1f}% stunting"
        
        st.metric("Perlu Perhatian", challenge_kecamatan, delta=delta_text)

    # Analisis menggunakan fungsi utility
    avg_faskes = analysis_df['Total Faskes'].mean()
    high_faskes_low_prev = len(faskes_tinggi_prev_rendah)
    low_faskes_high_prev = len(faskes_rendah_prev_tinggi)
    
    st.info(create_correlation_analysis(correlation, avg_faskes, high_faskes_low_prev, low_faskes_high_prev))

st.markdown("---")

# ========== KOMPOSISI STUNTING (FULL WIDTH) ==========
st.subheader("📊 Komposisi Jenis Stunting")

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
    textposition='inside'
))
fig_comp.add_trace(go.Bar(
    x=composition_df['Tahun'], 
    y=composition_df['Sangat Pendek'], 
    name='Sangat Pendek',
    text=composition_df['Sangat Pendek'],
    textposition='inside'
))
fig_comp.update_layout(
    barmode='stack', 
    title='Komposisi Kasus Stunting: Pendek vs Sangat Pendek', 
    xaxis_title='Tahun', 
    yaxis_title='Jumlah Kasus', 
    height=500
)
st.plotly_chart(fig_comp, use_container_width=True)

# Analisis komposisi
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

st.markdown("---")
