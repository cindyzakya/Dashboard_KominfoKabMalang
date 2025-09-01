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
        
        insight += f" Rata-rata kejadian bencana per kecamatan adalah {avg_bencana:.0f} kejadian. " \
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

def analyze_kb_performance_table(data):
    """Analyze KB Performance Table - DIPERBAIKI"""
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
            elif 'growth' in col_lower and '2024' in col_lower and '2023' in col_lower:
                growth_col = col
                break
        
        if not kecamatan_col:
            return "Data kecamatan tidak ditemukan dalam tabel performa KB."
        
        if not growth_col:
            return f"Data mencakup {len(df)} kecamatan namun tidak ditemukan kolom pertumbuhan untuk dianalisis."
        
        # Clean and convert growth data - PERBAIKAN UTAMA
        df_clean = df.copy()
        
        try:
            if df_clean[growth_col].dtype == 'object':
                # Remove %, commas, and convert to numeric
                df_clean['Growth_Rate_Clean'] = df_clean[growth_col].astype(str).str.replace('%', '').str.replace(',', '.').str.strip()
                df_clean['Growth_Rate_Clean'] = pd.to_numeric(df_clean['Growth_Rate_Clean'], errors='coerce')
                numeric_col = 'Growth_Rate_Clean'
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
        
        # Build insight
        insight = f"Kecamatan {best_kecamatan} menunjukkan performa KB terbaik dengan pertumbuhan {best_value:.2f}%, " \
                 f"sedangkan Kecamatan {worst_kecamatan} mengalami penurunan terbesar dengan {worst_value:.2f}%. "
        
        # Add comparison context
        if best_value > avg_value:
            diff_best = best_value - avg_value
            insight += f"Performa terbaik berada {diff_best:.2f}% di atas rata-rata ({avg_value:.2f}%). "
        
        if worst_value < avg_value:
            diff_worst = avg_value - worst_value
            insight += f"Performa terendah berada {diff_worst:.2f}% di bawah rata-rata. "
        
        # Add performance gap information
        performance_gap = best_value - worst_value
        insight += f"Terdapat kesenjangan performa sebesar {performance_gap:.2f}% antara kecamatan terbaik dan terburuk. "
        
        # Categorize performance levels
        above_avg = len(df_clean[df_clean[numeric_col] > avg_value])
        below_avg = len(df_clean[df_clean[numeric_col] < avg_value])
        
        insight += f"Dari {total_kecamatan} kecamatan, {above_avg} kecamatan berada di atas rata-rata dan {below_avg} kecamatan di bawah rata-rata."
        
        return insight
        
    except Exception as e:
        return f"Data performa KB tersedia untuk {len(data.get('Data Kb Performance', []))} kecamatan namun tidak dapat dianalisis secara detail."
    
def analyze_map_data_generic(map_data, map_type, selected_years=None):
    """Generic function to analyze map data - DIPERBAIKI"""
    try:
        if map_data is None or map_data.empty:
            return f"Tidak ada data {map_type.lower()} untuk dianalisis."
        
        # Tentukan kolom value dan unit berdasarkan map_type
        if map_type == "Bencana Alam":
            value_col = 'Total_Bencana'
            unit = 'kejadian bencana'
            metric = 'bencana'
        elif map_type == "Bantuan Sosial":
            value_col = 'Total_Penerima'
            unit = 'penerima bantuan'
            metric = 'penerima'
        elif map_type == "KB Performance":
            value_col = 'Growth_Rate'
            unit = '% pertumbuhan'
            metric = 'pertumbuhan'
        elif map_type == "Peserta KB":
            value_col = 'Total_Peserta'
            unit = 'peserta KB'
            metric = 'peserta'
        else:
            return "Jenis data tidak dikenali."
        
        if value_col not in map_data.columns:
            return f"Data {map_type.lower()} tidak memiliki kolom yang sesuai."
        
        total_kecamatan = len(map_data)
        
        if map_type == "KB Performance":
            # Analisis khusus untuk KB Performance - DIPERBAIKI
            positive_growth = len(map_data[map_data[value_col] > 0])
            negative_growth = len(map_data[map_data[value_col] < 0])
            avg_growth = map_data[value_col].mean()
            
            top_kecamatan = map_data.loc[map_data[value_col].idxmax()]
            worst_kecamatan = map_data.loc[map_data[value_col].idxmin()]
            
            insight = f"Dari {total_kecamatan} kecamatan, {positive_growth} kecamatan mengalami pertumbuhan positif " \
                     f"dan {negative_growth} kecamatan mengalami penurunan. "
            insight += f"Kecamatan {top_kecamatan['Kecamatan']} memiliki pertumbuhan tertinggi dengan {top_kecamatan[value_col]:.2f}%, " \
                      f"sedangkan Kecamatan {worst_kecamatan['Kecamatan']} mengalami penurunan terbesar dengan {worst_kecamatan[value_col]:.2f}%. "
            insight += f"Rata-rata pertumbuhan KB di Kabupaten Malang adalah {avg_growth:.2f}%."
            
        else:
            # Analisis untuk data lainnya
            total_value = map_data[value_col].sum()
            avg_value = map_data[value_col].mean()
            
            top_3 = map_data.nlargest(3, value_col)
            zero_value = map_data[map_data[value_col] == 0] if map_type == "Bencana Alam" else pd.DataFrame()
            
            insight = f"Total {unit} di Kabupaten Malang adalah {total_value:,.0f}. "
            
            if not top_3.empty:
                top_kecamatan = top_3.iloc[0]
                insight += f"Kecamatan {top_kecamatan['Kecamatan']} memiliki {metric} tertinggi dengan {top_kecamatan[value_col]:,.0f} {unit}. "
                
                if len(top_3) > 1:
                    second_kecamatan = top_3.iloc[1]
                    insight += f"Diikuti oleh Kecamatan {second_kecamatan['Kecamatan']} dengan {second_kecamatan[value_col]:,.0f} {unit}. "
            
            if not zero_value.empty and map_type == "Bencana Alam":
                insight += f"Terdapat {len(zero_value)} kecamatan yang tidak mengalami bencana dalam periode ini. "
            
            # PERBAIKAN RATA-RATA BERDASARKAN JENIS DATA
            if map_type == "Bencana Alam":
                insight += f"Rata-rata {unit} per kecamatan adalah {avg_value:.0f} bencana."
            elif map_type == "Bantuan Sosial":
                insight += f"Rata-rata {unit} per kecamatan adalah {avg_value:.0f} orang."
            elif map_type == "Peserta KB":
                insight += f"Rata-rata {unit} per kecamatan adalah {avg_value:.0f} orang."
            
            # Tambahan untuk periode waktu
            if selected_years and "Semua Tahun" not in selected_years:
                period = ', '.join(map(str, selected_years))
                insight += f" Data ini mencakup periode tahun {period}."
        
        return insight
        
    except Exception as e:
        return f"Error dalam analisis peta {map_type.lower()}: {str(e)}"