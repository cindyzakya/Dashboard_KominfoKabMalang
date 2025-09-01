"""
Layout components for the dashboard
"""

import streamlit as st
from datetime import datetime
from config import *

def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state=APP_SIDEBAR_STATE
    )

def render_main_header():
    """Render main application header"""
    st.markdown(f"""
    <div class="main-header">
        <h1>{APP_ICON} {APP_TITLE}</h1>
        <h2>Sistem Informasi Terpadu Data Kesehatan, Sosial & Pendidikan</h2>
        <p style="font-size: 1.2rem; margin-top: 20px;">
            📊 Platform Analisis Data Interaktif untuk Pengambilan Keputusan Berbasis Data
        </p>
        <p style="font-size: 1rem; opacity: 0.9; margin-top: 10px;">
            Dinas Komunikasi dan Informatika Kabupaten Malang
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Render application footer"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.markdown(f"""
    <div class="footer">
        <h3>{APP_ICON} {APP_TITLE}</h3>
        <p><strong>Dinas Komunikasi dan Informatika Kabupaten Malang</strong></p>
        <p>📧 Email: kominfo@malangkab.go.id | 🌐 Website: malangkab.go.id</p>
        <p><strong>🔗 Data Source:</strong> Kabupaten Malang Satu Data (KAMASUTA) | <strong>🕒 Last Updated: {current_time}</p>
        <hr style="margin: 20px 0; opacity: 0.3;">
        <p style="font-size: 0.9rem; opacity: 0.8;">
            © 2025 Kabupaten Malang. Dashboard ini dibuat untuk mendukung transparansi dan akuntabilitas data publik.
        </p>
        <p style="font-size: 0.8rem; opacity: 0.7;">
            👨‍💻 Developed by: @rosaaurelia, @cindyzakya, @anitamds - PKL Diskominfo Kabupaten Malang Juli-Agustus 2025
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_dashboard_header(title, subtitle, description):
    """Render dashboard page header"""
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        <h3>{subtitle}</h3>
        <p><em>{description}</em></p>
    </div>
    """, unsafe_allow_html=True)

def render_section_header(title, description=None):
    """Render section header"""
    html_string = f'<div class="section-header"><h2>{title}</h2>'
    
    # Secara kondisional tambahkan deskripsi jika ada
    if description:
        # Menggunakan <p> dan <em> untuk deskripsi yang bergaya dan miring
        html_string += f'<p><em>{description}</em></p>'
        
    html_string += '</div>'
    st.markdown(html_string, unsafe_allow_html=True)
    