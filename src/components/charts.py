"""
Chart components for dashboard visualization
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_line_chart(data, x_col, y_col, color_col=None, title="Line Chart"):
    """Create line chart with plotly"""
    fig = px.line(
        data, 
        x=x_col, 
        y=y_col, 
        color=color_col,
        title=title,
        markers=True
    )
    fig.update_layout(height=400)
    return fig

def create_bar_chart(data, x_col, y_col, color_col=None, title="Bar Chart", orientation='v'):
    """Create bar chart with plotly"""
    fig = px.bar(
        data,
        x=x_col if orientation == 'v' else y_col,
        y=y_col if orientation == 'v' else x_col,
        color=color_col,
        title=title,
        orientation='h' if orientation == 'h' else 'v'
    )
    fig.update_layout(height=400)
    return fig

def create_pie_chart(data, values_col, names_col, title="Pie Chart"):
    """Create pie chart with plotly"""
    fig = px.pie(
        data,
        values=values_col,
        names=names_col,
        title=title
    )
    fig.update_layout(height=400)
    return fig

def create_scatter_plot(data, x_col, y_col, color_col=None, title="Scatter Plot"):
    """Create scatter plot with plotly"""
    fig = px.scatter(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title
    )
    fig.update_layout(height=400)
    return fig

def create_heatmap(data, x_col, y_col, z_col, title="Heatmap"):
    """Create heatmap with plotly"""
    pivot_data = data.pivot(index=y_col, columns=x_col, values=z_col)
    
    fig = px.imshow(
        pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        title=title,
        aspect='auto'
    )
    fig.update_layout(height=400)
    return fig

def create_combo_chart(data, x_col, y1_col, y2_col, title="Combo Chart"):
    """Create combination chart with bar and line"""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=data[x_col],
        y=data[y1_col],
        name=y1_col,
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=data[x_col],
        y=data[y2_col],
        mode='lines+markers',
        name=y2_col,
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=title,
        yaxis=dict(title=y1_col, side='left'),
        yaxis2=dict(title=y2_col, side='right', overlaying='y'),
        height=400
    )
    
    return fig

def create_area_chart(data, x_col, y_col, color_col=None, title="Area Chart"):
    """Create area chart with plotly"""
    fig = px.area(
        data,
        x=x_col,
        y=y_col,
        color=color_col,
        title=title
    )
    fig.update_layout(height=400)
    return fig

# Chart creation functions
def create_penerima_per_tahun_chart(data, selected_years):
    """Create recipients per year chart"""
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
            marker_color='#2a89a6',
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
            yaxis=dict(title='Total Penerima', side='left'),
            yaxis2=dict(title='Rata-rata Penerima', side='right', overlaying='y'),
            height=400,
            legend=dict(x=0, y=1)
        )
        
        return fig
        
    except Exception as e:
        return None

def create_bantuan_donut_chart(data, selected_years):
    """Create social assistance donut chart"""
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
            color_discrete_sequence=[
                "#985356", "#c85a5a", "#e4acac", "#ad9ea5", "#574249", "#62718c", "#2a89a6", "#d1ecf2", "#e8e8e8"
            ]
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

def create_jenis_bencana_pie_chart(data, selected_years):
    """Create disaster type pie chart"""
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
                "#985356", "#c85a5a", "#e4acac", "#ad9ea5", "#574249", "#62718c", "#2a89a6", "#d1ecf2", "#e8e8e8"
            ]
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<br><extra></extra>'
        )
        
        fig.update_layout(height=500)
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
            color_continuous_scale=['#e4acac', '#c85a5a'],
        )
        fig.update_layout(height=500)
        return fig
        
    except Exception as e:
        return None

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
                'Kekerasan Anak': '#c85a5a',
                'Kekerasan Perempuan': '#2a89a6'
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
            title="Jumlah Kasus Kekerasan Anak berdasarkan Gender per Tahun",
            color_discrete_map={
                'Laki-laki': '#2a89a6', 
                'Perempuan': '#c85a5a'
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
            line_shape='linear',
            color_discrete_map={
                'Fisik': '#d64541',        # merah tegas tapi tetap elegan
                'Lainnya': '#e67e73',      # coral, lebih terang & jelas
                'Penelantaran': '#8e5c9c', # ungu medium, lebih kontras daripada abu-ungu
                'Psikis': '#3f88c5',       # biru terang tapi kalem
                'Seksual': '#2ca25f'       # hijau emerald (segar tapi nggak norak)
            }
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
            color_discrete_sequence=['#d64541', '#3f88c5', '#2ca25f']
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
            color_continuous_scale=['#d1ecf2', '#004c70']
        )
        
        fig.update_layout(
            height=470,
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
            if any(word in col_lower for word in [
                'kecamatan', 'growth', 'performance', 
                '2023', '2024', 'pertumbuhan', 
                'performa', 'pencapaian'
            ]):
                display_cols.append(col)
        
        # If no specific columns found, use first few columns
        if len(display_cols) < 2:
            display_cols = df.columns.tolist()[:min(5, len(df.columns))]
        
        # Menampilkan semua baris data, tidak dibatasi
        table_data = df[display_cols]
        
        # Clean the data - replace NaN with appropriate values
        table_data = table_data.fillna('-').reset_index(drop=True)
        
        return table_data
        
    except Exception as e:
        return None
