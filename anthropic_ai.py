"""
anthropic_ai.py
----------------
Claude API (Anthropic/ZenMux) ব্যবহার করে ইংরেজি নিউজকে বাংলায় সামারি এবং
Facebook ক্যাপশনে রূপান্তর করে।
"""

import time
import anthropic

import config

_client = anthropic.Anthropic(
    api_key=config.ANTHROPIC_API_KEY,
    base_url=config.ANTHROPIC_BASE_URL,  # None হলে SDK নিজে থেকেই অফিসিয়াল api.anthropic.com ব্যবহার করবে
)


def _call_claude(prompt: str, retries: int = 3) -> str:
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = _client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            text_parts = [block.text for block in response.content if block.type == "text"]
            return "".join(text_parts).strip()
        except Exception as e:
            last_error = e
            print(f"⚠️ Claude কল ব্যর্থ (চেষ্টা {attempt}/{retries}): {e}")
            time.sleep(2 * attempt)
    raise RuntimeError(f"Claude API একাধিকবার চেষ্টার পরও ব্যর্থ হলো: {last_error}")


def summarize_to_bangla(title: str, summary: str, category: str) -> str:
    prompt = f"""তুমি একজন পেশাদার বাংলা নিউজ এডিটর।
নিচের ইংরেজি খবরটি পড়ে সহজ, স্বাভাবিক বাংলায় ৩-৪ বাক্যের একটি সংক্ষিপ্ত সামারি লেখো।
কোনো ভূমিকা বা মন্তব্য যোগ করবে না, শুধু খবরের সারমর্ম দাও।
ক্যাটাগরি: {category}

শিরোনাম: {title}
বিবরণ: {summary}

শুধু বাংলা সামারিটুকু ফেরত দাও, অন্য কিছু নয়।"""
    return _call_claude(prompt)


def generate_facebook_caption(title: str, bangla_summary: str, link: str, category: str) -> str:
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
    return _call_claude(prompt)
