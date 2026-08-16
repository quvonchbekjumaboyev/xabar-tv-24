import os
import requests
import json
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("8769053184:AAE14RhNXFsdsmHi7CTHXDWCxLdz2-ExbFg")
API_URL = "http://localhost:8000/api/news"

def send_news_to_api(news_data):
    """Send news to API"""
    try:
        response = requests.post(API_URL, json=news_data)
        if response.status_code == 200:
            logger.info(f"✅ News sent to API: {news_data.get('title')}")
            return True
        else:
            logger.error(f"❌ API error: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error sending news: {e}")
        return False

def get_telegram_updates(offset=0):
    """Get updates from Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 30}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data.get("result", [])
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
    return []

def process_telegram_message(message):
    """Process Telegram message and create news"""
    try:
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        message_id = message.get("message_id")
        
        # Parse message (you can customize this logic)
        lines = text.split("\n")
        title = lines[0] if lines else "Sarlavhasiz"
        content = "\n".join(lines[1:]) if len(lines) > 1 else ""
        
        news_data = {
            "telegram_message_id": message_id,
            "title": title,
            "text": content,
            "image": "",
            "video": "",
            "date": message.get("date"),
            "telegram_url": f"https://t.me/XabarTV_24/{message_id}"
        }
        
        return send_news_to_api(news_data)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return False

def main():
    """Main bot loop"""
    logger.info("Telegram bot ishga tushdi...")
    offset = 0
    
    while True:
        try:
            updates = get_telegram_updates(offset)
            
            for update in updates:
                if "message" in update:
                    message = update["message"]
                    process_telegram_message(message)
                    offset = update["update_id"] + 1
            
        except Exception as e:
            logger.error(f"Bot error: {e}")
            
        # Wait before next request
        import time
        time.sleep(2)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_token_here":
        logger.error("❌ Telegram token .env faylda topilmadi!")
        exit(1)
    
    main()