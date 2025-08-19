import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dashboard Pendidikan Kabupaten Malang",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        /* Style Judul */
        .title h1 {
            color: #2E86C1;
            text-align: center;
            font-weight: 900;
            font-size: 2.3em;
        }

        /* Separator halus */
        hr {
            margin: 1rem 0;
            border: none;
            border-top: 2px solid #ddd;
        }

        /* KPI Card */
        .stMetric {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        }

        /* Subjudul Section */
        .section-title {
            font-size: 1.3em;
            font-weight: 700;
            color: #34495E;
            margin-top: 20px;
        }

        /* Dataframe lebih clean */
        .dataframe tbody tr:nth-child(even) {
            background-color: #f6f6f6;
        }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        column_mapping = {
            'ID Kecamatan': 'id_kecamatan',
            'Kecamatan': 'kecamatan',
            'Tahun': 'tahun',
            'Jenjang': 'jenjang',
            'Jumlah Penduduk Usia Sekolah': 'populasi_usia_sekolah',
            'Jumlah Siswa Usia Sekolah': 'siswa_usia_sekolah',
            'Total Siswa': 'total_siswa',
            'APK': 'apk',
            'APM': 'apm',
            'Jumlah Guru S1/D4': 'guru_s1_d4',
            'Total Guru': 'total_guru',
            'Persentase Guru S1': 'persen_guru_s1',
            'Jumlah Sekolah Terakreditasi': 'sekolah_terakreditasi',
            'Jumlah Sekolah': 'total_sekolah',
            'Persentase Sekolah Terakreditasi': 'persen_sekolah_terakreditasi'
        }
        df = df.rename(columns=column_mapping)

        cols_to_convert = ['apk', 'apm', 'persen_guru_s1', 'persen_sekolah_terakreditasi']
        for col in cols_to_convert:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'No' in df.columns:
            df = df.drop(columns=['No'])
        df.dropna(subset=cols_to_convert, inplace=True)

        df['rasio_siswa_guru'] = (df['total_siswa'] / df['total_guru']).replace([pd.NA, float('inf')], 0)
        df['guru_non_s1'] = df['total_guru'] - df['guru_s1_d4']

        return df
    except FileNotFoundError:
        st.error(f"File not found at {path}. Please make sure the CSV file is in the correct directory.")
        return pd.DataFrame()

# Load Data
DATA_PATH = "data/pendidikan/pendidikan_paud_sd_smp.csv"
df = load_data(DATA_PATH)

if df.empty:
    st.stop()

# --- MAIN DASHBOARD ---
st.markdown('<div class="title"><h1>🎓 Dashboard Pendidikan Kabupaten Malang</h1></div>', unsafe_allow_html=True)

# --- FILTERS ---
st.markdown("<div class='section-title'>🔎 Filter Data</div>", unsafe_allow_html=True)
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    year_options = sorted(df['tahun'].unique(), reverse=True)
    selected_years = st.multiselect("📅 Pilih Tahun", options=year_options, default=[year_options[0]])

with col_filter2:
    level_options = df['jenjang'].unique()
    selected_levels = st.multiselect("🏫 Pilih Jenjang Pendidikan", options=level_options, default=level_options)

with col_filter3:
    district_options = sorted(df['kecamatan'].unique())
    selected_districts = st.multiselect("🌍 Pilih Kecamatan", options=district_options, default=district_options[:5])

st.markdown("---")

# --- FILTERING DATA LOGIC ---
df_filtered = df[
    (df['tahun'].isin(selected_years)) &
    (df['jenjang'].isin(selected_levels))
]
if selected_districts:
    df_filtered = df_filtered[df_filtered['kecamatan'].isin(selected_districts)]

# --- SUBTITLE INFO ---
district_str = "Semua Kecamatan" if len(selected_districts) == len(district_options) else ", ".join(selected_districts)
st.markdown(f"📊 Analisis untuk Tahun **{', '.join(map(str, selected_years))}** | Jenjang **{', '.join(selected_levels)}** | Kecamatan: **{district_str}**")

if df_filtered.empty:
    st.warning("⚠️ Tidak ada data yang tersedia untuk filter yang dipilih.")
