import requests

def send_alert():
    # Plain text layout with zero special formatting characters to bypass filters
    reminder_msg = "COACH REMINDER: Task: Walk. This task needs to be completed right now! Note: Call me during your walk."
    
    url = "https://telegram.org"
    
    payload = {
        "chat_id": "1367309270",
        "text": reminder_msg
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Success! Notification sent down to Telegram channel tray perfectly.")
        else:
            print(f"Server responded with code: {response.status_code}")
    except Exception as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    send_alert()
