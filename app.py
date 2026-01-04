import streamlit as st
import datetime
import time
import extra_streamlit_components as stx
from automation import OfficeAutomator

# --- 1. CONFIGURATION & PHOSPHOR ICONS ---
st.set_page_config(page_title="WakaTime Automator", page_icon="⚡", layout="centered")

# Inject Phosphor Icons, GSAP & Custom CSS
st.markdown("""
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        /* --- GLOBAL THEME --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #000000;
            color: #FFFFFF;
        }

        /* --- COMPACT CONTAINER --- */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-width: 600px !important;
        }

        section[data-testid="stSidebar"] {display: none;}

        /* --- GLASSMORPHISM CARD STYLE --- */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 1rem 1.2rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .glass-card:hover {
            box-shadow: 0 0 20px rgba(255, 87, 34, 0.12);
            border-color: rgba(255, 87, 34, 0.25);
        }

        /* --- INPUT FIELDS --- */
        .stTextInput input, .stTextArea textarea {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
            color: white !important;
            padding: 0.5rem !important;
            font-size: 0.9rem !important;
            transition: all 0.2s ease-in-out;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #FF5722 !important;
            background-color: rgba(255, 87, 34, 0.05) !important;
            box-shadow: 0 0 8px rgba(255, 87, 34, 0.2);
        }

        .stTextArea textarea {
            min-height: 60px !important;
        }

        /* --- BUTTONS (Orange Glow) --- */
        div.stButton > button {
            background: linear-gradient(135deg, #FF5722 0%, #FF8A65 100%);
            color: black !important;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }

        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(255, 87, 34, 0.4);
        }

        div.stButton > button:active {
            transform: scale(0.98);
        }

        /* --- HEADERS --- */
        .custom-header {
            font-size: 1.6rem;
            font-weight: 700;
            background: -webkit-linear-gradient(left, #FF5722, #FFFFFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 0.8rem;
        }

        /* --- STATUS BADGES --- */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 16px;
            font-size: 0.75rem;
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

        /* --- SUCCESS ANIMATION --- */
        .success-box {
            text-align: center;
            padding: 1.5rem;
            background: rgba(46, 204, 113, 0.08);
            border: 1px solid rgba(46, 204, 113, 0.3);
            border-radius: 12px;
            margin-top: 1rem;
        }

        .success-icon {
            font-size: 2.5rem;
            color: #2ecc71;
            opacity: 0;
        }

        .success-text {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2ecc71;
            margin: 0.5rem 0;
            opacity: 0;
        }

        .fun-text {
            font-size: 0.85rem;
            color: rgba(255,255,255,0.6);
            font-style: italic;
            opacity: 0;
        }

        /* HIDE DEFAULT ELEMENTS */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* --- MOBILE RESPONSIVE --- */
        @media (max-width: 768px) {
            .block-container {
                padding: 0.5rem !important;
                max-width: 100% !important;
            }
            .custom-header {
                font-size: 1.3rem;
                gap: 8px;
                margin-bottom: 0.5rem;
            }
            .glass-card {
                padding: 0.8rem;
                margin-bottom: 0.5rem;
                border-radius: 10px;
            }
            .status-badge {
                font-size: 0.7rem;
                padding: 3px 8px;
            }
            div.stButton > button {
                padding: 0.4rem 0.8rem;
                font-size: 0.85rem;
            }
            .stTextInput input, .stTextArea textarea {
                font-size: 0.85rem !important;
                padding: 0.4rem !important;
            }
            .success-icon { font-size: 2rem; }
            .success-text { font-size: 1rem; }
            .fun-text { font-size: 0.75rem; }
        }

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
        <i class="ph-duotone ph-rocket-launch"></i> Office Automator <span style="font-size: 0.8rem; opacity: 0.4; font-weight: 400;">v3.0</span>
    </div>
""", unsafe_allow_html=True)

# VIEW 1: LOGIN (Glass Card)
if not st.session_state.logged_in:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="status-badge status-disconnected"><i class="ph-fill ph-lock-key"></i> Auth Required</div>', unsafe_allow_html=True)
    
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
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div class="status-badge status-connected">
                <i class="ph-fill ph-wifi-high"></i> Drive ({safe_folder})
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

    # Main Inputs
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<i class="ph-bold ph-clock"></i> **Hours**', unsafe_allow_html=True)
        wh = st.text_input("hours", value="08:30", label_visibility="collapsed")
    with col2:
        st.markdown('<i class="ph-bold ph-timer"></i> **OT**', unsafe_allow_html=True)
        ot = st.text_input("overtime", value="00:00", label_visibility="collapsed")

    st.markdown('<i class="ph-bold ph-notepad"></i> **Notes**', unsafe_allow_html=True)
    note = st.text_area("notes", placeholder="What did you achieve?", label_visibility="collapsed", height=60)

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
            
            progress_bar.progress(100, text="Done!")
            st.markdown("""
                <div class="success-box">
                    <i class="ph-fill ph-check-circle success-icon" id="successIcon"></i>
                    <div class="success-text" id="successText">Update Successful</div>
                    <div class="fun-text" id="funText">Another day, another spreadsheet conquered.</div>
                </div>
                <script>
                    setTimeout(() => {
                        if (typeof gsap !== 'undefined') {
                            gsap.to("#successIcon", {
                                opacity: 1,
                                scale: 1.2,
                                duration: 0.4,
                                ease: "back.out(1.7)"
                            });
                            gsap.to("#successIcon", {
                                scale: 1,
                                duration: 0.3,
                                delay: 0.4,
                                ease: "elastic.out(1, 0.5)"
                            });
                            gsap.to("#successText", {
                                opacity: 1,
                                y: 0,
                                duration: 0.5,
                                delay: 0.3,
                                ease: "back.out(1.7)"
                            });
                            gsap.from("#successText", {
                                y: 20,
                                duration: 0.5,
                                delay: 0.3
                            });
                            gsap.to("#funText", {
                                opacity: 1,
                                duration: 0.6,
                                delay: 0.6,
                                ease: "power2.out"
                            });
                        } else {
                            document.getElementById('successIcon').style.opacity = 1;
                            document.getElementById('successText').style.opacity = 1;
                            document.getElementById('funText').style.opacity = 1;
                        }
                    }, 100);
                </script>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            progress_bar.empty()
            st.markdown(f"""
                <div class="glass-card" style="border-color: #e74c3c; padding: 0.8rem;">
                    <i class="ph-fill ph-warning" style="font-size: 1.2rem; color: #e74c3c;"></i>
                    <strong>Error:</strong> {e}
                </div>
            """, unsafe_allow_html=True)

    # Terminal Style Logs
    with st.expander("Terminal", expanded=False):
        for log in st.session_state.logs:
            st.markdown(f"<div style='font-family: monospace; font-size: 0.8rem;'>{log}</div>", unsafe_allow_html=True)