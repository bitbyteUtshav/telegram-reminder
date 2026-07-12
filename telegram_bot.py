"""
telegram_bot.py
----------------
Telegram-এ মেসেজ পাঠানোর জন্য হেল্পার ফাংশন।
python-telegram-bot লাইব্রেরি ব্যবহার করে (async)।
"""

import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

import config

CATEGORY_EMOJI = {
    "news": "📰",
    "defense": "🛡️",
    "ai": "🤖",
    "space": "🚀",
}


def _escape_markdown_v2(text: str) -> str:
    """Telegram MarkdownV2 এর জন্য স্পেশাল ক্যারেক্টার এস্কেপ করে।"""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    for ch in special_chars:
        text = text.replace(ch, f"\\{ch}")
    return text


def format_news_message(category: str, title: str, bangla_summary: str, link: str, source: str) -> str:
    emoji = CATEGORY_EMOJI.get(category, "📌")
    title_esc = _escape_markdown_v2(title)
    summary_esc = _escape_markdown_v2(bangla_summary)
    source_esc = _escape_markdown_v2(source)
    link_esc = _escape_markdown_v2(link)

    return (
        f"{emoji} *{title_esc}*\n\n"
        f"{summary_esc}\n\n"
        f"🔗 সূত্র: {source_esc}\n"
        f"{link_esc}"
    )


async def send_message_async(text: str, chat_id: str = None) -> None:
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    chat_id = chat_id or config.TELEGRAM_CHAT_ID
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=False,
        )
    except TelegramError as e:
        print(f"⚠️ MarkdownV2 দিয়ে পাঠাতে ব্যর্থ, প্লেইন টেক্সট দিয়ে চেষ্টা করা হচ্ছে: {e}")
        # Markdown এস্কেপিং এ সমস্যা হলে প্লেইন টেক্সট ফলব্যাক
        plain = text.replace("\\", "")
        await bot.send_message(chat_id=chat_id, text=plain, disable_web_page_preview=False)


def send_message(text: str, chat_id: str = None) -> None:
    """সিঙ্ক্রোনাস র‍্যাপার — GitHub Actions স্ক্রিপ্ট থেকে সহজে কল করার জন্য।"""
    asyncio.run(send_message_async(text, chat_id))
