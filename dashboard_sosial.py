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
# MAPPING JENIS BENCANA
# ===========================
JENIS_BENCANA_MAPPING = {
    "Gempa_Bumi": "Gempa Bumi",
    "Tsunami": "Tsunami", 
    "Banjir": "Banjir",
    "Tanah_Longsor": "Tanah Longsor",
    "Letusan_Gunung_Api": "Letusan Gunung Api",
    "Kekeringan": "Kekeringan",
    "Gelombang_Ekstrem_dan_Abrasi": "Gelombang Ekstrem dan Abrasi",
    "Cuaca_Ekstrem_Angin_Puting_Beliung": "Cuaca Ekstrem Angin Puting Beliung",
    "Kebakaran_Hutan_dan_Lahan": "Kebakaran Hutan dan Lahan",
    "Kebakaran_Gedung_dan_Pemukiman": "Kebakaran Gedung dan Pemukiman",
    "Epidemi_dan_Wabah_Penyakit": "Epidemi dan Wabah Penyakit",
    "Gagal_Teknologi": "Gagal Teknologi",
    "Konflik_Sosial": "Konflik Sosial",
    "Angin_Kencang": "Angin Kencang",
    "Kebakaran": "Kebakaran",
    "Erupsi_Gunung_Api": "Erupsi Gunung Api",
    "Pohon_Tumbang": "Pohon Tumbang"
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
        
        if '.' in str_value and ',' not in str_value:
            parts = str_value.split('.')
            if len(parts) >= 2 and all(part.isdigit() for part in parts):
                if len(parts[0]) <= 3 and all(len(part) == 3 for part in parts[1:]):
                    clean_number = str_value.replace('.', '')
                    return int(clean_number)
        
        return int(float(str_value))
        
    except (ValueError, TypeError):
        return 0

def extract_rupiah_value(value):
    """Extract numeric value from Indonesian Rupiah format"""
    if pd.isna(value) or value == '':
        return 0
    
    str_val = str(value).strip()
    
    if str_val.lower() in ['rp0', '0', 'rp 0']:
        return 0
    
    str_val = str_val.replace('Rp', '').replace('rp', '').strip()
    
    try:
        if '.' in str_val and ',' not in str_val:
            parts = str_val.split('.')
            if len(parts) >= 2:
                if len(parts[0]) <= 3 and all(len(part) == 3 for part in parts[1:]) and all(part.isdigit() for part in parts):
                    clean_number = str_val.replace('.', '')
                    return int(clean_number)
        
        if ',' in str_val:
            str_val = str_val.replace(',', '.')
        
        return int(float(str_val))
        
    except (ValueError, TypeError):
        digits_only = ''.join(filter(str.isdigit, str_val))
        if digits_only:
            return int(digits_only)
        return 0

def clean_numeric_columns(df, exclude_columns=None):
    """Clean numeric columns but exclude specified columns"""
    if exclude_columns is None:
        exclude_columns = []
    
    df_clean = df.copy()
    numeric_patterns = ['jumlah', 'total', 'count', 'peserta', 'penerima', 'kasus', 'bencana']
    
    for col in df_clean.columns:
        if col in exclude_columns:
            continue
        
        if 'kerugian' in col.lower():
            continue
            
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
    """Load data from GitHub repository"""
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
    
    for filename in file_list:
        try:
            url = github_base_url + filename
            response = requests.get(url)
            
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.text))
                df.columns = df.columns.str.strip()
                
                if filename == "jenis_bencana.csv":
                    try:
                        df_clean = clean_numeric_columns(df, exclude_columns=['Jenis_Bencana'])
                        
                        if 'Jenis_Bencana' in df_clean.columns:
                            df_clean['Jenis_Bencana'] = df_clean['Jenis_Bencana'].astype(str)
                            df_clean['Jenis_Bencana_Nama'] = df_clean['Jenis_Bencana'].map(JENIS_BENCANA_MAPPING)
                            
                            mask = df_clean['Jenis_Bencana_Nama'].isna()
                            if mask.any():
                                df_clean.loc[mask, 'Jenis_Bencana_Nama'] = (
                                    df_clean.loc[mask, 'Jenis_Bencana']
                                    .str.replace('_', ' ')
                                    .str.title()
                                )
                        
                    except Exception as e:
                        df_clean = clean_numeric_columns(df, exclude_columns=['Jenis_Bencana'])
                
                elif filename == "bencana_alam.csv":
                    df_clean = clean_numeric_columns(df)
                    for col in df_clean.columns:
                        if 'kerugian' in col.lower():
                            df_clean[col + '_Numeric'] = df_clean[col].apply(extract_rupiah_value)
                    
                else:
                    df_clean = clean_numeric_columns(df)
                
                clean_name = filename.replace('.csv', '').replace('_', ' ').title()
                data[clean_name] = df_clean
                
        except Exception as e:
            continue
    
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
        if 'Jenis Bencana' in data:
            df = data['Jenis Bencana'].copy()
            
            tahun_col = None
            jumlah_col = None
            
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'tahun' in col_lower:
                    tahun_col = col
                elif 'jumlah' in col_lower and df[col].dtype in ['int64', 'float64']:
                    jumlah_col = col
            
            if tahun_col and "Semua Tahun" not in selected_years:
                df = df[df[tahun_col].isin(selected_years)]
            
            if jumlah_col:
                total = df[jumlah_col].sum()
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
        kpis = {
            'total_penerima_bantuan': 0,
            'total_bencana': 0,
            'kekerasan_anak': 0,
            'kekerasan_perempuan': 0,
            'peserta_kb': 0
        }
    
    return kpis

