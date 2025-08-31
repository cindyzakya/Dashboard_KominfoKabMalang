"""
Helper functions for the dashboard
"""

import os
import streamlit as st
from pathlib import Path

def check_file_exists(filename):
    """Check if file exists"""
    return os.path.exists(filename)

def format_number(number, format_type="default"):
    """Format numbers for display"""
    if format_type == "percentage":
        return f"{number:.2f}%"
    elif format_type == "currency":
        return f"Rp {number:,.0f}"
    elif format_type == "integer":
        return f"{number:,.0f}"
    else:
        return f"{number:,.2f}"

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default

def clean_column_names(df):
    """Clean column names"""
    df.columns = df.columns.str.strip().str.replace(' ', '_').str.lower()
    return df

def get_latest_period(df, year_col='tahun', month_col='bulan'):
    """Get latest period from dataframe"""
    if df.empty:
        return None, None
    
    if year_col not in df.columns:
        return None, None
    
    latest_year = df[year_col].max()
    
    if month_col in df.columns:
        from src.config.constants import MONTH_ORDER
        latest_year_data = df[df[year_col] == latest_year]
        available_months = latest_year_data[month_col].unique()
        
        latest_month = None
        for month in reversed(MONTH_ORDER):
            if month in available_months:
                latest_month = month
                break
        
        return latest_year, latest_month
    
    return latest_year, None

def create_download_link(df, filename, file_format="csv"):
    """Create download link for dataframe"""
    if file_format.lower() == "csv":
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download {filename}.csv",
            data=csv,
            file_name=f"{filename}.csv",
            mime="text/csv"
        )
    elif file_format.lower() == "excel":
        # This would require openpyxl
        # For now, just use CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"📥 Download {filename}.xlsx",
            data=csv,
            file_name=f"{filename}.csv",
            mime="text/csv"
        )

def validate_data(df, required_columns):
    """Validate if dataframe has required columns"""
    if df.empty:
        return False, "Data is empty"
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing columns: {', '.join(missing_columns)}"
    
    return True, "Data is valid"

def format_indicator_value(indicator, value):
    """Format indikator sesuai jenisnya"""
    if value is None:
        return "-"

    if indicator in ["apk", "apm", "persentase_guru_s1", "persentase_sekolah_akreditasi"]:
        return f"{value:.2f}%"
    elif indicator == "rasio_sekolah_penduduk":
        return f"{value:.2f} per 1000"
    elif indicator in ["jumlah_sekolah", "jumlah_penduduk_usia_sekolah"]:
        return f"{int(value):,}"
    else:
        # fallback -> gunakan format_number bawaan
        return format_number(value)
