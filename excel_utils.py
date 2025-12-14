import openpyxl
import datetime
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

def find_excel_file(service, parent_id, name="Time update.xlsx"):
    """Finds the file ID of the Excel sheet."""
    print(f"🔎 Searching for '{name}'...")
    
    # ADDED: supportsAllDrives=True to find files in shared folders
    query = f"name = '{name}' and '{parent_id}' in parents and trashed = false"
    results = service.files().list(
        q=query, 
        fields="files(id, name)",
        includeItemsFromAllDrives=True, 
        supportsAllDrives=True
    ).execute()
    
    files = results.get('files', [])
    
    if not files:
        print(f"❌ Could not find '{name}' in the folder.")
        # Debug: List what files ARE there so we can see the issue
        print("   (Files found in this folder:)")
        all_files = service.files().list(q=f"'{parent_id}' in parents", fields="files(name)", supportsAllDrives=True).execute()
        for f in all_files.get('files', [])[:5]:
            print(f"   - {f['name']}")
        return None
    
    return files[0]['id']

def download_excel(service, file_id, local_path):
    print(f"📥 Downloading Excel file...")
    request = service.files().get_media(fileId=file_id)
    with open(local_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    print("✅ Download complete.")

def update_excel_row(file_path, date_str, working_hours, overtime, note):
    print(f"✏️  Updating Excel for date: {date_str}...")
    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active 
        row_found = False
        
        for row in sheet.iter_rows(min_row=2):
            cell_date = row[0].value 
            if isinstance(cell_date, datetime.datetime):
                cell_date_str = cell_date.strftime("%d-%m-%Y")
            else:
                cell_date_str = str(cell_date)
            
            if cell_date_str == date_str:
                print(f"✅ Found row for {date_str}!")
                row[2].value = working_hours
                row[3].value = overtime
                row[4].value = note
                row_found = True
                break
        
        if row_found:
            wb.save(file_path)
            return True
        else:
            print(f"⚠️  Date {date_str} not found in Excel!")
            return False
    except Exception as e:
        print(f"❌ Excel Error: {e}")
        return False

def upload_excel_update(service, local_path, file_id):
    print("☁️  Uploading updated Excel...")
    media = MediaFileUpload(local_path, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resumable=True)
    service.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()
    print("🎉 Excel updated successfully!")