# ===========================
# CHART FUNCTIONS
# ===========================
def create_jenis_bencana_pie_chart(data, selected_years):
    """6. Jenis Bencana - Pie Chart"""
    try:
        if 'Jenis Bencana' not in data:
            return None
        
        df = data['Jenis Bencana'].copy()
        
        if 'Jenis_Bencana_Nama' in df.columns:
            jenis_col = 'Jenis_Bencana_Nama'
        else:
            if 'Jenis_Bencana' in df.columns:
                df['Jenis_Bencana_Display'] = df['Jenis_Bencana'].astype(str).str.replace('_', ' ').str.title()
                jenis_col = 'Jenis_Bencana_Display'
            else:
                return None
        
        jumlah_col = None
        for col in df.columns:
            if 'jumlah' in col.lower() and df[col].dtype in ['int64', 'float64']:
                jumlah_col = col
                break
        
        if not jumlah_col:
            return None
        
        tahun_col = None
        for col in df.columns:
            if 'tahun' in col.lower():
                tahun_col = col
                break
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df_filtered = df[df[tahun_col].isin(selected_years)]
        else:
            df_filtered = df
        
        if df_filtered.empty:
            return None
        
        chart_data = df_filtered.groupby(jenis_col)[jumlah_col].sum().reset_index()
        chart_data = chart_data[chart_data[jumlah_col] > 0]
        
        if chart_data.empty:
            return None
        
        fig = px.pie(
            chart_data,
            values=jumlah_col,
            names=jenis_col,
            title="Distribusi Jenis Bencana",
            color_discrete_sequence=[
                '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
                '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
            ]
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<br><extra></extra>'
        )
        
        fig.update_layout(height=400)
        return fig
        
    except Exception as e:
        return None

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
            elif 'kerugian' in col_lower and 'numeric' not in col_lower:
                kerugian_col = col
        
        if not all([kecamatan_col, tahun_col, kerugian_col]):
            return None
        
        if "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        df['Kerugian_Numeric'] = df[kerugian_col].apply(extract_rupiah_value)
        
        table_data = df.groupby([kecamatan_col, tahun_col])['Kerugian_Numeric'].sum().reset_index()
        table_data['Kerugian_Formatted'] = table_data['Kerugian_Numeric'].apply(
            lambda x: f"Rp {x:,.0f}" if x > 0 else "Rp 0"
        )
        
        table_data = table_data.sort_values('Kerugian_Numeric', ascending=False)
        
        return table_data[[kecamatan_col, tahun_col, 'Kerugian_Formatted']].rename(
            columns={'Kerugian_Formatted': 'Kerugian_Rupiah'}
        )
        
    except Exception as e:
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
        return None

