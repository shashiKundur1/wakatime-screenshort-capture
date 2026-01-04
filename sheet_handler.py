import datetime
from googleapiclient.discovery import build

class SheetHandler:
    def __init__(self, creds):
        # We build the service using the credentials passed from the main app
        self.service = build('sheets', 'v4', credentials=creds)

    def find_sheet_id_by_name(self, drive_service, folder_id, name="Time update"):
        """
        Finds the Google Sheet ID inside your specific folder.
        It uses the Drive API to look for the file ID.
        """
        query = f"name = '{name}' and '{folder_id}' in parents and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        results = drive_service.files().list(
            q=query, 
            fields="files(id)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None

    def update_or_append_log(self, spreadsheet_id, date_str, wh, ot, note):
        """
        THE BUG FIX LOGIC:
        1. Reads current dates from Column A.
        2. If today's date exists -> UPDATE that row.
        3. If today's date is missing -> APPEND a new row (Fixes the bug).
        """
        print(f"📊 Checking Sheet for date: {date_str}...")
        
        # 1. Read all dates in Column A (Sheet1)
        sheet_range = "Sheet1!A:A" 
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, 
            range=sheet_range
        ).execute()
        
        rows = result.get('values', [])

        # 2. Search for the date
        row_index = -1
        for i, row in enumerate(rows):
            # Check if row is not empty and matches date
            if row and row[0] == date_str:
                row_index = i + 1  # Sheets are 1-indexed (Row 1 is the first row)
                break

        # 3. Decision: Update or Append
        if row_index != -1:
            # --- OPTION A: UPDATE EXISTING ROW ---
            print(f"✅ Found date {date_str} at Row {row_index}. Updating...")
            
            # We want to update Columns C (Working Hours), D (Overtime), E (Note)
            # Syntax: Sheet1!C5:E5
            update_range = f"Sheet1!C{row_index}:E{row_index}" 
            
            body = {
                'values': [[wh, ot, note]]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, 
                range=update_range,
                valueInputOption="USER_ENTERED", 
                body=body
            ).execute()
            print("✨ Row updated successfully.")
            
        else:
            # --- OPTION B: APPEND NEW ROW (THE FIX) ---
            print(f"🆕 Date {date_str} not found. Creating new entry...")
            
            # We append a full row: [Date, User, WH, OT, Note]
            values = [[date_str, "User", wh, ot, note]]
            body = {'values': values}
            
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, 
                range="Sheet1!A:E",
                valueInputOption="USER_ENTERED", 
                body=body
            ).execute()
            print("✨ New row added successfully.")