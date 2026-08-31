import os
import argparse
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from yt_dlp import YoutubeDL

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    creds = None
    # Doğrudan repodaki token.pickle dosyasını arıyoruz
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # client_secrets.json dosyasını kullanarak kimlik doğrulama akışını başlatıyoruz
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

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