def create_penerima_per_tahun_chart(data, selected_years):
    """10. Rata-rata dan Jumlah Penerima per Tahun - Combo Chart"""
    try:
        if 'Bantuan Sosial' not in data:
            return None
        
        df = data['Bantuan Sosial'].copy()
        
        tahun_col = None
        penerima_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'tahun' in col_lower:
                tahun_col = col
            elif 'penerima' in col_lower:
                penerima_col = col
        
        if not all([tahun_col, penerima_col]):
            return None
        
        if "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        # Group by year
        yearly_data = df.groupby(tahun_col)[penerima_col].agg(['sum', 'mean']).reset_index()
        yearly_data.columns = [tahun_col, 'Total_Penerima', 'Rata_rata_Penerima']
        
        fig = go.Figure()
        
        # Add bar chart for total
        fig.add_trace(go.Bar(
            x=yearly_data[tahun_col],
            y=yearly_data['Total_Penerima'],
            name='Total Penerima',
            marker_color='#3498db',
            yaxis='y'
        ))
        
        # Add line chart for average
        fig.add_trace(go.Scatter(
            x=yearly_data[tahun_col],
            y=yearly_data['Rata_rata_Penerima'],
            mode='lines+markers',
            name='Rata-rata Penerima',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Rata-rata dan Jumlah Penerima per Tahun',
            xaxis_title='Tahun',
            yaxis=dict(
                title='Total Penerima',
                side='left'
            ),
            yaxis2=dict(
                title='Rata-rata Penerima',
                side='right',
                overlaying='y'
            ),
            height=400,
            legend=dict(x=0, y=1)
        )
        
        return fig
        
    except Exception as e:
        return None

def create_bantuan_donut_chart(data, selected_years):
    """11. Jumlah Penerima Bantuan - Donut Chart"""
    try:
        if 'Bantuan Sosial' not in data:
            return None
        
        df = data['Bantuan Sosial'].copy()
        
        program_col = None
        penerima_col = None
        tahun_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'program' in col_lower and 'type' in col_lower:
                program_col = col
            elif 'penerima' in col_lower:
                penerima_col = col
            elif 'tahun' in col_lower:
                tahun_col = col
        
        if not all([program_col, penerima_col]):
            return None
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        chart_data = df.groupby(program_col)[penerima_col].sum().reset_index()
        
        fig = px.pie(
            chart_data,
            values=penerima_col,
            names=program_col,
            title="Jumlah Penerima Bantuan",
            hole=0.4,  # Makes it a donut chart
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<br>Persentase: %{percent}<br><extra></extra>'
        )
        
        fig.update_layout(height=400)
        return fig
        
    except Exception as e:
        return None

def create_kontrasepsi_chart(data, selected_years):
    """12. Jumlah Peserta per Jenis Kontrasepsi - Horizontal Bar Chart"""
    try:
        if 'Peserta Kb' not in data:
            return None
        
        df = data['Peserta Kb'].copy()
        
        kontrasepsi_col = None
        peserta_col = None
        tahun_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kontrasepsi' in col_lower:
                kontrasepsi_col = col
            elif 'peserta' in col_lower:
                peserta_col = col
            elif 'tahun' in col_lower:
                tahun_col = col
        
        if not all([kontrasepsi_col, peserta_col]):
            return None
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        chart_data = df.groupby(kontrasepsi_col)[peserta_col].sum().reset_index()
        chart_data = chart_data.sort_values(peserta_col, ascending=True)
        
        fig = px.bar(
            chart_data,
            x=peserta_col,
            y=kontrasepsi_col,
            orientation='h',
            title="Jumlah Peserta per Jenis Kontrasepsi",
            color=peserta_col,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title='Jumlah Peserta',
            yaxis_title='Jenis Kontrasepsi'
        )
        
        return fig
        
    except Exception as e:
        return None

def create_kb_performance_table(data):
    """13. Performa KB Kecamatan 2023-2024 - Table"""
    try:
        if 'Data Kb Performance' not in data:
            return None
        
        df = data['Data Kb Performance'].copy()
        
        # Select relevant columns
        display_cols = []
        for col in df.columns:
            col_lower = col.lower().strip()
            if any(word in col_lower for word in ['kecamatan', 'growth', 'performance', '2023']):
                display_cols.append(col)
        
        if len(display_cols) < 3:
            return df.head(20)  # Fallback to show first 20 rows
        
        table_data = df[display_cols].head(20)
        return table_data
        
    except Exception as e:
        return None

def create_kb_trend_chart(data, selected_years):
    """14. Tren Program KB - Stacked Bar Chart"""
    try:
        if 'Data Kb Tren Metode' not in data:
            return None
        
        df = data['Data Kb Tren Metode'].copy()
        
        tahun_col = None
        for col in df.columns:
            if 'tahun' in col.lower():
                tahun_col = col
                break
        
        if not tahun_col:
            return None
        
        if "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        # Get method columns (excluding Tahun and Total)
        method_cols = []
        for col in df.columns:
            if col != tahun_col and 'total' not in col.lower():
                if df[col].dtype in ['int64', 'float64']:
                    method_cols.append(col)
        
        if not method_cols:
            return None
        
        fig = go.Figure()
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
        
        for i, method in enumerate(method_cols):
            fig.add_trace(go.Bar(
                x=df[tahun_col],
                y=df[method],
                name=method,
                marker_color=colors[i % len(colors)]
            ))
        
        fig.update_layout(
            title='Tren Program KB',
            xaxis_title='Tahun',
            yaxis_title='Jumlah Peserta',
            barmode='stack',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
        
    except Exception as e:
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
        <p><em>📊 Dashboard Interaktif untuk Analisis Data Sosial</em></p>
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
            else:
                st.info("📊 Data Jenis Bencana tidak tersedia")
        
        with col2:
            chart = create_bencana_kecamatan_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("📊 Data Bencana per Kecamatan tidak tersedia")
        
        # Row 2: Kerugian Table & Kekerasan Gender
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Total Kerugian per Kecamatan")
            table = create_kerugian_table(data, selected_years)
            if table is not None and not table.empty:
                st.dataframe(table, use_container_width=True, height=400)
            else:
                st.info("📊 Data Kerugian tidak tersedia")
        
        with col2:
            chart = create_kekerasan_gender_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("📊 Data Kekerasan berdasarkan Gender tidak tersedia")
        
        # Row 3: Penerima per Tahun & Bantuan Donut
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_penerima_per_tahun_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("📊 Data Penerima per Tahun tidak tersedia")
        
        with col2:
            chart = create_bantuan_donut_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("📊 Data Bantuan tidak tersedia")
        
        # Row 4: Kontrasepsi & KB Performance Table
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_kontrasepsi_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.info("📊 Data Kontrasepsi tidak tersedia")
        
        with col2:
            st.markdown("#### 📈 Performa KB Kecamatan 2023-2024")
            table = create_kb_performance_table(data)
            if table is not None and not table.empty:
                st.dataframe(table, use_container_width=True, height=400)
            else:
                st.info("📊 Data Performa KB tidak tersedia")
        
        # Row 5: KB Trend Chart
        st.markdown("#### 📊 Tren Program KB")
        chart = create_kb_trend_chart(data, selected_years)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("📊 Data Tren KB tidak tersedia")
        
        # Footer
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        ---
        <div style='text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 10px;'>
            <p><strong>📊 Dashboard Sosial Kabupaten Malang</strong></p>
            <p><strong>🔗 Data Source:</strong> GitHub Repository | <strong>🕒 Generated:</strong> {current_time}</p>
            <p><strong>💡 Insight:</strong> Dashboard ini menyediakan visualisasi data sosial untuk mendukung pengambilan keputusan</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan dalam memuat dashboard: {str(e)}")

if __name__ == "__main__":
    main()