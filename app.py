import streamlit as st
import datetime
import time
import extra_streamlit_components as stx
from automation import OfficeAutomator

# --- PAGE CONFIG ---
st.set_page_config(page_title="WakaTime Automator", page_icon="🚀", layout="centered")

# --- SESSION STATE SETUP (Instant Memory) ---
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

# --- MAIN UI ---
st.title("🚀 Office Automator")

# 1. READ COOKIES (The slow persistent storage)
# We check if cookies exist to auto-login returning users
cookie_session = cookie_manager.get(cookie="waka_session")
cookie_folder = cookie_manager.get(cookie="drive_folder")

# 2. SYNC LOGIC: If cookies exist, force login in session state
if cookie_session and cookie_folder:
    if not st.session_state.logged_in:
        st.session_state.waka_session = cookie_session
        st.session_state.drive_folder = cookie_folder
        st.session_state.logged_in = True
        # Silent rerun to refresh UI immediately
        st.rerun()

# --- VIEW 1: LOGIN SCREEN ---
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
                # A. Update INSTANT Memory (So UI updates now)
                st.session_state.waka_session = user_cookie
                st.session_state.drive_folder = folder_id
                st.session_state.logged_in = True
                
                # B. Update SLOW Cookie (So it remembers you tomorrow)
                expires = datetime.datetime.now() + datetime.timedelta(days=30)
                cookie_manager.set("waka_session", user_cookie, expires_at=expires, key="set_waka")
                cookie_manager.set("drive_folder", folder_id, expires_at=expires, key="set_drive")
                
                st.success("✅ Login Verified! Loading...")
                time.sleep(1) # Tiny pause to let cookies settle
                st.rerun()

# --- VIEW 2: AUTOMATION DASHBOARD ---
else:
    # Header with partial Folder ID
    safe_folder = str(st.session_state.drive_folder)[:5] + "..."
    st.success(f"✅ Connected (Folder: {safe_folder})")
    
    # Logout
    if st.button("🔄 Logout / Reset"):
        # Clear Instant Memory
        st.session_state.logged_in = False
        st.session_state.waka_session = ""
        st.session_state.drive_folder = ""
        
        # Clear Cookies
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
        
        # USE CREDENTIALS FROM SESSION STATE
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