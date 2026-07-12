"""
config.py
---------
সব environment variable / secret এক জায়গায় লোড করে রাখে।
GitHub Actions এ এগুলো Repository Secrets থেকে আসবে।
লোকাল টেস্টের জন্য .env ফাইল ব্যবহার করা যায় (python-dotenv দিয়ে)।
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_env(name: str, required: bool = True, default: str = None) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise EnvironmentError(
            f"❌ প্রয়োজনীয় environment variable পাওয়া যায়নি: {name}\n"
            f"GitHub repo Settings > Secrets and variables > Actions এ এটা যোগ করুন, "
            f"অথবা লোকাল .env ফাইলে দিন।"
        )
    return value


# ---- Telegram ----
TELEGRAM_BOT_TOKEN = _get_env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _get_env("TELEGRAM_CHAT_ID")

# ---- Gemini ----
GEMINI_API_KEY = _get_env("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ---- Claude (Anthropic) ----
ANTHROPIC_API_KEY = _get_env("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# ---- AI Provider ----
DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "gemini")  # "gemini" অথবা "claude"

# ---- RSS ফিড সোর্স (ক্যাটাগরি অনুযায়ী) ----
RSS_FEEDS = {
    "news": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.aljazeera.com/xml/rss/all.xml",
    ],
    "defense": [
        "https://www.defensenews.com/arc/outboundfeeds/rss/",
        "https://defence-blog.com/feed",
    ],
    "ai": [
        "https://www.artificialintelligence-news.com/feed/",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
    ],
    "space": [
        "https://spacenews.com/feed/",
        "https://www.space.com/feeds.xml",
    ],
}

MAX_ITEMS_PER_CATEGORY = int(os.getenv("MAX_ITEMS_PER_CATEGORY", "3"))
