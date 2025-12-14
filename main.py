import os
import json
import datetime
from playwright.sync_api import sync_playwright

# Import helpers
import drive_utils
import excel_utils

# CONFIG FILE NAME
CONFIG_FILE = "user_config.json"

# --- 2025 PRODUCTION OPTIMIZATION: BLOCK LIST ---
BLOCK_RESOURCE_TYPES = ['font', 'media', 'texttrack', 'object', 'beacon', 'csp_report', 'imageset']
BLOCK_DOMAINS = [
    'google-analytics',
    'googletagmanager',
    'intercom',
    'segment.com',
    'hotjar',
    'doubleclick',
    'facebook',
    'linkedin'
]

def get_folder_id():
    """Checks for saved Folder ID. If missing, asks user once and saves it."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("folder_id")
    
    # First time run setup
    print("\n⚠️  FIRST RUN SETUP")
    print("--------------------------------------------------")
    print("Please paste the Google Drive Folder ID provided by your manager.")
    print("(It is the random text at the end of the folder URL)")
    user_id = input("👉 Folder ID: ").strip()
    
    with open(CONFIG_FILE, "w") as f:
        json.dump({"folder_id": user_id}, f)
    
    print("✅ Configuration saved!\n")
    return user_id

def main_workflow():
    # 1. GET USER SPECIFIC FOLDER
    PARENT_FOLDER_ID = get_folder_id()
    
    today = datetime.date.today()
    waka_date_str = today.strftime("%Y-%m-%d") 
    folder_date_str = today.strftime("%d-%m-%Y") 
    
    auth_file = "auth.json"
    screenshot_path = f"screenshots/wakatime_{waka_date_str}.png"
    screenshot_name = f"wakatime_{waka_date_str}.png"
    excel_local_path = "Time_update_temp.xlsx"
    
    print(f"🚀 Office Automator: {folder_date_str}")
    
    # --- STEP 1: USER INPUT ---
    print("\n📝  Time Sheet Details:")
    wh = input("   - Working Hours: ")
    ot = input("   - Overtime: ")
    note = input("   - Note: ")

    # --- STEP 2: CAPTURE ---
    print("\n📸  [1/3] Launching Smart Capture...")
    capture_success = False
    
    with sync_playwright() as p:
        if not os.path.exists(auth_file):
            print("❌ Error: auth.json missing. Run manual login first.")
            return

        # --- PHASE 1: HEADLESS ENGINE ---
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--use-gl=egl",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        context = browser.new_context(
            storage_state=auth_file, 
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        page = context.new_page()
        page.set_default_timeout(30000) # Reduced from 60s to 30s for fail-fast

        # --- PHASE 1: RESOURCE BLOCKER ---
        def route_handler(route):
            req = route.request
            if req.resource_type in BLOCK_RESOURCE_TYPES:
                return route.abort()
            if any(d in req.url for d in BLOCK_DOMAINS):
                return route.abort()
            return route.continue_()

        page.route("**/*", route_handler)

        try:
            url = f"https://wakatime.com/dashboard/day?date={waka_date_str}"
            print(f"   -> Go: {url}")
            
            # --- PHASE 2: SMART NAVIGATION ---
            # 'domcontentloaded' triggers as soon as HTML is parsed (very fast)
            page.goto(url, wait_until="domcontentloaded")
            
            print("   -> 🧠 Smart-Waiting for data...")
            
            # --- PHASE 2: AUTO-WAIT LOGIC ---
            # 1. Wait for Network Idle: This confirms the API JSON has arrived.
            #    (Reliable now because we blocked the noisy tracking scripts)
            page.wait_for_load_state("networkidle")
            
            # 2. Wait for SVG Content: Explicitly check for internal elements (rect/path)
            #    This ensures the chart isn't just an empty container.
            page.wait_for_selector("svg >> css=rect,path", state="attached", timeout=10000)

            # 3. Visual Confirmation (Green Border)
            page.evaluate("document.querySelector('svg').style.border = '5px solid #00ff00'")
            
            # Ensure directory exists
            os.makedirs("screenshots", exist_ok=True)
            
            page.screenshot(path=screenshot_path)
            print("   -> 📸 SNAP! Screenshot taken.")
            capture_success = True
        except Exception as e:
            print(f"❌  Capture failed: {e}")
        
        browser.close()

    if not capture_success:
        return

    # --- STEP 3: DRIVE SYNC ---
    print("\n☁️  [2/3] Syncing Drive...")
    try:
        service = drive_utils.authenticate_google_drive()
        
        # A. Upload Screenshot
        today_folder_id = drive_utils.find_or_create_folder(service, PARENT_FOLDER_ID, folder_date_str)
        drive_utils.upload_file_to_drive(screenshot_path, screenshot_name, today_folder_id)
        
        # B. Update Excel
        print("\n📊  [3/3] Updating Excel...")
        excel_id = excel_utils.find_excel_file(service, PARENT_FOLDER_ID)
        
        if excel_id:
            excel_utils.download_excel(service, excel_id, excel_local_path)
            updated = excel_utils.update_excel_row(excel_local_path, folder_date_str, wh, ot, note)
            if updated:
                excel_utils.upload_excel_update(service, excel_local_path, excel_id)
                if os.path.exists(excel_local_path):
                    os.remove(excel_local_path)
        else:
            print("⚠️ Skipping Excel (File not found)")
        
    except Exception as e:
        print(f"❌  Cloud Error: {e}")

    print("\n🎉 DONE! Reliable & Fast.")

if __name__ == "__main__":
    main_workflow()