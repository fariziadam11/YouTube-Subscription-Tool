# Fix Error 403: access_denied

Error ini terjadi karena email Anda belum ditambahkan ke **Test Users** di OAuth Consent Screen.

## Solusi Cepat

### Step 1: Buka OAuth Consent Screen

1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Pastikan project yang benar dipilih (YouTube Subscription Tool)
3. Di menu kiri, klik **"APIs & Services"** > **"OAuth consent screen"**

### Step 2: Tambahkan Email ke Test Users

1. Scroll ke bawah sampai bagian **"Test users"**
2. Klik tombol **"ADD USERS"** (atau "+ ADD USERS")
3. Masukkan **email yang ingin Anda gunakan** (untuk login YouTube)
   - Jika export dari akun lama: masukkan email akun lama
   - Jika import ke akun baru: masukkan email akun baru
   - **BEST PRACTICE:** Tambahkan KEDUA email (lama dan baru) sekaligus
4. Klik **"ADD"**
5. Klik **"SAVE"** jika ada tombol save

### Step 3: Coba Lagi

1. Kembali ke terminal dan jalankan script lagi
2. Login dengan email yang sudah ditambahkan ke Test Users
3. Seharusnya sudah bisa akses

## Catatan Penting

- **Jika export dari akun lama:** Tambahkan email akun lama ke Test Users
- **Jika import ke akun baru:** Tambahkan email akun baru ke Test Users
- **Lebih baik:** Tambahkan KEDUA email sekaligus supaya tidak perlu setup lagi nanti

## Troubleshooting

### Masih Error Setelah Menambahkan?

1. **Pastikan email sudah benar:**
   - Email harus sama persis dengan yang digunakan untuk login Google
   - Cek apakah ada typo

2. **Pastikan sudah save:**
   - Setelah ADD, pastikan ada tombol SAVE dan klik
   - Tunggu beberapa detik agar perubahan tersimpan

3. **Hapus token lama (jika perlu):**
   ```bash
   # Hapus file token jika ada
   del token_export.pickle
   del token_import.pickle
   ```
   Lalu jalankan script lagi

4. **Cek OAuth Consent Screen Settings:**
   - Pastikan "Publishing status" masih "Testing"
   - User type harus "External" untuk personal use
   - Scopes harus sudah ditambahkan: `youtube.readonly` dan `youtube.force-ssl`

### Untuk Production (Opsional)

Jika ingin app bisa diakses semua orang tanpa perlu menambahkan test users:
1. Di OAuth Consent Screen, ubah "Publishing status" dari "Testing" ke "In production"
2. **PERINGATAN:** Untuk ini perlu verifikasi dari Google (butuh waktu beberapa hari)
3. Untuk personal use, cukup pakai Test Users saja (lebih cepat)

