import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_google_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def find_or_create_folder(service, parent_id, folder_name):
    print(f"📂 Checking for folder: {folder_name}...")
    
    # ADDED: includeItemsFromAllDrives and supportsAllDrives
    query = f"name = '{folder_name}' and '{parent_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(
        q=query, 
        spaces='drive', 
        fields='files(id, name)',
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True
    ).execute()
    
    items = results.get('files', [])

    if not items:
        print(f"✨ Folder not found. Creating '{folder_name}'...")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        # ADDED: supportsAllDrives=True
        folder = service.files().create(
            body=file_metadata, 
            fields='id', 
            supportsAllDrives=True
        ).execute()
        
        print(f"✅ Created folder ID: {folder.get('id')}")
        return folder.get('id')
    else:
        folder_id = items[0]['id']
        print(f"✅ Found existing folder ID: {folder_id}")
        return folder_id

def upload_file_to_drive(file_path, file_name, parent_id):
    service = authenticate_google_drive()
    print(f"🚀 Uploading {file_name} to Drive...")
    
    file_metadata = {
        'name': file_name,
        'parents': [parent_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    
    # ADDED: supportsAllDrives=True
    file = service.files().create(
        body=file_metadata, 
        media_body=media, 
        fields='id',
        supportsAllDrives=True
    ).execute()
    
    print(f"🎉 Upload Complete! File ID: {file.get('id')}")