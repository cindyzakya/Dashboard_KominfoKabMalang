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
    st.subheader("📅 Tahun")
    
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
            st.warning("⚠️ Tidak ada tahun dipilih, menampilkan semua tahun")
    
    # Reset flag after rerun
    if st.session_state.reset_year_filter:
        st.session_state.reset_year_filter = False
    
    # Filter Kecamatan
    st.subheader("🏘️ Kecamatan")
    
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
            st.warning("⚠️ Tidak ada kecamatan dipilih, menampilkan semua kecamatan")
    
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
    st.error("❌ Tidak ada data yang sesuai dengan filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

# Info filter aktif
col_info1, col_info2 = st.columns(2)
with col_info1:
    if len(selected_year) == len(df['Tahun'].unique()):
        st.info(f"📅 **Filter Tahun**: Semua tahun ({min(selected_year)}-{max(selected_year)})")
    else:
        st.info(f"📅 **Filter Tahun**: {len(selected_year)} tahun terpilih ({min(selected_year)}-{max(selected_year)})")

with col_info2:
    if len(selected_kecamatan) == len(df['Kecamatan'].unique()):
        st.info(f"🏘️ **Filter Kecamatan**: Semua kecamatan ({len(selected_kecamatan)} kecamatan)")
    else:
        st.info(f"🏘️ **Filter Kecamatan**: {len(selected_kecamatan)} kecamatan terpilih")

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
        st.caption(f"📅 Data per {latest_month} {latest_year}")

with col5:
    st.metric("Total Rumah Sakit", f"{total_rs:,}")
    if latest_month:
        st.caption(f"📅 Data per {latest_month} {latest_year}")

st.markdown("---")


# =================== ANALISIS TREN TEMPORAL (FULL WIDTH) ===================
st.header("📈 Analisis Tren Temporal")

# Radio button untuk memilih jenis tren (hanya bisa pilih satu)
trend_option = st.radio(
    "🔧 Pilih jenis tren yang ingin ditampilkan:",
    options=[
        "📊 Tren per Tahun",
        "📅 Tren per Periode", 
        "🏘️ Tren per Tahun (per Kecamatan)",
        "📍 Tren per Periode (per Kecamatan)"
    ],
    index=0,  # Default pilihan pertama
    horizontal=True,
    help="Pilih satu jenis analisis tren yang ingin ditampilkan"
)

# ========== TREN BERDASARKAN PILIHAN (FULL WIDTH) ==========
if trend_option == "📊 Tren per Tahun":
    yearly_trend = filtered_df.groupby('Tahun').agg({
        'Prevalensi Stunting Persen': ['mean', 'std'],
        'Stunting': 'sum',
        'Jumlah Yang Diukur': 'sum'
    }).reset_index()
    
    # Flatten column names
    yearly_trend.columns = ['Tahun', 'Prevalensi_Mean', 'Prevalensi_Std', 'Total_Stunting', 'Total_Diukur']
    yearly_trend['Prevalensi_Std'] = yearly_trend['Prevalensi_Std'].fillna(0)
    
    fig_trend = go.Figure()
    
    # Main trend line
    fig_trend.add_trace(go.Scatter(
        x=yearly_trend['Tahun'],
        y=yearly_trend['Prevalensi_Mean'],
        mode='lines+markers',
        name='Prevalensi',
        line=dict(width=4, color='#1f77b4'),
        marker=dict(size=12),
        hovertemplate='<b>Prevalensi</b><br>Tahun: %{x}<br>Prevalensi: %{y:.2f}%<br>Total Kasus: %{customdata[0]:,}<br>Total Diukur: %{customdata[1]:,}<br>Std Dev: %{customdata[2]:.2f}%<extra></extra>',
        customdata=yearly_trend[['Total_Stunting', 'Total_Diukur', 'Prevalensi_Std']].values
    ))
    
    # Error bars untuk variabilitas
    fig_trend.add_trace(go.Scatter(
        x=yearly_trend['Tahun'],
        y=yearly_trend['Prevalensi_Mean'] + yearly_trend['Prevalensi_Std'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig_trend.update_layout(
        title='📊 Tren Prevalensi Stunting per Tahun',
        xaxis_title="Tahun",
        yaxis_title="Prevalensi Stunting (%)",
        height=500,
        hovermode='x unified'
    )

elif trend_option == "📅 Tren per Periode":
    filtered_df['Periode'] = filtered_df['Tahun'].astype(str) + '-' + filtered_df['Bulan']
    
    period_trend = filtered_df.groupby('Periode').agg({
        'Prevalensi Stunting Persen': ['mean', 'std'],
        'Stunting': 'sum',
        'Jumlah Yang Diukur': 'sum'
    }).reset_index()
    
    # Flatten column names
    period_trend.columns = ['Periode', 'Prevalensi_Mean', 'Prevalensi_Std', 'Total_Stunting', 'Total_Diukur']
    period_trend['Prevalensi_Std'] = period_trend['Prevalensi_Std'].fillna(0)
    
    fig_trend = go.Figure()
    
    fig_trend.add_trace(go.Scatter(
        x=period_trend['Periode'],
        y=period_trend['Prevalensi_Mean'],
        mode='lines+markers',
        name='Prevalensi',
        line=dict(width=4, color='#2E8B57'),
        marker=dict(size=10),
        hovertemplate='<b>Prevalensi</b><br>Periode: %{x}<br>Prevalensi: %{y:.2f}%<br>Total Kasus: %{customdata[0]:,}<br>Total Diukur: %{customdata[1]:,}<br>Std Dev: %{customdata[2]:.2f}%<extra></extra>',
        customdata=period_trend[['Total_Stunting', 'Total_Diukur', 'Prevalensi_Std']].values
    ))
    
    # Error bars
    fig_trend.add_trace(go.Scatter(
        x=period_trend['Periode'],
        y=period_trend['Prevalensi_Mean'] + period_trend['Prevalensi_Std'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    
    fig_trend.update_layout(
        title='📅 Tren Prevalensi Stunting per Periode',
        xaxis_title="Periode (Tahun-Bulan)",
        yaxis_title="Prevalensi Stunting (%)",
        height=450,
        hovermode='x unified'
    )

elif trend_option == "🏘️ Tren per Tahun (per Kecamatan)":
    yearly_kec_trend = filtered_df.groupby(['Kecamatan', 'Tahun'])['Prevalensi Stunting Persen'].mean().reset_index()
    
    fig_trend = px.line(
        yearly_kec_trend,
        x='Tahun',
        y='Prevalensi Stunting Persen',
        color='Kecamatan',
        markers=True,
        title='🏘️ Tren Prevalensi Stunting per Tahun (per Kecamatan)',
        hover_data={'Prevalensi Stunting Persen': ':.2f'}
    )
    
    fig_trend.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    fig_trend.update_layout(
        xaxis_title="Tahun",
        yaxis_title="Prevalensi Stunting (%)",
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )

else:  # "📍 Tren per Periode (per Kecamatan)"
    if 'Periode' not in filtered_df.columns:
        filtered_df['Periode'] = filtered_df['Tahun'].astype(str) + '-' + filtered_df['Bulan']
        
    period_kec_trend = filtered_df.groupby(['Kecamatan', 'Periode'])['Prevalensi Stunting Persen'].mean().reset_index()
    
    fig_trend = px.line(
        period_kec_trend,
        x='Periode',
        y='Prevalensi Stunting Persen',
        color='Kecamatan',
        markers=True,
        title='📍 Tren Prevalensi Stunting per Periode (per Kecamatan)',
        hover_data={'Prevalensi Stunting Persen': ':.2f'}
    )
    
    fig_trend.update_traces(
        line=dict(width=3),
        marker=dict(size=7)
    )
    
    fig_trend.update_layout(
        xaxis_title="Periode (Tahun-Bulan)",
        yaxis_title="Prevalensi Stunting (%)",
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )

# Tampilkan grafik dalam full width
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

st.header("🗺️ Distribusi Prevalensi Stunting")

# Data untuk distribusi diambil dari periode terakhir untuk konsistensi dengan peta dan korelasi
if 'latest_year' in locals() and 'latest_month' in locals() and latest_month is not None:
    distribution_df = filtered_df[
        (filtered_df['Tahun'] == latest_year) & 
        (filtered_df['Bulan'] == latest_month)
    ]
    st.info(f"Data distribusi ditampilkan berdasarkan periode terakhir yang tersedia: **{latest_month} {latest_year}**")
else:
    distribution_df = filtered_df # Fallback jika periode terakhir tidak ditemukan
    st.info("Data distribusi ditampilkan berdasarkan rata-rata dari seluruh periode terfilter.")

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
        title='Top 10 Prevalensi Stunting Tertinggi',
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
        title='Top 10 Prevalensi Stunting Terendah',
        orientation='h',
        color='Prevalensi Stunting Persen',
        color_continuous_scale='Blues',
        text='Prevalensi Stunting Persen'
    )
    fig_bottom.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bottom.update_layout(height=500)
    st.plotly_chart(fig_bottom, use_container_width=True)

avg_prevalensi_kecamatan = distribution_df.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().reset_index()

def classify_prevalensi(prevalensi):
    if prevalensi < 5:
        return "Rendah (< 5%)"
    elif prevalensi < 10:
        return "Sedang (5-10%)"
    elif prevalensi < 20:
        return "Tinggi (10-20%)"
    else:
        return "Sangat Tinggi (> 20%)"

avg_prevalensi_kecamatan['Kategori'] = avg_prevalensi_kecamatan['Prevalensi Stunting Persen'].apply(classify_prevalensi)

kategori_counts = avg_prevalensi_kecamatan['Kategori'].value_counts()

col1, col2 = st.columns(2)

with col1:
    st.markdown("<h3 style='font-size: 18px; font-weight: bold;'>Distribusi Kecamatan Berdasarkan Kategori Prevalensi</h3>", unsafe_allow_html=True)
    fig_pie = px.pie(
        values=kategori_counts.values,
        names=kategori_counts.index,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.markdown("<h3 style='font-size: 18px; font-weight: bold;'>Detail Kecamatan per Kategori</h3>", unsafe_allow_html=True)
    for kategori in kategori_counts.index:
        kecamatan_list = avg_prevalensi_kecamatan[avg_prevalensi_kecamatan['Kategori'] == kategori]['Kecamatan'].tolist()
        st.write(f"**{kategori}**: {', '.join(kecamatan_list[:15])}" + ("..." if len(kecamatan_list) > 15 else ""))

st.markdown("---")

# =================== RANKING PERUBAHAN PREVALENSI ===================
# Header dengan filter sorting
col_header1, col_header2 = st.columns([3, 1])

with col_header1:
    st.header("📉📈 Ranking Perubahan Prevalensi")

with col_header2:
    # Filter sorting
    sort_option = st.selectbox(
        "🔧 Urutkan berdasarkan:",
        options=[
            "📉 Perbaikan Terbesar (↓)",
            "📈 Memburuk Terbesar (↑)",
        ],
        index=0,
        help="Pilih cara pengurutan data perubahan"
    )

if filtered_df['Tahun'].nunique() > 1:
    perubahan_df = filtered_df.groupby(['Kecamatan', 'Tahun'])['Prevalensi Stunting Persen'].mean().reset_index()
    tahun_awal, tahun_akhir = perubahan_df['Tahun'].min(), perubahan_df['Tahun'].max()

    perubahan_pivot = perubahan_df.pivot(index='Kecamatan', columns='Tahun', values='Prevalensi Stunting Persen').reset_index()
    perubahan_pivot = perubahan_pivot.dropna()  # Hanya kecamatan yang ada di kedua tahun
    
    if len(perubahan_pivot.columns) >= 3:  # Kecamatan + minimal 2 tahun
        perubahan_pivot['Perubahan'] = perubahan_pivot[tahun_akhir] - perubahan_pivot[tahun_awal]
        perubahan_pivot['Perubahan_Persen'] = (perubahan_pivot['Perubahan'] / perubahan_pivot[tahun_awal]) * 100
        

        # Sorting berdasarkan pilihan user
        if sort_option == "📉 Perbaikan Terbesar (↓)":
            sorted_data = perubahan_pivot.sort_values('Perubahan').head(15)  # Nilai paling negatif
            chart_title = f"🎯 Top Perbaikan Terbesar ({tahun_awal} → {tahun_akhir})"
            chart_color = 'Greens_r'
        elif sort_option == "📈 Memburuk Terbesar (↑)":
            sorted_data = perubahan_pivot.sort_values('Perubahan', ascending=False).head(15)  # Nilai paling positif
            chart_title = f"⚠️ Top Memburuk Terbesar ({tahun_awal} → {tahun_akhir})"
            chart_color = 'Reds'

        # ========== VISUALISASI GRAFIK PERUBAHAN ==========
        col1, col2 = st.columns(2)
        
        with col1:
            # Grafik berdasarkan pilihan sorting
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
            # Tabel data berdasarkan sorting
            display_data = sorted_data[['Kecamatan', tahun_awal, tahun_akhir, 'Perubahan', 'Perubahan_Persen']].copy()
            display_data.columns = ['Kecamatan', f'{tahun_awal} (%)', f'{tahun_akhir} (%)', 'Selisih (%)', 'Perubahan (%)']
            
            st.dataframe(display_data, column_config={
                f'{tahun_awal} (%)': st.column_config.NumberColumn(format='%.2f'),
                f'{tahun_akhir} (%)': st.column_config.NumberColumn(format='%.2f'),
                'Selisih (%)': st.column_config.NumberColumn(format='%.2f'),
                'Perubahan (%)': st.column_config.NumberColumn(format='%.1f')
            }, hide_index=True, height=400)
        
        # ========== METRICS INSIGHT ==========
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            perbaikan_count = len(perubahan_pivot[perubahan_pivot['Perubahan'] < 0])
            st.metric("Kecamatan Membaik", perbaikan_count, delta=f"{perbaikan_count/len(perubahan_pivot)*100:.1f}% dari total")
        
        with col2:
            memburuk_count = len(perubahan_pivot[perubahan_pivot['Perubahan'] > 0])
            st.metric("Kecamatan Memburuk", memburuk_count, delta=f"{memburuk_count/len(perubahan_pivot)*100:.1f}% dari total")
        
        with col3:
            avg_change = perubahan_pivot['Perubahan'].mean()
            st.metric("Rata-rata Perubahan", f"{avg_change:.2f}%", delta="Negatif = Baik")
        
        with col4:
            best_performer = perubahan_pivot.sort_values('Perubahan').iloc[0]['Kecamatan']
            worst_performer = perubahan_pivot.sort_values('Perubahan', ascending=False).iloc[0]['Kecamatan']
            st.metric("Best Performer", best_performer)
            st.metric("Needs Attention", worst_performer)

        # ========== REKOMENDASI BERDASARKAN PERUBAHAN ==========
        with st.expander("📋 Detail Perubahan"):
            col1, col2 = st.columns(2)
            
            # Ambil top 3 terbaik dan terburuk
            top_improve = perubahan_pivot.sort_values('Perubahan').head(3)
            top_worsen = perubahan_pivot.sort_values('Perubahan', ascending=False).head(3)
            
            with col1:
                st.markdown("**🎯 Kecamatan dengan Perbaikan Signifikan:**")
                for _, row in top_improve.iterrows():
                    st.success(f"**{row['Kecamatan']}**: Turun {abs(row['Perubahan']):.1f}% ({row['Perubahan_Persen']:.1f}%)")

            
            with col2:
                st.markdown("**⚠️ Kecamatan Membutuhkan Perhatian Khusus:**")
                for _, row in top_worsen.iterrows():
                    st.error(f"**{row['Kecamatan']}**: Naik {row['Perubahan']:.1f}% ({row['Perubahan_Persen']:.1f}%)")
    else:
        st.info("Data tidak cukup untuk menghitung perubahan (perlu data di minimal 2 tahun untuk kecamatan yang sama).")
else:
    st.info("Data hanya 1 tahun, tidak bisa menghitung perubahan.")

st.markdown("---")

# =================== ANALISIS KORELASI & KOMPOSISI ===================
st.header("🔬 Analisis Korelasi & Komposisi")

# ========== ANALISIS KORELASI (FULL WIDTH) ==========
# Definisikan urutan bulan
month_order = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
               'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

if 'latest_year' in locals() and 'latest_month' in locals() and latest_month is not None:
    # Data prevalensi: ambil dari periode terakhir untuk konsistensi
    latest_period_data_for_corr = filtered_df[
        (filtered_df['Tahun'] == latest_year) & 
        (filtered_df['Bulan'] == latest_month)
    ]
    prevalensi_df = latest_period_data_for_corr.groupby('Kecamatan').agg({
        'Prevalensi Stunting Persen': 'mean'
    }).reset_index()
    st.info(f"Analisis korelasi menggunakan data dari periode: **{latest_month} {latest_year}**")
else:
    # Fallback jika periode terakhir tidak bisa ditentukan
    prevalensi_df = filtered_df.groupby('Kecamatan').agg({'Prevalensi Stunting Persen': 'mean'}).reset_index()
    st.info("Analisis korelasi menggunakan data rata-rata dari seluruh periode terfilter.")

# Data fasilitas: ambil dari periode terakhir yang ada di data terfilter
def get_latest_facilities_data(data):
    if data.empty:
        return pd.DataFrame()

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

faskes_df = get_latest_facilities_data(filtered_df)

# Merge data prevalensi dan fasilitas
analysis_df = pd.merge(prevalensi_df, faskes_df, on='Kecamatan', how='inner')

if not analysis_df.empty and len(analysis_df) > 1:
    # Hitung total fasilitas kesehatan per kecamatan
    facility_cols = [col for col in faskes_df.columns if col != 'Kecamatan']
    analysis_df['Total Faskes'] = analysis_df[facility_cols].sum(axis=1)

    # TAMPILKAN SEMUA KECAMATAN YANG DIPILIH USER (bukan top 15)
    # Urutkan berdasarkan prevalensi dari tinggi ke rendah
    display_kecamatan = analysis_df.sort_values('Prevalensi Stunting Persen', ascending=False)

    # Reshape data untuk visualisasi side-by-side
    plot_data = []
    for _, row in display_kecamatan.iterrows():
        plot_data.append({
            'Kecamatan': row['Kecamatan'],
            'Metrik': 'Prevalensi Stunting (%)',
            'Nilai': row['Prevalensi Stunting Persen']
        })
        plot_data.append({
            'Kecamatan': row['Kecamatan'],
            'Metrik': 'Total Fasilitas',
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
        title=f'Prevalensi Stunting vs Jumlah Fasilitas Kesehatan - {len(display_kecamatan)} Kecamatan ({latest_month} {latest_year})',
        text='Nilai',
        color_discrete_map={
            'Prevalensi Stunting (%)': '#FF6B6B',
            'Total Fasilitas': '#4ECDC4'
        }
    )
    
    fig_faskes_comp.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_faskes_comp.update_layout(
        height=600,  # Tinggi lebih besar untuk banyak kecamatan
        yaxis_title='Nilai',
        xaxis_title='Kecamatan',
        xaxis={'tickangle': 45}
    )
    
    st.plotly_chart(fig_faskes_comp, use_container_width=True)


        # ========== ANALISIS KORELASI & INSIGHT ==========
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
        if correlation < -0.5:
            delta_text = "Negatif Kuat"
        elif correlation < -0.3:
            delta_text = "Negatif Sedang"
        elif correlation > 0.5:
            delta_text = "Positif Kuat"
        elif correlation > 0.3:
            delta_text = "Positif Sedang"
        else:
            delta_text = "Tidak Signifikan"
        st.metric("Koefisien Korelasi", f"{correlation:.3f}", delta=delta_text)
    
    with col2:
        # Best Performer
        if not faskes_tinggi_prev_rendah.empty:
            best_kecamatan = faskes_tinggi_prev_rendah.iloc[0]['Kecamatan']
            best_prevalensi = faskes_tinggi_prev_rendah.iloc[0]['Prevalensi Stunting Persen']
            best_faskes = faskes_tinggi_prev_rendah.iloc[0]['Total Faskes']
            delta_text = f"{best_faskes:.0f} faskes, {best_prevalensi:.1f}% stunting"
        else:
            # Fallback: kecamatan dengan prevalensi terendah
            best_row = analysis_df.nsmallest(1, 'Prevalensi Stunting Persen').iloc[0]
            best_kecamatan = best_row['Kecamatan']
            delta_text = f"{best_row['Total Faskes']:.0f} faskes, {best_row['Prevalensi Stunting Persen']:.1f}% stunting"
        
        st.metric("Best Performer", best_kecamatan, delta=delta_text)
    
    with col3:
        # Needs Attention
        if not faskes_rendah_prev_tinggi.empty:
            needs_attention_kecamatan = faskes_rendah_prev_tinggi.iloc[0]['Kecamatan']
            needs_prevalensi = faskes_rendah_prev_tinggi.iloc[0]['Prevalensi Stunting Persen']
            needs_faskes = faskes_rendah_prev_tinggi.iloc[0]['Total Faskes']
            delta_text = f"{needs_faskes:.0f} faskes, {needs_prevalensi:.1f}% stunting"
        else:
            # Fallback: kecamatan dengan prevalensi tertinggi
            needs_row = analysis_df.nlargest(1, 'Prevalensi Stunting Persen').iloc[0]
            needs_attention_kecamatan = needs_row['Kecamatan']
            delta_text = f"{needs_row['Total Faskes']:.0f} faskes, {needs_row['Prevalensi Stunting Persen']:.1f}% stunting"
        
        st.metric("Needs Attention", needs_attention_kecamatan, delta=delta_text)

st.markdown("---")

# ========== KOMPOSISI STUNTING (FULL WIDTH) ==========
st.subheader("📊 Komposisi Kasus Stunting")

# Komposisi Stunting (Pendek vs Sangat Pendek) - logika tidak diubah
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
    title='Komposisi Kasus Stunting (Pendek vs Sangat Pendek)', 
    xaxis_title='Tahun', 
    yaxis_title='Jumlah Kasus', 
    height=500
)
st.plotly_chart(fig_comp, use_container_width=True)
st.markdown("---")
st.header("🗺️ Peta Sebaran Indikator")

all_indicator_options = {
    "Prevalensi Stunting (%)": "Prevalensi Stunting Persen",
    "Jumlah Rumah Sakit": "Jumlah Rumah Sakit",
    "Jumlah Puskesmas": "Jumlah Puskesmas",
    "Jumlah Puskesmas Pembantu": "Jumlah Puskesmas Pembantu",
    "Jumlah Klinik": "Jumlah Klinik",
    "Pos Kesehatan": "Pos Kesehatan",
    "Jumlah Pondak Bersalin Desa (Polindes)": "Jumlah Pondak Bersalin Desa (Polindes)",
}

available_indicators = {label: col for label, col in all_indicator_options.items() if col in filtered_df.columns}

selected_indicator_label = st.selectbox("Pilih Indikator Peta", list(available_indicators.keys()))
selected_indicator = available_indicators[selected_indicator_label]

# Data untuk peta diambil HANYA dari periode terakhir yang tersedia dalam filter
# untuk memastikan semua indikator (faskes dan prevalensi) konsisten.
if 'latest_year' in locals() and 'latest_month' in locals() and not faskes_df.empty:
    latest_period_data = filtered_df[
        (filtered_df['Tahun'] == latest_year) & 
        (filtered_df['Bulan'] == latest_month)
    ]
    prevalence_latest_df = latest_period_data.groupby('Kecamatan').agg({
        'Prevalensi Stunting Persen': 'mean'
    }).reset_index()

    # Gabungkan data faskes terbaru dengan data prevalensi terbaru
    map_data_source = pd.merge(faskes_df, prevalence_latest_df, on="Kecamatan", how="left")
else:
    map_data_source = pd.DataFrame() # Kosongkan jika data tidak cukup

if not map_data_source.empty and selected_indicator in map_data_source.columns:
    # Pastikan tidak ada nilai NaN yang bisa menyebabkan error
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
        hover_data={selected_indicator: ':.0f'} # Tampilkan sebagai angka bulat
    )
    fig_map.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        title=f"Peta Sebaran {selected_indicator_label} per Kecamatan (Data per {latest_month} {latest_year})"
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning(f"Data untuk indikator '{selected_indicator_label}' tidak tersedia untuk ditampilkan di peta dengan filter saat ini.")