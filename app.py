import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import requests
import json

# ---------------------------------------------------------
# 1. INITIALIZATION & SECURE DATABASE GATEWAY
# ---------------------------------------------------------
try:
    # Read the raw single-string block directly from Streamlit secrets
    raw_credential_data = st.secrets["GCP_JSON_CREDENTIALS"]
    
    # Load the structured JSON dictionary natively
    gcp_dict = json.loads(raw_credential_data)
    
    # Open connection via standard Google API scopes
    scope = ["https://google.com", "https://googleapis.com"]
    creds = Credentials.from_service_account_info(gcp_dict, scopes=scope)
    gc = gspread.authorize(creds)
    
    # Secure active connection to data worksheets
    spreadsheet = gc.open("Boyfriend_Routine_DB")
    tasks_sheet = spreadsheet.worksheet("Tasks")
    fitness_sheet = spreadsheet.worksheet("Fitness")
except Exception as e:
    st.error(f"Backend Verification Failure: {e}")
    st.stop()

# Load verified Telegram bot configuration settings 
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

def send_push_notification(message):
    """Sends a real-time system notification alert directly to his phone via Telegram."""
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        st.error(f"Notification alert delivery error: {e}")

# ---------------------------------------------------------
# 2. APPLICATION VISUAL DESIGN FRAMEWORK
# ---------------------------------------------------------
st.set_page_config(page_title="Athlete Peak Performance Hub", page_icon="🏆", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #ff4b4b; text-align: center; font-family: 'Arial Black', sans-serif; }
    h2, h3 { color: #ffffff; }
    .stButton>button { background-color: #ff4b4b; color: white; width: 100%; border-radius: 8px; }
    .card { background-color: #1e222b; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

st.title("🏆 ATHLETE PEAK PERFORMANCE HUB")
st.subheader("⚡ Long-Distance Coordinated Routine & Tracker")

col_left, col_right = st.columns(2, gap="large")

# ---------------------------------------------------------
# 3. COLUMN 1: INTERACTIVE DAILY DIRECTIVES & TO-DO LISTS
# ---------------------------------------------------------
with col_left:
    st.header("📝 Today's Routine & Tasks")
    raw_tasks = tasks_sheet.get_all_records()
    
    if not raw_tasks:
        st.info("Coach hasn't assigned any training tasks yet today!")
    else:
        for idx, row in enumerate(raw_tasks):
            sheet_row_idx = idx + 2 
            status_emoji = "✅" if row['Status'] == "Completed" else "⏳"
            
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <h4>{status_emoji} [{row['Time']}] {row['Task']}</h4>
                    <p style="color: #888888; font-style: italic;">Coach's Note: {row['Hype Note']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                is_done = row['Status'] == "Completed"
                checked = st.checkbox("Mark as Completed", value=is_done, key=f"task_{sheet_row_idx}")
                
                if checked != is_done:
                    new_status = "Completed" if checked else "Pending"
                    tasks_sheet.update_cell(sheet_row_idx, 3, new_status)
                    if checked:
                        send_push_notification(f"🔥 *Workout Update:* He just completed: '{row['Task']}' at {row['Time']}!")
                    st.rerun()
            st.write("---")

# ---------------------------------------------------------
# 4. COLUMN 2: REAL-TIME FITNESS PROGRESS & COACH ADVANCED PANELS
# ---------------------------------------------------------
with col_right:
    st.header("📊 Performance Matrix")
    try:
        raw_fitness = fitness_sheet.get_all_records()
        for fit_row in raw_fitness:
            val = float(fit_row['Value'])
            target = float(fit_row['Target'])
            progress = min(val / target, 1.0) if target > 0 else 0.0
            
            st.metric(label=f"👟 {fit_row['Metric']}", value=f"{int(val)} / {int(target)}")
            st.progress(progress)
    except Exception as fetch_err:
        st.info("Log fitness tracking metrics via your Google Sheet to view progress bars here.")
    
    st.write("---")
    
    with st.expander("🛠️ Coach Admin Controls (Hidden Option)"):
        st.subheader("Assign a New Task & Push Alert")
        with st.form("new_task_form", clear_on_submit=True):
            new_time = st.text_input("Time Slot (e.g., 08:30 AM)")
            new_task = st.text_input("Task Assignment")
            new_hype = st.text_area("Hype Note / Instructions")
            submit_btn = st.form_submit_button("Deploy Task to Phone")
            
            if submit_btn and new_task:
                tasks_sheet.append_row([new_time, new_task, "Pending", new_hype])
                alert_msg = f"🔔 *New Directive from Coach:* \n⏰ Time: {new_time}\n🏋️‍♂️ Task: {new_task}\n💬 Note: {new_hype}"
                send_push_notification(alert_msg)
                st.success("Task deployed and notification sent successfully!")
                st.rerun()
