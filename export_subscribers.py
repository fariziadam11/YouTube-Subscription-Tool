"""
Script utama untuk export subscriber dari YouTube channel
"""

import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import json
from config import CLIENT_SECRETS_FILE, SCOPES, DEFAULT_OUTPUT_DIR, DEFAULT_CSV_FILE, DEFAULT_JSON_FILE
from utils import export_to_json, export_to_csv, get_timestamp


class YouTubeSubscriberExporter:
    """Class untuk mengekspor subscriber dari YouTube channel"""
    
    def __init__(self):
        self.youtube = None
        self.credentials = None
        
    def authenticate(self):
        """Authentikasi dengan YouTube API menggunakan OAuth 2.0"""
        creds = None
        
        # File token.pickle menyimpan access & refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
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
                    CLIENT_SECRETS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Simpan credentials untuk penggunaan selanjutnya
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.youtube = build('youtube', 'v3', credentials=creds)
        print("✅ Berhasil terhubung ke YouTube API")
    
    def get_my_channel_info(self):
        """Mendapatkan informasi channel yang sedang login"""
        try:
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                channel_info = {
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', '0'),
                    'video_count': channel['statistics'].get('videoCount', '0'),
                    'view_count': channel['statistics'].get('viewCount', '0')
                }
                return channel_info
            else:
                print("⚠️ Tidak ada channel yang ditemukan")
                return None
        except Exception as e:
            print(f"❌ Error mendapatkan channel info: {e}")
            return None
    
    def get_channel_subscribers(self, channel_id: str = None):
        """
        Mendapatkan daftar subscriber dari channel
        
        CATATAN: YouTube API memiliki limitasi - hanya bisa mendapatkan subscriber
        jika channel memiliki setidaknya 1000 subscriber dan Anda adalah owner channel.
        Untuk channel kecil, hanya bisa mendapatkan subscriber count, bukan list detail.
        """
        try:
            # Jika channel_id tidak diberikan, gunakan channel yang sedang login
            if not channel_id:
                channel_info = self.get_my_channel_info()
                if not channel_info:
                    return []
                channel_id = channel_info['channel_id']
            
            subscribers = []
            next_page_token = None
            
            print(f"📊 Mengambil data subscriber dari channel: {channel_id}")
            print("⏳ Mohon tunggu...")
            
            while True:
                request = self.youtube.subscriptions().list(
                    part='snippet,contentDetails',
                    mySubscribers=True,
                    maxResults=50,
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                if 'items' in response:
                    for item in response['items']:
                        subscriber_data = {
                            'subscriber_id': item['snippet']['resourceId']['channelId'],
                            'subscriber_name': item['snippet']['title'],
                            'subscriber_description': item['snippet'].get('description', ''),
                            'subscribed_date': item['snippet']['publishedAt'],
                            'subscriber_url': f"https://www.youtube.com/channel/{item['snippet']['resourceId']['channelId']}"
                        }
                        subscribers.append(subscriber_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                print(f"  ✓ Mengambil {len(subscribers)} subscriber...")
            
            return subscribers
            
        except Exception as e:
            error_msg = str(e)
            if '403' in error_msg or 'Forbidden' in error_msg:
                print("\n⚠️ PERINGATAN: YouTube API membatasi akses ke daftar subscriber detail.")
                print("Hanya channel dengan minimal 1000 subscriber yang bisa mengakses daftar lengkap.")
                print("Untuk channel kecil, hanya bisa mendapatkan subscriber count saja.\n")
                
                # Coba ambil channel statistics sebagai alternatif
                try:
                    channel_info = self.get_channel_info(channel_id)
                    if channel_info:
                        print(f"📈 Statistik Channel:")
                        print(f"   - Jumlah Subscriber: {channel_info.get('subscriber_count', 'N/A')}")
                        print(f"   - Jumlah Video: {channel_info.get('video_count', 'N/A')}")
                        print(f"   - Total Views: {channel_info.get('view_count', 'N/A')}")
                except:
                    pass
            
            return []
    
    def get_channel_info(self, channel_id: str = None):
        """Mendapatkan informasi channel"""
        try:
            if not channel_id:
                return self.get_my_channel_info()
            
            request = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', '0'),
                    'video_count': channel['statistics'].get('videoCount', '0'),
                    'view_count': channel['statistics'].get('viewCount', '0')
                }
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def export_subscribers(self, channel_id: str = None, format: str = 'both'):
        """
        Export subscriber ke file
        
        Args:
            channel_id: ID channel (optional, default: channel yang sedang login)
            format: 'csv', 'json', atau 'both'
        """
        # Authentikasi
        if not self.youtube:
            self.authenticate()
        
        # Get channel info
        channel_info = self.get_my_channel_info() if not channel_id else self.get_channel_info(channel_id)
        if not channel_info:
            print("❌ Tidak bisa mendapatkan informasi channel")
            return
        
        print(f"\n📺 Channel: {channel_info['title']}")
        print(f"📊 Subscriber Count: {channel_info['subscriber_count']}")
        print()
        
        # Get subscribers
        subscribers = self.get_channel_subscribers(channel_id)
        
        if not subscribers:
            print("\n⚠️ Tidak ada data subscriber detail yang bisa diambil.")
            print("   Kemungkinan channel memiliki kurang dari 1000 subscriber.")
            print("\n💡 Exporting channel statistics sebagai gantinya...\n")
            
            # Export channel statistics
            timestamp = get_timestamp()
            stats_data = [{
                'export_date': timestamp,
                'channel_id': channel_info['channel_id'],
                'channel_title': channel_info['title'],
                'subscriber_count': channel_info.get('subscriber_count', '0'),
                'video_count': channel_info.get('video_count', '0'),
                'view_count': channel_info.get('view_count', '0')
            }]
            
            os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
            
            if format in ['json', 'both']:
                json_file = os.path.join(DEFAULT_OUTPUT_DIR, f"channel_stats_{timestamp}.json")
                export_to_json(stats_data, json_file)
            
            if format in ['csv', 'both']:
                csv_file = os.path.join(DEFAULT_OUTPUT_DIR, f"channel_stats_{timestamp}.csv")
                export_to_csv(stats_data, csv_file)
            
            return
        
        print(f"\n✅ Berhasil mengambil {len(subscribers)} subscriber\n")
        
        # Prepare output
        timestamp = get_timestamp()
        os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
        
        # Add channel info to each subscriber record
        for sub in subscribers:
            sub['channel_id'] = channel_info['channel_id']
            sub['channel_title'] = channel_info['title']
            sub['export_date'] = timestamp
        
        # Export
        if format in ['json', 'both']:
            json_file = os.path.join(DEFAULT_OUTPUT_DIR, f"subscribers_{timestamp}.json")
            export_to_json(subscribers, json_file)
        
        if format in ['csv', 'both']:
            csv_file = os.path.join(DEFAULT_OUTPUT_DIR, f"subscribers_{timestamp}.csv")
            export_to_csv(subscribers, csv_file)
        
        print(f"\n✨ Export selesai! Total {len(subscribers)} subscriber diekspor.")


def main():
    """Main function"""
    print("=" * 60)
    print("YouTube Subscriber Exporter")
    print("=" * 60)
    print()
    
    exporter = YouTubeSubscriberExporter()
    
    try:
        # Export subscribers dari channel yang sedang login
        exporter.export_subscribers(format='both')
        
        print("\n" + "=" * 60)
        print("⚠️ CATATAN PENTING:")
        print("YouTube tidak mengizinkan import subscriber langsung.")
        print("Data ini hanya untuk backup dan analisis.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n❌ Dibatalkan oleh user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

