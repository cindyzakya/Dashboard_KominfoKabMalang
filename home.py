import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import subprocess
import sys
import socket
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Kabupaten Malang",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
        height: 450px;
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
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
    
    .feature-item {
        background: white;
        padding: 25px;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    
    .info-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px;
        border-radius: 15px;
        margin: 40px 0;
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

def check_file_exists(filename):
    """Check if dashboard file exists"""
    return os.path.exists(filename)

def find_available_port(start_port=8502):
    """Find available port starting from start_port"""
    port = start_port
    while port < start_port + 10:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result != 0:
                return port
            port += 1
        except:
            port += 1
    return start_port

def open_dashboard(script_name, dashboard_name):
    """Function to open dashboard in new browser tab"""
    if not check_file_exists(script_name):
        st.error(f"❌ File {script_name} tidak ditemukan!")
        st.info(f"💡 Pastikan file {script_name} ada di directory yang sama dengan home.py")
        return
    
    try:
        port = find_available_port()
        
        # Command untuk Windows
        if os.name == 'nt':  # Windows
            subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", script_name, 
                "--server.port", str(port)
            ], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", script_name, 
                "--server.port", str(port)
            ])
        
        st.success(f"✅ {dashboard_name} sedang dibuka...")
        st.info(f"🌐 URL: http://localhost:{port}")
        st.warning("⏳ Tunggu beberapa detik, dashboard akan terbuka di browser/tab baru")
        
        # Tampilkan link manual jika auto-open gagal
        st.markdown(f"""
        <div style="margin-top: 15px;">
            <p>Jika tidak terbuka otomatis, klik link berikut:</p>
            <a href="http://localhost:{port}" target="_blank" class="manual-link">
                🔗 Buka {dashboard_name} Manual
            </a>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error membuka {dashboard_name}: {str(e)}")
        st.info(f"💡 Coba jalankan manual dengan command: `streamlit run {script_name}`")

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏛️ Dashboard Kabupaten Malang</h1>
        <h2>Sistem Informasi Terpadu Data Kesehatan, Sosial & Pendidikan</h2>
        <p style="font-size: 1.2rem; margin-top: 20px;">
            📊 Platform Analisis Data Interaktif untuk Pengambilan Keputusan Berbasis Data
        </p>
        <p style="font-size: 1rem; opacity: 0.9; margin-top: 10px;">
            Dinas Komunikasi dan Informatika Kabupaten Malang
        </p>
        <div style="margin-top: 20px;">
            <a href="https://github.com/cindyzakya/Dashboard_KominfokabMalang" target="_blank" class="github-link">
                🔗 GitHub Repository
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # File Status Check
    st.markdown("## 📁 Status File Dashboard")
    
    files_to_check = [
        ("dashboard_kesehatan.py", "Dashboard Kesehatan"),
        ("dashboard_sosial.py", "Dashboard Sosial"), 
        ("dashboard_pendidikan.py", "Dashboard Pendidikan")
    ]
    
    col1, col2, col3 = st.columns(3)
    file_status = {}
    
    for i, (filename, name) in enumerate(files_to_check):
        exists = check_file_exists(filename)
        file_status[filename] = exists
        
        with [col1, col2, col3][i]:
            if exists:
                st.success(f"✅ {name}")
            else:
                st.error(f"❌ {name}")
    
    # Stats Section
    st.markdown("""
    <div class="stats-container">
        <h2 style="text-align: center; margin-bottom: 30px;">📈 Statistik Dashboard</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        available_dashboards = sum(file_status.values())
        st.markdown(f"""
        <div class="stat-item">
            <div class="stat-number">{available_dashboards}</div>
            <div class="stat-label">Dashboard Tersedia</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-item">
            <div class="stat-number">25+</div>
            <div class="stat-label">Jenis Visualisasi</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-item">
            <div class="stat-number">2020-2024</div>
            <div class="stat-label">Rentang Data</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-item">
            <div class="stat-number">33</div>
            <div class="stat-label">Kecamatan</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Dashboard Selection
    st.markdown("## 🎯 Pilih Dashboard")
    st.markdown("Klik tombol di bawah untuk membuka dashboard di tab browser baru:")
    
    # 3 Dashboard Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <div>
                <div class="card-icon">🏥</div>
                <div class="card-title">Dashboard Kesehatan</div>
                <div class="card-description">
                    Analisis komprehensif data stunting, fasilitas kesehatan, dan tren kesehatan masyarakat di Kabupaten Malang.
                    <br><br>
                    <strong>Fitur Utama:</strong><br>
                    • Analisis Data Stunting & Prevalensi<br>
                    • Analisis Tren Prevalensi <br>
                    • Analisis Perubahan Prevalensi<br>
                    • Analisis Korelasi & Komposisi<br>
                    • Data Fasilitas Kesehatan & Sebaran
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Buka Dashboard Kesehatan", key="health", use_container_width=True, 
                    disabled=not file_status.get("dashboard_kesehatan.py", False)):
            open_dashboard("dashboard_kesehatan.py", "Dashboard Kesehatan")
    
    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <div>
                <div class="card-icon">👥</div>
                <div class="card-title">Dashboard Sosial</div>
                <div class="card-description">
                    Monitoring data sosial meliputi bantuan sosial, bencana alam, kekerasan, dan program KB dengan insight otomatis.
                    <br><br>
                    <strong>Fitur Utama:</strong><br>
                    • Data Bantuan Sosial & Penerima<br>
                    • Analisis Bencana Alam & Kerugian<br>
                    • Monitoring Kekerasan Gender & Anak<br>
                    • Program KB & Jenis Kontrasepsi<br>
                    • Filter Tahun Dinamis & KPI Real-time
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Buka Dashboard Sosial", key="social", use_container_width=True,
                    disabled=not file_status.get("dashboard_sosial.py", False)):
            open_dashboard("dashboard_sosial.py", "Dashboard Sosial")
    
    with col3:
        st.markdown("""
        <div class="dashboard-card">
            <div>
                <div class="card-icon">🎓</div>
                <div class="card-title">Dashboard Pendidikan</div>
                <div class="card-description">
                    Analisis data pendidikan dari PAUD hingga SMP, termasuk data siswa, guru, sekolah, dan infrastruktur pendidikan.
                    <br><br>
                    <strong>Fitur Utama:</strong><br>
                    • Data Siswa & Guru per Jenjang<br>
                    • Infrastruktur & Fasilitas Sekolah<br>
                    • Tren Pendidikan PAUD-SD-SMP<br>
                    • Analisis Rasio Siswa-Guru<br>
                    • Mapping Sebaran Sekolah
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Buka Dashboard Pendidikan", key="education", use_container_width=True,
                    disabled=not file_status.get("dashboard_pendidikan.py", False)):
            open_dashboard("dashboard_pendidikan.py", "Dashboard Pendidikan")
    
    # Manual Commands
    st.markdown("---")
    st.markdown("## 🔧 Perintah Manual")
    st.markdown("Jika tombol tidak berfungsi, gunakan perintah berikut di Command Prompt/Terminal:")
    
    manual_col1, manual_col2, manual_col3 = st.columns(3)
    
    with manual_col1:
        st.code("streamlit run dashboard_kesehatan.py", language="bash")
    
    with manual_col2:
        st.code("streamlit run dashboard_sosial.py", language="bash")
    
    with manual_col3:
        st.code("streamlit run dashboard_pendidikan.py", language="bash")
    
    # Quick Access Section
    st.markdown("---")
    st.markdown("## ⚡ Akses Cepat")
    
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        if st.button("📊 Analisis Stunting", use_container_width=True):
            if file_status.get("dashboard_kesehatan.py", False):
                open_dashboard("dashboard_kesehatan.py", "Dashboard Kesehatan")
            else:
                st.error("❌ File dashboard_kesehatan.py tidak ditemukan!")
    
    with quick_col2:
        if st.button("🌊 Data Bencana", use_container_width=True):
            if file_status.get("dashboard_sosial.py", False):
                open_dashboard("dashboard_sosial.py", "Dashboard Sosial")
            else:
                st.error("❌ File dashboard_sosial.py tidak ditemukan!")
    
    with quick_col3:
        if st.button("🎓 Data Pendidikan", use_container_width=True):
            if file_status.get("dashboard_pendidikan.py", False):
                open_dashboard("dashboard_pendidikan.py", "Dashboard Pendidikan")
            else:
                st.error("❌ File dashboard_pendidikan.py tidak ditemukan!")
    
    # Instructions
    st.markdown("---")
    st.markdown("## 📖 Petunjuk Penggunaan")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 Cara Menggunakan:
        1. **Pastikan semua file dashboard ada** (cek status di atas)
        2. **Klik tombol dashboard** yang ingin Anda akses
        3. **Dashboard akan terbuka** di browser/tab baru
        4. **Setiap dashboard** berjalan di port berbeda
        5. **Gunakan filter** untuk analisis spesifik
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Troubleshooting:
        - **File tidak ditemukan:** Pastikan file ada di folder yang sama
        - **Port sudah digunakan:** Dashboard akan mencari port lain otomatis
        - **Browser tidak terbuka:** Gunakan link manual yang muncul
        - **Error lain:** Gunakan perintah manual di Command Prompt
        """)
    
    # Footer
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="footer">
        <h3>🏛️ Dashboard Kabupaten Malang</h3>
        <p><strong>Dinas Komunikasi dan Informatika Kabupaten Malang</strong></p>
        <p>📧 Email: kominfo@malangkab.go.id | 🌐 Website: malangkab.go.id</p>
        <p>🔗 GitHub: <a href="https://github.com/cindyzakya/Dashboard_KominfokabMalang" target="_blank" style="color: #3498db;">Dashboard_KominfokabMalang</a></p>
        <p>🕒 Last Updated: {current_time}</p>
        <hr style="margin: 20px 0; opacity: 0.3;">
        <p style="font-size: 0.9rem; opacity: 0.8;">
            © 2024 Kabupaten Malang. Dashboard ini dibuat untuk mendukung transparansi dan akuntabilitas data publik.
        </p>
        <p style="font-size: 0.8rem; opacity: 0.7;">
            👨‍💻 Developed by: @rosaaurelia, @cindyzakya, @anitamds - PKL Team Dinas Kominfo
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()