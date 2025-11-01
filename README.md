# YouTube Subscription Export & Import Tool

Tool untuk mengekspor daftar channel yang sudah di-subscribe dari akun YouTube lama, lalu mengimpornya ke akun YouTube baru agar tidak perlu subscribe manual lagi.

## Fitur

- ✅ Export daftar channel yang sudah di-subscribe dari akun lama
- ✅ Import otomatis ke akun YouTube baru
- ✅ Export ke format CSV dan JSON
- ✅ Progress tracking dengan summary hasil
- ✅ Rate limiting untuk menghindari API limit
- ✅ Handle channel yang sudah di-subscribe

## Alur Lengkap

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Setup YouTube API Credentials

**A. Buat Project di Google Cloud Console**

1. Buka https://console.cloud.google.com/
2. Login dengan akun Google (bisa pakai akun lama atau baru)
3. Buat project baru:
   - Klik "NEW PROJECT"
   - Isi nama project (contoh: "YouTube Subscription Tool")
   - Klik "CREATE"

**B. Enable YouTube Data API v3**

1. Di Google Cloud Console, pilih project yang baru dibuat
2. Di search bar, ketik "YouTube Data API v3"
3. Klik pada "YouTube Data API v3"
4. Klik tombol "ENABLE"

**C. Buat OAuth 2.0 Credentials**

1. Di menu kiri, klik "Credentials"
2. Klik "CREATE CREDENTIALS" di atas
3. Pilih "OAuth client ID"
4. Jika diminta setup OAuth consent screen:
   - Pilih "External" (untuk testing)
   - Isi App name: "YouTube Subscription Tool"
   - Isi User support email
   - Tambahkan email Anda di "Developer contact information"
   - Klik "SAVE AND CONTINUE"
   - Di Scopes, klik "ADD OR REMOVE SCOPES"
     - Pilih: `youtube.readonly` dan `youtube.force-ssl`
     - Klik "UPDATE" lalu "SAVE AND CONTINUE"
   - Di Test users, tambahkan **KEDUA email** (email lama dan baru)
   - Klik "SAVE AND CONTINUE"
5. Back ke Create OAuth Client ID:
   - Application type: pilih **"Desktop app"**
   - Name: "Subscription Tool"
   - Klik "CREATE"
6. Download credentials:
   - Klik tombol **"DOWNLOAD JSON"**
   - Rename file menjadi `client_secret.json`
   - Letakkan di folder project ini

### Step 3: Export dari Akun Lama

```bash
python export_subscriptions.py
```

**Proses:**
1. Browser otomatis terbuka → Login dengan **akun YouTube LAMA**
2. Klik "Allow" untuk memberikan akses
3. Script otomatis mengambil semua channel yang sudah di-subscribe
4. File tersimpan di `exports/subscriptions_YYYYMMDD_HHMMSS.json` dan `.csv`

**Output:**
- File JSON berisi semua data subscriptions
- File CSV untuk preview/editing di Excel

### Step 4: Import ke Akun Baru

```bash
python import_subscriptions.py
```

**Proses:**
1. Script menampilkan daftar file export yang tersedia
2. Pilih file yang ingin diimport
3. Browser otomatis terbuka → Login dengan **akun YouTube BARU**
4. Klik "Allow" untuk memberikan akses
5. Script otomatis subscribe ke semua channel dalam file
6. Progress ditampilkan real-time dengan summary di akhir

**Features:**
- Delay antar subscribe (default 1 detik) untuk menghindari rate limit
- Skip channel yang sudah di-subscribe
- Simpan daftar channel yang gagal (jika ada)

## Contoh Penggunaan

### Export dari Akun Lama

```bash
$ python export_subscriptions.py

============================================================
YouTube Subscription Exporter
Export daftar channel yang sudah di-subscribe
============================================================

⚠️  PENTING: Login dengan akun YouTube LAMA

✅ Berhasil terhubung ke YouTube API
📋 Mengambil daftar channel yang sudah di-subscribe...
⏳ Mohon tunggu...
  ✓ Mengambil 50 subscriptions...
  ✓ Mengambil 100 subscriptions...

✅ Berhasil mengambil 127 subscriptions

✨ Export selesai! Total 127 subscriptions diekspor.
📁 File tersimpan di folder: exports/
```

### Import ke Akun Baru

```bash
$ python import_subscriptions.py

============================================================
YouTube Subscription Importer
Import daftar subscription ke akun YouTube baru
============================================================

⚠️  PENTING: Login dengan akun YouTube BARU

📁 File export yang tersedia:

   1. subscriptions_20241215_143022.json
      (2024-12-15 14:30:22)

Pilih file (1-1): 1

📄 File yang dipilih: subscriptions_20241215_143022.json
📊 Total subscriptions dalam file: 127

📋 Preview (5 pertama):
   1. Channel A
   2. Channel B
   3. Channel C
   ...

Lanjutkan import? (y/n): y

✅ Berhasil terhubung ke YouTube API

📥 Mulai import 127 subscriptions...
⏳ Proses mungkin memakan waktu beberapa menit...
   Delay: 1.0 detik antar subscribe

[1/127] Subscribing: Channel A... ✅ Berhasil
[2/127] Subscribing: Channel B... ✅ Berhasil
...

============================================================
📊 RINGKASAN IMPORT:
============================================================
✅ Berhasil subscribe: 125
⚠️  Sudah subscribed: 2
❌ Gagal: 0
📊 Total diproses: 127
============================================================
```

## File Structure

```
importsubs/
├── export_subscriptions.py   # Script export (akun lama)
├── import_subscriptions.py   # Script import (akun baru)
├── export_subscribers.py    # Script lama (export subscriber dari channel)
├── config.py                # Konfigurasi
├── utils.py                 # Utility functions
├── requirements.txt         # Dependencies
├── README.md               # Dokumentasi
├── client_secret.json      # OAuth credentials (buat sendiri)
└── exports/                # Folder output
    ├── subscriptions_xxx.json
    └── subscriptions_xxx.csv
```

## Catatan Penting

### Rate Limiting
- YouTube API memiliki rate limit
- Default delay: 1 detik antar subscribe
- Jika terlalu cepat, bisa dapat error 429 (rate limit)
- Disarankan menggunakan delay minimal 0.5 detik

### Error Handling
- Channel yang sudah di-subscribe akan di-skip (tidak error)
- Channel yang gagal akan disimpan di file `failed_import_xxx.json`
- Network error akan ditampilkan di summary

### OAuth Consent Screen
- **PENTING:** Tambahkan **KEDUA email** (lama dan baru) ke Test Users
- Jika tidak, akan muncul error "Access blocked"
- Untuk production, perlu verifikasi dari Google (tapi untuk personal use, test users cukup)

## Troubleshooting

### Error: "Access blocked: This app's request is invalid"
**Solusi:** Pastikan email sudah ditambahkan ke Test Users di OAuth Consent Screen

### Error: "Rate limit exceeded"
**Solusi:** Gunakan delay yang lebih besar (misalnya 2 detik) saat import

### Error: "client_secret.json tidak ditemukan"
**Solusi:** Pastikan file ada di folder root project dan sudah di-rename dengan benar

### Channel tertentu selalu gagal
**Solusi:** 
- Channel mungkin sudah dihapus atau private
- Cek file `failed_import_xxx.json` untuk detail
- Bisa coba subscribe manual untuk channel tersebut

## License

MIT
