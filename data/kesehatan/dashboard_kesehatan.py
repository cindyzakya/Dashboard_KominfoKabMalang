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
    initial_sidebar_state="collapsed"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('kesehatan_stunting.csv')
    # Membersihkan kolom Prevalensi Stunting
    df['Prevalensi Stunting Persen'] = df['Prevalensi Stunting'].str.replace('%', '').str.replace(' ', '').str.replace('%%', '').astype(float)
    return df

df = load_data()

# Title dan Header
st.title("📊 Dashboard Analisis Data Stunting")
st.markdown("Dashboard komprehensif untuk analisis data stunting di berbagai kecamatan")
st.markdown("---")

# Filter di bagian atas
st.header("🔍 Filter Data")
col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    selected_year = st.multiselect(
        "Pilih Tahun:",
        options=sorted(df['Tahun'].unique()),
        default=sorted(df['Tahun'].unique()),
        key="year_filter"
    )

with col_filter2:
    selected_kecamatan = st.multiselect(
        "Pilih Kecamatan:",
        options=sorted(df['Kecamatan'].unique()),
        default=sorted(df['Kecamatan'].unique())[:10],  # Default 10 kecamatan pertama
        key="kecamatan_filter"
    )

# Filter data berdasarkan seleksi
filtered_df = df[
    (df['Tahun'].isin(selected_year)) &
    (df['Kecamatan'].isin(selected_kecamatan))
]

st.markdown("---")

# =================== METRICS UTAMA ===================
st.header("📋 Ringkasan Utama")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_stunting = filtered_df['Stunting'].sum()
    st.metric("Total Kasus Stunting", f"{total_stunting:,}")

with col2:
    total_diukur = filtered_df['Jumlah Yang Diukur'].sum()
    st.metric("Total Anak Diukur", f"{total_diukur:,}")

with col3:
    avg_prevalensi = filtered_df['Prevalensi Stunting Persen'].mean()
    st.metric("Rata-rata Prevalensi", f"{avg_prevalensi:.2f}%")

with col4:
    total_puskesmas = filtered_df['Jumlah Puskesmas'].sum()
    st.metric("Total Puskesmas", f"{total_puskesmas:,}")

with col5:
    total_rs = filtered_df['Jumlah Rumah Sakit'].sum()
    st.metric("Total Rumah Sakit", f"{total_rs:,}")

st.markdown("---")

# =================== ANALISIS TREN TEMPORAL ===================
st.header("📈 Analisis Tren Temporal")

col1, col2 = st.columns(2)

