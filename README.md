🚀 Office Automator (High-Performance Edition)

A production-ready automation tool optimized for speed (2025 Standards). It captures WakaTime dashboards using headless Chrome with GPU acceleration, effectively blocks tracking scripts, and syncs screenshots + Excel data to Google Drive.

✨ Features

⚡ Blazing Fast: Uses Playwright headless=True with EGL GPU acceleration.

🛡️ Smart Blocking: Automatically blocks analytics, fonts, and heavy media to reduce load times by ~40%.

🧠 Auto-Wait: Uses networkidle and deep selectors to snapshot exactly when the chart is ready (no fixed delays).

☁️ Cloud Sync: Uploads screenshots and updates Excel logs on Google Drive automatically.

🛠️ Prerequisites

Python 3.8+

Google Cloud credentials.json (OAuth Client ID) placed in the project root.

📦 Installation

Install Python Dependencies:

pip install -r requirements.txt

Install Playwright Browsers:

playwright install chromium

🔑 Setup & Authentication

1. Google Drive Auth

Place your credentials.json file in the root folder. The first time you run the script, it will open a browser to authorize Google Drive access.

2. WakaTime Login (One-Time Setup)

Since the main script runs headless (invisible), you must log in once manually to save your session.

Create a temporary file named login.py with this code, run it, and log in:

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
browser = p.chromium.launch(headless=False) # Opens visible browser
context = browser.new_context()
page = context.new_page()

    print("👉 Log in to WakaTime manually in the browser window...")
    page.goto("[https://wakatime.com/login](https://wakatime.com/login)")

    # Wait until you are redirected to the dashboard
    page.wait_for_url("**/dashboard**", timeout=0)

    # Save the session cookie
    context.storage_state(path="auth.json")
    print("✅ auth.json created! You can now run main.py")
    browser.close()

🚀 Usage

Run the main automation script:

python main.py

How it works:

Inputs: It asks for your working hours, overtime, and notes.

Capture: It invisibly launches a high-speed browser, blocks ads/trackers, waits for the chart to render, and takes a snapshot.

Sync: It uploads the image to the correct date folder in Drive and updates the Excel sheet.

First Run Configuration

On the very first run, the script will ask for the Google Drive Folder ID (the string of characters at the end of your shared folder URL). It saves this to user_config.json so you never have to enter it again.

📂 Project Structure

main.py: Core logic (Headless browser, Resource blocking, Smart waits).

drive_utils.py: Google Drive API helpers.

excel_utils.py: Excel manipulation helpers.

auth.json: Stores your WakaTime session (DO NOT share this file).

user_config.json: Stores your target Drive Folder ID.

⚠️ Troubleshooting

"Chart detector timed out": Your internet might be extremely slow, or WakaTime changed their layout. The script will still try to take a screenshot.

"auth.json missing": You deleted the file or didn't run the login.py step.

Slow execution: Ensure you are not running this on a machine with 100% CPU usage; Playwright needs some resources to render the chart.
