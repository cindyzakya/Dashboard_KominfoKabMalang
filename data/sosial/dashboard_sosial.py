import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests
from io import StringIO
import re

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Sosial Kabupaten Malang",
    page_icon="📊",
    layout="wide"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .filter-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #2E86AB;
        margin: 20px 0;
    }
    
    .section-header {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
        margin: 20px 0;
    }
    
    .accurate-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# MAPPING JENIS BENCANA (SOLUTION!)
# ===========================
JENIS_BENCANA_MAPPING = {
    1: "Banjir",
    2: "Gempa Bumi", 
    3: "Tanah Longsor",
    4: "Banjir",
    5: "Tsunami",
    6: "Letusan Gunung Api",
    7: "Kekeringan",
    8: "Gelombang Ekstrem dan Abrasi",
    9: "Cuaca Ekstrem Angin Puting Beliung",
    10: "Kebakaran Hutan dan Lahan",
    11: "Kebakaran Gedung dan Pemukiman",
    12: "Epidemi dan Wabah Penyakit",
    13: "Gagal Teknologi"
}

# ===========================
# UTILITY FUNCTIONS
# ===========================
def convert_indonesian_number(value):
    """Convert Indonesian number format to integer"""
    if pd.isna(value) or value == '':
        return 0
    
    str_value = str(value).strip()
    
    try:
        if str_value.isdigit():
            return int(str_value)
        
        # Handle Indonesian format with dots as thousands separator
        if '.' in str_value and ',' not in str_value:
            parts = str_value.split('.')
            if len(parts) >= 2 and all(part.isdigit() for part in parts):
                if len(parts[0]) <= 3 and all(len(part) == 3 for part in parts[1:]):
                    clean_number = str_value.replace('.', '')
                    return int(clean_number)
        
        return int(float(str_value))
        
    except (ValueError, TypeError):
        return 0

def clean_numeric_columns(df):
    """Clean numeric columns"""
    df_clean = df.copy()
    numeric_patterns = ['jumlah', 'total', 'count', 'peserta', 'penerima', 'kasus', 'bencana', 'kerugian']
    
    for col in df_clean.columns:
        col_lower = col.lower().strip()
        if any(pattern in col_lower for pattern in numeric_patterns):
            df_clean[col] = df_clean[col].apply(convert_indonesian_number)
        elif df_clean[col].dtype == 'object':
            sample_vals = df_clean[col].dropna().head(5)
            if len(sample_vals) > 0:
                numeric_count = 0
                for val in sample_vals:
                    str_val = str(val).strip()
                    if str_val.isdigit() or ('.' in str_val and len(str_val.replace('.', '').replace(' ', '')) > 0):
                        try:
                            convert_indonesian_number(val)
                            numeric_count += 1
                        except:
                            pass
                
                if numeric_count / len(sample_vals) > 0.6:
                    df_clean[col] = df_clean[col].apply(convert_indonesian_number)
    
    return df_clean

