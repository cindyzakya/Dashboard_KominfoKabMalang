"""
Constants and mappings used throughout the application - LENGKAP
"""

# Map Configuration
MAP_CENTER = {
    "lat": -8.1,
    "lon": 112.6
}

MAP_ZOOM_DEFAULT = 8

# Jenis Bencana Mapping
JENIS_BENCANA_MAPPING = {
    "Gempa_Bumi": "Gempa Bumi",
    "Tsunami": "Tsunami", 
    "Banjir": "Banjir",
    "Tanah_Longsor": "Tanah Longsor",
    "Letusan_Gunung_Api": "Letusan Gunung Api",
    "Kekeringan": "Kekeringan",
    "Gelombang_Ekstrem_dan_Abrasi": "Gelombang Ekstrem dan Abrasi",
    "Cuaca_Ekstrem_Angin_Puting_Beliung": "Cuaca Ekstrem Angin Puting Beliung",
    "Kebakaran_Hutan_dan_Lahan": "Kebakaran Hutan dan Lahan",
    "Kebakaran_Gedung_dan_Pemukiman": "Kebakaran Gedung dan Pemukiman",
    "Epidemi_dan_Wabah_Penyakit": "Epidemi dan Wabah Penyakit",
    "Gagal_Teknologi": "Gagal Teknologi",
    "Konflik_Sosial": "Konflik Sosial",
    "Angin_Kencang": "Angin Kencang",
    "Kebakaran": "Kebakaran",
    "Erupsi_Gunung_Api": "Erupsi Gunung Api",
    "Pohon_Tumbang": "Pohon Tumbang"
}

# Label Mapping untuk Pendidikan
PENDIDIKAN_LABEL_MAPPING = {
    "apk": "Angka Partisipasi Kasar (APK)",
    "apm": "Angka Partisipasi Murni (APM)",
    "persentase_guru_s1": "Persentase Guru S1",
    "persentase_sekolah_akreditasi": "Persentase Sekolah Terakreditasi",
    "jumlah_siswa": "Jumlah Siswa",
    "jumlah_sekolah": "Jumlah Sekolah",
    "jumlah_penduduk_usia_sekolah": "Jumlah Penduduk Usia Sekolah",
    "rasio_sekolah_penduduk": "Rasio Sekolah per 1000 Penduduk"
}

# Koordinat Kecamatan Kabupaten Malang
KECAMATAN_COORDINATES = {
    'Dau': [-7.9167, 112.5833],
    'Pujon': [-7.8667, 112.4833],
    'Ngantang': [-7.7667, 112.4333],
    'Kasembon': [-7.8167, 112.3833],
    'Singosari': [-7.8833, 112.6667],
    'Lawang': [-7.8333, 112.6833],
    'Pakisaji': [-8.0667, 112.6167],
    'Tajinan': [-8.1500, 112.5833],
    'Tumpang': [-8.0167, 112.7333],
    'Pakis': [-7.9333, 112.7167],
    'Jabung': [-8.0833, 112.7833],
    'Wajak': [-8.1167, 112.7333],
    'Dampit': [-8.2167, 112.7500],
    'Tirtoyudo': [-8.3333, 112.6833],
    'Ampelgading': [-8.2833, 112.6167],
    'Poncokusumo': [-8.0500, 112.7833],
    'Wagir': [-8.0333, 112.5500],
    'Karangploso': [-7.9167, 112.6000],
    'Gondanglegi': [-8.1500, 112.6833],
    'Kepanjen': [-8.1333, 112.5833],
    'Sumberpucung': [-8.1000, 112.4833],
    'Sumbermanjing Wetan': [-8.3500, 112.5833],
    'Donomulyo': [-8.4000, 112.5000],
    'Pagak': [-8.3667, 112.4500],
    'Bantur': [-8.3167, 112.5167],
    'Turen': [-8.1667, 112.6000],
    'Kalipare': [-8.2000, 112.5500],
    'Bululawang': [-8.0833, 112.6000],
    'Ngajum': [-8.1167, 112.5167],
    'Gedangan': [-8.0667, 112.7667],
    'Kromengan': [-8.1833, 112.5667],
    'Wonosari': [-8.2833, 112.5167],
    'Pagelaran': [-8.3167, 112.4833]
}

# Month Order
MONTH_ORDER = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]

# Color Palettes
COLOR_PALETTES = {
    'default': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
    'health': ['#2a89a6', '#62718c', '#574249', '#ad9ea5', '#e4acac'],
    'social': ['#1e3c72', '#2a5298', '#667eea', '#764ba2'],
    'education': ['#004c70', '#62718c', '#2a89a6']
}

# Status Messages
STATUS_MESSAGES = {
    'loading': '📊 Loading data...',
    'error': '❌ Error loading data',
    'success': '✅ Data loaded successfully',
    'no_data': '⚠️ No data available',
    'filtered_empty': '🔍 No data matches current filters'
}

# File Paths (relative to project root)
DATA_FILES = {
    'kesehatan': 'data/kesehatan/kesehatan_stunting.csv',
    'pendidikan': 'data/pendidikan/pendidikan_paud_sd_smp.csv',
    'sosial': {
        'bantuan_sosial': 'data/sosial/bantuan_sosial.csv',
        'bencana_alam': 'data/sosial/bencana_alam.csv',
        'kekerasan_anak': 'data/sosial/kekerasan_anak.csv',
        'kekerasan_perempuan': 'data/sosial/bentuk_kekerasan_perempuan.csv',
        'kb_performance': 'data/sosial/data_kb_performance.csv',
        'peserta_kb': 'data/sosial/peserta_kb.csv'
    },
    'geo': {
        'kecamatan': 'data/geo/35.07_kecamatan.geojson',
        'kelurahan': 'data/geo/35.07_kelurahan.geojson',
        'malang': 'data/geo/35.07_Malang.geojson'
    }
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'kesehatan': {
        'title': 'Dashboard Kesehatan',
        'icon': '🏥',
        'color_scheme': 'health',
        'primary_color': '#2a89a6'
    },
    'sosial': {
        'title': 'Dashboard Sosial',
        'icon': '👥', 
        'color_scheme': 'social',
        'primary_color': '#1e3c72'
    },
    'pendidikan': {
        'title': 'Dashboard Pendidikan',
        'icon': '🎓',
        'color_scheme': 'education', 
        'primary_color': '#004c70'
    }
}

# Validation Rules
VALIDATION_RULES = {
    'required_columns': {
        'kesehatan': ['Tahun', 'Kecamatan', 'Stunting', 'Prevalensi Stunting'],
        'pendidikan': ['Tahun', 'Jenjang', 'Kecamatan', 'APK (%)', 'APM (%)'],
        'sosial': ['Tahun', 'Kecamatan']
    },
    'numeric_columns': {
        'kesehatan': ['Stunting', 'Jumlah Yang Diukur'],
        'pendidikan': ['APK (%)', 'APM (%)'],
        'sosial': ['Jumlah_Kasus', 'Jumlah_Penerima']
    }
}

# Default Values
DEFAULT_VALUES = {
    'year_range': [2020, 2024],
    'cache_ttl': 300,  # 5 minutes for development
    'max_display_rows': 1000,
    'decimal_places': 2
}