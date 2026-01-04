import os
import json
import datetime
import re
from playwright.sync_api import sync_playwright
from googleapiclient.discovery import build

# Import helpers
import drive_utils
from smart_handler import SmartHandler

class OfficeAutomator:
    def __init__(self, logger=print):
        self.log = logger
        self.auth_file = "auth.json"
        self._folder_id = None 
        self.sheet_url = None
        
        # AGGRESSIVE BLOCKING LIST (Speeds up loading by ~60%)
        self.BLOCK_RESOURCE_TYPES = ['image', 'font', 'media', 'texttrack', 'object', 'beacon', 'csp_report', 'imageset']
        self.BLOCK_DOMAINS = [
            'google-analytics', 'googletagmanager', 'intercom', 'hotjar', 'facebook', 
            'doubleclick', 'twitter', 'linkedin', 'stripe'
        ]

    @property
    def folder_id(self):
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value):
        if not value:
            self._folder_id = None
            return
        match = re.search(r'[-\w]{25,}', value)
        self._folder_id = match.group(0) if match else value.strip()

    def run(self, working_hours, overtime, note):
        today = datetime.date.today()
        waka_date_str = today.strftime("%Y-%m-%d")
        display_date = today.strftime("%d-%m-%Y")
        screenshot_path = f"screenshots/wakatime_{waka_date_str}.png"

        self.log("🚀 Speed Run Initiated...")

        # --- STEP 1: LIGHTNING CAPTURE ---
        if not os.path.exists(self.auth_file):
            self.log("❌ Error: auth.json missing.")
            return

        with sync_playwright() as p:
            self.log("⚡ Browser Engine: Start")
            # ARGS: Disable unnecessary Chrome features for speed
            browser = p.chromium.launch(
                headless=True, 
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox", 
                    "--disable-extensions", 
                    "--disable-gpu", 
                    "--blink-settings=imagesEnabled=false" # Don't even try to render images
                ]
            )
            context = browser.new_context(storage_state=self.auth_file, viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            
            # 1. Enable Aggressive Blocker
            page.route("**/*", self.intercept_route)

            try:
                # 2. Fast Navigation (Don't wait for network idle)
                url = f"https://wakatime.com/dashboard/day?date={waka_date_str}"
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                # 3. Smart Trigger: Snap as soon as the SVG chart exists
                # We wait for the specific 'rect' element inside the chart.
                try:
                    page.locator("svg >> css=rect").first.wait_for(state="visible", timeout=10000)
                except:
                    self.log("⚠️ Chart delayed, snapping anyway...")

                # 4. Instant Screenshot
                os.makedirs("screenshots", exist_ok=True)
                page.screenshot(path=screenshot_path)
                self.log("📸 Screenshot: DONE")
            
            except Exception as e:
                self.log(f"❌ Browser Error: {e}")
                browser.close()
                return

            browser.close()

        # --- STEP 2: CLOUD SYNC (Parallel-like feel) ---
        try:
            self.log("☁️ Syncing Data...")
            drive_service = drive_utils.authenticate_google_drive()
            smart_bot = SmartHandler(drive_service)

            if not self.folder_id:
                self.log("❌ Error: No Folder ID.")
                return

            # A. Upload Image
            today_folder_id = drive_utils.find_or_create_folder(drive_service, self.folder_id, display_date)
            drive_utils.upload_file_to_drive(screenshot_path, os.path.basename(screenshot_path), today_folder_id)

            # B. Update Excel (Fast Search)
            query = f"name contains 'Time update' and '{self.folder_id}' in parents and trashed = false"
            results = drive_service.files().list(
                q=query, 
                fields="files(id, name, mimeType)",
                includeItemsFromAllDrives=True, 
                supportsAllDrives=True
            ).execute()
            files = results.get('files', [])

            if files:
                target_file = files[0]
                self.log(f"📎 Editing: {target_file['name']}")
                smart_bot.handle_excel_file(target_file['id'], working_hours, overtime, note)
                self.log("✅ Excel Updated!")
            else:
                self.log("⚠️ 'Time update' file not found.")
                # Debug listing
                # all_files = drive_service.files().list(q=f"'{self.folder_id}' in parents", fields="files(name)", includeItemsFromAllDrives=True, supportsAllDrives=True).execute()
                # self.log(f"Files seen: {[f['name'] for f in all_files.get('files', [])]}")

        except Exception as e:
            self.log(f"❌ Cloud Error: {e}")

        self.log("✨ Finished!")

    def intercept_route(self, route):
        req = route.request
        # Block everything except the main document and API calls
        if req.resource_type in self.BLOCK_RESOURCE_TYPES:
            return route.abort()
        if any(d in req.url for d in self.BLOCK_DOMAINS):
            return route.abort()
        return route.continue_()