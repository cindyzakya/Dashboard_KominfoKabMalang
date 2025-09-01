"""
Data processing utilities
"""

import pandas as pd
import numpy as np
from src.config.constants import MONTH_ORDER

def clean_numeric_columns(df, exclude_columns=None):
    """Clean numeric columns in dataframe"""
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

def create_sorted_period_data(df):
    """Create sorted period data with proper month ordering"""
    month_mapping = {month: i+1 for i, month in enumerate(MONTH_ORDER)}
    
    df_sorted = df.copy()
    if 'Bulan' in df_sorted.columns:
        df_sorted['Month_Num'] = df_sorted['Bulan'].map(month_mapping)
        df_sorted['Periode'] = df_sorted['Tahun'].astype(str) + '-' + df_sorted['Bulan']
        df_sorted = df_sorted.sort_values(['Tahun', 'Month_Num']).reset_index(drop=True)
    
    return df_sorted

def aggregate_data_by_period(df, group_cols, agg_cols, agg_funcs='sum'):
    """Aggregate data by specified period"""
    if isinstance(agg_funcs, str):
        agg_funcs = {col: agg_funcs for col in agg_cols}
    
    return df.groupby(group_cols).agg(agg_funcs).reset_index()

def calculate_growth_rate(df, value_col, period_col):
    """Calculate growth rate between periods"""
    df_sorted = df.sort_values(period_col)
    df_sorted['growth_rate'] = df_sorted[value_col].pct_change() * 100
    return df_sorted

def handle_missing_values(df, strategy='mean'):
    """Handle missing values in dataframe"""
    df_clean = df.copy()
    
    for col in df_clean.columns:
        if df_clean[col].dtype in ['int64', 'float64']:
            if strategy == 'mean':
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            elif strategy == 'median':
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
            elif strategy == 'zero':
                df_clean[col] = df_clean[col].fillna(0)
        else:
            df_clean[col] = df_clean[col].fillna('Unknown')
    
    return df_clean

def normalize_data(df, columns, method='min-max'):
    """Normalize specified columns"""
    df_norm = df.copy()
    
    for col in columns:
        if col in df_norm.columns:
            if method == 'min-max':
                min_val = df_norm[col].min()
                max_val = df_norm[col].max()
                if max_val != min_val:
                    df_norm[col] = (df_norm[col] - min_val) / (max_val - min_val)
            elif method == 'z-score':
                mean_val = df_norm[col].mean()
                std_val = df_norm[col].std()
                if std_val != 0:
                    df_norm[col] = (df_norm[col] - mean_val) / std_val
    
    return df_norm

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

def prepare_bantuan_sosial_data_for_map(data, selected_years):
    """Prepare bantuan sosial data for mapping"""
    try:
        if 'Bantuan Sosial' not in data:
            return None
        
        df = data['Bantuan Sosial'].copy()
        
        kecamatan_col = None
        penerima_col = None
        tahun_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kecamatan' in col_lower:
                kecamatan_col = col
            elif 'penerima' in col_lower:
                penerima_col = col
            elif 'tahun' in col_lower:
                tahun_col = col
        
        if not all([kecamatan_col, penerima_col]):
            return None
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        map_data = df.groupby(kecamatan_col)[penerima_col].sum().reset_index()
        map_data.columns = ['Kecamatan', 'Total_Penerima']
        
        map_data['Kecamatan'] = map_data['Kecamatan'].str.strip().str.title()
        return map_data
        
    except Exception as e:
        return None

def prepare_kb_performance_data_for_map(data):
    """Prepare KB performance data for mapping - DIPERBAIKI"""
    try:
        if 'Data Kb Performance' not in data:
            return None
        
        df = data['Data Kb Performance'].copy()
        
        kecamatan_col = None
        growth_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kecamatan' in col_lower:
                kecamatan_col = col
            elif 'growth' in col_lower and '2024' in col_lower and '2023' in col_lower:
                growth_col = col
                break
        
        if not all([kecamatan_col, growth_col]):
            return None
        
        # Clean growth data - PERBAIKAN UTAMA
        df_clean = df.copy()
        if df_clean[growth_col].dtype == 'object':
            # Remove % and convert to numeric
            df_clean['Growth_Rate_Numeric'] = df_clean[growth_col].astype(str).str.replace('%', '').str.replace(',', '.').str.strip()
            df_clean['Growth_Rate_Numeric'] = pd.to_numeric(df_clean['Growth_Rate_Numeric'], errors='coerce')
            numeric_col = 'Growth_Rate_Numeric'
        else:
            numeric_col = growth_col
        
        map_data = df_clean[[kecamatan_col, numeric_col]].copy()
        map_data.columns = ['Kecamatan', 'Growth_Rate']
        map_data = map_data.dropna()
        
        map_data['Kecamatan'] = map_data['Kecamatan'].str.strip().str.title()
        return map_data
        
    except Exception as e:
        return None

def prepare_peserta_kb_data_for_map(data, selected_years):
    """Prepare peserta KB data for mapping"""
    try:
        if 'Peserta Kb' not in data:
            return None
        
        df = data['Peserta Kb'].copy()
        
        kecamatan_col = None
        peserta_col = None
        tahun_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'kecamatan' in col_lower:
                kecamatan_col = col
            elif 'peserta' in col_lower:
                peserta_col = col
            elif 'tahun' in col_lower:
                tahun_col = col
        
        if not all([kecamatan_col, peserta_col]):
            return None
        
        if tahun_col and "Semua Tahun" not in selected_years:
            df = df[df[tahun_col].isin(selected_years)]
        
        map_data = df.groupby(kecamatan_col)[peserta_col].sum().reset_index()
        map_data.columns = ['Kecamatan', 'Total_Peserta']
        
        map_data['Kecamatan'] = map_data['Kecamatan'].str.strip().str.title()
        return map_data
        
    except Exception as e:
        return None
