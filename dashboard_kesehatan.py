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

# =================== SIDEBAR FILTERS ===================
with st.sidebar:
    st.header("🔍 Filter Data")
    
    # Filter Tahun
    st.subheader("📅 Tahun")
    semua_tahun = st.checkbox("Pilih Semua Tahun", value=True)
    
    if semua_tahun:
        selected_year = sorted(df['Tahun'].unique())
        st.info(f"Terpilih: {len(selected_year)} tahun")
    else:
        selected_year = st.multiselect(
            "Pilih Tahun:",
            options=sorted(df['Tahun'].unique()),
            default=sorted(df['Tahun'].unique())
        )
    
    # Filter Kecamatan
    st.subheader("🏘️ Kecamatan")
    semua_kecamatan = st.checkbox("Pilih Semua Kecamatan", value=False)
    
    if semua_kecamatan:
        selected_kecamatan = sorted(df['Kecamatan'].unique())
        st.info(f"Terpilih: {len(selected_kecamatan)} kecamatan")
    else:
        selected_kecamatan = st.multiselect(
            "Pilih Kecamatan:",
            options=sorted(df['Kecamatan'].unique()),
            default=sorted(df['Kecamatan'].unique())[:10],
            help="Pilih maksimal 20 kecamatan untuk performa terbaik"
        )
    

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
    
    # Limit kecamatan jika terlalu banyak
    if len(selected_kecamatan) > 25:
        st.warning(f"⚠️ Menampilkan 25 kecamatan dengan prevalensi tertinggi dari {len(selected_kecamatan)} kecamatan terpilih untuk performa optimal")
        top_kecamatan = yearly_kec_trend.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().sort_values(ascending=False).head(25).index
        yearly_kec_trend = yearly_kec_trend[yearly_kec_trend['Kecamatan'].isin(top_kecamatan)]
    
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
    
    # Limit kecamatan untuk performa
    if len(selected_kecamatan) > 20:
        st.warning(f"⚠️ Menampilkan 20 kecamatan dengan prevalensi tertinggi dari {len(selected_kecamatan)} kecamatan terpilih untuk performa optimal")
        top_kecamatan = period_kec_trend.groupby('Kecamatan')['Prevalensi Stunting Persen'].mean().sort_values(ascending=False).head(20).index
        period_kec_trend = period_kec_trend[period_kec_trend['Kecamatan'].isin(top_kecamatan)]
    
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

col1, col2 = st.columns(2)

with col1:
    # Kecamatan dengan prevalensi tertinggi
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
        color_continuous_scale='Reds',
        text='Prevalensi Stunting Persen'
    )
    fig_top.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_top.update_layout(height=500)
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    bottom_kecamatan = filtered_df.groupby('Kecamatan').agg({
        'Prevalensi Stunting Persen': 'mean',
        'Stunting': 'sum'
    }).reset_index().sort_values('Prevalensi Stunting Persen', ascending=True).head(10)
    
    fig_bottom = px.bar(
        bottom_kecamatan,
        x='Prevalensi Stunting Persen',
        y='Kecamatan',
        title='Top 10 Kecamatan dengan Prevalensi Stunting Terendah',
        orientation='h',
        color='Prevalensi Stunting Persen',
        color_continuous_scale='Blues',
        text='Prevalensi Stunting Persen'
    )
    fig_bottom.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bottom.update_layout(height=500)
    st.plotly_chart(fig_bottom, use_container_width=True)

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

col1, col2 = st.columns(2)