# ===========================
# DATA LOADING FROM GITHUB
# ===========================
@st.cache_data
def load_github_data():
    """Load data from GitHub repository with jenis bencana mapping"""
    github_base_url = "https://raw.githubusercontent.com/cindyzakya/Dashboard_KominfokabMalang/main/data/sosial/"
    
    file_list = [
        "bantuan_sosial.csv",
        "bencana_alam.csv",
        "bentuk_kekerasan_perempuan.csv",
        "data_kb_performance.csv",
        "data_kb_tren_metode.csv",
        "jenis_bencana.csv",
        "kekerasan_anak.csv",
        "master_kecamatan.csv",
        "master_tahun.csv",
        "peserta_kb.csv",
        "usia_kekerasan_perempuan.csv"
    ]
    
    data = {}
    loading_info = []
    
    for filename in file_list:
        try:
            url = github_base_url + filename
            response = requests.get(url)
            
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text))
                df.columns = df.columns.str.strip()
                
                # Special handling for jenis_bencana.csv
                if filename == "jenis_bencana.csv":
                    # Clean numeric columns first
                    df_clean = clean_numeric_columns(df)
                    
                    # Map jenis bencana codes to names
                    if 'Jenis_Bencana' in df_clean.columns:
                        # Convert codes to descriptive names
                        df_clean['Jenis_Bencana_Nama'] = df_clean['Jenis_Bencana'].map(JENIS_BENCANA_MAPPING)
                        
                        # If mapping fails, create generic names
                        df_clean['Jenis_Bencana_Nama'] = df_clean['Jenis_Bencana_Nama'].fillna(
                            'Jenis Bencana ' + df_clean['Jenis_Bencana'].astype(str)
                        )
                        
                        loading_info.append(f"🎯 JENIS BENCANA FIXED:")
                        loading_info.append(f"   ✅ Mapped {df_clean['Jenis_Bencana'].nunique()} jenis bencana codes to names")
                        loading_info.append(f"   📊 Shape: {df_clean.shape}")
                        loading_info.append(f"   📊 Columns: {list(df_clean.columns)}")
                        loading_info.append(f"   📊 Sample mapping:")
                        
                        sample_mapping = df_clean[['Jenis_Bencana', 'Jenis_Bencana_Nama']].drop_duplicates().head(5)
                        for _, row in sample_mapping.iterrows():
                            loading_info.append(f"      {row['Jenis_Bencana']} → {row['Jenis_Bencana_Nama']}")
                    
                else:
                    # Regular cleaning for other files
                    df_clean = clean_numeric_columns(df)
                    loading_info.append(f"✅ {filename}: {len(df_clean)} rows, {len(df_clean.columns)} cols")
                
                clean_name = filename.replace('.csv', '').replace('_', ' ').title()
                data[clean_name] = df_clean
                
            else:
                loading_info.append(f"❌ Failed to load {filename} (Status: {response.status_code})")
                
        except Exception as e:
            loading_info.append(f"❌ Error loading {filename}: {str(e)}")
    
    # Display loading info
    with st.sidebar:
        st.markdown("### 📊 Data Loading Status")
        for info in loading_info:
            if "🎯" in info or "📊" in info or "✅" in info:
                if "🎯" in info:
                    st.success(info)
                else:
                    st.write(info)
            elif info.startswith("❌"):
                st.error(info)
            else:
                st.write(info)
    
    return data

# ===========================
# KPI CALCULATION
# ===========================
def calculate_kpis(data, selected_years):
    """Calculate KPI values"""
    kpis = {}
    
    try:
        # 1. Total Penerima Bantuan
        if 'Bantuan Sosial' in data:
            df = data['Bantuan Sosial'].copy()
            
            tahun_col = None
            penerima_col = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'tahun' in col_lower:
                    tahun_col = col
                elif 'penerima' in col_lower:
                    penerima_col = col
            
            if tahun_col and "Semua Tahun" not in selected_years:
                df = df[df[tahun_col].isin(selected_years)]
            
            if penerima_col:
                total = df[penerima_col].sum()
            else:
                total = len(df)
            
            kpis['total_penerima_bantuan'] = int(total)
        
        # 2. Total Bencana
        if 'Bencana Alam' in data:
            df = data['Bencana Alam'].copy()
            
            tahun_col = None
            bencana_col = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'tahun' in col_lower:
                    tahun_col = col
                elif 'bencana' in col_lower and df[col].dtype in ['int64', 'float64']:
                    bencana_col = col
            
            if tahun_col and "Semua Tahun" not in selected_years:
                df = df[df[tahun_col].isin(selected_years)]
            
            if bencana_col:
                total = df[bencana_col].sum()
            else:
                total = len(df)
            
            kpis['total_bencana'] = int(total)
        
        # 3. Kekerasan Anak
        if 'Kekerasan Anak' in data:
            df = data['Kekerasan Anak'].copy()
            
            tahun_col = None
            kasus_col = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'tahun' in col_lower:
                    tahun_col = col
                elif 'kasus' in col_lower and df[col].dtype in ['int64', 'float64']:
                    kasus_col = col
            
            if tahun_col and "Semua Tahun" not in selected_years:
                df = df[df[tahun_col].isin(selected_years)]
            
            if kasus_col:
                total = df[kasus_col].sum()
            else:
                total = len(df)
            
            kpis['kekerasan_anak'] = int(total)
        
        # 4. Kekerasan Perempuan
        if 'Bentuk Kekerasan Perempuan' in data:
            df = data['Bentuk Kekerasan Perempuan'].copy()
            
            tahun_col = None
            kasus_col = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'tahun' in col_lower:
                    tahun_col = col
                elif 'kasus' in col_lower and df[col].dtype in ['int64', 'float64']:
                    kasus_col = col
            
            if tahun_col and "Semua Tahun" not in selected_years:
                df = df[df[tahun_col].isin(selected_years)]
            
            if kasus_col:
                total = df[kasus_col].sum()
            else:
                total = len(df)
            
            kpis['kekerasan_perempuan'] = int(total)
        
        # 5. Peserta KB
        if 'Peserta Kb' in data:
            df = data['Peserta Kb'].copy()
            
            tahun_col = None
            peserta_col = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'tahun' in col_lower:
                    tahun_col = col
                elif 'peserta' in col_lower and df[col].dtype in ['int64', 'float64']:
                    peserta_col = col
            
            if tahun_col and "Semua Tahun" not in selected_years:
                df = df[df[tahun_col].isin(selected_years)]
            
            if peserta_col:
                total = df[peserta_col].sum()
            else:
                total = len(df)
            
            kpis['peserta_kb'] = int(total)
            
    except Exception as e:
        st.error(f"Error calculating KPIs: {str(e)}")
        kpis = {
            'total_penerima_bantuan': 0,
            'total_bencana': 0,
            'kekerasan_anak': 0,
            'kekerasan_perempuan': 0,
            'peserta_kb': 0
        }
    
    return kpis

