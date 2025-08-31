"""
Analyzer functions specifically for education dashboard
"""

import pandas as pd
import numpy as np
from src.config.constants import PENDIDIKAN_LABEL_MAPPING

def get_latest_period(df):
    """Get latest year from education data (no monthly data)"""
    if df.empty:
        return None, None
    
    latest_year = df['tahun'].max()
    return latest_year, None  # No monthly data in education

def create_trend_analysis(trend_data, period_type="tahun"):
    """Generate trend analysis for education data"""
    if len(trend_data) <= 1:
        return "Data tidak cukup untuk analisis tren."
    
    # Education data is always yearly, no monthly analysis
    if period_type == "tahun":
        # Check if we have the right columns for APK/APM analysis
        if 'apk' in trend_data.columns and 'apm' in trend_data.columns:
            first_year = trend_data.iloc[0]['tahun']
            last_year = trend_data.iloc[-1]['tahun']
            
            apk_change = trend_data.iloc[-1]['apk'] - trend_data.iloc[0]['apk']
            apm_change = trend_data.iloc[-1]['apm'] - trend_data.iloc[0]['apm']
            
            best_apk_year = trend_data.loc[trend_data['apk'].idxmax(), 'tahun']
            best_apk_value = trend_data['apk'].max()
            
            best_apm_year = trend_data.loc[trend_data['apm'].idxmax(), 'tahun']
            best_apm_value = trend_data['apm'].max()
            
            if abs(apk_change) < 1 and abs(apm_change) < 1:
                return f"📊 **Perkembangan**: APK dan APM relatif stabil dari tahun {first_year} ke {last_year}. APK terbaik pada tahun {best_apk_year} ({best_apk_value:.1f}%), APM terbaik pada tahun {best_apm_year} ({best_apm_value:.1f}%)."
            elif apk_change > 0 and apm_change > 0:
                return f"📊 **Perkembangan**: Terjadi peningkatan positif baik APK ({apk_change:+.1f}%) maupun APM ({apm_change:+.1f}%) dari tahun {first_year} ke {last_year}."
            elif apk_change < 0 and apm_change < 0:
                return f"📊 **Perkembangan**: Terjadi penurunan APK ({apk_change:+.1f}%) dan APM ({apm_change:+.1f}%) dari tahun {first_year} ke {last_year}. Perlu perhatian khusus."
            else:
                return f"📊 **Perkembangan**: Tren beragam dari tahun {first_year} ke {last_year}. APK berubah {apk_change:+.1f}%, APM berubah {apm_change:+.1f}%."
        
        # Generic analysis for other metrics
        elif 'Prevalensi_Mean' in trend_data.columns:
            trend_change = trend_data.iloc[-1]['Prevalensi_Mean'] - trend_data.iloc[0]['Prevalensi_Mean']
            best_period = trend_data.loc[trend_data['Prevalensi_Mean'].idxmax(), 'tahun']
            best_value = trend_data['Prevalensi_Mean'].max()
            
            if abs(trend_change) < 1:
                return f"📊 **Perkembangan**: Indikator relatif stabil dengan perubahan {abs(trend_change):.1f}%. Nilai terbaik tercatat pada tahun {best_period} ({best_value:.1f}%)."
            elif trend_change > 0:
                return f"📊 **Perkembangan**: Terjadi peningkatan sebesar {trend_change:.1f}% dalam periode analisis."
            else:
                return f"📊 **Perkembangan**: Terjadi penurunan sebesar {abs(trend_change):.1f}% dalam periode analisis."
    
    return "Analisis tren pendidikan berdasarkan data tahunan."

def analyze_prevalence_category(prevalensi):
    """Classify education performance based on percentage"""
    if prevalensi >= 95:
        return "Sangat Baik (≥ 95%)"
    elif prevalensi >= 85:
        return "Baik (85-95%)"
    elif prevalensi >= 70:
        return "Cukup (70-85%)"
    else:
        return "Perlu Perbaikan (< 70%)"

def analyze_apk_apm_gap(apk, apm):
    """Analyze the gap between APK and APM"""
    gap = apk - apm
    
    if gap <= 5:
        return f"Gap sangat kecil ({gap:.1f}%) - Indikasi partisipasi tepat usia sangat baik"
    elif gap <= 10:
        return f"Gap kecil ({gap:.1f}%) - Partisipasi tepat usia cukup baik"
    elif gap <= 20:
        return f"Gap sedang ({gap:.1f}%) - Ada anak di luar usia ideal yang bersekolah"
    else:
        return f"Gap besar ({gap:.1f}%) - Banyak anak tidak pada usia ideal jenjangnya"

