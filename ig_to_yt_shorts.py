import os
import argparse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from yt_dlp import YoutubeDL

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    # Doğrudan elimizdeki bilgilerle (tarayıcı açmadan) kimlik doğruluyoruz
    creds = Credentials(
        token=None,
        refresh_token="1//04oTwPp4U9UCgYIARAAGAcSNwF-L9IrYdkF3JEgWcoxmxHun5Whqp0A6LH1gjMBM2UAg5nlBcbv-IOK4h146P54dNv9kBM9aRs",
        client_id="644890746233-s72ol3jbbdflac45msb277eeml3629pg.apps.googleusercontent.com",
        client_secret="GOCSPX-0vTozAIPnlsPGGaxv0V5EdD68.Jjb",
        token_uri="https://oauth2.googleapis.com/token"
    )
    
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build('youtube', 'v3', credentials=creds)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='Instagram Reel URL')
    args = parser.parse_args()

    print("[Instagram] Setting up session...")
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'temp/%(id)s.%(ext)s',
    }

    with YoutubeDL(ydl_opts) as ydl:
        print("Extracting Reel metadata...")
        info = ydl.extract_info(args.url, download=True)
        video_title = info.get('title', 'Instagram Reel')
        video_path = ydl.prepare_filename(info)

    print(f"Downloaded to {video_path}")
    print("Authenticating with YouTube...")
    youtube = get_authenticated_service()

    print("Uploading to YouTube Shorts...")
    body = {
        'snippet': {
            'title': video_title[:100],
            'description': 'Auto-uploaded via Instagram to YouTube Shorts #shorts',
            'tags': ['shorts', 'instagram'],
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f"Video id '{response.get('idid') if 'idid' in response else response.get('id')}' was successfully uploaded.")

if __name__ == '__main__':
    main()
