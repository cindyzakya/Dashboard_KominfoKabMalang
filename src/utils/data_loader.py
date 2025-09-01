"""
Data loading utilities
"""

import streamlit as st
import pandas as pd
import json
import geopandas as gpd
from pathlib import Path
from config import *

@st.cache_data(ttl=CACHE_TTL)
def load_csv_data(file_path, **kwargs):
    """Load CSV data with caching"""
    try:
        df = pd.read_csv(file_path, **kwargs)
        return df
    except FileNotFoundError:
        st.error(f"File tidak ditemukan: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def load_geojson_data(file_path):
    """Load GeoJSON data with caching"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"File GeoJSON tidak ditemukan: {file_path}")
        return None
    except Exception as e:
        st.error(f"Error loading GeoJSON {file_path}: {str(e)}")
        return None

@st.cache_data(ttl=CACHE_TTL)
def load_geodataframe(file_path):
    """Load GeoDataFrame with caching"""
    try:
        gdf = gpd.read_file(file_path)
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        return gdf
    except Exception as e:
        st.error(f"Error loading GeoDataFrame {file_path}: {str(e)}")
        return gpd.GeoDataFrame()

def load_kesehatan_data():
    """Load health data"""
    file_path = KESEHATAN_DATA_PATH / "kesehatan_stunting.csv"
    df = load_csv_data(file_path)
    
    if not df.empty:
        # Clean prevalensi stunting column
        df['Prevalensi Stunting Persen'] = df['Prevalensi Stunting'].str.replace('%', '').str.replace(' ', '').str.replace('%%', '').astype(float)
    
    return df

def load_pendidikan_data():
    """Load education data"""
    file_path = PENDIDIKAN_DATA_PATH / "pendidikan_paud_sd_smp.csv"
    df = load_csv_data(file_path)
    
    if not df.empty:
        # Column mapping
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
        
        # Convert numeric columns
        numeric_cols = ['apk', 'apm', 'persentase_guru_s1', 'persentase_sekolah_akreditasi']
        for col in numeric_cols:
            if col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def load_sosial_data():
    """Load social data"""
    data = {}
    
    file_list = [
        "bantuan_sosial.csv",
        "bencana_alam.csv", 
        "bentuk_kekerasan_perempuan.csv",
        "data_kb_performance.csv",
        "data_kb_tren_metode.csv",
        "jenis_bencana.csv",
        "kekerasan_anak.csv",
        "peserta_kb.csv",
        "usia_kekerasan_perempuan.csv"
    ]
    
    for filename in file_list:
        file_path = SOSIAL_DATA_PATH / filename
        df = load_csv_data(file_path)
        
        if not df.empty:
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Process specific files
            if filename == "jenis_bencana.csv":
                # Add jenis bencana mapping
                from src.config.constants import JENIS_BENCANA_MAPPING
                if 'Jenis_Bencana' in df.columns:
                    df['Jenis_Bencana_Nama'] = df['Jenis_Bencana'].map(JENIS_BENCANA_MAPPING)
            
            clean_name = filename.replace('.csv', '').replace('_', ' ').title()
            data[clean_name] = df
    
    return data

def load_geo_data():
    """Load geographical data"""
    geo_data = {}
    
    geo_files = {
        'kecamatan': '35.07_kecamatan.geojson',
        'kelurahan': '35.07_kelurahan.geojson', 
        'malang': '35.07_Malang.geojson'
    }
    
    for key, filename in geo_files.items():
        file_path = GEO_DATA_PATH / filename
        geojson = load_geojson_data(file_path)
        if geojson:
            geo_data[key] = geojson
    
    return geo_data