def create_education_insight(data, indicator_type="apk_apm"):
    """Create education-specific insights"""
    if data.empty:
        return "Tidak ada data untuk dianalisis."
    
    if indicator_type == "apk_apm":
        avg_apk = data['apk'].mean()
        avg_apm = data['apm'].mean()
        gap = avg_apk - avg_apm
        
        # Find best and worst performing districts
        best_district = data.loc[data['apm'].idxmax(), 'kecamatan']
        best_apm = data['apm'].max()
        
        worst_district = data.loc[data['apm'].idxmin(), 'kecamatan']
        worst_apm = data['apm'].min()
        
        insight = f"Rata-rata APK adalah {avg_apk:.1f}% dan APM adalah {avg_apm:.1f}%. "
        insight += analyze_apk_apm_gap(avg_apk, avg_apm) + ". "
        insight += f"Kecamatan {best_district} memiliki APM tertinggi ({best_apm:.1f}%), "
        insight += f"sedangkan Kecamatan {worst_district} memiliki APM terendah ({worst_apm:.1f}%)."
        
        return insight
    
    elif indicator_type == "guru_akreditasi":
        if 'persentase_guru_s1' in data.columns and 'persentase_sekolah_akreditasi' in data.columns:
            avg_guru_s1 = data['persentase_guru_s1'].mean()
            avg_akreditasi = data['persentase_sekolah_akreditasi'].mean()
            
            insight = f"Rata-rata guru berpendidikan S1 adalah {avg_guru_s1:.1f}% dan "
            insight += f"sekolah terakreditasi adalah {avg_akreditasi:.1f}%. "
            
            if avg_guru_s1 >= 80 and avg_akreditasi >= 80:
                insight += "Kualitas pendidikan sudah cukup baik dari segi kualifikasi guru dan akreditasi sekolah."
            elif avg_guru_s1 < 60 or avg_akreditasi < 60:
                insight += "Perlu peningkatan kualitas guru dan proses akreditasi sekolah."
            else:
                insight += "Kualitas pendidikan dalam kategori sedang, masih ada ruang untuk perbaikan."
            
            return insight
    
    return "Insight untuk indikator pendidikan."

def calculate_education_performance_score(data):
    """Calculate overall education performance score"""
    if data.empty:
        return 0, "Tidak ada data"
    
    score = 0
    max_score = 0
    details = []
    
    # APK Score (weight: 25%)
    if 'apk' in data.columns:
        avg_apk = data['apk'].mean()
        if avg_apk >= 95:
            apk_score = 25
        elif avg_apk >= 85:
            apk_score = 20
        elif avg_apk >= 75:
            apk_score = 15
        else:
            apk_score = 10
        
        score += apk_score
        max_score += 25
        details.append(f"APK: {avg_apk:.1f}% (skor: {apk_score}/25)")
    
    # APM Score (weight: 25%)
    if 'apm' in data.columns:
        avg_apm = data['apm'].mean()
        if avg_apm >= 90:
            apm_score = 25
        elif avg_apm >= 80:
            apm_score = 20
        elif avg_apm >= 70:
            apm_score = 15
        else:
            apm_score = 10
        
        score += apm_score
        max_score += 25
        details.append(f"APM: {avg_apm:.1f}% (skor: {apm_score}/25)")
    
    # Teacher Quality Score (weight: 25%)
    if 'persentase_guru_s1' in data.columns:
        avg_guru = data['persentase_guru_s1'].mean()
        if avg_guru >= 90:
            guru_score = 25
        elif avg_guru >= 80:
            guru_score = 20
        elif avg_guru >= 70:
            guru_score = 15
        else:
            guru_score = 10
        
        score += guru_score
        max_score += 25
        details.append(f"Guru S1: {avg_guru:.1f}% (skor: {guru_score}/25)")
    
    # Accreditation Score (weight: 25%)
    if 'persentase_sekolah_akreditasi' in data.columns:
        avg_akred = data['persentase_sekolah_akreditasi'].mean()
        if avg_akred >= 90:
            akred_score = 25
        elif avg_akred >= 80:
            akred_score = 20
        elif avg_akred >= 70:
            akred_score = 15
        else:
            akred_score = 10
        
        score += akred_score
        max_score += 25
        details.append(f"Akreditasi: {avg_akred:.1f}% (skor: {akred_score}/25)")
    
    if max_score == 0:
        return 0, "Tidak ada indikator yang dapat dievaluasi"
    
    final_score = (score / max_score) * 100
    
    if final_score >= 80:
        category = "Sangat Baik"
    elif final_score >= 70:
        category = "Baik"
    elif final_score >= 60:
        category = "Cukup"
    else:
        category = "Perlu Perbaikan"
    
    summary = f"Skor Kinerja Pendidikan: {final_score:.1f}/100 ({category})"
    detail_text = "; ".join(details)
    
    return final_score, f"{summary}. Detail: {detail_text}"

def analyze_education_correlation(data):
    """Analyze correlation between education indicators"""
    if data.empty or len(data) < 2:
        return "Data tidak cukup untuk analisis korelasi."
    
    correlations = []
    
    # APK vs APM correlation
    if 'apk' in data.columns and 'apm' in data.columns:
        corr_apk_apm = data['apk'].corr(data['apm'])
        correlations.append(f"APK-APM: {corr_apk_apm:.3f}")
    
    # Teacher quality vs APM correlation
    if 'persentase_guru_s1' in data.columns and 'apm' in data.columns:
        corr_guru_apm = data['persentase_guru_s1'].corr(data['apm'])
        correlations.append(f"Guru S1-APM: {corr_guru_apm:.3f}")
    
    # Accreditation vs APM correlation
    if 'persentase_sekolah_akreditasi' in data.columns and 'apm' in data.columns:
        corr_akred_apm = data['persentase_sekolah_akreditasi'].corr(data['apm'])
        correlations.append(f"Akreditasi-APM: {corr_akred_apm:.3f}")
    
    if correlations:
        return "Korelasi antar indikator: " + "; ".join(correlations)
    else:
        return "Tidak dapat menghitung korelasi dengan data yang tersedia."