"""
Script untuk export daftar channel yang sudah di-subscribe dari akun YouTube
"""

import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import json
import time
from config import CLIENT_SECRETS_FILE, SCOPES_READ, DEFAULT_OUTPUT_DIR
from utils import export_to_json, export_to_csv, get_timestamp


class YouTubeSubscriptionExporter:
    """Class untuk export subscriptions (channel yang sudah di-subscribe)"""
    
    def __init__(self):
        self.youtube = None
        self.credentials = None
        
    def authenticate(self, scopes):
        """Authentikasi dengan YouTube API menggunakan OAuth 2.0"""
        creds = None
        
        # File token menyimpan access & refresh tokens untuk read
        token_file = 'token_export.pickle'
        
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
    
    def get_my_subscriptions(self):
        """Mendapatkan daftar semua channel yang sudah di-subscribe"""
        try:
            subscriptions = []
            next_page_token = None
            
            print("📋 Mengambil daftar channel yang sudah di-subscribe...")
            print("⏳ Mohon tunggu...")
            
            while True:
                request = self.youtube.subscriptions().list(
                    part='snippet,contentDetails',
                    mine=True,
                    maxResults=50,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                if 'items' in response:
                    for item in response['items']:
                        subscription_data = {
                            'channel_id': item['snippet']['resourceId']['channelId'],
                            'channel_title': item['snippet']['title'],
                            'channel_description': item['snippet'].get('description', ''),
                            'channel_url': f"https://www.youtube.com/channel/{item['snippet']['resourceId']['channelId']}",
                            'subscription_id': item['id'],
                            'subscribed_date': item['snippet']['publishedAt'],
                            'total_item_count': item['contentDetails'].get('totalItemCount', '0'),
                            'new_item_count': item['contentDetails'].get('newItemCount', '0')
                        }
                        subscriptions.append(subscription_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                print(f"  ✓ Mengambil {len(subscriptions)} subscriptions...")
            
            return subscriptions
            
        except Exception as e:
            print(f"❌ Error mengambil subscriptions: {e}")
            return []
    
    def export_subscriptions(self, format: str = 'both'):
        """
        Export subscriptions ke file
        
        Args:
            format: 'csv', 'json', atau 'both'
        """
        # Authentikasi dengan scope read-only
        if not self.youtube:
            self.authenticate(SCOPES_READ)
        
        # Get subscriptions
        subscriptions = self.get_my_subscriptions()
        
        if not subscriptions:
            print("\n⚠️ Tidak ada subscription yang ditemukan atau terjadi error.")
            return
        
        print(f"\n✅ Berhasil mengambil {len(subscriptions)} subscriptions\n")
        
        # Prepare output
        timestamp = get_timestamp()
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        
        # Add export metadata
        export_data = {
            'export_date': timestamp,
            'total_subscriptions': len(subscriptions),
            'subscriptions': subscriptions
        }
        
        # Export
        if format in ['json', 'both']:
            json_file = os.path.join(DEFAULT_OUTPUT_DIR, f"subscriptions_{timestamp}.json")
            export_to_json(export_data, json_file)
        
        if format in ['csv', 'both']:
            csv_file = os.path.join(DEFAULT_OUTPUT_DIR, f"subscriptions_{timestamp}.csv")
            # Export hanya array subscriptions untuk CSV
            export_to_csv(subscriptions, csv_file)
        
        print(f"\n✨ Export selesai! Total {len(subscriptions)} subscriptions diekspor.")
        print(f"📁 File tersimpan di folder: {DEFAULT_OUTPUT_DIR}/")
        
        return subscriptions


def main():
    """Main function"""
    print("=" * 60)
    print("YouTube Subscription Exporter")
    print("Export daftar channel yang sudah di-subscribe")
    print("=" * 60)
    print()
    print("⚠️  PENTING: Login dengan akun YouTube LAMA")
    print("    (akun yang sudah subscribe banyak channel)")
    print()
    
    exporter = YouTubeSubscriptionExporter()
    
    try:
        # Export subscriptions
        subscriptions = exporter.export_subscriptions(format='both')
        
        if subscriptions:
            print("\n" + "=" * 60)
            print("📝 Langkah selanjutnya:")
            print("   1. File sudah tersimpan di folder exports/")
            print("   2. Jalankan import_subscriptions.py dengan akun BARU")
            print("   3. Pilih file yang baru saja diexport")
            print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ Dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

