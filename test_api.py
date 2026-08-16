import requests
import json

# API endpoint
API_URL = "http://localhost:8000/api/news"

# Test news data
test_news = {
    "telegram_message_id": 1,
    "title": "O'zbekiston yangi iqtisodiy strategiyani taqdim etdi",
    "text": "Prezident Shavkat Mirziyoyev 2026-2030 yillarga mo'ljallangan yangi iqtisodiy strategiyani taqdim etdi. Strategiya doirasida sanoatni rivojlantirish, eksportni ko'paytirish va xorijiy investitsiyalarni jalb qilish bo'yicha kompleks chora-tadbirlar nazarda tutilgan.",
    "image": "https://example.com/image.jpg",
    "video": "",
    "date": "2026-08-16T10:00:00",
    "telegram_url": "https://t.me/XabarTV_24/1"
}

# Send test news
try:
    response = requests.post(API_URL, json=test_news)
    if response.status_code == 200:
        print("✅ Yangilik muvaffaqiyatli qo'shildi!")
        print(f"Javob: {response.json()}")
    else:
        print(f"❌ Xatolik: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Xatolik: {e}")