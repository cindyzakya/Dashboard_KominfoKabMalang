"""
Analyzer functions specifically for health dashboard
"""

import pandas as pd
import numpy as np

def get_latest_period(df):
    """Get latest year and month from health data"""
    if df.empty:
        return None, None
    
    month_order = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                   'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    
    latest_year = df['Tahun'].max()
    latest_year_data = df[df['Tahun'] == latest_year]
    available_months = latest_year_data['Bulan'].unique()

    latest_month = None
    for month in reversed(month_order):
        if month in available_months:
            latest_month = month
            break
    
    return latest_year, latest_month

def analyze_prevalence_category(prevalensi):
    """Classify stunting prevalence"""
    if prevalensi < 5:
        return "Rendah (< 5%)"
    elif prevalensi < 10:
        return "Sedang (5-10%)"
    elif prevalensi < 20:
        return "Tinggi (10-20%)"
    else:
        return "Sangat Tinggi (> 20%)"

def get_latest_facilities_data(data):
    """Get facilities data from latest period"""
    if data.empty:
        return pd.DataFrame()

    latest_year, latest_month = get_latest_period(data)
    
    if not latest_year or not latest_month:
        return pd.DataFrame()

    latest_period_df = data[(data['Tahun'] == latest_year) & (data['Bulan'] == latest_month)]

    # Kolom fasilitas kesehatan
    per_kecamatan_cols = ['Jumlah Rumah Sakit', 'Jumlah Puskesmas', 'Jumlah Puskesmas Pembantu']
    per_unit_kerja_cols = ['Jumlah Klinik', 'Pos Kesehatan', 'Jumlah Pondak Bersalin Desa (Polindes)']

    # Filter kolom yang ada
    per_kecamatan_cols = [col for col in per_kecamatan_cols if col in latest_period_df.columns]
    per_unit_kerja_cols = [col for col in per_unit_kerja_cols if col in latest_period_df.columns]

    # Proses data
    faskes_kec_df = latest_period_df[['Kecamatan'] + per_kecamatan_cols].drop_duplicates(subset=['Kecamatan']).reset_index(drop=True)
    faskes_unit_df = latest_period_df.groupby('Kecamatan')[per_unit_kerja_cols].sum().reset_index()

    # Gabungkan
    final_faskes_df = pd.merge(faskes_kec_df, faskes_unit_df, on='Kecamatan', how='outer').fillna(0)
    return final_faskes_df

def create_correlation_analysis(correlation, avg_faskes, high_faskes_low_prev, low_faskes_high_prev):
    """Generate analisis korelasi"""
    if correlation < -0.4:
        return f"**Hubungan Negatif Kuat**: Data menunjukkan korelasi negatif yang kuat ({correlation:.2f}) antara jumlah fasilitas kesehatan dan tingkat stunting. Rata-rata terdapat {avg_faskes:.1f} fasilitas per kecamatan. {high_faskes_low_prev} kecamatan menunjukkan pola fasilitas banyak dengan stunting rendah."
    elif correlation < -0.2:
        return f"**Hubungan Negatif Sedang**: Terdapat korelasi negatif sedang ({correlation:.2f}) yang menunjukkan adanya hubungan antara fasilitas kesehatan dan tingkat stunting. {high_faskes_low_prev} kecamatan menunjukkan kondisi optimal dengan fasilitas memadai dan stunting rendah."
    elif correlation > 0.2:
        return f"**Hubungan Positif**: Data menunjukkan korelasi positif ({correlation:.2f}), dimana wilayah dengan fasilitas kesehatan lebih banyak cenderung memiliki tingkat stunting yang lebih tinggi. {low_faskes_high_prev} kecamatan memiliki fasilitas terbatas namun stunting tinggi."
    else:
        return f"**Hubungan Lemah**: Korelasi yang lemah ({correlation:.2f}) menunjukkan bahwa faktor selain jumlah fasilitas kesehatan mungkin lebih berpengaruh terhadap tingkat stunting. {low_faskes_high_prev} kecamatan memiliki kondisi yang memerlukan perhatian khusus."