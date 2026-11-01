import pandas as pd
import requests
import datetime

# Link your verified Google Sheet database
SHEET_ID = "1Cweyn2B7L5ZVbtgE0crA0JQ8O_qRjbkiZ55wXa1Xn4A"
TELEGRAM_BOT_TOKEN = "9235933487:AAGA-b3aAqS8YxfjG2c7GSaJyQNXmXZOWO8"
TELEGRAM_CHAT_ID = "1367309270"

def send_alert(message):
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"})

try:
    # Fetch your live tasks
    url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Tasks"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
    
    # Get the current time (formatted to match your sheet style, e.g., '2:00 PM')
    now = datetime.datetime.now()
    current_time_str = now.strftime("%I:%M %p").lstrip("0") # Strips leading zeros like 02:00 -> 2:00
    
    for _, row in df.iterrows():
        task_time = str(row.get('time')).strip()
        task_name = str(row.get('task')).strip()
        status = str(row.get('status')).strip().lower()
        hype = str(row.get('hype note')).strip()
        
        # If the task matches the clock and is not done yet, send a phone alert
        if task_time == current_time_str and status != "completed":
            reminder_msg = f"⏰ *COACH REMINDER:* \n🏋️‍♂️ Task: {task_name}\n⏳ This task needs to be completed right now!\n💬 Note: {hype}"
            send_alert(reminder_msg)
            
except Exception as e:
    print(f"Error checking routine schedule: {e}")
