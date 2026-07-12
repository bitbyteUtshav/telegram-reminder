"""
gemini_ai.py
------------
Gemini API ব্যবহার করে ইংরেজি নিউজকে বাংলায় সামারি এবং
Facebook ক্যাপশনে রূপান্তর করে।
"""

import time
import google.generativeai as genai

import config

genai.configure(api_key=config.GEMINI_API_KEY)
_model = genai.GenerativeModel(config.GEMINI_MODEL)


def _call_gemini(prompt: str, retries: int = 3) -> str:
    """Gemini API কল করে, নেটওয়ার্ক এরর হলে কয়েকবার চেষ্টা করে।"""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = _model.generate_content(prompt)
            return (response.text or "").strip()
        except Exception as e:
            last_error = e
            print(f"⚠️ Gemini কল ব্যর্থ (চেষ্টা {attempt}/{retries}): {e}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"Gemini API একাধিকবার চেষ্টার পরও ব্যর্থ হলো: {last_error}")


def summarize_to_bangla(title: str, summary: str, category: str) -> str:
    """
    একটি ইংরেজি নিউজ আইটেমকে সংক্ষিপ্ত, স্বাভাবিক বাংলা পোস্টে রূপান্তর করে।
    """
    prompt = f"""তুমি একজন পেশাদার বাংলা নিউজ এডিটর।
নিচের ইংরেজি খবরটি পড়ে সহজ, স্বাভাবিক বাংলায় ৩-৪ বাক্যের একটি সংক্ষিপ্ত সামারি লেখো।
কোনো ভূমিকা বা মন্তব্য যোগ করবে না, শুধু খবরের সারমর্ম দাও।
ক্যাটাগরি: {category}

শিরোনাম: {title}
বিবরণ: {summary}

শুধু বাংলা সামারিটুকু ফেরত দাও, অন্য কিছু নয়।"""
    return _call_gemini(prompt)


def generate_facebook_caption(title: str, bangla_summary: str, link: str, category: str) -> str:
    """
    Facebook পোস্টের জন্য আকর্ষণীয় বাংলা ক্যাপশন + হ্যাশট্যাগ তৈরি করে।
    """
    prompt = f"""তুমি একজন সোশ্যাল মিডিয়া কনটেন্ট রাইটার।
নিচের খবরের ভিত্তিতে Facebook-এর জন্য একটি আকর্ষণীয় বাংলা ক্যাপশন লেখো।
এর মধ্যে থাকবে:
- একটি ক্যাচি শুরু (হুক লাইন)
- ২-৩ বাক্যের মূল বার্তা
- শেষে ৩-৫টি প্রাসঙ্গিক বাংলা/ইংরেজি হ্যাশট্যাগ

ক্যাটাগরি: {category}
শিরোনাম: {title}
সামারি: {bangla_summary}
সোর্স লিংক: {link}

শুধু চূড়ান্ত ক্যাপশনটুকু ফেরত দাও।"""
    return _call_gemini(prompt)
