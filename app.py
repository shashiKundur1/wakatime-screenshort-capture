import streamlit as st
import datetime
import extra_streamlit_components as stx
from automation import OfficeAutomator

# --- PAGE CONFIG ---
st.set_page_config(page_title="WakaTime Automator", page_icon="🚀", layout="centered")

# --- COOKIE MANAGER SETUP ---
# This tool allows us to save/load data from your browser's real cookies
@st.cache_resource
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# --- LOGGING SETUP ---
if "logs" not in st.session_state:
    st.session_state.logs = []

def logger(message):
    st.session_state.logs.append(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}")

# --- AUTHENTICATION LOGIC ---
st.title("🚀 Office Automator")

# 1. Try to get the cookie from the browser
stored_session = cookie_manager.get(cookie="waka_session")
stored_folder = cookie_manager.get(cookie="drive_folder")

# STATE: NOT LOGGED IN
if not stored_session:
    st.info("👋 Welcome! Please log in once to setup your automation.")
    
    with st.form("login_form"):
        user_cookie = st.text_input("WakaTime Session Cookie", type="password", help="Found in F12 -> Application -> Cookies -> 'session'")
        folder_id = st.text_input("Google Drive Folder ID")
        submitted = st.form_submit_button("💾 Save & Login")
        
        if submitted:
            if not user_cookie or not folder_id:
                st.error("Please fill in both fields.")
            else:
                # SAVE TO BROWSER COOKIES (Expires in 30 days)
                cookie_manager.set("waka_session", user_cookie, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                cookie_manager.set("drive_folder", folder_id, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                st.success("✅ Login Saved! Refreshing...")
                st.rerun()

# STATE: LOGGED IN
else:
    st.success(f"✅ Logged in (Folder: {stored_folder[:5]}...)")
    
    # Logout Button
    if st.button("bs Logout / Reset"):
        cookie_manager.delete("waka_session")
        cookie_manager.delete("drive_folder")
        st.rerun()

    st.divider()

    # --- AUTOMATION INPUTS ---
    col1, col2 = st.columns(2)
    with col1:
        wh = st.text_input("Working Hours", value="08:30")
    with col2:
        ot = st.text_input("Overtime", value="00:00")

    note = st.text_area("Notes", placeholder="Task details...")

    # --- RUN BUTTON ---
    if st.button("⚡ Run Automation", type="primary"):
        st.info("⏳ Starting Automation...")
        
        # Initialize Bot with the STORED credentials
        bot = OfficeAutomator(logger=logger)
        bot.user_cookie = stored_session
        bot.folder_id = stored_folder
        
        try:
            bot.run(wh, ot, note)
            st.success("✅ Automation Complete!")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    # --- LOGS ---
    with st.expander("📜 Process Logs", expanded=True):
        for log in st.session_state.logs:
            st.code(log, language="text")