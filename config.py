"""
Konfigurasi utama aplikasi Dashboard Kabupaten Malang
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Data paths
GEO_DATA_PATH = DATA_DIR / "geo"
KESEHATAN_DATA_PATH = DATA_DIR / "kesehatan"
PENDIDIKAN_DATA_PATH = DATA_DIR / "pendidikan"
SOSIAL_DATA_PATH = DATA_DIR / "sosial"

# Application settings
APP_TITLE = "Dashboard Kabupaten Malang"
APP_ICON = "🏛️"
APP_LAYOUT = "wide"
APP_SIDEBAR_STATE = "collapsed"

# Page configuration
PAGES_CONFIG = {
    "kesehatan": {
        "title": "Dashboard Kesehatan",
        "icon": "🏥",
        "description": "Analisis Data Stunting dan Fasilitas Kesehatan"
    },
    "sosial": {
        "title": "Dashboard Sosial", 
        "icon": "👥",
        "description": "Monitoring Data Bantuan Sosial, Bencana, dan Kekerasan"
    },
    "pendidikan": {
        "title": "Dashboard Pendidikan",
        "icon": "🎓", 
        "description": "Analisis Data Pendidikan PAUD, SD, dan SMP"
    }
}

# Map configuration
MAP_CENTER = {
    "lat": -8.1,
    "lon": 112.6
}
MAP_ZOOM = 8

# Color schemes
COLOR_SCHEMES = {
    "primary": "#2a89a6",
    "secondary": "#62718c", 
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8"
}

# Development vs Production
IS_PRODUCTION = os.getenv("STREAMLIT_ENV") == "production"
DEBUG = not IS_PRODUCTION

# Hosting configuration
if IS_PRODUCTION:
    # Konfigurasi untuk hosting di web Kabupaten Malang
    BASE_URL = "https://dashboard.malangkab.go.id"  # Sesuaikan dengan URL hosting
    CACHE_TTL = 3600  # 1 hour cache in production
else:
    # Konfigurasi untuk development
    BASE_URL = "http://localhost:8501"
    CACHE_TTL = 300  # 5 minutes cache in development