import streamlit as st
import pandas as pd
import requests

# ---------------------------------------------------------
# 1. LINK YOUR PERSONAL GOOGLE SHEET DATABASE HERE
# ---------------------------------------------------------
# Embedded with your verified Sheet ID securely
SHEET_ID = "1Cweyn2B7L5ZVbtgE0crA0JQ8O_qRjbkiZ55wXa1Xn4A"

try:
    # Build clean CSV export links for both tabs using your Sheet ID
    tasks_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Tasks"
    fitness_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Fitness"
    
    # Read the live rows using pandas data pipelines
    df_tasks = pd.read_csv(tasks_url)
    
    # Try reading fitness rows, fallback to empty if tab is still blank
    try:
        df_fitness = pd.read_csv(fitness_url)
        df_fitness.columns = df_fitness.columns.str.strip().str.lower()
        raw_fitness = df_fitness.to_dict(orient="records")
    except:
        raw_fitness = []
    
    # Clean and force column headers to be lowercase to avoid typos
    df_tasks.columns = df_tasks.columns.str.strip().str.lower()
    
    # Convert active tables to dictionary arrays
    raw_tasks = df_tasks.to_dict(orient="records")
except Exception as e:
    st.error(f"Live Spreadsheet Read Error: {e}")
    st.info("💡 Make sure you clicked the green 'Share' button in your Google Sheet, changed General Access to 'Anyone with the link can view', and saved it!")
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
    
    if not raw_tasks or pd.isna(raw_tasks[0].get('task')):
        st.info("Coach hasn't assigned any training tasks yet today!")
    else:
        for idx, row in enumerate(raw_tasks):
            # Read columns dynamically by matching lowercase strings safely
            time_val = str(row.get('time') or '00:00')
            task_val = str(row.get('task') or 'No Task Assigned')
            status_val = str(row.get('status') or 'Pending')
            hype_val = str(row.get('hype note') or '')
            
            # Skip empty rows gracefully if any
            if task_val == 'nan' or time_val == 'nan':
                continue
                
            status_emoji = "✅" if status_val.strip().lower() == "completed" else "⏳"
            
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <h4>{status_emoji} [{time_val}] {task_val}</h4>
                    <p style="color: #888888; font-style: italic;">Coach's Note: {hype_val}</p>
                </div>
                """, unsafe_allow_html=True)
                
                is_done = status_val.strip().lower() == "completed"
                checked = st.checkbox("Mark as Completed", value=is_done, key=f"task_{idx}")
                
                if checked != is_done:
                    st.info("✏️ Update the 'Status' column to 'Completed' inside your Google Sheet to finish this task live!")
            st.write("---")

# ---------------------------------------------------------
# 4. COLUMN 2: PROGRESS MATRIX OVERVIEW
# ---------------------------------------------------------
with col_right:
    st.header("📊 Performance Matrix")
    
    if not raw_fitness or pd.isna(raw_fitness[0].get('metric')):
        st.info("Populate metric entries inside your 'Fitness' sheet tab to view progress bars here.")
    else:
        for fit_row in raw_fitness:
            try:
                metric_name = str(fit_row.get('metric') or 'Activity Log')
                val = float(fit_row.get('value', 0))
                target = float(fit_row.get('target', 1))
                
                if metric_name == 'nan':
                    continue
                    
                progress = min(val / target, 1.0) if target > 0 else 0.0
                
                st.metric(label=f"👟 {metric_name}", value=f"{int(val)} / {int(target)}")
                st.progress(progress)
            except:
                pass