with col1:
    facility_cols = {
        'Jumlah Rumah Sakit': 'Rumah Sakit',
        'Jumlah Puskesmas': 'Puskesmas',
        'Jumlah Puskesmas Pembantu': 'Puskesmas Pembantu',
        'Jumlah Klinik': 'Klinik',
        'Pos Kesehatan': 'Pos Kesehatan'
    }
    comparison_data = []

    analysis_df = filtered_df.groupby(['Kecamatan', 'Tahun']).agg({
        'Prevalensi Stunting Persen': 'mean',
        **{col: 'mean' for col in facility_cols.keys()}
    }).reset_index()

    if not analysis_df.empty and len(analysis_df) > 1:
        for col, name in facility_cols.items():
            if analysis_df[col].nunique() <= 1:
                continue
            
            threshold = analysis_df[col].median()
            if threshold == 0:
                threshold = analysis_df[col].mean()
            if threshold == 0:
                continue

            analysis_df['Kategori Faskes'] = np.where(analysis_df[col] > threshold, 'Jumlah Faskes Tinggi', 'Jumlah Faskes Rendah')
            avg_prevalence = analysis_df.groupby('Kategori Faskes')['Prevalensi Stunting Persen'].mean().reset_index()
            avg_prevalence['Tipe Faskes'] = name
            comparison_data.append(avg_prevalence)

        if comparison_data:
            final_comparison_df = pd.concat(comparison_data, ignore_index=True)
            fig_faskes_comp = px.bar(
                final_comparison_df,
                x='Tipe Faskes',
                y='Prevalensi Stunting Persen',
                color='Kategori Faskes',
                barmode='group',
                title='Prevalensi Stunting: Faskes Banyak vs Sedikit',
                labels={'Prevalensi Stunting Persen': 'Prevalensi (%)', 'Tipe Faskes': 'Tipe Fasilitas', 'Kategori Faskes': 'Kategori'},
                color_discrete_map={'Jumlah Faskes Rendah': '#FF6B6B', 'Jumlah Faskes Tinggi': '#4ECDC4'},
                text='Prevalensi Stunting Persen'
            )
            fig_faskes_comp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_faskes_comp.update_layout(height=500)
            st.plotly_chart(fig_faskes_comp, use_container_width=True)

            # --- ANALISIS ANOMALI ---
            anomalies_df = final_comparison_df.pivot(index='Tipe Faskes', columns='Kategori Faskes', values='Prevalensi Stunting Persen').reset_index()
            if 'Jumlah Faskes Tinggi' in anomalies_df.columns and 'Jumlah Faskes Rendah' in anomalies_df.columns:
                anomalies_df = anomalies_df.dropna()
                anomalous_faskes = anomalies_df[anomalies_df['Jumlah Faskes Tinggi'] > anomalies_df['Jumlah Faskes Rendah']]

                # if not anomalous_faskes.empty:
                #     with st.expander("⚠️ Klik untuk Melihat Detail Kecamatan dengan Anomali"):
                #         st.warning("""
                #         **Anomali Terdeteksi!** Ditemukan kasus dimana daerah dengan jumlah fasilitas kesehatan lebih banyak 
                #         justru memiliki rata-rata prevalensi stunting yang lebih tinggi. Ini bisa menunjukkan:
                #         - Konsentrasi fasilitas kesehatan di daerah dengan masalah stunting yang lebih besar
                #         - Kebutuhan intervensi yang lebih komprehensif selain penambahan fasilitas
                #         """)
                        
                #         reverse_facility_cols = {v: k for k, v in facility_cols.items()}

                #         for faskes_name in anomalous_faskes['Tipe Faskes']:
                #             st.markdown(f"---")
                #             st.markdown(f"**Kecamatan Penyumbang Anomali untuk '{faskes_name}':**")
                            
                #             col_name = reverse_facility_cols.get(faskes_name)
                #             if not col_name: continue

                #             threshold = analysis_df[col_name].median()
                #             if threshold == 0: threshold = analysis_df[col_name].mean()

                #             anomalous_districts = analysis_df[analysis_df[col_name] > threshold].sort_values('Prevalensi Stunting Persen', ascending=False)

                #             for _, row in anomalous_districts.head(3).iterrows():
                #                 st.write(f"- **{row['Kecamatan']}**: Prevalensi {row['Prevalensi Stunting Persen']:.2f}% (dengan {int(row[col_name])} {faskes_name})")
        else:
            st.info("Data tidak cukup untuk menampilkan perbandingan fasilitas kesehatan.")
    else:
        st.info("Data tidak cukup untuk menampilkan perbandingan fasilitas kesehatan.")

