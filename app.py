import streamlit as st
import datetime
import time
import extra_streamlit_components as stx
from automation import OfficeAutomator

# --- PAGE CONFIG ---
st.set_page_config(page_title="WakaTime Automator", page_icon="🚀", layout="centered")

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "waka_session" not in st.session_state:
    st.session_state.waka_session = ""
if "drive_folder" not in st.session_state:
    st.session_state.drive_folder = ""
if "logs" not in st.session_state:
    st.session_state.logs = []

# --- COOKIE MANAGER ---
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# --- LOGGER ---
def logger(message):
    st.session_state.logs.append(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}")

# --- MAIN LOGIC ---
st.title("🚀 Office Automator")

# 1. FETCH ALL COOKIES (More reliable than fetching one by one)
# We accept that on the very first split-second load, this might be empty.
all_cookies = cookie_manager.get_all()
cookie_session = all_cookies.get("waka_session")
cookie_folder = all_cookies.get("drive_folder")

# 2. AUTO-LOGIN CHECK
# If we see cookies in the browser, but Session State is empty, sync them.
if cookie_session and cookie_folder:
    if not st.session_state.logged_in:
        st.session_state.waka_session = cookie_session
        st.session_state.drive_folder = cookie_folder
        st.session_state.logged_in = True
        st.rerun()

# --- VIEW 1: LOGIN FORM ---
if not st.session_state.logged_in:
    st.info("👋 Welcome! Please log in to setup your automation.")
    
    with st.form("login_form"):
        user_cookie = st.text_input("WakaTime Session Cookie", type="password", help="Found in F12 -> Application -> Cookies -> 'session'")
        folder_id = st.text_input("Google Drive Folder ID")
        submitted = st.form_submit_button("💾 Save & Login")
        
        if submitted:
            if not user_cookie or not folder_id:
                st.error("❌ Please fill in both fields.")
            else:
                # UPDATE STATE INSTANTLY
                st.session_state.waka_session = user_cookie
                st.session_state.drive_folder = folder_id
                st.session_state.logged_in = True
                
                # SAVE COOKIES (Fixed Expiration Logic)
                # We use a explicit future date to avoid timezone bugs
                future_date = datetime.datetime.now() + datetime.timedelta(days=30)
                
                cookie_manager.set("waka_session", user_cookie, expires_at=future_date, key="set_waka")
                cookie_manager.set("drive_folder", folder_id, expires_at=future_date, key="set_drive")
                
                st.success("✅ Login Saved! Reloading...")
                time.sleep(1) 
                st.rerun()

# --- VIEW 2: AUTOMATION DASHBOARD ---
else:
    # Display current user (masked)
    safe_folder = str(st.session_state.drive_folder)[:5] + "..."
    st.success(f"✅ Connected (Folder: {safe_folder})")
    
    # Logout Button
    if st.button("🔄 Logout / Reset"):
        # Clear Memory
        st.session_state.logged_in = False
        st.session_state.waka_session = ""
        st.session_state.drive_folder = ""
        
        # Clear Browser Cookies
        cookie_manager.delete("waka_session", key="del_waka")
        cookie_manager.delete("drive_folder", key="del_drive")
        st.rerun()

    st.divider()

    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        wh = st.text_input("Working Hours", value="08:30")
    with col2:
        ot = st.text_input("Overtime", value="00:00")

    note = st.text_area("Notes", placeholder="Task details...")

    # Run Button
    if st.button("⚡ Run Automation", type="primary"):
        st.info("⏳ Starting Automation...")
        
        # Use credentials from memory
        bot = OfficeAutomator(logger=logger)
        bot.user_cookie = st.session_state.waka_session
        bot.folder_id = st.session_state.drive_folder
        
        try:
            bot.run(wh, ot, note)
            st.success("✅ Automation Complete!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    # Logs
    with st.expander("📜 Process Logs", expanded=True):
        for log in st.session_state.logs:
            st.code(log, language="text")