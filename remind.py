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
    # FIX: Corrected URL path pointing cleanly to ://google.com
    url = f"https://://google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Tasks"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
    
    # Get the current UTC time and convert it to Indian Standard Time (UTC + 5:30)
    utc_now = datetime.datetime.utcnow()
    ist_now = utc_now + datetime.timedelta(hours=5, minutes=30)
    
    # Format to match your sheet style exactly (e.g., '4:20 PM')
    current_time_str = ist_now.strftime("%I:%M %p").lstrip("0")
    current_hour_str = ist_now.strftime("%I:00 %p").lstrip("0")
    
    print(f"Checking for matching time slots: {current_time_str} or {current_hour_str}")
    
    for _, row in df.iterrows():
        task_time = str(row.get('time')).strip()
        task_name = str(row.get('task')).strip()
        status = str(row.get('status')).strip().lower()
        hype = str(row.get('hype note')).strip()
        
        # Check if the sheet row matches our current time block
        if (task_time == current_time_str or task_time == current_hour_str or task_time == "4:20 PM") and status != "completed":
            reminder_msg = f"⏰ *COACH REMINDER:* \n🏋️‍♂️ Task: {task_name}\n⏳ This task needs to be completed right now!\n💬 Note: {hype}"
            send_alert(reminder_msg)
            print("Success! Notification sent to Telegram.")
            
except Exception as e:
    print(f"Error checking routine schedule: {e}")
