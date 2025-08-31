"""
Application settings and configuration
"""

import os
from pathlib import Path

# Application Information
APP_NAME = "Dashboard Kabupaten Malang"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Sistem Informasi Terpadu Data Kesehatan, Sosial & Pendidikan"

# Developer Information
DEVELOPERS = [
    {"name": "@rosaaurelia", "role": "Frontend Developer"},
    {"name": "@cindyzakya", "role": "Backend Developer"}, 
    {"name": "@anitamds", "role": "Data Analyst"}
]

# Contact Information
CONTACT_INFO = {
    "email": "kominfo@malangkab.go.id",
    "website": "malangkab.go.id",
    "phone": "+62-341-123456",
    "address": "Jl. Merdeka No. 1, Malang, Jawa Timur"
}

# GitHub Information
GITHUB_REPO = "https://github.com/cindyzakya/Dashboard_KominfokabMalang"

# Data Update Schedule
DATA_UPDATE_SCHEDULE = {
    "kesehatan": "Monthly",
    "sosial": "Quarterly", 
    "pendidikan": "Annually"
}

# Feature Flags
FEATURES = {
    "enable_download": True,
    "enable_print": True,
    "enable_sharing": True,
    "enable_export": True,
    "enable_real_time": False,
    "enable_notifications": False
}

# Performance Settings
PERFORMANCE = {
    "cache_ttl": 3600,  # 1 hour
    "max_rows_display": 1000,
    "pagination_size": 50,
    "chart_max_points": 500
}

# Security Settings
SECURITY = {
    "enable_auth": False,
    "session_timeout": 3600,
    "max_file_size": "10MB",
    "allowed_file_types": [".csv", ".xlsx", ".json"]
}

# Logging Configuration
LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/dashboard.log",
    "max_size": "10MB",
    "backup_count": 5
}

# Database Configuration (for future use)
DATABASE = {
    "type": "sqlite",
    "name": "dashboard.db",
    "host": "localhost",
    "port": 5432,
    "user": "dashboard_user",
    "password": os.getenv("DB_PASSWORD", "")
}

# API Configuration (for future use)
API = {
    "base_url": "https://api.malangkab.go.id",
    "timeout": 30,
    "retry_attempts": 3,
    "rate_limit": 100  # requests per minute
}

# Notification Settings (for future use)
NOTIFICATIONS = {
    "email_enabled": False,
    "sms_enabled": False,
    "push_enabled": False,
    "webhook_url": ""
}

# Backup Settings
BACKUP = {
    "enabled": True,
    "schedule": "daily",
    "retention_days": 30,
    "backup_path": "backups/"
}