"""
Script untuk import daftar subscription ke akun YouTube baru
"""

import os
import sys
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import time
from config import CLIENT_SECRETS_FILE, SCOPES_WRITE, DEFAULT_OUTPUT_DIR
from utils import get_timestamp


class YouTubeSubscriptionImporter:
    """Class untuk import subscriptions ke akun YouTube baru"""
    
    def __init__(self):
        self.youtube = None
        self.credentials = None
        
    def authenticate(self, scopes):
        """Authentikasi dengan YouTube API menggunakan OAuth 2.0"""
        creds = None
        
        # File token untuk write access
        token_file = 'token_import.pickle'
        
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Jika tidak ada credentials yang valid, lakukan OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CLIENT_SECRETS_FILE):
                    print(f"❌ Error: File {CLIENT_SECRETS_FILE} tidak ditemukan!")
                    print("\nSilakan:")
                    print("1. Buka Google Cloud Console")
                    print("2. Enable YouTube Data API v3")
                    print("3. Buat OAuth 2.0 credentials")
                    print("4. Download sebagai client_secret.json")
                    sys.exit(1)
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE, scopes)
                creds = flow.run_local_server(port=0)
            
            # Simpan credentials untuk penggunaan selanjutnya
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✅ Berhasil terhubung ke YouTube API")
    
    def load_subscriptions_from_file(self, filepath):
        """Load subscriptions dari file JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle format baru (dengan metadata) atau format lama (array langsung)
            if isinstance(data, dict) and 'subscriptions' in data:
                return data['subscriptions']
            elif isinstance(data, list):
                return data
            else:
                print("❌ Format file tidak valid")
                return []
                
        except Exception as e:
            print(f"❌ Error membaca file: {e}")
            return []
    
    def import_subscription(self, channel_id):
        """Subscribe ke satu channel"""
        try:
            self.youtube.subscriptions().insert(
                part='snippet',
                body={
                    'snippet': {
                        'resourceId': {
                            'kind': 'youtube#channel',
                            'channelId': channel_id
                        }
                    }
                }
            ).execute()
            return True
        except Exception as e:
            error_msg = str(e)
            if 'duplicate' in error_msg.lower() or '409' in error_msg:
                return 'already_subscribed'
            return False
    
    def import_subscriptions(self, subscriptions, delay=1.0):
        """
        Import semua subscriptions ke akun baru
        
        Args:
            subscriptions: List of subscription data
            delay: Delay antar subscribe (dalam detik) untuk menghindari rate limit
        """
        if not subscriptions:
            print("❌ Tidak ada subscription untuk diimport")
            return
        
        print(f"\n📥 Mulai import {len(subscriptions)} subscriptions...")
        print("⏳ Proses mungkin memakan waktu beberapa menit...")
        print(f"   Delay: {delay} detik antar subscribe (untuk menghindari rate limit)\n")
        
        success_count = 0
        already_subscribed_count = 0
        failed_count = 0
        failed_channels = []
        
        for i, sub in enumerate(subscriptions, 1):
            channel_id = sub.get('channel_id')
            channel_title = sub.get('channel_title', 'Unknown')
            
            if not channel_id:
                print(f"⚠️  [{i}/{len(subscriptions)}] Skip: Channel ID tidak ditemukan")
                failed_count += 1
                continue
            
            print(f"[{i}/{len(subscriptions)}] Subscribing: {channel_title[:50]}...", end=' ', flush=True)
            
            result = self.import_subscription(channel_id)
            
            if result == True:
                print("✅ Berhasil")
                success_count += 1
            elif result == 'already_subscribed':
                print("⚠️  Sudah subscribed")
                already_subscribed_count += 1
            else:
                print("❌ Gagal")
                failed_count += 1
                failed_channels.append({
                    'channel_id': channel_id,
                    'channel_title': channel_title
                })
            
            # Delay untuk menghindari rate limit (kecuali untuk item terakhir)
            if i < len(subscriptions):
                time.sleep(delay)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 RINGKASAN IMPORT:")
        print("=" * 60)
        print(f"✅ Berhasil subscribe: {success_count}")
        print(f"⚠️  Sudah subscribed: {already_subscribed_count}")
        print(f"❌ Gagal: {failed_count}")
        print(f"📊 Total diproses: {len(subscriptions)}")
        
        if failed_channels:
            print(f"\n⚠️  Channel yang gagal ({len(failed_channels)}):")
            for ch in failed_channels[:10]:  # Tampilkan max 10
                print(f"   - {ch['channel_title']} ({ch['channel_id']})")
            if len(failed_channels) > 10:
                print(f"   ... dan {len(failed_channels) - 10} lainnya")
            
            # Save failed channels to file
            timestamp = get_timestamp()
            failed_file = os.path.join(DEFAULT_OUTPUT_DIR, f"failed_import_{timestamp}.json")
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(failed_channels, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Daftar channel yang gagal disimpan di: {failed_file}")
        
        print("=" * 60)


def list_export_files():
    """List semua file export yang tersedia"""
    if not os.path.exists(DEFAULT_OUTPUT_DIR):
        return []
    
    files = []
    for filename in os.listdir(DEFAULT_OUTPUT_DIR):
        if filename.startswith('subscriptions_') and filename.endswith('.json'):
            filepath = os.path.join(DEFAULT_OUTPUT_DIR, filename)
            files.append((filename, filepath, os.path.getmtime(filepath)))
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x[2], reverse=True)
    return files


def main():
    """Main function"""
    print("=" * 60)
    print("YouTube Subscription Importer")
    print("Import daftar subscription ke akun YouTube baru")
    print("=" * 60)
    print()
    print("⚠️  PENTING: Login dengan akun YouTube BARU")
    print("    (akun yang akan menerima subscriptions)")
    print()
    
    # List available export files
    export_files = list_export_files()
    
    if not export_files:
        print("❌ Tidak ada file export yang ditemukan!")
        print(f"   Folder: {DEFAULT_OUTPUT_DIR}/")
        print("\n💡 Jalankan export_subscriptions.py dulu untuk membuat file export.")
        return
    
    print("📁 File export yang tersedia:")
    print()
    for i, (filename, filepath, mtime) in enumerate(export_files, 1):
        from datetime import datetime
        mod_time = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"   {i}. {filename}")
        print(f"      ({mod_time})")
    
    print()
    
    # Select file
    while True:
        try:
            choice = input(f"Pilih file (1-{len(export_files)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(export_files):
                selected_file = export_files[index][1]
                break
            else:
                print("❌ Pilihan tidak valid. Coba lagi.")
        except ValueError:
            print("❌ Input tidak valid. Masukkan angka.")
        except KeyboardInterrupt:
            print("\n\n❌ Dibatalkan oleh user")
            return
    
    # Confirm
    print(f"\n📄 File yang dipilih: {os.path.basename(selected_file)}")
    
    # Load and show preview
    importer = YouTubeSubscriptionImporter()
    subscriptions = importer.load_subscriptions_from_file(selected_file)
    
    if not subscriptions:
        print("❌ Tidak ada subscription dalam file ini atau file tidak valid.")
        return
    
    print(f"📊 Total subscriptions dalam file: {len(subscriptions)}")
    print("\n📋 Preview (5 pertama):")
    for i, sub in enumerate(subscriptions[:5], 1):
        print(f"   {i}. {sub.get('channel_title', 'Unknown')}")
    if len(subscriptions) > 5:
        print(f"   ... dan {len(subscriptions) - 5} lainnya")
    
    print("\n" + "=" * 60)
    confirm = input("Lanjutkan import? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Dibatalkan.")
        return
    
    # Authenticate
    try:
        importer.authenticate(SCOPES_WRITE)
    except Exception as e:
        print(f"\n❌ Error saat autentikasi: {e}")
        return
    
    # Import
    try:
        # Ask for delay
        print("\n⏱️  Rate limiting:")
        delay_input = input("Delay antar subscribe (detik, default 1.0): ").strip()
        delay = float(delay_input) if delay_input else 1.0
        
        if delay < 0.5:
            confirm_slow = input("⚠️  Delay < 0.5 detik bisa menyebabkan rate limit. Lanjutkan? (y/n): ").strip().lower()
            if confirm_slow != 'y':
                delay = 0.5
                print(f"✅ Menggunakan delay {delay} detik")
        
        importer.import_subscriptions(subscriptions, delay=delay)
        
    except KeyboardInterrupt:
        print("\n\n❌ Dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