# ===========================
# JENIS BENCANA CHART (FIXED!)
# ===========================
def create_jenis_bencana_pie_chart(data, selected_years):
    """6. Jenis Bencana - Pie Chart (FIXED WITH MAPPING)"""
    try:
        if 'Jenis Bencana' not in data:
            st.error("❌ Dataset 'Jenis Bencana' tidak ditemukan")
            return None
        
        df = data['Jenis Bencana'].copy()
        
        # Debug info
        with st.sidebar:
            st.markdown("### 🔍 Jenis Bencana Debug")
            st.write(f"📊 Shape: {df.shape}")
            st.write(f"📊 Columns: {list(df.columns)}")
            st.write("📊 Sample data:")
            st.dataframe(df.head())
        
        # Use mapped names if available, otherwise use original
        if 'Jenis_Bencana_Nama' in df.columns:
            jenis_col = 'Jenis_Bencana_Nama'  # Use mapped names
            st.sidebar.write("✅ Using mapped jenis bencana names")
        else:
            # Fallback: convert codes to generic names
            if 'Jenis_Bencana' in df.columns:
                df['Jenis_Bencana_Display'] = 'Jenis Bencana ' + df['Jenis_Bencana'].astype(str)
                jenis_col = 'Jenis_Bencana_Display'
                st.sidebar.write("⚠️ Using generic jenis bencana names")
            else:
                st.error("❌ No suitable jenis bencana column found")
                return None
        
        # Find jumlah column
        jumlah_col = None
        for col in df.columns:
            if 'jumlah' in col.lower() and df[col].dtype in ['int64', 'float64']:
                jumlah_col = col
                break
        
        if not jumlah_col:
            st.error("❌ Jumlah column not found")
            return None
        
        st.sidebar.write(f"📈 Using columns: {jenis_col} (names), {jumlah_col} (values)")
        
        # Filter by year if needed
        tahun_col = None
        for col in df.columns:
            if 'tahun' in col.lower():
                tahun_col = col
                break
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df_filtered = df[df[tahun_col].isin(selected_years)]
            st.sidebar.write(f"📅 After year filter: {df_filtered.shape}")
        else:
            df_filtered = df
            st.sidebar.write(f"📅 No year filter: {df_filtered.shape}")
        
        if df_filtered.empty:
            st.warning("⚠️ No data after filtering")
            return None
        
        # Group by jenis bencana names and sum
        chart_data = df_filtered.groupby(jenis_col)[jumlah_col].sum().reset_index()
        chart_data = chart_data[chart_data[jumlah_col] > 0]  # Remove zeros
        
        st.sidebar.write(f"📈 Final chart data:")
        st.sidebar.dataframe(chart_data)
        
        if chart_data.empty:
            st.warning("⚠️ No data for chart")
            return None
        
        # Create pie chart with beautiful colors
        fig = px.pie(
            chart_data,
            values=jumlah_col,
            names=jenis_col,
            title="Jenis Bencana",
            color_discrete_sequence=[
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
                '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA',
                '#F1948A', '#AED6F1', '#A9DFBF', '#F9E79F'
            ]
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>' +
                         'Jumlah: %{value}<br>' +
                         'Persentase: %{percent}<br>' +
                         '<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            legend=dict(
                orientation="v", 
                yanchor="middle", 
                y=0.5, 
                xanchor="left", 
                x=1.05
            )
        )
        
        return fig
        
    except Exception as e:
        st.error(f"❌ Error creating jenis bencana chart: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

# ===========================
# OTHER CHART FUNCTIONS
# ===========================
def create_bencana_kecamatan_chart(data, selected_years):
    """7. Bencana per Kecamatan"""
    try:
        if 'Bencana Alam' not in data:
            return None
        
        df = data['Bencana Alam'].copy()
        
        kecamatan_col = None
        jumlah_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kecamatan' in col_lower:
                kecamatan_col = col
            elif any(word in col_lower for word in ['jumlah', 'bencana']) and df[col].dtype in ['int64', 'float64']:
                jumlah_col = col
        
        if not kecamatan_col:
            return None
        
        if jumlah_col:
            chart_data = df.groupby(kecamatan_col)[jumlah_col].sum().reset_index()
            value_col = jumlah_col
        else:
            chart_data = df[kecamatan_col].value_counts().reset_index()
            chart_data.columns = [kecamatan_col, 'Count']
            value_col = 'Count'
        
        chart_data = chart_data.sort_values(value_col, ascending=True)
        
        fig = px.bar(
            chart_data,
            x=value_col,
            y=kecamatan_col,
            orientation='h',
            title="Jumlah Bencana per Kecamatan",
            color=value_col,
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=600)
        return fig
        
    except Exception as e:
        st.error(f"Error creating bencana kecamatan chart: {str(e)}")
        return None

def create_kerugian_table(data, selected_years):
    """8. Kerugian Table"""
    try:
        if 'Bencana Alam' not in data:
            return None
        
        df = data['Bencana Alam'].copy()
        
        kecamatan_col = None
        tahun_col = None
        kerugian_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kecamatan' in col_lower:
                kecamatan_col = col
            elif 'tahun' in col_lower:
                tahun_col = col
            elif 'kerugian' in col_lower:
                kerugian_col = col
        
        if not all([kecamatan_col, tahun_col, kerugian_col]):
            return None
        
        if "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        table_data = df.groupby([kecamatan_col, tahun_col])[kerugian_col].sum().reset_index()
        table_data['Kerugian_Formatted'] = table_data[kerugian_col].apply(lambda x: f"Rp {x:,.0f}")
        
        return table_data[[kecamatan_col, tahun_col, 'Kerugian_Formatted']].rename(
            columns={'Kerugian_Formatted': 'Kerugian_Rupiah'}
        )
        
    except Exception as e:
        st.error(f"Error creating kerugian table: {str(e)}")
        return None

def create_kekerasan_gender_chart(data, selected_years):
    """9. Kekerasan Gender Chart"""
    try:
        if 'Kekerasan Anak' not in data:
            return None
        
        df = data['Kekerasan Anak'].copy()
        
        tahun_col = None
        gender_col = None
        kasus_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'tahun' in col_lower:
                tahun_col = col
            elif any(word in col_lower for word in ['gender', 'kelamin']):
                gender_col = col
            elif 'kasus' in col_lower and df[col].dtype in ['int64', 'float64']:
                kasus_col = col
        
        if not all([tahun_col, gender_col]):
            return None
        
        if "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        if kasus_col:
            chart_data = df.groupby([tahun_col, gender_col])[kasus_col].sum().reset_index()
            value_col = kasus_col
        else:
            chart_data = df.groupby([tahun_col, gender_col]).size().reset_index(name='Jumlah_Kasus')
            value_col = 'Jumlah_Kasus'
        
        fig = px.bar(
            chart_data,
            x=tahun_col,
            y=value_col,
            color=gender_col,
            barmode='group',
            title="Jumlah Kasus Berdasarkan Gender",
            color_discrete_map={
                'Laki-laki': '#3498db', 'Perempuan': '#e74c3c', 
                'L': '#3498db', 'P': '#e74c3c'
            }
        )
        fig.update_layout(height=400)
        return fig
        
    except Exception as e:
        st.error(f"Error creating kekerasan gender chart: {str(e)}")
        return None

# ===========================
# MAIN APPLICATION
# ===========================
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Dashboard Sosial Kabupaten Malang</h1>
        <h3>Sistem Monitoring Data Sosial 2020-2024</h3>
        <p><em>📊 Fixed Version - Jenis Bencana Mapping Applied</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Load data
        with st.spinner("📊 Loading data from GitHub..."):
            data = load_github_data()
        
        if not data:
            st.error("❌ Tidak ada data yang berhasil dimuat!")
            return
        
        # Get available years
        available_years = []
        for df in data.values():
            for col in df.columns:
                if 'tahun' in col.lower():
                    years = df[col].dropna().unique()
                    available_years.extend([int(y) for y in years if str(y).isdigit()])
        
        available_years = sorted(list(set(available_years))) if available_years else [2020, 2021, 2022, 2023, 2024]
        
        # Filter section
        st.markdown("""
        <div class="filter-container">
            <h3>🔍 Filter Data</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col_filter1, col_filter2 = st.columns([3, 1])
        
        with col_filter1:
            selected_years = st.multiselect(
                "📅 Pilih Tahun:",
                options=["Semua Tahun"] + available_years,
                default=["Semua Tahun"],
                help="Filter tahun untuk visualisasi data"
            )
            
            if "Semua Tahun" in selected_years and len(selected_years) > 1:
                selected_years = ["Semua Tahun"]
        
        with col_filter2:
            st.markdown("**Tahun Tersedia:**")
            if available_years:
                st.write(f"🗓️ {min(available_years)} - {max(available_years)}")
            else:
                st.write("🗓️ 2020 - 2024")
        
        # Calculate KPIs
        kpis = calculate_kpis(data, selected_years)
        
        # Display KPIs
        st.markdown("---")
        st.markdown("### 📊 Key Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            value = int(kpis.get('total_penerima_bantuan', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👥 Total Penerima Bantuan</h4>
                <h2>{value:,}</h2>
                <p>✅ {value} Orang</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            value = int(kpis.get('total_bencana', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>🌊 Total Bencana</h4>
                <h2>{value:,}</h2>
                <p>✅ {value} Kejadian</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            value = int(kpis.get('kekerasan_anak', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👶 Kekerasan Anak</h4>
                <h2>{value:,}</h2>
                <p>✅ {value} Kasus</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            value = int(kpis.get('kekerasan_perempuan', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👩 Kekerasan Perempuan</h4>
                <h2>{value:,}</h2>
                <p>✅ {value} Kasus</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            value = int(kpis.get('peserta_kb', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👶 Peserta KB</h4>
                <h2>{value:,}</h2>
                <p>✅ {value} Orang</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts section
        st.markdown("---")
        st.markdown("""
        <div class="section-header">
            <h2>📊 Data Visualizations</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Row 1: Jenis Bencana & Bencana per Kecamatan
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_jenis_bencana_pie_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.success("✅ Jenis Bencana Chart - FIXED!")
            else:
                st.error("❌ Jenis Bencana Chart gagal")
        
        with col2:
            chart = create_bencana_kecamatan_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.success("✅ Bencana per Kecamatan Chart")
            else:
                st.error("❌ Bencana per Kecamatan Chart gagal")
        
        # Row 2: Kerugian Table & Kekerasan Gender
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Total Kerugian per Kecamatan")
            table = create_kerugian_table(data, selected_years)
            if table is not None:
                st.dataframe(table, use_container_width=True, height=400)
                st.success("✅ Kerugian Table")
            else:
                st.error("❌ Kerugian Table gagal")
        
        with col2:
            chart = create_kekerasan_gender_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                st.success("✅ Kekerasan Gender Chart")
            else:
                st.error("❌ Kekerasan Gender Chart gagal")
        
        # Show mapping info
        st.markdown("---")
        st.markdown("### 🎯 Jenis Bencana Mapping Applied")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔢 Kode → Nama Mapping:**")
            for code, name in JENIS_BENCANA_MAPPING.items():
                st.write(f"{code} → {name}")
        
        with col2:
            if 'Jenis Bencana' in data:
                st.markdown("**📊 Data setelah mapping:**")
                if 'Jenis_Bencana_Nama' in data['Jenis Bencana'].columns:
                    mapping_sample = data['Jenis Bencana'][['Jenis_Bencana', 'Jenis_Bencana_Nama']].drop_duplicates().head(8)
                    st.dataframe(mapping_sample)
                else:
                    st.write("Mapping column not found")
        
        # Footer
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        ---
        <div style='text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 10px;'>
            <p><strong>📊 Dashboard Sosial Kabupaten Malang</strong></p>
            <p><strong>🔗 Data Source:</strong> GitHub Repository | <strong>🕒 Generated:</strong> {current_time}</p>
            <p><strong>✅ FIXED:</strong> Jenis Bencana codes mapped to descriptive names!</p>
            <p><strong>🎯 Solution:</strong> Integer codes (2,3,4,5...) → String names (Gempa Bumi, Tanah Longsor...)</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()