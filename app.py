import streamlit as st
import datetime
import time
import extra_streamlit_components as stx
from automation import OfficeAutomator

# --- 1. CONFIGURATION & PHOSPHOR ICONS ---
st.set_page_config(page_title="WakaTime Automator", page_icon="⚡", layout="centered")

# Inject Phosphor Icons (Script) & Custom CSS
st.markdown("""
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
        /* --- GLOBAL THEME --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #000000; 
            color: #FFFFFF;
        }

        /* --- GLASSMORPHISM CARD STYLE --- */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .glass-card:hover {
            box-shadow: 0 0 25px rgba(255, 87, 34, 0.15);
            border-color: rgba(255, 87, 34, 0.3);
        }

        /* --- INPUT FIELDS --- */
        .stTextInput input, .stTextArea textarea {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            color: white !important;
            transition: all 0.2s ease-in-out;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #FF5722 !important;
            background-color: rgba(255, 87, 34, 0.05) !important;
            box-shadow: 0 0 10px rgba(255, 87, 34, 0.2);
        }

        /* --- BUTTONS (Orange Glow) --- */
        div.stButton > button {
            background: linear-gradient(135deg, #FF5722 0%, #FF8A65 100%);
            color: black !important;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 87, 34, 0.4);
        }
        
        div.stButton > button:active {
            transform: scale(0.98);
        }

        /* --- HEADERS --- */
        .custom-header {
            font-size: 2.2rem;
            font-weight: 700;
            background: -webkit-linear-gradient(left, #FF5722, #FFFFFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 2rem;
        }

        /* --- STATUS BADGES --- */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .status-connected {
            background: rgba(39, 174, 96, 0.15);
            color: #2ecc71;
            border: 1px solid rgba(39, 174, 96, 0.3);
        }
        .status-disconnected {
            background: rgba(255, 87, 34, 0.1);
            color: #FF5722;
            border: 1px solid rgba(255, 87, 34, 0.3);
        }
        
        /* HIDE DEFAULT ELEMENTS */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
    </style>
""", unsafe_allow_html=True)

# --- BACKEND LOGIC REMAINS THE SAME ---
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "waka_session" not in st.session_state:
    st.session_state.waka_session = ""
if "drive_folder" not in st.session_state:
    st.session_state.drive_folder = ""
if "logs" not in st.session_state:
    st.session_state.logs = []

def logger(message):
    timestamp = datetime.datetime.now().strftime('%H:%M')
    # Use HTML formatting for logs to make them look like a terminal
    log_entry = f"<span style='color: #888;'>[{timestamp}]</span> {message}"
    st.session_state.logs.append(log_entry)

# --- 2. LOGIC SYNC ---
all_cookies = cookie_manager.get_all()
cookie_session = all_cookies.get("waka_session")
cookie_folder = all_cookies.get("drive_folder")

if cookie_session and cookie_folder:
    if not st.session_state.logged_in:
        st.session_state.waka_session = cookie_session
        st.session_state.drive_folder = cookie_folder
        st.session_state.logged_in = True
        st.rerun()

# --- 3. THE MODERN UI STRUCTURE ---

# Header
st.markdown("""
    <div class="custom-header">
        <i class="ph-duotone ph-rocket-launch"></i> Office Automator <span style="font-size: 1rem; opacity: 0.5; font-weight: 400;">v3.0</span>
    </div>
""", unsafe_allow_html=True)

# VIEW 1: LOGIN (Glass Card)
if not st.session_state.logged_in:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="status-badge status-disconnected"><i class="ph-fill ph-lock-key"></i> Authentication Required</div>', unsafe_allow_html=True)
    st.caption(" ") # Spacer
    
    with st.form("login_form"):
        st.markdown("**Credentials Setup**")
        user_cookie = st.text_input("WakaTime Session", type="password", help="Paste your session cookie here")
        folder_id = st.text_input("Drive Folder ID")
        
        submitted = st.form_submit_button("Authenticate System")
        
        if submitted:
            if not user_cookie or not folder_id:
                st.error("Fields cannot be empty")
            else:
                st.session_state.waka_session = user_cookie
                st.session_state.drive_folder = folder_id
                st.session_state.logged_in = True
                
                future = datetime.datetime.now() + datetime.timedelta(days=30)
                cookie_manager.set("waka_session", user_cookie, expires_at=future, key="set_waka")
                cookie_manager.set("drive_folder", folder_id, expires_at=future, key="set_drive")
                
                st.success("Credentials Verified.")
                time.sleep(1)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# VIEW 2: DASHBOARD
else:
    # Status Bar
    safe_folder = str(st.session_state.drive_folder)[:5] + "..."
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div class="status-badge status-connected">
                <i class="ph-fill ph-wifi-high"></i> Connected to Drive ({safe_folder})
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Logout (Small link instead of big button)
    if st.button("Disconnect", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.waka_session = ""
        st.session_state.drive_folder = ""
        cookie_manager.delete("waka_session", key="del_waka")
        cookie_manager.delete("drive_folder", key="del_drive")
        st.rerun()

    # Main Inputs in Glass Card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<i class="ph-bold ph-clock"></i> **Working Hours**', unsafe_allow_html=True)
        wh = st.text_input("hours", value="08:30", label_visibility="collapsed")
    with col2:
        st.markdown('<i class="ph-bold ph-timer"></i> **Overtime**', unsafe_allow_html=True)
        ot = st.text_input("overtime", value="00:00", label_visibility="collapsed")

    st.markdown('<div style="margin-top: 15px;"><i class="ph-bold ph-notepad"></i> **Daily Notes**</div>', unsafe_allow_html=True)
    note = st.text_area("notes", placeholder="What did you achieve today?", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Action Button
    if st.button("Initiate Sequence", type="primary", use_container_width=True):
        progress_bar = st.progress(0, text="Initializing...")
        
        bot = OfficeAutomator(logger=logger)
        bot.user_cookie = st.session_state.waka_session
        bot.folder_id = st.session_state.drive_folder
        
        try:
            # Fake smooth progress for UX
            progress_bar.progress(10, text="Accessing Secure Browser...")
            time.sleep(0.5)
            progress_bar.progress(30, text="Capturing Analytics...")
            
            # Run Actual Bot
            bot.run(wh, ot, note)
            
            progress_bar.progress(100, text="Process Complete")
            st.balloons()
            st.markdown("""
                <div class="glass-card" style="border-color: #2ecc71; text-align: center;">
                    <i class="ph-fill ph-check-circle" style="font-size: 2rem; color: #2ecc71;"></i><br>
                    <strong>Update Successful</strong>
                </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            progress_bar.empty()
            st.markdown(f"""
                <div class="glass-card" style="border-color: #e74c3c;">
                    <i class="ph-fill ph-warning" style="font-size: 1.5rem; color: #e74c3c;"></i>
                    <strong>System Error:</strong> {e}
                </div>
            """, unsafe_allow_html=True)

    # Terminal Style Logs
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("System Terminal", expanded=True):
        for log in st.session_state.logs:
            st.markdown(f"<div style='font-family: monospace; font-size: 0.85rem;'>{log}</div>", unsafe_allow_html=True)