with col2:
    # Komposisi Stunting (Pendek vs Sangat Pendek)
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


# # =================== HIGHLIGHT KECAMATAN PRIORITAS ===================
# st.header("🚨 Highlight Kecamatan Prioritas")

# # Menambahkan sub-judul dinamis untuk konfirmasi bahwa filter diterapkan
# kecamatan_info = f"{len(selected_kecamatan)} kecamatan terpilih"
# if semua_kecamatan:
#     kecamatan_info = "semua kecamatan"

# tahun_info = f"tahun {', '.join(map(str, selected_year))}"
# if semua_tahun:
#     tahun_info = "semua tahun"

# st.markdown(f"<i>Analisis prioritas ini dihitung berdasarkan data gabungan dari <b>{tahun_info}</b> untuk <b>{kecamatan_info}</b>.</i>", unsafe_allow_html=True)

# with st.expander("ℹ️ Klik untuk melihat metodologi perhitungan prioritas"):
#     st.markdown("""
#     - **Data Agregat**: Data dari tahun dan kecamatan yang Anda filter digabungkan untuk setiap kecamatan.
#         - `Prevalensi Stunting Persen` dihitung sebagai **rata-rata (mean)** dari semua periode yang difilter.
#         - `Jumlah Yang Diukur` dan `Stunting` dihitung sebagai **jumlah total (sum)** dari semua periode yang difilter.
#     - **Threshold Dinamis**: Kategori prioritas ditentukan oleh perbandingan dengan nilai-nilai berikut:
#         - **Prevalensi**: Dibandingkan dengan nilai tetap (e.g., > 20%).
#         - **Jumlah Diukur**: Dibandingkan dengan *persentil ke-75* dari **data yang sedang ditampilkan**. Artinya, ambang batas ini berubah tergantung filter Anda.
#         - **Jumlah Kasus Stunting**: Dibandingkan dengan *median* dari **data yang sedang ditampilkan**. Ambang batas ini juga dinamis.
#     - **Tujuan**: Pendekatan ini membantu mengidentifikasi kecamatan yang paling menonjol (baik atau buruk) *relatif terhadap kelompok yang sedang Anda analisis*.
#     """)

# priority_df = filtered_df.groupby('Kecamatan').agg({
#     'Prevalensi Stunting Persen': 'mean',
#     'Jumlah Yang Diukur': 'sum',
#     'Stunting': 'sum'
# }).reset_index()

# # Definisi yang lebih jelas untuk kategori prioritas
# threshold_diukur = priority_df['Jumlah Yang Diukur'].quantile(0.75)  # 75th percentile
# median_stunting = priority_df['Stunting'].median()

# def categorize_priority(row):
#     prevalensi = row['Prevalensi Stunting Persen']
#     jumlah_diukur = row['Jumlah Yang Diukur']
#     stunting = row['Stunting']
    
#     if prevalensi > 20 and jumlah_diukur > threshold_diukur:
#         return "🚨 Prioritas Tinggi"
#     elif prevalensi < 10 and stunting > median_stunting:
#         return "⚠️ Risiko Tersembunyi"
#     elif prevalensi > 15:
#         return "📍 Perlu Perhatian"
#     else:
#         return "✅ Kondisi Baik"

# priority_df['Kategori'] = priority_df.apply(categorize_priority, axis=1)

