"""
Dashboard Kabupaten Malang - Aplikasi Utama
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Import dengan error handling
try:
    from config import *
    from src.components.layouts import setup_page_config, render_main_header, render_footer
    from src.components.cards import create_dashboard_card
    from src.utils.helpers import check_file_exists
    from src.styles.main import load_main_css
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# --- Konfigurasi Dashboard ---
DASHBOARD_PAGES = [
    {
        "file": "pages/dashboard_kesehatan.py",
        "title": "Dashboard Kesehatan",
        "icon": "🏥",
        "description": "Analisis komprehensif data stunting, fasilitas kesehatan, dan tren kesehatan masyarakat.",
        "features": [
            "Analisis Data Stunting & Prevalensi",
            "Analisis Tren Prevalensi",
            "Analisis Perubahan Prevalensi",
            "Analisis Korelasi & Komposisi",
            "Data Fasilitas Kesehatan & Sebaran"
        ],
        "page_key": "kesehatan"
    },
    {
        "file": "pages/dashboard_sosial.py",
        "title": "Dashboard Sosial",
        "icon": "👥",
        "description": "Monitoring data sosial meliputi bantuan sosial, bencana alam, kekerasan, dan program KB.",
        "features": [
            "Data Bantuan Sosial & Penerima",
            "Analisis Bencana Alam & Kerugian",
            "Monitoring Kekerasan Gender & Anak",
            "Program KB & Jenis Kontrasepsi",
            "Filter Tahun Dinamis & KPI Real-time"
        ],
        "page_key": "sosial"
    },
    {
        "file": "pages/dashboard_pendidikan.py",
        "title": "Dashboard Pendidikan",
        "icon": "🎓",
        "description": "Analisis data pendidikan dari PAUD hingga SMP, termasuk data siswa, guru, dan infrastruktur.",
        "features": [
            "Data Siswa & Guru per Jenjang",
            "Infrastruktur & Fasilitas Sekolah",
            "Tren Pendidikan PAUD-SD-SMP",
            "Analisis Rasio Siswa-Guru",
            "Mapping Sebaran Sekolah"
        ],
        "page_key": "pendidikan"
    }
]

# --- Fungsi Render ---

def main():
    """Main application function"""
    
    # Setup page configuration
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state=APP_SIDEBAR_STATE
    )
    
    # Load CSS
    load_main_css()

    # Hide sidebar on this specific page
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Render header
    render_main_header()
    
    # Render file status and get the status dictionary
    file_status = render_file_status(DASHBOARD_PAGES)
    
    # Render statistics section
    render_statistics(file_status)
    
    # Render dashboard selection cards
    render_dashboard_cards(DASHBOARD_PAGES)
    
    # Footer
    render_footer()

def render_file_status(pages):
    """Renders the file status section and returns a status dictionary."""
    st.markdown("## 📁 Status Dashboard")
    cols = st.columns(len(pages))
    file_status = {}
    
    for i, page in enumerate(pages):
        exists = check_file_exists(page["file"])
        file_status[page["file"]] = exists
        with cols[i]:
            if exists:
                st.success(f"✅ {page['title']}")
            else:
                st.error(f"❌ {page['title']}")
    return file_status

def render_stat_item(value, label):
    """Renders a single statistic item."""
    st.markdown(f"""
    <div class="stat-item">
        <div class="stat-number">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def render_statistics(file_status):
    """Renders the main statistics section."""
    st.markdown("""
    <div class="stats-container">
        <h2 style="text-align: center; margin-bottom: 30px;">📈 Statistik Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(4)
    with cols[0]:
        available_dashboards = sum(file_status.values())
        render_stat_item(available_dashboards, "Dashboard Tersedia")
    with cols[1]:
        render_stat_item("10+", "Jenis Visualisasi")
    with cols[2]:
        render_stat_item("2020-2024", "Rentang Data")
    with cols[3]:
        render_stat_item("33", "Kecamatan")

def render_dashboard_cards(pages):
    """Renders the dashboard selection cards."""
    st.markdown("## 🎯 Pilih Dashboard")
    st.markdown("Klik kartu di bawah untuk membuka dashboard:")
    
    cols = st.columns(len(pages))
    for i, page in enumerate(pages):
        with cols[i]:
            # Buat salinan dictionary dan hapus kunci 'file' yang tidak dibutuhkan oleh create_dashboard_card
            card_args = page.copy()
            card_args.pop('file', None)  # Hapus 'file', None sebagai default jika tidak ada
            create_dashboard_card(**card_args)

if __name__ == "__main__":
    main()