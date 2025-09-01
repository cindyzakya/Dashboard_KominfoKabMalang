"""
Main CSS styles for the dashboard - GABUNGAN LENGKAP SEMUA CSS
"""

import streamlit as st

def load_main_css():
    """Load main CSS styles - GABUNGAN SEMUA CSS DARI ORIGINAL"""
    st.markdown("""
    <style>
        /* HOME PAGE CSS */
        .main-header {
            background: linear-gradient(135deg, #2a89a6 0%, #574249 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
        
        .dashboard-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border: 2px solid #e0e6ed;
            transition: all 0.3s ease;
            text-align: center;
            height: 470px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
            border-color: #4CAF50;
        }
        
        .card-icon {
            font-size: 4.5rem;
            margin-bottom: 20px;
        }
        
        .card-title {
            font-size: 1.9rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #2c3e50;
        }
        
        .card-description {
            color: #7f8c8d;
            margin-bottom: 25px;
            line-height: 1.6;
            font-size: 0.95rem;
        }
        
        .stats-container {
            background: linear-gradient(135deg, #e4acac 0%, #c85a5a 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 20px;
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .footer {
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-top: 50px;
        }
        
        .github-link {
            background: linear-gradient(135deg, #24292e 0%, #586069 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            text-decoration: none;
            display: inline-block;
            margin: 10px 5px;
            transition: all 0.3s ease;
        }
        
        .github-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        
        .manual-link {
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)

def load_kesehatan_css():
    """Load CSS khusus untuk dashboard kesehatan"""
    st.markdown("""
    <style>
        /* Garis custom lebih rapat */
        .custom-hr {
            border: 0;
            border-top: 1px solid #ddd;
            margin: 0.3rem 0;
        }

        /* Rapikan jarak antar elemen */
        .stMarkdown, .stText, .stMetric, .stPlotlyChart, .stDataFrame {
            margin-top: 0rem;
            margin-bottom: 0.4rem;
            padding: 0rem;
        }

        /* Atur kolom agar sejajar di top */
        div[data-testid="column"] {
            vertical-align: top;
        }

        /* Header Utama */
        .main-header {
            background: linear-gradient(90deg, #2a89a6 0%, #62718c 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .main-header h1 { margin-bottom: 0.2rem; font-size: 2.5rem; }
        .main-header h3 { margin-bottom: 0.5rem; font-weight: 500; font-size: 1.2rem; }
        .main-header p { font-style: italic; font-size: 1rem; }

        /* Header untuk setiap seksi */
        .section-header {
            background-color: #f0f2f6;
            padding: 1rem 1rem;
            border-radius: 7px;
            margin-top: 1.5rem;
            margin-bottom: 1.2rem;
            border-left: 5px solid #2a89a6;
        }
        .section-header h2 {
            margin: 0;
            padding: 0;
            color: #31333F;
            font-size: 2rem;
            font-weight: 600;
        }

        /* KPI Box Style */
        .kpi-box {
            background-color: #2a89a6;
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .kpi-box:hover {
            transform: scale(1.03);
        }
        .kpi-icon {
            font-size: 2.5rem;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        .kpi-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
            line-height: 1.2;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
        }

        /* White KPI Cards - konsisten dengan kpi-box */
        .white-kpi-card {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 10px; /* Sama seperti kpi-box */
            padding: 1rem;
            text-align: center;
            height: 160px; /* Sama seperti kpi-box */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Sama seperti kpi-box */
            transition: transform 0.2s;
        }

        .white-kpi-card:hover {
            transform: scale(1.03); /* Efek hover sama seperti kpi-box */
        }

        .white-kpi-card .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
            color: #2a89a6;
            margin-bottom: 0.3rem;
        }

        .white-kpi-card .kpi-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.2rem;
            line-height: 1.2;
            color: #333;
        }

        .white-kpi-card .kpi-description {
            font-size: 0.9rem;
            color: #555;
            line-height: 1.2;
            margin-top: 0.3rem;
        }

        /* Insight Box di samping peta */
        .insight-box {
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin-bottom: 0.8rem;
            border-left: 5px solid;
            text-align: center;
        }
        .insight-box h4 {
            margin: 0 0 0.2rem 0;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            color: #555;
        }
        .insight-box .kecamatan-name {
            margin: 0;
            font-size: 1.2rem;
            font-weight: 700;
            color: #333;
        }
        .insight-box .value {
            font-size: 1rem;
            font-weight: 500;
            color: #444;
        }
        .insight-box-good {
            border-color: #28a745;
            background-color: #f0fff4;
        }
        .insight-box-bad {
            border-color: #ffeeba;
            background-color: #fff3cd;
        }

        /* Custom Alerts for Trend Section */
        .custom-alert {
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            border: 1px solid transparent;
            border-radius: .375rem;
            font-size: 0.9rem;
        }
        .custom-alert-success {
            color: #2a89a6;
            background-color: #eef7fa;
            border-color: #bde0eb;
        }
        .custom-alert-info {
            color: #31333F;
            background-color: #f0f2f6;
            border-color: #d6d8db;
        }
        .custom-alert-warning {
            color: #856404;
            background-color: #fff3cd;
            border-color: #ffeeba;
        }
        .custom-alert-error {
            color: #985356;
            background-color: #fff0f0;
            border-color: #c85a5a;
        }

        /* Insight Summary Box */
        .insight-summary-box {
            background-color: #f0f2f6;
            border: 1px solid #d6d8db;
            border-left: 5px solid #2a89a6;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-top: 0.2rem;
        }
        .insight-summary-box ul {
            margin: 0;
            padding-left: 1.2rem;
        }
        .insight-summary-box li {
            margin-bottom: 0.5rem;
            padding-left: 0.5rem;
        }

        /* Sidebar Customization */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }

        .sidebar-header {
            background-color: #2a89a6;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
        }

        .sidebar-header h2 {
            margin: 0;
            font-size: 1.5rem;
        }

        [data-testid="stExpander"] summary {
            font-size: 1.1rem;
            font-weight: 600;
            color: #31333F;
        }

        /* Status Cards */
        .status-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #2a89a6;
        }

        .status-card h4 {
            color: #2a89a6;
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
        }

        .status-card p {
            margin: 0;
            color: #495057;
            font-size: 0.9rem;
        }

        /* Metric Cards */
        .metric-card {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .metric-card .metric-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #2a89a6;
            margin-bottom: 0.3rem;
        }

        .metric-card .metric-label {
            font-size: 0.85rem;
            color: #6c757d;
            font-weight: 500;
        }

        /* Filter Info Box */
        .filter-info {
            background-color: #e8f4f8;
            border: 1px solid #b3d9e6;
            border-radius: 8px;
            padding: 0.75rem;
            margin: 1rem 0;
            font-size: 0.9rem;
            color: #2a89a6;
        }

        /* Chart Container */
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #f8f9fa;
            border-radius: 8px 8px 0px 0px;
            color: #495057;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background-color: #2a89a6;
            color: white;
        }

        /* Data Table Styling */
        .dataframe {
            font-size: 0.9rem;
        }

        /* Custom Button Styling */
        .stButton > button {
            background-color: #2a89a6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: background-color 0.3s;
        }

        .stButton > button:hover {
            background-color: #62718c;
        }
    </style>
    """, unsafe_allow_html=True)

def load_pendidikan_css():
    """Load CSS khusus untuk dashboard pendidikan"""
    st.markdown("""
    <style>
        /* Garis custom lebih rapat */
        .custom-hr {
            border: 0;
            border-top: 1px solid #ddd;
            margin: 0.3rem 0;   /* jarak atas-bawah garis */
        }

        /* Rapikan jarak antar elemen */
        .stMarkdown, .stText, .stMetric, .stPlotlyChart, .stDataFrame {
            margin-top: 0rem;
            margin-bottom: 0.4rem;
            padding: 0rem;
        }

        /* Atur kolom agar sejajar di top */
        div[data-testid="column"] {
            vertical-align: top;
        }

        /* Header Utama */
        .main-header {
            background: linear-gradient(90deg, #62718c 0%, #2a89a6 100%, #62718c 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .main-header h1 { margin-bottom: 0.2rem; font-size: 2.5rem; }
        .main-header h3 { margin-bottom: 0.5rem; font-weight: 500; font-size: 1.2rem; }
        .main-header p { font-style: italic; font-size: 1rem; }

        /* Header untuk setiap seksi */
        .section-header {
            background-color: #f0f2f6;
            padding: 1rem 1rem;
            border-radius: 7px;
            margin-top: 1.5rem;
            margin-bottom: 1.2rem;
            border-left: 5px solid #62718c; /* Aksen warna biru */
        }
        .section-header h2 {
            margin: 0;
            padding: 0;
            color: #31333F;
            font-size: 2rem; /* Ukuran font diperbesar */
            font-weight: 600;  /* Diberi sedikit ketebalan */
        }

        /* KPI Box Style */
        .kpi-box {
            background-color: #62718c; /* Warna abu-abu kebiruan dari palet peta */
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            height: 160px; /* Tinggi tetap untuk keseragaman */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .kpi-box:hover {
            transform: scale(1.03);
        }
        .kpi-icon {
            font-size: 2.5rem;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        .kpi-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
            line-height: 1.2;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
        }

        /* Insight Box di samping peta */
        .insight-box {
            padding: 0.8rem 1rem;
            border-radius: 8px;
            margin-bottom: 0.8rem;
            border-left: 5px solid;
            text-align: center;
        }
        .insight-box h4 {
            margin: 0 0 0.2rem 0;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            color: #555;
        }
        .insight-box .kecamatan-name {
            margin: 0;
            font-size: 1.2rem;
            font-weight: 700;
            color: #333;
        }
        .insight-box .value {
            font-size: 1rem;
            font-weight: 500;
            color: #444;
        }
        .insight-box-good {
            border-color: #28a745; /* Green */
            background-color: #f0fff4; /* Light Green */
        }
        .insight-box-bad {
            border-color: #ffeeba; /* Yellow for warning */
            background-color: #fff3cd; /* Light yellow for warning */
        }

        /* Custom Alerts for Trend Section */
        .custom-alert {
            padding: 0.75rem 1rem;
            margin-bottom: 1rem;
            border: 1px solid transparent;
            border-radius: .375rem;
            font-size: 0.9rem;
        }
        .custom-alert-success {
            color: #004c70; /* Dark Blue */
            background-color: #eef7fa; /* Light Blue */
            border-color: #bde0eb;
        }
        .custom-alert-info {
            color: #31333F; /* Dark Gray */
            background-color: #f0f2f6; /* Light Gray */
            border-color: #d6d8db;
        }
        .custom-alert-warning {
            color: #856404;
            background-color: #fff3cd;
            border-color: #ffeeba;
        }
        .custom-alert-error {
            color: #985356; /* Darker Red from theme */
            background-color: #fff0f0; /* Light Red from theme */
            border-color: #c85a5a; /* Main Red from theme */
        }

        /* Insight Summary Box for Trend Section */
        .insight-summary-box {
            background-color: #f0f2f6; /* Light Gray */
            border: 1px solid #d6d8db;
            border-left: 5px solid #004c70; /* Blue accent */
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-top: 0.2rem; /* Jarak atas dikurangi */
        }
        .insight-summary-box ul {
            margin: 0;
            padding-left: 1.2rem;
        }
        .insight-summary-box li {
            margin-bottom: 0.5rem;
            padding-left: 0.5rem;
        }

        /* Sidebar Customization */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }

        .sidebar-header {
            background-color: #62718c;
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            text-align: center;
        }

        .sidebar-header h2 {
            margin: 0;
            font-size: 1.5rem;
        }

        [data-testid="stExpander"] summary {
            font-size: 1.1rem;
            font-weight: 600;
            color: #31333F;
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #f8f9fa;
            border-radius: 8px 8px 0px 0px;
            color: #495057;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background-color: #62718c;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

def load_sosial_css():
    """Load CSS khusus untuk dashboard sosial"""
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
        .main-header h1 { margin-bottom: 0.2rem; font-size: 2.5rem; }
        .main-header h3 { margin-bottom: 0.5rem; font-weight: 500; font-size: 1.2rem; }
        .main-header p { font-style: italic; font-size: 1rem; }
        
        /* Header untuk setiap seksi */
        .section-header {
            background-color: #f0f2f6;
            padding: 1rem 1.5rem 1rem 1rem;
            border-radius: 7px;
            margin-top: 1.5rem;
            margin-bottom: 1.2rem;
            border-left: 5px solid #1e3c72;
        }
        .section-header h2 {
            margin: 0;
            padding: 0;
            color: #31333F;
            font-size: 2rem; /* Ukuran font diperbesar */
            font-weight: 600;  /* Diberi sedikit ketebalan */
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
        
        /* KPI Box Style */
        .kpi-container {
            display: grid;
            grid-template-columns: repeat(5, 1fr); /* Selalu 5 kolom */
            gap: 1rem;
            align-items: stretch; /* Biar tinggi box sama */
        }

        .kpi-box {
            flex: 1;
            background-color: #1e3c72;
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            word-wrap: break-word;
        }
        .kpi-box:hover {
            transform: scale(1.03);
        }
        .kpi-icon {
            font-size: 2.5rem;
            line-height: 1;
            margin-bottom: 0.5rem;
        }
        .kpi-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
            line-height: 1.2;
        }
        .kpi-value {
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
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
        
        /* Instructions */
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
        
        .year-selection-area {
            background-color: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 8px;
            min-height: 50px;
            border: 1px dashed rgba(255, 255, 255, 0.3);
            margin-bottom: 15px;
        }

        /* FILTER PETA */
        .map-filter-container {
            background: rgba(255,255,255,0.95);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .map-filter-header {
            color: #2c3e50;
            font-weight: 700;
            font-size: 1.1rem;
            margin: 0 0 15px 0;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .filter-info-box {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
            color: #1565c0;
            font-size: 0.9rem;
            margin-top: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .filter-info-box strong {
            color: #0d47a1;
        }
        
        /* Styling untuk selectbox */
        .stSelectbox > div > div {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border: 2px solid #e9ecef;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stSelectbox > div > div:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        }
        
        .stSelectbox label {
            font-weight: 600;
            color: #2c3e50;
            font-size: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)