# # Penjelasan kategori
# st.info("""
# **Penjelasan Kategori:**
# - 🚨 **Prioritas Tinggi**: Prevalensi > 20% DAN jumlah anak yang diukur tinggi (perlu intervensi segera)
# - ⚠️ **Risiko Tersembunyi**: Prevalensi rendah (< 10%) TAPI jumlah kasus stunting tinggi (bisa jadi underreporting atau populasi besar)
# - 📍 **Perlu Perhatian**: Prevalensi > 15% (monitoring ketat diperlukan)
# - ✅ **Kondisi Baik**: Prevalensi rendah dengan kasus yang terkendali
# """)

# st.subheader("📌 Daftar Kecamatan Berdasarkan Kategori Prioritas")
# priority_table = priority_df[priority_df['Kategori'] != "✅ Kondisi Baik"].sort_values('Prevalensi Stunting Persen', ascending=False)

# if not priority_table.empty:
#     st.dataframe(
#         priority_table[['Kecamatan', 'Prevalensi Stunting Persen', 'Jumlah Yang Diukur', 'Stunting', 'Kategori']],
#         column_config={
#             'Prevalensi Stunting Persen': st.column_config.NumberColumn(
#                 'Prevalensi (%)',
#                 format='%.2f%%'
#             ),
#             'Jumlah Yang Diukur': st.column_config.NumberColumn(
#                 'Jumlah Diukur',
#                 format='%d'
#             ),
#             'Stunting': st.column_config.NumberColumn(
#                 'Kasus Stunting',
#                 format='%d'
#             )
#         }
#     )
# else:
#     st.success("Semua kecamatan dalam kondisi baik!")

# # =================== QUADRANT ANALYSIS ===================
# st.subheader("🗺️ Analisis Kuadran Prioritas")
# st.markdown("""
# Analisis kuadran ini memetakan kecamatan berdasarkan dua metrik utama: **Rata-rata Prevalensi Stunting** (sumbu x) dan **Total Anak yang Diukur** (sumbu y). Ukuran titik merepresentasikan **Total Kasus Stunting**.
# - **Kuadran Kanan Atas (Prioritas Tinggi)**: Prevalensi tinggi dan banyak anak diukur. Membutuhkan intervensi segera.
# - **Kuadran Kiri Atas (Risiko Tersembunyi)**: Prevalensi rendah, namun jumlah anak yang diukur banyak. Kasus stunting absolut bisa jadi tinggi.
# - **Kuadran Kanan Bawah (Perlu Perhatian)**: Prevalensi tinggi, namun jumlah anak yang diukur sedikit. Mungkin ada *under-reporting*.
# - **Kuadran Kiri Bawah (Kondisi Baik)**: Prevalensi rendah dan jumlah kasus terkendali.
# """)

# if not priority_df.empty:
#     # Thresholds for quadrant lines
#     threshold_prevalensi = 20  # Sesuai definisi "Prioritas Tinggi"
#     threshold_diukur = priority_df['Jumlah Yang Diukur'].quantile(0.75) # Sesuai definisi

#     fig_quadrant = px.scatter(
#         priority_df,
#         x="Prevalensi Stunting Persen",
#         y="Jumlah Yang Diukur",
#         color="Kategori",
#         size="Stunting",
#         hover_name="Kecamatan",
#         hover_data={
#             'Prevalensi Stunting Persen': ':.2f%',
#             'Jumlah Yang Diukur': ':,',
#             'Stunting': ':,'
#         },
#         color_discrete_map={
#             "🚨 Prioritas Tinggi": "#d62728", # red
#             "⚠️ Risiko Tersembunyi": "#ff7f0e", # orange
#             "📍 Perlu Perhatian": "#ffbb78", # light orange
#             "✅ Kondisi Baik": "#2ca02c" # green
#         },
#         size_max=60
#     )

#     # Add quadrant lines
#     fig_quadrant.add_vline(x=threshold_prevalensi, line_width=2, line_dash="dash", line_color="grey")
#     fig_quadrant.add_hline(y=threshold_diukur, line_width=2, line_dash="dash", line_color="grey")

