"""
Konfigurasi untuk YouTube API
"""

# Path ke file OAuth credentials
CLIENT_SECRETS_FILE = "client_secret.json"

# Scopes yang dibutuhkan
# Read-only untuk export
SCOPES_READ = ['https://www.googleapis.com/auth/youtube.readonly']
# Write access untuk import (subscribe)
SCOPES_WRITE = ['https://www.googleapis.com/auth/youtube.force-ssl']

# File output default
DEFAULT_OUTPUT_DIR = "exports"
DEFAULT_CSV_FILE = "subscribers.csv"
DEFAULT_JSON_FILE = "subscribers.json"

