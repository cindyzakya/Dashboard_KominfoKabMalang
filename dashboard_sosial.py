import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import folium
from streamlit_folium import st_folium
import json
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Sosial Kabupaten Malang",
    page_icon="📊",
    layout="wide"
)

# CSS Styling (sama seperti sebelumnya)
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
    
    .section-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 30px 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        border: 2px solid #e0e6ed;
    }
    
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .section-header h2 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    .sidebar-filter {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .sidebar-filter h3 {
        color: white;
        margin-bottom: 15px;
    }
    
    .filter-section {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .year-chip {
        display: inline-block;
        background-color: #2c5aa0;
        color: white;
        padding: 5px 12px;
        margin: 3px;
        border-radius: 15px;
        font-size: 12px;
        cursor: pointer;
        border: 1px solid #4a90e2;
        position: relative;
    }
    
    .year-chip:hover {
        background-color: #1e4080;
    }
    
    .year-chip.selected {
        background-color: #4a90e2;
        border-color: #ffffff;
    }
    
    .chip-close {
        margin-left: 8px;
        font-weight: bold;
        cursor: pointer;
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
    
    .kpi-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        border: 1px solid #dee2e6;
    }
    
    /* Map Container */
    .map-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin: 30px 0;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        border: 2px solid #e0e6ed;
    }
    
    .map-header {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
    }
    
    .map-header h2 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .map-stats {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
        flex-wrap: wrap;
    }
    
    .map-stat-card {
        background: rgba(255,255,255,0.9);
        padding: 1rem;
        border-radius: 10px;
        color: #333;
        flex: 1;
        min-width: 200px;
        backdrop-filter: blur(5px);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .map-stat-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;
    }
    
    .map-stat-card p {
        margin: 0.25rem 0;
        color: #495057;
        font-size: 0.9rem;
    }
    
    /* Instructions - WARNA HITAM */
    .instructions {
        background: rgba(255,255,255,0.95);
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1.5rem;
        color: #2c3e50;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .instructions h4 {
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3c72;
    }
    
    .instructions ul {
        margin: 0;
        padding-left: 1.2rem;
    }
    
    .instructions li {
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        line-height: 1.4;
        color: #495057;
    }
    
    .stSelectbox > div > div > div > div {
        background-color: rgba(255, 255, 255, 0.9);
        color: #333;
    }
    
    .stMultiSelect > div > div > div > div {
        background-color: rgba(255, 255, 255, 0.9);
        color: #333;
    }
    
    .year-selection-area {
        background-color: rgba(0, 0, 0, 0.3);
        padding: 10px;
        border-radius: 8px;
        min-height: 50px;
        border: 1px dashed rgba(255, 255, 255, 0.3);
        margin-bottom: 15px;
    }
    
    .year-button {
        margin: 2px;
        padding: 8px 12px;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        font-size: 12px;
        min-width: 80px;
        text-align: center;
    }
    
    .year-button.available {
        background-color: #f0f2f6;
        color: #333;
        border: 1px solid #ddd;
    }
    
    .year-button.selected {
        background-color: #28a745;
        color: white;
        border: 1px solid #28a745;
    }
    
    /* Chart Explanation */
    .chart-explanation {
        background: linear-gradient(135deg, #e8f4fd 0%, #d6eaf8 100%);
        border-left: 4px solid #3498db;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-style: italic;
        color: #2c3e50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# MAPPING JENIS BENCANA (sama seperti sebelumnya)
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
# UTILITY FUNCTIONS (sama seperti sebelumnya)
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
# ANALYSIS FUNCTIONS - BARU!
# ===========================
def analyze_penerima_per_tahun(data, selected_years):
    """Analyze penerima bantuan per tahun data"""
    try:
        if 'Bantuan Sosial' not in data:
            return "Data bantuan sosial tidak tersedia untuk analisis."
        
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
            return "Kolom tahun atau penerima tidak ditemukan."
        
        if "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        yearly_data = df.groupby(tahun_col)[penerima_col].agg(['sum', 'mean']).reset_index()
        yearly_data.columns = [tahun_col, 'Total_Penerima', 'Rata_rata_Penerima']
        
        if yearly_data.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Find insights
        max_year = yearly_data.loc[yearly_data['Total_Penerima'].idxmax(), tahun_col]
        max_total = yearly_data['Total_Penerima'].max()
        min_year = yearly_data.loc[yearly_data['Total_Penerima'].idxmin(), tahun_col]
        min_total = yearly_data['Total_Penerima'].min()
        
        avg_highest_year = yearly_data.loc[yearly_data['Rata_rata_Penerima'].idxmax(), tahun_col]
        avg_highest = yearly_data['Rata_rata_Penerima'].max()
        
        total_all_years = yearly_data['Total_Penerima'].sum()
        
        insight = f"Tahun {max_year} adalah tahun dengan penerima bantuan terbanyak ({max_total:,.0f} orang), " \
                 f"sedangkan tahun {min_year} memiliki penerima paling sedikit ({min_total:,.0f} orang). " \
                 f"Rata-rata penerima per program tertinggi terjadi pada tahun {avg_highest_year} " \
                 f"dengan {avg_highest:,.0f} orang per program. " \
                 f"Total penerima bantuan dalam periode yang dipilih adalah {total_all_years:,.0f} orang."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

def analyze_bantuan_donut(data, selected_years):
    """Analyze bantuan distribution"""
    try:
        if 'Bantuan Sosial' not in data:
            return "Data bantuan sosial tidak tersedia untuk analisis."
        
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
            return "Kolom program atau penerima tidak ditemukan."
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        chart_data = df.groupby(program_col)[penerima_col].sum().reset_index()
        chart_data = chart_data.sort_values(penerima_col, ascending=False)
        
        if chart_data.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Find insights
        top_program = chart_data.iloc[0]
        total_penerima = chart_data[penerima_col].sum()
        percentage_top = (top_program[penerima_col] / total_penerima) * 100
        
        second_program = chart_data.iloc[1] if len(chart_data) > 1 else None
        
        insight = f"Program {top_program[program_col]} memiliki penerima terbanyak dengan {top_program[penerima_col]:,.0f} orang " \
                 f"({percentage_top:.1f}% dari total penerima)."
        
        if second_program is not None:
            percentage_second = (second_program[penerima_col] / total_penerima) * 100
            insight += f" Diikuti oleh program {second_program[program_col]} dengan {second_program[penerima_col]:,.0f} orang " \
                      f"({percentage_second:.1f}%)."
        
        insight += f" Total ada {len(chart_data)} jenis program bantuan dengan {total_penerima:,.0f} penerima."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

def analyze_jenis_bencana_pie(data, selected_years):
    """Analyze jenis bencana distribution"""
    try:
        if 'Jenis Bencana' not in data:
            return "Data jenis bencana tidak tersedia untuk analisis."
        
        df = data['Jenis Bencana'].copy()
        
        if 'Jenis_Bencana_Nama' in df.columns:
            jenis_col = 'Jenis_Bencana_Nama'
        else:
            if 'Jenis_Bencana' in df.columns:
                df['Jenis_Bencana_Display'] = df['Jenis_Bencana'].astype(str).str.replace('_', ' ').str.title()
                jenis_col = 'Jenis_Bencana_Display'
            else:
                return "Kolom jenis bencana tidak ditemukan."
        
        jumlah_col = None
        for col in df.columns:
            if 'jumlah' in col.lower() and df[col].dtype in ['int64', 'float64']:
                jumlah_col = col
                break
        
        if not jumlah_col:
            return "Kolom jumlah bencana tidak ditemukan."
        
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
            return "Tidak ada data untuk periode yang dipilih."
        
        chart_data = df_filtered.groupby(jenis_col)[jumlah_col].sum().reset_index()
        chart_data = chart_data[chart_data[jumlah_col] > 0].sort_values(jumlah_col, ascending=False)
        
        if chart_data.empty:
            return "Tidak ada data bencana untuk periode yang dipilih."
        
        # Find insights
        total_bencana = chart_data[jumlah_col].sum()
        top_bencana = chart_data.iloc[0]
        percentage_top = (top_bencana[jumlah_col] / total_bencana) * 100
        
        insight = f"{top_bencana[jenis_col]} adalah jenis bencana yang paling sering terjadi dengan {top_bencana[jumlah_col]:,.0f} kejadian " \
                 f"({percentage_top:.1f}% dari total bencana)."
        
        if len(chart_data) > 1:
            second_bencana = chart_data.iloc[1]
            percentage_second = (second_bencana[jumlah_col] / total_bencana) * 100
            insight += f" Diikuti oleh {second_bencana[jenis_col]} dengan {second_bencana[jumlah_col]:,.0f} kejadian " \
                      f"({percentage_second:.1f}%)."
        
        insight += f" Total tercatat {total_bencana:,.0f} kejadian bencana dari {len(chart_data)} jenis bencana yang berbeda."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

def analyze_bencana_kecamatan(data, selected_years):
    """Analyze bencana per kecamatan"""
    try:
        if 'Bencana Alam' not in data:
            return "Data bencana alam tidak tersedia untuk analisis."
        
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
            return "Kolom kecamatan tidak ditemukan."
        
        tahun_col = None
        for col in df.columns:
            if 'tahun' in col.lower():
                tahun_col = col
                break
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        if jumlah_col:
            chart_data = df.groupby(kecamatan_col)[jumlah_col].sum().reset_index()
            value_col = jumlah_col
        else:
            chart_data = df[kecamatan_col].value_counts().reset_index()
            chart_data.columns = [kecamatan_col, 'Count']
            value_col = 'Count'
        
        chart_data = chart_data.sort_values(value_col, ascending=False)
        
        if chart_data.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Find insights
        top_kecamatan = chart_data.iloc[0]
        total_bencana = chart_data[value_col].sum()
        avg_bencana = chart_data[value_col].mean()
        
        kecamatan_aman = chart_data[chart_data[value_col] == 0]
        kecamatan_rawan = chart_data[chart_data[value_col] >= avg_bencana]
        
        insight = f"Kecamatan {top_kecamatan[kecamatan_col]} adalah daerah paling rawan bencana dengan {top_kecamatan[value_col]:,.0f} kejadian bencana."
        
        if len(chart_data) > 1:
            second_kecamatan = chart_data.iloc[1]
            insight += f" Diikuti oleh Kecamatan {second_kecamatan[kecamatan_col]} dengan {second_kecamatan[value_col]:,.0f} kejadian."
        
        insight += f" Rata-rata kejadian bencana per kecamatan adalah {avg_bencana:.1f} kejadian. " \
                  f"Terdapat {len(kecamatan_rawan)} kecamatan yang memiliki tingkat bencana di atas rata-rata."
        
        if not kecamatan_aman.empty:
            insight += f" Ada {len(kecamatan_aman)} kecamatan yang tidak mengalami bencana dalam periode ini."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

def analyze_kekerasan_total_yearly(data, selected_years):
    """Analyze total kekerasan yearly trend"""
    try:
        if 'Kekerasan Anak' not in data or 'Bentuk Kekerasan Perempuan' not in data:
            return "Data kekerasan tidak lengkap untuk analisis."
        
        df_anak = data['Kekerasan Anak'].copy()
        df_perempuan = data['Bentuk Kekerasan Perempuan'].copy()
        
        if "Semua Tahun" not in selected_years:
            df_anak = df_anak[df_anak['Tahun'].isin(selected_years)]
            df_perempuan = df_perempuan[df_perempuan['Tahun'].isin(selected_years)]
        
        anak_yearly = df_anak.groupby('Tahun')['Jumlah_Kasus'].sum().reset_index()
        perempuan_yearly = df_perempuan.groupby('Tahun')['Jumlah_Kasus'].sum().reset_index()
        
        if anak_yearly.empty or perempuan_yearly.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Find insights
        total_anak = anak_yearly['Jumlah_Kasus'].sum()
        total_perempuan = perempuan_yearly['Jumlah_Kasus'].sum()
        
        max_anak_year = anak_yearly.loc[anak_yearly['Jumlah_Kasus'].idxmax(), 'Tahun']
        max_anak_cases = anak_yearly['Jumlah_Kasus'].max()
        
        max_perempuan_year = perempuan_yearly.loc[perempuan_yearly['Jumlah_Kasus'].idxmax(), 'Tahun']
        max_perempuan_cases = perempuan_yearly['Jumlah_Kasus'].max()
        
        # Trend analysis
        anak_trend = "naik" if anak_yearly.iloc[-1]['Jumlah_Kasus'] > anak_yearly.iloc[0]['Jumlah_Kasus'] else "turun"
        perempuan_trend = "naik" if perempuan_yearly.iloc[-1]['Jumlah_Kasus'] > perempuan_yearly.iloc[0]['Jumlah_Kasus'] else "turun"
        
        insight = f"Total kasus kekerasan anak adalah {total_anak:,.0f} kasus, dengan puncak tertinggi pada tahun {max_anak_year} " \
                 f"({max_anak_cases:,.0f} kasus). Total kasus kekerasan perempuan adalah {total_perempuan:,.0f} kasus, " \
                 f"dengan puncak tertinggi pada tahun {max_perempuan_year} ({max_perempuan_cases:,.0f} kasus). " \
                 f"Tren kekerasan anak menunjukkan kecenderungan {anak_trend}, " \
                 f"sedangkan kekerasan perempuan cenderung {perempuan_trend}."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"
    
# ===========================
# ANALYSIS FUNCTIONS UNTUK KEKERASAN - TAMBAHAN
# ===========================

def analyze_kekerasan_gender_comparison(data, selected_years):
    """Analyze kekerasan berdasarkan gender"""
    try:
        if 'Kekerasan Anak' not in data:
            return "Data kekerasan anak tidak tersedia untuk analisis."
        
        df = data['Kekerasan Anak'].copy()
        
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        gender_data = df.groupby(['Tahun', 'Gender'])['Jumlah_Kasus'].sum().reset_index()
        total_by_gender = df.groupby('Gender')['Jumlah_Kasus'].sum()
        
        if len(total_by_gender) >= 2:
            gender_tertinggi = total_by_gender.idxmax()
            kasus_tertinggi = total_by_gender.max()
            gender_terendah = total_by_gender.idxmin()
            kasus_terendah = total_by_gender.min()
            
            # Find year with highest cases for each gender
            tahun_puncak = {}
            for gender in total_by_gender.index:
                gender_yearly = df[df['Gender'] == gender].groupby('Tahun')['Jumlah_Kasus'].sum()
                tahun_puncak[gender] = gender_yearly.idxmax()
            
            insight = f"Korban kekerasan anak dengan gender {gender_tertinggi.lower()} lebih dominan dengan total {kasus_tertinggi:,.0f} kasus, " \
                     f"sedangkan korban {gender_terendah.lower()} sebanyak {kasus_terendah:,.0f} kasus. " \
                     f"Puncak kasus korban {gender_tertinggi.lower()} terjadi pada tahun {tahun_puncak[gender_tertinggi]}, " \
                     f"sementara korban {gender_terendah.lower()} tertinggi pada tahun {tahun_puncak[gender_terendah]}."
        else:
            total_kasus = df['Jumlah_Kasus'].sum()
            insight = f"Total kasus kekerasan anak adalah {total_kasus:,.0f} kasus dalam periode yang dipilih."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

def analyze_kekerasan_perempuan_yearly(data, selected_years):
    """Analyze kekerasan perempuan per tahun berdasarkan bentuk kekerasan"""
    try:
        if 'Bentuk Kekerasan Perempuan' not in data:
            return "Data kekerasan perempuan tidak tersedia untuk analisis."
        
        df = data['Bentuk Kekerasan Perempuan'].copy()
        
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Analisis bentuk kekerasan dominan
        bentuk_total = df.groupby('Bentuk_Kekerasan')['Jumlah_Kasus'].sum().sort_values(ascending=False)
        bentuk_tertinggi = bentuk_total.index[0]
        kasus_tertinggi = bentuk_total.iloc[0]
        
        # Analisis tahun dengan kasus tertinggi
        yearly_total = df.groupby('Tahun')['Jumlah_Kasus'].sum()
        tahun_tertinggi = yearly_total.idxmax()
        kasus_tahun_tertinggi = yearly_total.max()
        
        # Analisis tren
        if len(yearly_total) > 1:
            tren = "meningkat" if yearly_total.iloc[-1] > yearly_total.iloc[0] else "menurun"
        else:
            tren = "stabil"
        
        total_kasus = df['Jumlah_Kasus'].sum()
        persentase_dominan = (kasus_tertinggi / total_kasus) * 100
        
        insight = f"{bentuk_tertinggi} adalah bentuk kekerasan terhadap perempuan yang paling dominan dengan {kasus_tertinggi:,.0f} kasus " \
                 f"({persentase_dominan:.1f}% dari total kasus). Tahun {tahun_tertinggi} mencatat kasus tertinggi dengan {kasus_tahun_tertinggi:,.0f} kasus. " \
                 f"Secara keseluruhan, tren kekerasan perempuan menunjukkan kecenderungan {tren} dalam periode yang dianalisis. " \
                 f"Total kasus kekerasan perempuan adalah {total_kasus:,.0f} kasus."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

def analyze_kekerasan_perempuan_usia(data, selected_years):
    """Analyze kekerasan perempuan berdasarkan kelompok usia"""
    try:
        if 'Usia Kekerasan Perempuan' not in data:
            return "Data usia kekerasan perempuan tidak tersedia untuk analisis."
        
        df = data['Usia Kekerasan Perempuan'].copy()
        
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Analisis kelompok usia paling rentan
        usia_total = df.groupby('Kelompok_Usia')['Jumlah_Kasus'].sum().sort_values(ascending=False)
        usia_tertinggi = usia_total.index[0]
        kasus_tertinggi = usia_total.iloc[0]
        
        total_kasus = df['Jumlah_Kasus'].sum()
        persentase_tertinggi = (kasus_tertinggi / total_kasus) * 100
        
        # Analisis tahun dengan kasus tertinggi untuk kelompok usia dominan
        usia_yearly = df[df['Kelompok_Usia'] == usia_tertinggi].groupby('Tahun')['Jumlah_Kasus'].sum()
        tahun_puncak = usia_yearly.idxmax()
        
        insight = f"Kelompok usia {usia_tertinggi} adalah yang paling rentan mengalami kekerasan dengan {kasus_tertinggi:,.0f} kasus " \
                 f"({persentase_tertinggi:.1f}% dari total kasus). Puncak kasus pada kelompok usia ini terjadi pada tahun {tahun_puncak}. "
        
        if len(usia_total) > 1:
            usia_kedua = usia_total.index[1]
            kasus_kedua = usia_total.iloc[1]
            persentase_kedua = (kasus_kedua / total_kasus) * 100
            insight += f"Diikuti oleh kelompok usia {usia_kedua} dengan {kasus_kedua:,.0f} kasus ({persentase_kedua:.1f}%). "
        
        insight += f"Total kasus kekerasan perempuan berdasarkan kelompok usia adalah {total_kasus:,.0f} kasus."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

def analyze_kekerasan_anak_monthly_pattern(data, selected_years):
    """Analyze pola bulanan kekerasan anak"""
    try:
        if 'Kekerasan Anak' not in data:
            return "Data kekerasan anak tidak tersedia untuk analisis."
        
        df = data['Kekerasan Anak'].copy()
        
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Analisis bulan dengan kasus tertinggi
        monthly_total = df.groupby('Bulan')['Jumlah_Kasus'].sum().sort_values(ascending=False)
        bulan_tertinggi = monthly_total.index[0]
        kasus_tertinggi = monthly_total.iloc[0]
        
        bulan_terendah = monthly_total.index[-1]
        kasus_terendah = monthly_total.iloc[-1]
        
        # Analisis tahun dan bulan dengan kombinasi kasus tertinggi
        yearly_monthly = df.groupby(['Tahun', 'Bulan'])['Jumlah_Kasus'].sum()
        puncak_kombinasi = yearly_monthly.idxmax()
        kasus_puncak = yearly_monthly.max()
        
        total_kasus = df['Jumlah_Kasus'].sum()
        rata_rata_bulanan = monthly_total.mean()
        
        insight = f"Bulan {bulan_tertinggi} adalah periode dengan kasus kekerasan anak tertinggi ({kasus_tertinggi:,.0f} kasus), " \
                 f"sedangkan bulan {bulan_terendah} memiliki kasus terendah ({kasus_terendah:,.0f} kasus). " \
                 f"Puncak absolut terjadi pada {bulan_tertinggi} {puncak_kombinasi[0]} dengan {kasus_puncak:,.0f} kasus. " \
                 f"Rata-rata kasus per bulan adalah {rata_rata_bulanan:.1f} kasus. " \
                 f"Total kasus dalam periode ini adalah {total_kasus:,.0f} kasus."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

def analyze_kekerasan_anak_cumulative(data, selected_years):
    """Analyze kumulatif kekerasan anak"""
    try:
        if 'Kekerasan Anak' not in data:
            return "Data kekerasan anak tidak tersedia untuk analisis."
        
        df = data['Kekerasan Anak'].copy()
        
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Analisis kumulatif per gender dan tahun
        yearly_data = df.groupby(['Tahun', 'Gender'])['Jumlah_Kasus'].sum().reset_index()
        
        total_by_gender = df.groupby('Gender')['Jumlah_Kasus'].sum()
        total_keseluruhan = df['Jumlah_Kasus'].sum()
        
        years = sorted(df['Tahun'].unique())
        
        if len(total_by_gender) >= 2:
            gender_dominan = total_by_gender.idxmax()
            kasus_dominan = total_by_gender.max()
            persentase_dominan = (kasus_dominan / total_keseluruhan) * 100
            
            # Analisis pertumbuhan kumulatif
            gender_data = yearly_data[yearly_data['Gender'] == gender_dominan].sort_values('Tahun')
            if len(gender_data) > 1:
                pertumbuhan = "meningkat" if gender_data.iloc[-1]['Jumlah_Kasus'] > gender_data.iloc[0]['Jumlah_Kasus'] else "menurun"
            else:
                pertumbuhan = "stabil"
            
            insight = f"Secara kumulatif, korban kekerasan anak dengan gender {gender_dominan.lower()} mendominasi dengan {kasus_dominan:,.0f} kasus " \
                     f"({persentase_dominan:.1f}% dari total kasus). Tren kumulatif untuk korban {gender_dominan.lower()} menunjukkan pola {pertumbuhan} " \
                     f"dari tahun {years[0]} hingga {years[-1]}. Total akumulasi kasus kekerasan anak adalah {total_keseluruhan:,.0f} kasus " \
                     f"dalam {len(years)} tahun periode analisis."
        else:
            insight = f"Total akumulasi kasus kekerasan anak adalah {total_keseluruhan:,.0f} kasus dalam periode {len(years)} tahun."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

# ===========================
# CHART FUNCTIONS UNTUK KEKERASAN - LENGKAP
# ===========================

def create_kekerasan_gender_comparison_chart(data, selected_years):
    """Perbandingan Kekerasan berdasarkan Gender per Tahun - Stacked Bar Chart"""
    try:
        if 'Kekerasan Anak' not in data:
            return None
        
        df = data['Kekerasan Anak'].copy()
        
        # Filter data berdasarkan tahun yang dipilih
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return None
        
        # Group by tahun dan gender
        chart_data = df.groupby(['Tahun', 'Gender'])['Jumlah_Kasus'].sum().reset_index()
        
        fig = px.bar(
            chart_data,
            x='Tahun',
            y='Jumlah_Kasus',
            color='Gender',
            title="Jumlah Kasus Kekerasan berdasarkan Gender per Tahun",
            color_discrete_map={
                'Laki-laki': '#3498db', 
                'Perempuan': '#e74c3c'
            },
            barmode='stack'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title='Tahun',
            yaxis_title='Jumlah Kasus',
            legend_title='Gender'
        )
        
        return fig
        
    except Exception as e:
        return None

def create_kekerasan_perempuan_yearly_chart(data, selected_years):
    """Tren Kekerasan Perempuan per Tahun - Line Chart"""
    try:
        if 'Bentuk Kekerasan Perempuan' not in data:
            return None
        
        df = data['Bentuk Kekerasan Perempuan'].copy()
        
        # Filter data berdasarkan tahun yang dipilih
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return None
        
        # Group by tahun dan bentuk kekerasan
        chart_data = df.groupby(['Tahun', 'Bentuk_Kekerasan'])['Jumlah_Kasus'].sum().reset_index()
        
        fig = px.line(
            chart_data,
            x='Tahun',
            y='Jumlah_Kasus',
            color='Bentuk_Kekerasan',
            title="Tren Kekerasan Perempuan per Tahun",
            markers=True,
            line_shape='linear'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title='Tahun',
            yaxis_title='Jumlah Kasus',
            legend_title='Bentuk Kekerasan'
        )
        
        return fig
        
    except Exception as e:
        return None

def create_kekerasan_perempuan_usia_chart(data, selected_years):
    """Kekerasan Perempuan berdasarkan Kelompok Usia - Stacked Bar Chart"""
    try:
        if 'Usia Kekerasan Perempuan' not in data:
            return None
        
        df = data['Usia Kekerasan Perempuan'].copy()
        
        # Filter data berdasarkan tahun yang dipilih
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return None
        
        # Group by tahun dan kelompok usia
        chart_data = df.groupby(['Tahun', 'Kelompok_Usia'])['Jumlah_Kasus'].sum().reset_index()
        
        fig = px.bar(
            chart_data,
            x='Tahun',
            y='Jumlah_Kasus',
            color='Kelompok_Usia',
            title="Kekerasan Perempuan berdasarkan Kelompok Usia",
            color_discrete_sequence=['#FF9999', '#66B2FF', '#99FF99']
        )
        
        fig.update_layout(
            height=400,
            xaxis_title='Tahun',
            yaxis_title='Jumlah Kasus',
            legend_title='Kelompok Usia',
            barmode='stack'
        )
        
        return fig
        
    except Exception as e:
        return None

def create_kekerasan_anak_monthly_pattern_chart(data, selected_years):
    """Pola Kekerasan Anak per Bulan - Heatmap"""
    try:
        if 'Kekerasan Anak' not in data:
            return None
        
        df = data['Kekerasan Anak'].copy()
        
        # Filter data berdasarkan tahun yang dipilih
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return None
        
        # Create month order for proper sorting
        month_order = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                      'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
        
        # Aggregate data by month and year
        pivot_data = df.groupby(['Tahun', 'Bulan'])['Jumlah_Kasus'].sum().reset_index()
        pivot_table = pivot_data.pivot(index='Bulan', columns='Tahun', values='Jumlah_Kasus')
        
        # Reorder months
        pivot_table = pivot_table.reindex(month_order)
        pivot_table = pivot_table.fillna(0)
        
        fig = px.imshow(
            pivot_table.values,
            x=pivot_table.columns,
            y=pivot_table.index,
            title="Pola Kekerasan Anak per Bulan dan Tahun",
            color_continuous_scale='Reds',
            aspect='auto'
        )
        
        fig.update_layout(
            height=400,
            xaxis_title='Tahun',
            yaxis_title='Bulan'
        )
        
        return fig
        
    except Exception as e:
        return None

def create_kekerasan_anak_cumulative_chart(data, selected_years):
    """Kumulatif Kekerasan Anak per Tahun - Area Chart"""
    try:
        if 'Kekerasan Anak' not in data:
            return None
        
        df = data['Kekerasan Anak'].copy()
        
        # Filter data berdasarkan tahun yang dipilih
        if "Semua Tahun" not in selected_years:
            df = df[df['Tahun'].isin(selected_years)]
        
        if df.empty:
            return None
        
        # Group by tahun dan gender untuk mendapatkan total per tahun
        yearly_data = df.groupby(['Tahun', 'Gender'])['Jumlah_Kasus'].sum().reset_index()
        
        # Sort by year
        yearly_data = yearly_data.sort_values('Tahun')
        
        # Calculate cumulative sum for each gender
        cumulative_data = []
        
        for gender in yearly_data['Gender'].unique():
            gender_data = yearly_data[yearly_data['Gender'] == gender].copy()
            gender_data = gender_data.sort_values('Tahun')
            gender_data['Kumulatif'] = gender_data['Jumlah_Kasus'].cumsum()
            cumulative_data.append(gender_data)
        
        # Combine all cumulative data
        final_data = pd.concat(cumulative_data, ignore_index=True)
        
        fig = px.area(
            final_data,
            x='Tahun',
            y='Kumulatif',
            color='Gender',
            title="Kumulatif Kekerasan Anak per Tahun",
            color_discrete_map={
                'Laki-laki': '#3498db', 
                'Perempuan': '#e74c3c'
            }
        )
        
        fig.update_layout(
            height=400,
            xaxis_title='Tahun',
            yaxis_title='Jumlah Kasus Kumulatif',
            legend_title='Gender'
        )
        
        return fig
        
    except Exception as e:
        return None

def analyze_kontrasepsi_chart(data, selected_years):
    """Analyze kontrasepsi usage"""
    try:
        if 'Peserta Kb' not in data:
            return "Data peserta KB tidak tersedia untuk analisis."
        
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
            return "Kolom kontrasepsi atau peserta tidak ditemukan."
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        chart_data = df.groupby(kontrasepsi_col)[peserta_col].sum().reset_index()
        chart_data = chart_data.sort_values(peserta_col, ascending=False)
        
        if chart_data.empty:
            return "Tidak ada data untuk periode yang dipilih."
        
        # Find insights
        total_peserta = chart_data[peserta_col].sum()
        top_kontrasepsi = chart_data.iloc[0]
        percentage_top = (top_kontrasepsi[peserta_col] / total_peserta) * 100
        
        insight = f"{top_kontrasepsi[kontrasepsi_col]} adalah jenis kontrasepsi yang paling banyak digunakan " \
                 f"dengan {top_kontrasepsi[peserta_col]:,.0f} peserta ({percentage_top:.1f}% dari total peserta KB)."
        
        if len(chart_data) > 1:
            second_kontrasepsi = chart_data.iloc[1]
            percentage_second = (second_kontrasepsi[peserta_col] / total_peserta) * 100
            insight += f" Diikuti oleh {second_kontrasepsi[kontrasepsi_col]} dengan {second_kontrasepsi[peserta_col]:,.0f} peserta " \
                      f"({percentage_second:.1f}%)."
        
        # Find least used
        least_kontrasepsi = chart_data.iloc[-1]
        percentage_least = (least_kontrasepsi[peserta_col] / total_peserta) * 100
        
        insight += f" Jenis kontrasepsi yang paling sedikit digunakan adalah {least_kontrasepsi[kontrasepsi_col]} " \
                  f"dengan {least_kontrasepsi[peserta_col]:,.0f} peserta ({percentage_least:.1f}%). " \
                  f"Total peserta KB adalah {total_peserta:,.0f} orang dari {len(chart_data)} jenis kontrasepsi."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis: {str(e)}"

# ===========================
# MAP FUNCTIONS (sama seperti sebelumnya)
# ===========================
def prepare_disaster_data_for_map(data, selected_years):
    """Prepare disaster data for mapping"""
    try:
        if 'Bencana Alam' not in data:
            return None
        
        df = data['Bencana Alam'].copy()
        
        kecamatan_col = None
        jumlah_col = None
        tahun_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kecamatan' in col_lower:
                kecamatan_col = col
            elif 'tahun' in col_lower:
                tahun_col = col
            elif any(word in col_lower for word in ['jumlah', 'bencana']) and df[col].dtype in ['int64', 'float64']:
                jumlah_col = col
        
        if not kecamatan_col:
            return None
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        if jumlah_col:
            map_data = df.groupby(kecamatan_col)[jumlah_col].sum().reset_index()
            map_data.columns = ['Kecamatan', 'Total_Bencana']
        else:
            map_data = df[kecamatan_col].value_counts().reset_index()
            map_data.columns = ['Kecamatan', 'Total_Bencana']
        
        map_data['Kecamatan'] = map_data['Kecamatan'].str.strip().str.title()
        return map_data
        
    except Exception as e:
        return None

def create_simple_disaster_map(disaster_data):
    """Create a simple map with proper sizing"""
    try:
        center_lat = -8.1
        center_lon = 112.6
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles='OpenStreetMap',
            width='100%',
            height='500px'  # Diperbesar dari 400px ke 500px
        )
        
        if disaster_data is not None and not disaster_data.empty:
            kecamatan_coords = {
                'Dau': [-7.9167, 112.5833],
                'Pujon': [-7.8667, 112.4833],
                'Ngantang': [-7.7667, 112.4333],
                'Kasembon': [-7.8167, 112.3833],
                'Singosari': [-7.8833, 112.6667],
                'Lawang': [-7.8333, 112.6833],
                'Pakisaji': [-8.0667, 112.6167],
                'Tajinan': [-8.1500, 112.5833],
                'Tumpang': [-8.0167, 112.7333],
                'Pakis': [-7.9333, 112.7167],
                'Jabung': [-8.0833, 112.7833],
                'Wajak': [-8.1167, 112.7333],
                'Dampit': [-8.2167, 112.7500],
                'Tirtoyudo': [-8.3333, 112.6833],
                'Ampelgading': [-8.2833, 112.6167],
                'Poncokusumo': [-8.0500, 112.7833],
                'Wagir': [-8.0333, 112.5500],
                'Karangploso': [-7.9167, 112.6000],
                'Gondanglegi': [-8.1500, 112.6833],
                'Kepanjen': [-8.1333, 112.5833],
                'Sumberpucung': [-8.1000, 112.4833],
                'Sumbermanjing Wetan': [-8.3500, 112.5833],
            }
            
            max_disasters = disaster_data['Total_Bencana'].max()
            
            for _, row in disaster_data.iterrows():
                kecamatan = row['Kecamatan']
                disasters = row['Total_Bencana']
                
                coords = kecamatan_coords.get(kecamatan)
                if coords:
                    if disasters == 0:
                        color = 'green'
                        icon = 'ok'
                    elif disasters <= max_disasters * 0.3:
                        color = 'lightgreen'
                        icon = 'info-sign'
                    elif disasters <= max_disasters * 0.6:
                        color = 'orange'
                        icon = 'warning-sign'
                    else:
                        color = 'red'
                        icon = 'exclamation-sign'
                    
                    popup_content = f"""
                    <div style="font-family: Arial, sans-serif; min-width: 200px;">
                        <h4 style="margin: 0; color: #2c3e50;">{kecamatan}</h4>
                        <hr style="margin: 5px 0;">
                        <p style="margin: 5px 0;"><strong>🌊 Total Bencana:</strong> {disasters}</p>
                    </div>
                    """
                    
                    folium.Marker(
                        location=coords,
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=f"{kecamatan}: {disasters} bencana",
                        icon=folium.Icon(color=color, icon=icon)
                    ).add_to(m)
        
        return m
        
    except Exception as e:
        return None

def analyze_map_data(disaster_data):
    """Analyze map data and return insights"""
    try:
        if disaster_data is None or disaster_data.empty:
            return "Tidak ada data bencana untuk dianalisis."
        
        total_disasters = disaster_data['Total_Bencana'].sum()
        total_kecamatan = len(disaster_data)
        kecamatan_terdampak = len(disaster_data[disaster_data['Total_Bencana'] > 0])
        avg_disasters = disaster_data['Total_Bencana'].mean()
        
        top_3 = disaster_data.nlargest(3, 'Total_Bencana')
        kecamatan_aman = disaster_data[disaster_data['Total_Bencana'] == 0]
        
        insight = f"Dari {total_kecamatan} kecamatan di Kabupaten Malang, {kecamatan_terdampak} kecamatan mengalami bencana " \
                 f"dengan total {total_disasters} kejadian bencana. "
        
        if not top_3.empty:
            top_kecamatan = top_3.iloc[0]
            insight += f"Kecamatan {top_kecamatan['Kecamatan']} adalah yang paling rawan dengan {top_kecamatan['Total_Bencana']} kejadian bencana. "
        
        if not kecamatan_aman.empty:
            insight += f"Terdapat {len(kecamatan_aman)} kecamatan yang relatif aman (tidak ada kejadian bencana). "
        
        insight += f"Rata-rata kejadian bencana per kecamatan adalah {avg_disasters:.1f} kejadian."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis peta: {str(e)}"

# ===========================
# DATA LOADING FROM LOCAL FILES (sama seperti sebelumnya)
# ===========================
@st.cache_data
def load_local_data():
    """Load data from local CSV files"""
    data_path = "data/sosial/"
    
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
            file_path = data_path + filename
            df = pd.read_csv(file_path)
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
            
        except FileNotFoundError:
            st.error(f"File not found: {file_path}. Please make sure the CSV file is in the correct directory.")
            continue
        except Exception as e:
            st.error(f"Error loading {filename}: {str(e)}")
            continue
    
    return data

# ===========================
# FUNCTION TO GET AVAILABLE YEARS (sama seperti sebelumnya)
# ===========================
def get_available_years(data):
    """Get available years from data (2020-2024 only)"""
    available_years = set()
    
    for df in data.values():
        for col in df.columns:
            if 'tahun' in col.lower():
                years = df[col].dropna().unique()
                for year in years:
                    try:
                        year_int = int(year)
                        if 2020 <= year_int <= 2024:
                            available_years.add(year_int)
                    except (ValueError, TypeError):
                        continue
    
    return sorted(list(available_years))

# ===========================
# CHIP SELECTION COMPONENT (sama seperti sebelumnya)
# ===========================
def create_year_chips(available_years, key):
    """Create chip-style year selection"""
    
    # Initialize session state
    if f"selected_years_{key}" not in st.session_state:
        st.session_state[f"selected_years_{key}"] = ["Semua Tahun"]
    
    st.markdown("**📅 Select the Year:**")
    
    # Display selected chips
    if st.session_state[f"selected_years_{key}"]:
        chips_html = '<div class="year-selection-area">'
        for year in st.session_state[f"selected_years_{key}"]:
            chips_html += f'<span class="year-chip selected">{year} ✕</span>'
        chips_html += '</div>'
        st.markdown(chips_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="year-selection-area"><em style="color: #ccc;">No years selected</em></div>', unsafe_allow_html=True)
    
    # Available Years section
    st.markdown("**Available Years:**")
    
    # Semua Tahun and Clear All buttons
    col1, col2 = st.columns(2)
    
    with col1:
        semua_tahun_selected = "Semua Tahun" in st.session_state[f"selected_years_{key}"]
        button_text = "✅ Semua Tahun" if semua_tahun_selected else "📋 Semua Tahun"
        if st.button(button_text, key=f"all_years_{key}", use_container_width=True):
            if semua_tahun_selected:
                pass
            else:
                st.session_state[f"selected_years_{key}"] = ["Semua Tahun"]
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All", key=f"clear_all_{key}", use_container_width=True):
            st.session_state[f"selected_years_{key}"] = []
            st.rerun()
    
    # Individual Years section
    st.markdown("**Individual Years:**")
    
    cols = st.columns(2)
    
    for i, year in enumerate(available_years):
        col_idx = i % 2
        with cols[col_idx]:
            is_selected = year in st.session_state[f"selected_years_{key}"]
            button_text = f"✅ {year}" if is_selected else f"📅 {year}"
            
            if st.button(button_text, key=f"year_{year}_{key}", use_container_width=True):
                current_selection = st.session_state[f"selected_years_{key}"].copy()
                
                if "Semua Tahun" in current_selection:
                    current_selection.remove("Semua Tahun")
                
                if year in current_selection:
                    current_selection.remove(year)
                else:
                    current_selection.append(year)
                
                if not current_selection:
                    current_selection = ["Semua Tahun"]
                
                st.session_state[f"selected_years_{key}"] = sorted(current_selection, key=lambda x: x if x == "Semua Tahun" else int(x))
                st.rerun()
    
    return st.session_state[f"selected_years_{key}"]

# ===========================
# KPI CALCULATION (sama seperti sebelumnya)
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
        
        # 3. Kekerasan Anak - DIPERBAIKI
        if 'Kekerasan Anak' in data:
            df = data['Kekerasan Anak'].copy()
            
            if "Semua Tahun" not in selected_years:
                df = df[df['Tahun'].isin(selected_years)]
            
            # Hitung total kasus (tidak perlu filter 'Total' karena kita mau semua data bulanan)
            total = df['Jumlah_Kasus'].sum()
            kpis['kekerasan_anak'] = int(total)
        
        # 4. Kekerasan Perempuan - DIPERBAIKI
        if 'Bentuk Kekerasan Perempuan' in data:
            df = data['Bentuk Kekerasan Perempuan'].copy()
            
            if "Semua Tahun" not in selected_years:
                df = df[df['Tahun'].isin(selected_years)]
            
            # Hitung total kasus
            total = df['Jumlah_Kasus'].sum()
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
# CHART FUNCTIONS (dipersingkat karena fokus pada analisis)
# ===========================

# BANTUAN SOSIAL SECTION CHARTS
def create_penerima_per_tahun_chart(data, selected_years):
    """Rata-rata dan Jumlah Penerima per Tahun - Combo Chart"""
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
        
        yearly_data = df.groupby(tahun_col)[penerima_col].agg(['sum', 'mean']).reset_index()
        yearly_data.columns = [tahun_col, 'Total_Penerima', 'Rata_rata_Penerima']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=yearly_data[tahun_col],
            y=yearly_data['Total_Penerima'],
            name='Total Penerima',
            marker_color='#3498db',
            yaxis='y'
        ))
        
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
    """Jumlah Penerima Bantuan - Donut Chart"""
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
            title="Distribusi Penerima Bantuan per Program",
            hole=0.4,
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

# BENCANA SECTION CHARTS
def create_jenis_bencana_pie_chart(data, selected_years):
    """Jenis Bencana - Pie Chart"""
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
    """Bencana per Kecamatan"""
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
        
        tahun_col = None
        for col in df.columns:
            if 'tahun' in col.lower():
                tahun_col = col
                break
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
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
        fig.update_layout(height=500)
        return fig
        
    except Exception as e:
        return None

def create_kerugian_table(data, selected_years):
    """Kerugian Table"""
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

# KEKERASAN SECTION CHARTS
def create_kekerasan_total_yearly_chart(data, selected_years):
    """Total Kekerasan per Tahun - Line Chart"""
    try:
        if 'Kekerasan Anak' not in data or 'Bentuk Kekerasan Perempuan' not in data:
            return None
        
        df_anak = data['Kekerasan Anak'].copy()
        df_perempuan = data['Bentuk Kekerasan Perempuan'].copy()
        
        # Filter data berdasarkan tahun yang dipilih
        if "Semua Tahun" not in selected_years:
            df_anak = df_anak[df_anak['Tahun'].isin(selected_years)]
            df_perempuan = df_perempuan[df_perempuan['Tahun'].isin(selected_years)]
        
        # Aggregate kekerasan anak per tahun (semua bulan)
        anak_yearly = df_anak.groupby('Tahun')['Jumlah_Kasus'].sum().reset_index()
        anak_yearly['Jenis'] = 'Kekerasan Anak'
        
        # Aggregate kekerasan perempuan per tahun (semua bulan)
        perempuan_yearly = df_perempuan.groupby('Tahun')['Jumlah_Kasus'].sum().reset_index()
        perempuan_yearly['Jenis'] = 'Kekerasan Perempuan'
        
        # Combine data
        combined_data = pd.concat([anak_yearly, perempuan_yearly], ignore_index=True)
        
        fig = px.line(
            combined_data,
            x='Tahun',
            y='Jumlah_Kasus',
            color='Jenis',
            title="Tren Total Kekerasan per Tahun",
            markers=True,
            line_shape='linear',
            color_discrete_map={
                'Kekerasan Anak': '#FF6B6B',
                'Kekerasan Perempuan': '#4ECDC4'
            }
        )
        
        fig.update_layout(
            height=400,
            xaxis_title='Tahun',
            yaxis_title='Jumlah Kasus',
            legend_title='Jenis Kekerasan'
        )
        
        return fig
        
    except Exception as e:
        return None

# KB SECTION CHARTS
def create_kontrasepsi_chart(data, selected_years):
    """Jumlah Peserta per Jenis Kontrasepsi - Horizontal Bar Chart"""
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
    """Performa KB Kecamatan 2023-2024 - Table"""
    try:
        if 'Data Kb Performance' not in data:
            return None
        
        df = data['Data Kb Performance'].copy()
        
        if df.empty:
            return None
        
        # Find relevant columns
        display_cols = []
        for col in df.columns:
            col_lower = col.lower().strip()
            if any(word in col_lower for word in ['kecamatan', 'growth', 'performance', '2023', '2024', 'pertumbuhan', 'performa', 'pencapaian']):
                display_cols.append(col)
        
        # If no specific columns found, use first few columns
        if len(display_cols) < 2:
            display_cols = df.columns.tolist()[:min(5, len(df.columns))]
        
        # Limit to reasonable number of rows and columns
        table_data = df[display_cols].head(20)
        
        # Clean the data - replace NaN with appropriate values
        table_data = table_data.fillna('-')
        
        return table_data
        
    except Exception as e:
        return None

def analyze_kb_performance_table(data):
    """Analyze KB Performance Table - Focus on Best and Worst Performance"""
    try:
        if 'Data Kb Performance' not in data:
            return "Data performa KB tidak tersedia untuk analisis."
        
        df = data['Data Kb Performance'].copy()
        
        if df.empty:
            return "Tidak ada data performa KB untuk dianalisis."
        
        # Find columns dynamically
        kecamatan_col = None
        growth_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kecamatan' in col_lower:
                kecamatan_col = col
            elif any(word in col_lower for word in ['growth', 'pertumbuhan', 'tumbuh', '%']):
                growth_col = col
                break
        
        if not kecamatan_col:
            return "Data kecamatan tidak ditemukan dalam tabel performa KB."
        
        if not growth_col:
            # Try to find any numeric column that might represent performance
            for col in df.columns:
                if col != kecamatan_col and (df[col].dtype in ['int64', 'float64'] or 
                   (df[col].dtype == 'object' and any(str(val).replace('%','').replace(',','').replace('.','').isdigit() 
                                                     for val in df[col].dropna().head(3)))):
                    growth_col = col
                    break
        
        if not growth_col:
            return f"Data mencakup {len(df)} kecamatan namun tidak ditemukan kolom pertumbuhan untuk dianalisis."
        
        # Clean and convert growth data
        df_clean = df.copy()
        
        try:
            if df_clean[growth_col].dtype == 'object':
                # Remove %, commas, and convert to numeric
                df_clean[growth_col + '_numeric'] = pd.to_numeric(
                    df_clean[growth_col].astype(str)
                    .str.replace('%', '')
                    .str.replace(',', '')
                    .str.replace('Rp', '')
                    .str.strip(), 
                    errors='coerce'
                )
                numeric_col = growth_col + '_numeric'
            else:
                numeric_col = growth_col
                
        except:
            return f"Data performa KB mencakup {len(df)} kecamatan namun format data tidak dapat dianalisis."
        
        # Remove rows with NaN values
        df_clean = df_clean.dropna(subset=[numeric_col])
        
        if df_clean.empty or len(df_clean) < 2:
            return f"Data performa KB mencakup {len(df)} kecamatan namun data numerik tidak mencukupi untuk analisis."
        
        # Find best and worst performers
        best_idx = df_clean[numeric_col].idxmax()
        worst_idx = df_clean[numeric_col].idxmin()
        
        best_kecamatan = df_clean.loc[best_idx, kecamatan_col]
        best_value = df_clean.loc[best_idx, numeric_col]
        
        worst_kecamatan = df_clean.loc[worst_idx, kecamatan_col]
        worst_value = df_clean.loc[worst_idx, numeric_col]
        
        # Calculate statistics
        avg_value = df_clean[numeric_col].mean()
        total_kecamatan = len(df_clean)
        
        # Determine if values are percentages or regular numbers
        is_percentage = '%' in str(df[growth_col].iloc[0]) if not df[growth_col].empty else False
        unit = '%' if is_percentage else ''
        
        # Build insight
        insight = f"Kecamatan {best_kecamatan} menunjukkan performa KB terbaik dengan nilai {best_value:.1f}{unit}, " \
                 f"sedangkan Kecamatan {worst_kecamatan} memiliki performa terendah dengan nilai {worst_value:.1f}{unit}. "
        
        # Add comparison context
        if best_value > avg_value:
            diff_best = best_value - avg_value
            insight += f"Performa terbaik berada {diff_best:.1f}{unit} di atas rata-rata ({avg_value:.1f}{unit}). "
        
        if worst_value < avg_value:
            diff_worst = avg_value - worst_value
            insight += f"Performa terendah berada {diff_worst:.1f}{unit} di bawah rata-rata. "
        
        # Add performance gap information
        performance_gap = best_value - worst_value
        insight += f"Terdapat kesenjangan performa sebesar {performance_gap:.1f}{unit} antara kecamatan terbaik dan terburuk. "
        
        # Categorize performance levels
        above_avg = len(df_clean[df_clean[numeric_col] > avg_value])
        below_avg = len(df_clean[df_clean[numeric_col] < avg_value])
        
        insight += f"Dari {total_kecamatan} kecamatan, {above_avg} kecamatan berada di atas rata-rata dan {below_avg} kecamatan di bawah rata-rata."
        
        return insight
        
    except Exception as e:
        return f"Data performa KB tersedia untuk {len(data.get('Data Kb Performance', []))} kecamatan namun tidak dapat dianalisis secara detail."

# ===========================
# MAIN APPLICATION
# ===========================
def main():
    # Load data
    with st.spinner("📊 Loading data..."):
        data = load_local_data()
    
    if not data:
        st.error("❌ Tidak ada data yang berhasil dimuat!")
        return
    
    # Get available years
    available_years = get_available_years(data)
    
    if not available_years:
        available_years = [2020, 2021, 2022, 2023, 2024]
    
    # SIDEBAR FILTERS
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-filter">
            <h3>🔍 Please Filter Here:</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="filter-section">
        """, unsafe_allow_html=True)
        
        selected_years = create_year_chips(available_years, "main")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
            <h4 style="color: white; margin: 0;">📋 Main Menu</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 Home", use_container_width=True):
            st.rerun()
        
        if st.button("📊 Progress", use_container_width=True):
            st.info("Progress feature coming soon!")
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Dashboard Sosial Kabupaten Malang</h1>
        <h3>Sistem Monitoring Data Sosial 2020-2024</h3>
        <p><em>📊 Dashboard Interaktif untuk Analisis Data Sosial</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Calculate KPIs
        kpis = calculate_kpis(data, selected_years)
        
        # Display KPIs
        st.markdown("""
        <div class="kpi-section">
            <h3>📊 Key Performance Indicators</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            value = int(kpis.get('total_penerima_bantuan', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👥 Total Penerima Bantuan</h4>
                <h2>{value:,}</h2>
                <p>{value} Orang</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            value = int(kpis.get('total_bencana', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>🌊 Total Bencana</h4>
                <h2>{value:,}</h2>
                <p>{value} Kejadian</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            value = int(kpis.get('kekerasan_anak', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👶 Kekerasan Anak</h4>
                <h2>{value:,}</h2>
                <p>{value} Kasus</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            value = int(kpis.get('kekerasan_perempuan', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👩 Kekerasan Perempuan</h4>
                <h2>{value:,}</h2>
                <p>{value} Kasus</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            value = int(kpis.get('peserta_kb', 0))
            st.markdown(f"""
            <div class="accurate-card">
                <h4>👶 Peserta KB</h4>
                <h2>{value:,}</h2>
                <p>{value} Orang</p>
            </div>
            """, unsafe_allow_html=True)
        
                # ===========================
        # SECTION: PETA KERAWANAN BENCANA
        # ===========================
        st.markdown("""
        <div class="map-container">
            <div class="map-header">
                <h2>🗺️ PETA KERAWANAN BENCANA KABUPATEN MALANG</h2>
                <p><em>Visualisasi tingkat kerawanan bencana per kecamatan berdasarkan data historis</em></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Prepare disaster data
        disaster_data = prepare_disaster_data_for_map(data, selected_years)
        
        # Create and display map - DIPERLEBAR DAN DITENGAH
        simple_map = create_simple_disaster_map(disaster_data)
        
        if simple_map:
            # Container untuk memusatkan peta
            col1, col2, col3 = st.columns([1, 5, 1])  # Ratio 1:8:1 untuk memusatkan
            
            with col2:  # Peta di kolom tengah
                map_data = st_folium(simple_map, width=2000, height=500)  # Diperlebar dari 700 ke 900, tinggi dari 400 ke 500
            
            # Map statistics - WARNA HITAM
            if disaster_data is not None and not disaster_data.empty:
                total_disasters = disaster_data['Total_Bencana'].sum()
                avg_disasters = disaster_data['Total_Bencana'].mean()
                top_3 = disaster_data.nlargest(3, 'Total_Bencana')
                
                st.markdown(f"""
                <div class="map-stats">
                    <div class="map-stat-card">
                        <h4>📊 Statistik Kerawanan</h4>
                        <p><strong>Total Kecamatan:</strong> {len(disaster_data)}</p>
                        <p><strong>Kecamatan Terdampak:</strong> {len(disaster_data[disaster_data['Total_Bencana'] > 0])}</p>
                    </div>
                    <div class="map-stat-card">
                        <h4>🔥 Top 3 Kecamatan Rawan</h4>
                        {'<br>'.join([f"• {row['Kecamatan']}: {row['Total_Bencana']} bencana" for _, row in top_3.iterrows()])}
                    </div>
                    <div class="map-stat-card">
                        <h4>📈 Ringkasan Data</h4>
                        <p><strong>Total Bencana:</strong> {total_disasters}</p>
                        <p><strong>Rata-rata per Kecamatan:</strong> {avg_disasters:.1f}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Instructions - WARNA HITAM
        st.markdown("""
        <div class="instructions">
            <h4>💡 Cara Menggunakan Peta:</h4>
            <ul>
                <li>📍 <strong>Marker</strong> menunjukkan lokasi kecamatan dengan data bencana</li>
                <li>🖱️ <strong>Klik marker</strong> untuk melihat detail bencana per kecamatan</li>
                <li>🎨 <strong>Warna marker:</strong> Hijau = Rendah, Orange = Sedang, Merah = Tinggi</li>
                <li>🔍 <strong>Zoom</strong> dan geser peta untuk eksplorasi detail</li>
                <li>📅 <strong>Filter tahun</strong> di sidebar untuk melihat data periode tertentu</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ===========================
        # SECTION 1: BANTUAN SOSIAL
        # ===========================
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>👥 BANTUAN SOSIAL</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_penerima_per_tahun_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for penerima per tahun
                analysis = analyze_penerima_per_tahun(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    📊 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Penerima per Tahun tidak tersedia")
        
        with col2:
            chart = create_bantuan_donut_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for bantuan donut
                analysis = analyze_bantuan_donut(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    🍩 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Bantuan tidak tersedia")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ===========================
        # SECTION 2: BENCANA ALAM
        # ===========================
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>🌊 BENCANA ALAM</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_jenis_bencana_pie_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for jenis bencana
                analysis = analyze_jenis_bencana_pie(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    🥧 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Jenis Bencana tidak tersedia")
        
        with col2:
            chart = create_bencana_kecamatan_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for bencana kecamatan
                analysis = analyze_bencana_kecamatan(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    📊 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Bencana per Kecamatan tidak tersedia")
        
        # Kerugian table (full width)
        st.markdown("#### 💰 Total Kerugian per Kecamatan")
        table = create_kerugian_table(data, selected_years)
        if table is not None and not table.empty:
            st.dataframe(table, use_container_width=True, height=400)
            # Analysis for kerugian table
            try:
                total_kerugian = table['Kerugian_Rupiah'].apply(lambda x: int(x.replace('Rp ', '').replace(',', ''))).sum()
                top_kerugian = table.iloc[0] if not table.empty else None
                kecamatan_terdampak = len(table[table['Kerugian_Rupiah'] != 'Rp 0'])
                
                analysis = f"Total kerugian akibat bencana mencapai Rp {total_kerugian:,.0f}. "
                if top_kerugian is not None:
                    analysis += f"Kerugian terbesar terjadi di {top_kerugian.iloc[0]} pada tahun {top_kerugian.iloc[1]} " \
                               f"dengan nilai {top_kerugian.iloc[2]}. "
                analysis += f"Terdapat {kecamatan_terdampak} kecamatan yang mengalami kerugian finansial akibat bencana."
                
                st.markdown(f"""
                <div class="chart-explanation">
                    💰 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            except:
                st.markdown("""
                <div class="chart-explanation">
                    💰 <strong>Hasil Analisis:</strong> Data kerugian menunjukkan dampak finansial bencana alam di berbagai kecamatan.
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📊 Data Kerugian tidak tersedia")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
                # ===========================
        # SECTION 3: KEKERASAN - LENGKAP
        # ===========================
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>⚠️ KEKERASAN</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # First row: Tren Total Kekerasan dan Perbandingan Gender
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_kekerasan_total_yearly_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan total yearly
                analysis = analyze_kekerasan_total_yearly(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    📈 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Total Kekerasan tidak tersedia")
        
        with col2:
            chart = create_kekerasan_gender_comparison_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan gender comparison
                analysis = analyze_kekerasan_gender_comparison(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    📊 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Kekerasan berdasarkan Gender tidak tersedia")
        
        # Second row: Kekerasan Perempuan Tren dan Usia
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_kekerasan_perempuan_yearly_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan perempuan yearly
                analysis = analyze_kekerasan_perempuan_yearly(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    📈 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Kekerasan Perempuan tidak tersedia")
        
        with col2:
            chart = create_kekerasan_perempuan_usia_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan perempuan usia
                analysis = analyze_kekerasan_perempuan_usia(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    📊 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Kekerasan berdasarkan Usia tidak tersedia")
        
        # Third row: Pola Kekerasan Anak Bulanan dan Kumulatif
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_kekerasan_anak_monthly_pattern_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan anak monthly pattern
                analysis = analyze_kekerasan_anak_monthly_pattern(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    🔥 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Pola Bulanan Kekerasan Anak tidak tersedia")
        
        with col2:
            chart = create_kekerasan_anak_cumulative_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kekerasan anak cumulative
                analysis = analyze_kekerasan_anak_cumulative(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    📈 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Kumulatif Kekerasan Anak tidak tersedia")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # ===========================
        # SECTION 4: KELUARGA BERENCANA (KB)
        # ===========================
        st.markdown("""
        <div class="section-container">
            <div class="section-header">
                <h2>👶 KELUARGA BERENCANA (KB)</h2>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart = create_kontrasepsi_chart(data, selected_years)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
                # Analysis for kontrasepsi
                analysis = analyze_kontrasepsi_chart(data, selected_years)
                st.markdown(f"""
                <div class="chart-explanation">
                    📊 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Kontrasepsi tidak tersedia")
        
        with col2:
            st.markdown("#### 📈 Performa KB Kecamatan 2023-2024")
            table = create_kb_performance_table(data)
            if table is not None and not table.empty:
                st.dataframe(table, use_container_width=True, height=400)
                # Analysis for KB performance table
                analysis = analyze_kb_performance_table(data)
                st.markdown(f"""
                <div class="chart-explanation">
                    📈 <strong>Hasil Analisis:</strong> {analysis}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📊 Data Performa KB tidak tersedia")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display active filters info
        st.markdown("---")
        st.markdown("### 🎯 Active Filter")
        st.info(f"📅 **Tahun:** {', '.join(map(str, selected_years))}")
        
        # Footer
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"""
        ---
        <div style='text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 10px;'>
            <p><strong>📊 Dashboard Sosial Kabupaten Malang</strong></p>
            <p><strong>🔗 Data Source:</strong> Local CSV Files | <strong>🕒 Generated:</strong> {current_time}</p>
            <p><strong>💡 Insight:</strong> Dashboard ini menyediakan visualisasi data sosial untuk mendukung pengambilan keputusan (Periode 2020-2024)</p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan dalam memuat dashboard: {str(e)}")

if __name__ == "__main__":
    main()