#     fig_quadrant.update_layout(
#         title="Analisis Kuadran Prioritas Kecamatan",
#         xaxis_title="Rata-rata Prevalensi Stunting (%)",
#         yaxis_title="Total Anak Diukur",
#         legend_title="Kategori Prioritas",
#         height=600
#     )
    
#     st.plotly_chart(fig_quadrant, use_container_width=True)
# else:
#     st.info("Tidak ada data untuk ditampilkan di analisis kuadran.")

# # =================== RANKING PERUBAHAN ===================
# st.header("📉📈 Ranking Perubahan Prevalensi (2020 → 2024)")

# if filtered_df['Tahun'].nunique() > 1:
#     perubahan_df = filtered_df.groupby(['Kecamatan', 'Tahun'])['Prevalensi Stunting Persen'].mean().reset_index()
#     tahun_awal, tahun_akhir = perubahan_df['Tahun'].min(), perubahan_df['Tahun'].max()

#     perubahan_pivot = perubahan_df.pivot(index='Kecamatan', columns='Tahun', values='Prevalensi Stunting Persen').reset_index()
#     perubahan_pivot = perubahan_pivot.dropna()  # Hanya kecamatan yang ada di kedua tahun
    
#     if len(perubahan_pivot.columns) >= 3:  # Kecamatan + minimal 2 tahun
#         perubahan_pivot['Perubahan'] = perubahan_pivot[tahun_akhir] - perubahan_pivot[tahun_awal]
#         perubahan_pivot['Perubahan_Persen'] = (perubahan_pivot['Perubahan'] / perubahan_pivot[tahun_awal]) * 100

#         top_improve = perubahan_pivot.sort_values('Perubahan').head(10)  # penurunan terbesar
#         top_worsen = perubahan_pivot.sort_values('Perubahan', ascending=False).head(10)  # kenaikan terbesar

#         col1, col2 = st.columns(2)
#         with col1:
#             st.subheader(f"✅ Top 10 Perbaikan Terbesar ({tahun_awal} → {tahun_akhir})")
#             improve_display = top_improve[['Kecamatan', tahun_awal, tahun_akhir, 'Perubahan', 'Perubahan_Persen']].copy()
#             improve_display.columns = ['Kecamatan', f'{tahun_awal} (%)', f'{tahun_akhir} (%)', 'Selisih (%)', 'Perubahan (%)']
#             st.dataframe(improve_display, column_config={
#                 f'{tahun_awal} (%)': st.column_config.NumberColumn(format='%.2f'),
#                 f'{tahun_akhir} (%)': st.column_config.NumberColumn(format='%.2f'),
#                 'Selisih (%)': st.column_config.NumberColumn(format='%.2f'),
#                 'Perubahan (%)': st.column_config.NumberColumn(format='%.1f')
#             })
            
#         with col2:
#             st.subheader(f"❌ Top 10 Memburuk Terbesar ({tahun_awal} → {tahun_akhir})")
#             worsen_display = top_worsen[['Kecamatan', tahun_awal, tahun_akhir, 'Perubahan', 'Perubahan_Persen']].copy()
#             worsen_display.columns = ['Kecamatan', f'{tahun_awal} (%)', f'{tahun_akhir} (%)', 'Selisih (%)', 'Perubahan (%)']
#             st.dataframe(worsen_display, column_config={
#                 f'{tahun_awal} (%)': st.column_config.NumberColumn(format='%.2f'),
#                 f'{tahun_akhir} (%)': st.column_config.NumberColumn(format='%.2f'),
#                 'Selisih (%)': st.column_config.NumberColumn(format='%.2f'),
#                 'Perubahan (%)': st.column_config.NumberColumn(format='%.1f')
#             })
#     else:
#         st.info("Data tidak cukup untuk menghitung perubahan (perlu data di minimal 2 tahun untuk kecamatan yang sama).")
# else:
#     st.info("Data hanya 1 tahun, tidak bisa menghitung perubahan.")