else:
    # --- KPI METRICS ---
    st.markdown("<div class='section-title'>📌 Ringkasan Utama</div>", unsafe_allow_html=True)
    total_students = int(df_filtered['total_siswa'].sum())
    avg_apm = df_filtered['apm'].mean()
    avg_apk = df_filtered['apk'].mean()
    avg_teacher_qual = df_filtered['persen_guru_s1'].mean()
    avg_school_accred = df_filtered['persen_sekolah_terakreditasi'].mean()
    total_teachers = int(df_filtered['total_guru'].sum())
    student_teacher_ratio = total_students / total_teachers if total_teachers > 0 else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("👩‍🎓 Total Siswa", f"{total_students:,.0f}")
    col2.metric("📐 Rasio Siswa/Guru", f"{student_teacher_ratio:.1f}")
    col3.metric("📊 Rata-rata APM", f"{avg_apm:.2%}")
    col4.metric("📈 Rata-rata APK", f"{avg_apk:.2%}")
    col5.metric("🎓 Guru S1/D4", f"{avg_teacher_qual:.2%}")
    col6.metric("🏫 Sekolah Terakreditasi", f"{avg_school_accred:.2%}")

    st.markdown("---")

    # --- VISUALIZATIONS ---
    st.markdown("### Analisis Partisipasi dan Kualitas Pendidikan")
    col_viz1, col_viz2 = st.columns(2)

    with col_viz1:
        st.markdown(f"#### Perbandingan Angka Partisipasi Murni (APM) per Kecamatan")
        # Group by kecamatan and calculate mean APM for the selected years/levels
        df_chart = df_filtered.groupby('kecamatan')['apm'].mean().reset_index()
        df_chart = df_chart.sort_values('apm', ascending=False)
        fig_apm = px.bar(
            df_chart,
            x='kecamatan',
            y='apm',
            title=f'Rata-rata APM per Kecamatan',
            labels={'kecamatan': 'Kecamatan', 'apm': 'Rata-rata Angka Partisipasi Murni (APM)'},
            color='apm',
            color_continuous_scale=px.colors.sequential.Viridis,
            text_auto='.2%'
        )
        fig_apm.update_layout(xaxis_title=None, yaxis_tickformat=".2%")
        fig_apm.update_traces(textangle=0, textposition='outside')
        st.plotly_chart(fig_apm, use_container_width=True)

    with col_viz2:
        st.markdown(f"#### Kualitas Guru dan Sekolah per Kecamatan")
        # Group by kecamatan and calculate mean percentages
        df_quality_agg = df_filtered.groupby('kecamatan')[['persen_guru_s1', 'persen_sekolah_terakreditasi']].mean().reset_index()

        df_chart = df_quality_agg.melt(
            id_vars='kecamatan', 
            value_vars=['persen_guru_s1', 'persen_sekolah_terakreditasi'],
            var_name='Indikator',
            value_name='Persentase'
        )
        # Custom labels for the legend
        df_chart['Indikator'] = df_chart['Indikator'].map({
            'persen_guru_s1': 'Guru S1/D4',
            'persen_sekolah_terakreditasi': 'Sekolah Terakreditasi'
        })

        fig_quality = px.bar(
            df_chart,
            x='kecamatan',
            y='Persentase',
            color='Indikator',
            barmode='group',
            title=f'Rata-rata Kualitas Guru & Sekolah',
            labels={'kecamatan': 'Kecamatan', 'Persentase': 'Persentase'},
            color_discrete_map={
                'Guru S1/D4': '#1f77b4',
                'Sekolah Terakreditasi': '#ff7f0e'
            },
            text_auto='.1%'
        )
        fig_quality.update_layout(xaxis_title=None, yaxis_tickformat=".2%")
        st.plotly_chart(fig_quality, use_container_width=True)

    # --- NEW SECTION: CORRELATION AND COMPOSITION ---
    st.markdown("---")
    st.markdown("### Analisis Korelasi dan Komposisi")
    col_corr, col_comp = st.columns(2)

    with col_corr:
        st.markdown("#### Korelasi Antar Indikator")

        # Let user select indicators for correlation plot
        indicator_options = {
            'Angka Partisipasi Murni (APM)': 'apm',
            'Angka Partisipasi Kasar (APK)': 'apk',
            'Persentase Guru S1/D4': 'persen_guru_s1',
            'Persentase Sekolah Terakreditasi': 'persen_sekolah_terakreditasi',
            'Rasio Siswa per Guru': 'rasio_siswa_guru'
        }

        x_axis_label = st.selectbox("Pilih Indikator Sumbu X:", options=list(indicator_options.keys()), index=2)
        y_axis_label = st.selectbox("Pilih Indikator Sumbu Y:", options=list(indicator_options.keys()), index=0)

        x_axis_val = indicator_options[x_axis_label]
        y_axis_val = indicator_options[y_axis_label]

        fig_corr = px.scatter(
            df_filtered,
            x=x_axis_val,
            y=y_axis_val,
            trendline="ols",
            trendline_color_override="red",
            hover_name='kecamatan',
            title=f'Korelasi: {x_axis_label} vs. {y_axis_label}',
            labels={
                x_axis_val: x_axis_label,
                y_axis_val: y_axis_label
            }
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_comp:
        st.markdown("#### Komposisi Guru per Kecamatan")

        # Aggregate teacher counts by summing them up for selected years/levels
        df_teacher_agg = df_filtered.groupby('kecamatan')[['guru_s1_d4', 'guru_non_s1']].sum().reset_index()

        df_teacher_comp = df_teacher_agg.melt(
            id_vars='kecamatan',
            value_vars=['guru_s1_d4', 'guru_non_s1'], 
            var_name='Kualifikasi Guru',
            value_name='Jumlah'
        )
        df_teacher_comp['Kualifikasi Guru'] = df_teacher_comp['Kualifikasi Guru'].map({
            'guru_s1_d4': 'S1/D4',
            'guru_non_s1': 'Non S1/D4'
        })

        fig_teacher_comp = px.bar(
            df_teacher_comp,
            x='kecamatan',
            y='Jumlah',
            color='Kualifikasi Guru',
            title=f'Total Komposisi Guru per Kecamatan',
            barmode='stack',
            labels={'kecamatan': 'Kecamatan', 'Jumlah': 'Jumlah Guru'},
            color_discrete_map={
                'S1/D4': '#2ca02c',
                'Non S1/D4': '#d62728'
            }
        )
        fig_teacher_comp.update_layout(xaxis_title=None)
        st.plotly_chart(fig_teacher_comp, use_container_width=True)

    # --- TIME SERIES ANALYSIS ---
    st.markdown("---")
    st.markdown("### Tren Indikator Pendidikan (Lintas Tahun)")

    # Filter data for the selected level and district for time series
    df_trend = df[df['jenjang'].isin(selected_levels)]

    # Buat judul dinamis untuk grafik tren
    if not selected_districts or not selected_levels:
        district_str_trend = "Tidak Ada Kecamatan Terpilih"
    elif len(selected_districts) == len(district_options):
        district_str_trend = "Semua Kecamatan"
    else:
        district_str_trend = ", ".join(selected_districts)

    if not selected_levels:
        level_str = "Tidak Ada Jenjang Terpilih"
    elif len(selected_levels) == len(level_options):
        level_str = "Semua Jenjang"
    else:
        level_str = ", ".join(selected_levels)

    title_trend = f'Tren Indikator untuk Jenjang {level_str} ({district_str_trend})'

    if selected_districts:
        df_trend = df_trend[df_trend['kecamatan'].isin(selected_districts)]

    # Group by year and calculate the mean for the selected scope
    trend_data = df_trend.groupby('tahun')[['apm', 'apk', 'persen_guru_s1', 'persen_sekolah_terakreditasi']].mean().reset_index()

    fig_trend = px.line(
        trend_data,
        x='tahun',
        y=['apm', 'apk', 'persen_guru_s1', 'persen_sekolah_terakreditasi'],
        title=title_trend,
        markers=True,
        labels={'tahun': 'Tahun', 'value': 'Nilai Indikator', 'variable': 'Indikator'}
    )
    fig_trend.update_layout(yaxis_tickformat=".2%")
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- DATA TABLE ---
    with st.expander("Lihat Data Lengkap (Hasil Filter)"):
        display_df = df_filtered.copy()
        # Format columns for better readability
        st.dataframe(display_df.style.format({
            "apk": "{:.2%}",
            "apm": "{:.2%}",
            "rasio_siswa_guru": "{:.1f}",
            "persen_guru_s1": "{:.2%}",
            "persen_sekolah_terakreditasi": "{:.2%}"
        }))
