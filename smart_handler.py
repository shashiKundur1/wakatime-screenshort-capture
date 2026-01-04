import datetime
import io
from dateutil import parser
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

class SmartHandler:
    def __init__(self, drive_service, sheets_service=None):
        self.drive = drive_service
        self.sheets = sheets_service

    def normalize_date(self, date_val):
        """Attempts to convert any date format into a standard python date object."""
        if isinstance(date_val, datetime.datetime):
            return date_val.date()
        if isinstance(date_val, datetime.date):
            return date_val
        try:
            return parser.parse(str(date_val), dayfirst=True).date()
        except:
            return None

    def handle_excel_file(self, file_id, wh, ot, note):
        import openpyxl
        
        print(f"📥 Downloading Excel file (ID: {file_id})...")
        request = self.drive.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        wb = openpyxl.load_workbook(fh)
        sheet = wb.active
        
        target_date = datetime.date.today()
        row_found = False
        
        # Iterates through Column A (User provided dates)
        for row in sheet.iter_rows(min_row=2):
            cell_val = row[0].value
            if not cell_val: continue
            
            parsed_date = self.normalize_date(cell_val)
            
            if parsed_date == target_date:
                print(f"✅ Found match: {cell_val}")
                # Update Columns C(2), D(3), E(4) - 0-indexed logic
                row[2].value = wh
                row[3].value = ot
                row[4].value = note
                row_found = True
                break
        
        if not row_found:
            print(f"🆕 Date {target_date} not found. Appending...")
            sheet.append([target_date.strftime("%d-%m-%Y"), "User", wh, ot, note])

        # Save and Re-upload
        out_buffer = io.BytesIO()
        wb.save(out_buffer)
        out_buffer.seek(0)
        
        print("☁️ Uploading updated Excel...")
        media_upload = MediaIoBaseUpload(out_buffer, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resumable=True)
        
        # --- THE FIX IS HERE: Added supportsAllDrives=True ---
        self.drive.files().update(
            fileId=file_id, 
            media_body=media_upload,
            supportsAllDrives=True  # <--- CRITICAL FIX for shared files
        ).execute()
        
        return True