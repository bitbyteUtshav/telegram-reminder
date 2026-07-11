import os
import requests
from google import genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = """
বাংলায় আজকের ৫টি গুরুত্বপূর্ণ আন্তর্জাতিক, প্রতিরক্ষা, AI ও মহাকাশ বিষয় লিখো।
প্রতিটি ২-৩ লাইনে লিখবে।
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

message = response.text

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)

print("Message sent successfully!")
