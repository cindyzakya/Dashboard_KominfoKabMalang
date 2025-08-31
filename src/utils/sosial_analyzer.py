"""
Analyzer functions specifically for social dashboard
"""

import pandas as pd
import numpy as np
from src.config.constants import JENIS_BENCANA_MAPPING

def calculate_kpis(data, selected_years):
    """Calculate KPI values for social dashboard"""
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
        
        # 3-5. Kekerasan dan KB data
        if 'Kekerasan Anak' in data:
            df = data['Kekerasan Anak'].copy()
            if "Semua Tahun" not in selected_years:
                df = df[df['Tahun'].isin(selected_years)]
            kpis['kekerasan_anak'] = int(df['Jumlah_Kasus'].sum())
        
        if 'Bentuk Kekerasan Perempuan' in data:
            df = data['Bentuk Kekerasan Perempuan'].copy()
            if "Semua Tahun" not in selected_years:
                df = df[df['Tahun'].isin(selected_years)]
            kpis['kekerasan_perempuan'] = int(df['Jumlah_Kasus'].sum())
        
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

def get_available_years(data):
    """Get available years from social data"""
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