with col1:
    # Tren prevalensi stunting per tahun
    yearly_trend = filtered_df.groupby('Tahun').agg({
        'Prevalensi Stunting Persen': 'mean',
        'Stunting': 'sum',
        'Jumlah Yang Diukur': 'sum'
    }).reset_index()
    
    fig_trend = px.line(
        yearly_trend, 
        x='Tahun', 
        y='Prevalensi Stunting Persen',
        title='Tren Prevalensi Stunting per Tahun',
        markers=True
    )
    fig_trend.update_layout(
        xaxis_title="Tahun",
        yaxis_title="Prevalensi Stunting (%)"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    # Perbandingan Februari vs Agustus
    monthly_comparison = filtered_df.groupby(['Tahun', 'Bulan']).agg({
        'Prevalensi Stunting Persen': 'mean'
    }).reset_index()
    
    fig_monthly = px.bar(
        monthly_comparison,
        x='Tahun',
        y='Prevalensi Stunting Persen',
        color='Bulan',
        title='Perbandingan Prevalensi: Februari vs Agustus',
        barmode='group'
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

# Heatmap tren per kecamatan
st.subheader("🔥 Heatmap Prevalensi Stunting per Kecamatan dan Tahun")

heatmap_data = filtered_df.groupby(['Kecamatan', 'Tahun'])['Prevalensi Stunting Persen'].mean().reset_index()
heatmap_pivot = heatmap_data.pivot(index='Kecamatan', columns='Tahun', values='Prevalensi Stunting Persen')

fig_heatmap = px.imshow(
    heatmap_pivot,
    title="Heatmap Prevalensi Stunting",
    color_continuous_scale="Reds",
    aspect="auto"
)
fig_heatmap.update_layout(height=600)
st.plotly_chart(fig_heatmap, use_container_width=True)

st.markdown("---")

# =================== ANALISIS GEOGRAFIS ===================
st.header("🗺️ Analisis Geografis")

col1, col2 = st.columns(2)

with col1:
    # Top 10 kecamatan dengan prevalensi tertinggi
    top_kecamatan = filtered_df.groupby('Kecamatan').agg({
        'Prevalensi Stunting Persen': 'mean',
        'Stunting': 'sum'
    }).reset_index().sort_values('Prevalensi Stunting Persen', ascending=False).head(10)
    
    fig_top = px.bar(
        top_kecamatan,
        x='Prevalensi Stunting Persen',
        y='Kecamatan',
        title='Top 10 Kecamatan dengan Prevalensi Stunting Tertinggi',
        orientation='h',
        color='Prevalensi Stunting Persen',
        color_continuous_scale='Reds'
    )
    fig_top.update_layout(height=500)
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    # Distribusi kasus stunting per kecamatan
    kecamatan_stats = filtered_df.groupby('Kecamatan').agg({
        'Stunting': 'sum',
        'Jumlah Yang Diukur': 'sum'
    }).reset_index()
    kecamatan_stats['Rasio'] = kecamatan_stats['Stunting'] / kecamatan_stats['Jumlah Yang Diukur'] * 100
    
    fig_scatter = px.scatter(
        kecamatan_stats,
        x='Jumlah Yang Diukur',
        y='Stunting',
        size='Rasio',
        hover_name='Kecamatan',
        title='Hubungan Jumlah Pemeriksaan vs Kasus Stunting',
        color='Rasio',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# Analisis performa kecamatan
st.subheader("📊 Klasifikasi Kecamatan Berdasarkan Prevalensi")

avg_prevalensi_kecamatan = filtered_df.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().reset_index()

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
    fig_pie = px.pie(
        values=kategori_counts.values,
        names=kategori_counts.index,
        title='Distribusi Kecamatan Berdasarkan Kategori Prevalensi'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Detail Kecamatan per Kategori")
    for kategori in kategori_counts.index:
        kecamatan_list = avg_prevalensi_kecamatan[avg_prevalensi_kecamatan['Kategori'] == kategori]['Kecamatan'].tolist()
        st.write(f"**{kategori}**: {', '.join(kecamatan_list[:5])}" + ("..." if len(kecamatan_list) > 5 else ""))

st.markdown("---")

# =================== FASILITAS KESEHATAN ===================
st.header("🏥 Analisis Fasilitas Kesehatan")

# Korelasi fasilitas kesehatan dengan prevalensi stunting
col1, col2 = st.columns(2)

with col1:
    # Korelasi Puskesmas vs Prevalensi
    fig_puskesmas = px.scatter(
        filtered_df,
        x='Jumlah Puskesmas',
        y='Prevalensi Stunting Persen',
        trendline='ols',
        title='Korelasi Jumlah Puskesmas vs Prevalensi Stunting',
        hover_data=['Kecamatan']
    )
    st.plotly_chart(fig_puskesmas, use_container_width=True)

with col2:
    # Korelasi Rumah Sakit vs Prevalensi
    fig_rs = px.scatter(
        filtered_df,
        x='Jumlah Rumah Sakit',
        y='Prevalensi Stunting Persen',
        trendline='ols',
        title='Korelasi Jumlah Rumah Sakit vs Prevalensi Stunting',
        hover_data=['Kecamatan']
    )
    st.plotly_chart(fig_rs, use_container_width=True)

# Analisis komprehensif fasilitas kesehatan
st.subheader("📈 Analisis Komprehensif Fasilitas Kesehatan")

fasilitas_cols = ['Jumlah Rumah Sakit', 'Jumlah Puskesmas', 'Jumlah Puskesmas Pembantu', 
                 'Jumlah Klinik', 'Jumlah Pondak Bersalin Desa (Polindes)', 'Pos Kesehatan']

# Hitung total fasilitas per kecamatan
fasilitas_analysis = filtered_df.groupby('Kecamatan').agg({
    **{col: 'mean' for col in fasilitas_cols},
    'Prevalensi Stunting Persen': 'mean'
}).reset_index()

fasilitas_analysis['Total Fasilitas'] = fasilitas_analysis[fasilitas_cols].sum(axis=1)

col1, col2 = st.columns(2)

with col1:
    fig_fasilitas = px.scatter(
        fasilitas_analysis,
        x='Total Fasilitas',
        y='Prevalensi Stunting Persen',
        size='Total Fasilitas',
        hover_name='Kecamatan',
        title='Hubungan Total Fasilitas Kesehatan vs Prevalensi Stunting',
        trendline='ols'
    )
    st.plotly_chart(fig_fasilitas, use_container_width=True)

with col2:
    # Tabel ranking fasilitas kesehatan
    st.subheader("🏆 Top 10 Kecamatan - Fasilitas Kesehatan")
    
    ranking_fasilitas = fasilitas_analysis.sort_values('Total Fasilitas', ascending=False)[
        ['Kecamatan', 'Total Fasilitas', 'Prevalensi Stunting Persen']
    ].head(10)
    
    st.dataframe(ranking_fasilitas, use_container_width=True)

st.markdown("---")

# =================== KORELASI & DISTRIBUSI ===================
st.header("📊 Analisis Korelasi & Distribusi")

# Matrix korelasi
st.subheader("🔗 Matrix Korelasi")

correlation_cols = ['Pendek', 'Sangat Pendek', 'Stunting', 'Jumlah Yang Diukur', 
                   'Prevalensi Stunting Persen', 'Jumlah Rumah Sakit', 'Jumlah Puskesmas']

corr_matrix = filtered_df[correlation_cols].corr()

fig_corr = px.imshow(
    corr_matrix,
    title="Matrix Korelasi Variabel Utama",
    color_continuous_scale="RdBu",
    aspect="auto"
)
fig_corr.update_layout(height=600)
st.plotly_chart(fig_corr, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    # Distribusi prevalensi stunting
    fig_hist = px.histogram(
        filtered_df,
        x='Prevalensi Stunting Persen',
        nbins=30,
        title='Distribusi Prevalensi Stunting',
        marginal='box'
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    # Box plot prevalensi per tahun
    fig_box = px.box(
        filtered_df,
        x='Tahun',
        y='Prevalensi Stunting Persen',
        title='Distribusi Prevalensi Stunting per Tahun'
    )
    st.plotly_chart(fig_box, use_container_width=True)

# Analisis outlier
st.subheader("🎯 Identifikasi Outlier")

Q1 = filtered_df['Prevalensi Stunting Persen'].quantile(0.25)
Q3 = filtered_df['Prevalensi Stunting Persen'].quantile(0.75)
IQR = Q3 - Q1

outlier_threshold_high = Q3 + 1.5 * IQR
outlier_threshold_low = Q1 - 1.5 * IQR

outliers = filtered_df[
    (filtered_df['Prevalensi Stunting Persen'] > outlier_threshold_high) |
    (filtered_df['Prevalensi Stunting Persen'] < outlier_threshold_low)
]

if not outliers.empty:
    st.write(f"Ditemukan {len(outliers)} data outlier:")
    st.dataframe(
        outliers[['Kecamatan', 'Unit Kerja (Puskesmas)', 'Tahun', 'Bulan', 'Prevalensi Stunting Persen']],
        use_container_width=True
    )
else:
    st.write("Tidak ditemukan outlier signifikan dalam data.")

st.markdown("---")

# =================== REKOMENDASI ===================
st.header("🎯 Rekomendasi dan Insights")

# Insights utama
st.subheader("💡 Key Insights")

# Analisis tren
yearly_trend = filtered_df.groupby('Tahun')['Prevalensi Stunting Persen'].mean()
if len(yearly_trend) > 1:
    trend_direction = "menurun" if yearly_trend.iloc[-1] < yearly_trend.iloc[0] else "meningkat"
    trend_percentage = abs((yearly_trend.iloc[-1] - yearly_trend.iloc[0]) / yearly_trend.iloc[0] * 100)
else:
    trend_direction = "stabil"
    trend_percentage = 0

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    **Tren Prevalensi Stunting:**
    - Prevalensi stunting {trend_direction} {trend_percentage:.1f}%
    - Rata-rata prevalensi: {filtered_df['Prevalensi Stunting Persen'].mean():.2f}%
    - Kecamatan dengan prevalensi tertinggi: {filtered_df.loc[filtered_df['Prevalensi Stunting Persen'].idxmax(), 'Kecamatan']}
    """)

with col2:
    kecamatan_terbaik = filtered_df.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().idxmin()
    prevalensi_terbaik = filtered_df.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().min()
    
    st.success(f"""
    **Kecamatan dengan Performa Terbaik:**
    - {kecamatan_terbaik}
    - Prevalensi rata-rata: {prevalensi_terbaik:.2f}%
    - Dapat dijadikan model best practice
    """)

# Rekomendasi berdasarkan analisis
st.subheader("📋 Rekomendasi Strategis")

# Identifikasi kecamatan prioritas
priority_kecamatan = filtered_df.groupby('Kecamatan').agg({
    'Prevalensi Stunting Persen': 'mean',
    'Stunting': 'sum',
    'Jumlah Yang Diukur': 'sum'
}).reset_index()

priority_kecamatan['Priority_Score'] = (
    priority_kecamatan['Prevalensi Stunting Persen'] * 0.5 +
    (priority_kecamatan['Stunting'] / priority_kecamatan['Stunting'].max() * 100) * 0.3 +
    (priority_kecamatan['Jumlah Yang Diukur'] / priority_kecamatan['Jumlah Yang Diukur'].max() * 100) * 0.2
)

top_priority = priority_kecamatan.nlargest(5, 'Priority_Score')

st.warning("**🚨 Kecamatan Prioritas Tinggi (Perlu Intervensi Segera):**")
for idx, row in top_priority.iterrows():
    st.write(f"• **{row['Kecamatan']}** - Prevalensi: {row['Prevalensi Stunting Persen']:.2f}%, Total Kasus: {row['Stunting']}")

# Rekomendasi spesifik
st.subheader("🎯 Rekomendasi Aksi")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📍 Intervensi Geografis**")
    st.write(f"• Fokus intervensi pada {len(top_priority)} kecamatan prioritas tinggi")
    st.write("• Pelajari best practice dari kecamatan dengan prevalensi rendah")
    st.write("• Implementasi program khusus untuk daerah dengan tren meningkat")
    
    st.markdown("**🏥 Peningkatan Fasilitas**")
    st.write("• Tingkatkan rasio puskesmas per populasi di daerah prevalensi tinggi")
    st.write("• Optimalkan peran Polindes dan Pos Kesehatan untuk deteksi dini")
    st.write("• Perkuat koordinasi antar fasilitas kesehatan")

with col2:
    st.markdown("**📊 Monitoring & Evaluasi**")
    st.write("• Implementasi sistem monitoring real-time")
    st.write("• Evaluasi berkala program intervensi stunting")
    st.write("• Standardisasi metode pengukuran dan pelaporan")
    
    st.markdown("**🎯 Program Spesifik**")
    st.write("• Program edukasi gizi untuk ibu hamil dan balita")
    st.write("• Fortifikasi makanan di daerah prevalensi tinggi")
    st.write("• Pemberdayaan kader kesehatan masyarakat")

# Action Plan Template
st.subheader("📅 Template Rencana Aksi")

action_plan = pd.DataFrame({
    'Prioritas': ['Tinggi', 'Tinggi', 'Sedang', 'Sedang', 'Rendah'],
    'Aksi': [
        'Intervensi segera di 5 kecamatan prioritas',
        'Penambahan fasilitas kesehatan di daerah kurang terlayani',
        'Program edukasi gizi masyarakat',
        'Pelatihan kader kesehatan',
        'Evaluasi dan monitoring rutin'
    ],
    'Target Waktu': ['3 bulan', '6 bulan', '6 bulan', '3 bulan', 'Berkelanjutan'],
    'PIC': ['Dinas Kesehatan', 'Pemerintah Daerah', 'Puskesmas', 'Kader Kesehatan', 'Tim Monitoring']
})

st.dataframe(action_plan, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**📊 Dashboard Analisis Stunting** | Dibuat untuk membantu analisis dan pengambilan keputusan dalam penanganan stunting")
st.markdown("*Data dapat difilter menggunakan filter di bagian atas untuk analisis yang lebih spesifik*")