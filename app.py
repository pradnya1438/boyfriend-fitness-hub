import streamlit as st
from streamlit_gsheets import GSheetsConnection
import requests
import json

# ---------------------------------------------------------
# 1. INITIALIZATION & NATIVE STREAMLIT DATA CONN
# ---------------------------------------------------------
try:
    # Explicitly pull down and format JSON variables from Secrets dashboard
    raw_credential_data = st.secrets["GCP_JSON_CREDENTIALS"]
    gcp_dict = json.loads(raw_credential_data)
    
    # Establish Connection using Streamlit's official GSheets system adapter
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Read the data frames live from your worksheets using the service_account keyword parameter
    df_tasks = conn.read(spreadsheet="Boyfriend_Routine_DB", worksheet="Tasks", service_account=gcp_dict, ttl=2)
    df_fitness = conn.read(spreadsheet="Boyfriend_Routine_DB", worksheet="Fitness", service_account=gcp_dict, ttl=2)
    
    # Convert active records to readable row dicts
    raw_tasks = df_tasks.to_dict(orient="records")
    raw_fitness = df_fitness.to_dict(orient="records")
except Exception as e:
    st.error(f"Live Spreadsheet Read Error: {e}")
    st.info("Make sure the Google Sheet name matches 'Boyfriend_Routine_DB' exactly and contains your data tables.")
    st.stop()

# Load verified Telegram parameters
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

def send_push_notification(message):
    """Sends a real-time system notification alert directly to his phone via Telegram."""
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        st.error(f"Notification error: {e}")

# ---------------------------------------------------------
# 2. VISUAL LAYOUT & INTERFACE OVERVIEW
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
# 3. COLUMN 1: INTERACTIVE DAILY TO-DO LISTS
# ---------------------------------------------------------
with col_left:
    st.header("📝 Today's Routine & Tasks")
    
    if not raw_tasks:
        st.info("Coach hasn't assigned any training tasks yet today!")
    else:
        for idx, row in enumerate(raw_tasks):
            status_emoji = "✅" if row.get('Status') == "Completed" else "⏳"
            
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <h4>{status_emoji} [{row.get('Time', '00:00')}] {row.get('Task', 'No Task')}</h4>
                    <p style="color: #888888; font-style: italic;">Coach's Note: {row.get('Hype Note', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                is_done = row.get('Status') == "Completed"
                checked = st.checkbox("Mark as Completed", value=is_done, key=f"task_{idx}")
                
                if checked != is_done:
                    st.info("Log directly onto your data sheet to clear status variables live.")
            st.write("---")

# ---------------------------------------------------------
# 4. COLUMN 2: PROGRESS MATRIX OVERVIEW
# ---------------------------------------------------------
with col_right:
    st.header("📊 Performance Matrix")
    
    if raw_fitness:
        for fit_row in raw_fitness:
            try:
                val = float(fit_row.get('Value', 0))
                target = float(fit_row.get('Target', 1))
                progress = min(val / target, 1.0) if target > 0 else 0.0
                
                st.metric(label=f"👟 {fit_row.get('Metric', 'Activity')}", value=f"{int(val)} / {int(target)}")
                st.progress(progress)
            except:
                pass
    else:
        st.info("Populate metric entries inside your sheet tables to clear metric bars here.")
