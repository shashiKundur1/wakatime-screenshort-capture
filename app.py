import streamlit as st
import datetime
import threading
from automation import OfficeAutomator

# --- PAGE CONFIG ---
st.set_page_config(page_title="WakaTime Automator", page_icon="🚀", layout="centered")

# --- UI HEADER ---
st.title("🚀 Office Automator Web")
st.markdown("Automate your daily WakaTime screenshots and timesheet updates.")

# --- SIDEBAR: SETTINGS ---
st.sidebar.header("⚙️ Configuration")
# We use a default value for easier local testing if you want
folder_id = st.sidebar.text_input("Drive Folder ID", help="The ID from your Google Drive folder URL.")
sheet_url = st.sidebar.text_input("Sheet URL (Optional)", help="Direct link to the Google Sheet or Excel file.")

# --- MAIN INPUTS ---
col1, col2 = st.columns(2)
with col1:
    wh = st.text_input("Working Hours", value="08:30")
with col2:
    ot = st.text_input("Overtime", value="00:00")

note = st.text_area("Notes", placeholder="Task details...")

# --- LOGGING CALLBACK ---
if "logs" not in st.session_state:
    st.session_state.logs = []

def logger(message):
    # Add timestamp and message to session logs
    st.session_state.logs.append(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}")

# --- ACTION BUTTON ---
if st.button("⚡ Run Automation", type="primary"):
    if not folder_id:
        st.error("⚠️ Please enter a Folder ID in the sidebar!")
    else:
        st.info("⏳ Starting Automation... (Check terminal for browser popup)")
        
        # Initialize Bot
        bot = OfficeAutomator(logger=logger)
        
        # Inject user configs dynamically
        bot.folder_id = folder_id.strip()
        bot.sheet_url = sheet_url.strip() if sheet_url else None
        
        # Run
        try:
            bot.run(wh, ot, note)
            st.success("✅ Automation Complete!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# --- LOG DISPLAY ---
with st.expander("📜 Process Logs", expanded=True):
    for log in st.session_state.logs:
        st.code(log, language="text")