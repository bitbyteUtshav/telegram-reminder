"""
handlers.py
-----------
এইগুলো শুধুমাত্র 'polling mode' (bot.py) চালালে কাজে লাগে —
অর্থাৎ বট যদি ২৪/৭ কোনো সার্ভারে চলে এবং ইউজার লাইভ কমান্ড পাঠায়।
GitHub Actions শিডিউলড মোডে এই ফাইলটার দরকার হয় না (তখন main.py চলে)।

এখানে প্রতিটা /news, /defense, /ai, /space, /post কমান্ডের পর
ইউজারকে ইনলাইন বাটনে জিজ্ঞেস করা হয়: 🟢 Gemini নাকি 🟣 Claude দিয়ে উত্তর চান।
বাটন চাপার পর সেই প্রোভাইডার দিয়েই সামারি/ক্যাপশন তৈরি হয়।
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import news_fetcher
import ai_provider
import telegram_bot

CATEGORY_COMMANDS = {"news", "defense", "ai", "space"}


def _provider_keyboard(action: str, category: str) -> InlineKeyboardMarkup:
    """action: 'summarize' বা 'caption' — কোন কাজের জন্য প্রোভাইডার বেছে নেওয়া হচ্ছে।"""
    buttons = [
        InlineKeyboardButton(
            ai_provider.PROVIDER_LABELS["gemini"], callback_data=f"{action}:{category}:gemini"
        ),
        InlineKeyboardButton(
            ai_provider.PROVIDER_LABELS["claude"], callback_data=f"{action}:{category}:claude"
        ),
    ]
    return InlineKeyboardMarkup([buttons])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 স্বাগতম! আমি একটি AI নিউজ বট।\n\n"
        "কমান্ডসমূহ:\n"
        "/news — সাধারণ খবর\n"
        "/defense — প্রতিরক্ষা সংক্রান্ত খবর\n"
        "/ai — এআই সংক্রান্ত খবর\n"
        "/space — মহাকাশ সংক্রান্ত খবর\n"
        "/post <ক্যাটাগরি> — ঐ ক্যাটাগরির জন্য Facebook ক্যাপশন বানাও\n\n"
        "প্রতিটা কমান্ডের পর আপনাকে জিজ্ঞেস করা হবে 🟢 Gemini নাকি 🟣 Claude "
        "দিয়ে উত্তর চান।"
    )


async def category_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/news, /defense, /ai, /space — কমান্ড দিলে প্রথমে প্রোভাইডার বেছে নিতে বলে।"""
    command = update.message.text.strip().lstrip("/").split("@")[0]
    if command not in CATEGORY_COMMANDS:
        await update.message.reply_text("❌ অজানা কমান্ড।")
        return

    await update.message.reply_text(
        f"'{command}' ক্যাটাগরির খবরের জন্য কোন AI দিয়ে সামারি চান?",
        reply_markup=_provider_keyboard("summarize", command),
    )


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/post <category> — Facebook ক্যাপশনের জন্যও প্রোভাইডার বেছে নিতে বলে।"""
    if not context.args:
        await update.message.reply_text("ব্যবহার: /post <news|defense|ai|space>")
        return

    category = context.args[0].lower()
    if category not in CATEGORY_COMMANDS:
        await update.message.reply_text(f"❌ ক্যাটাগরি হতে হবে এর একটি: {', '.join(CATEGORY_COMMANDS)}")
        return

    await update.message.reply_text(
        f"'{category}' এর Facebook ক্যাপশন কোন AI দিয়ে বানাতে চান?",
        reply_markup=_provider_keyboard("caption", category),
    )


async def handle_provider_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ইউজার 🟢 Gemini / 🟣 Claude বাটনে চাপ দিলে এটা চলে।"""
    query = update.callback_query
    await query.answer()  # Telegram-কে জানানো যে বাটন-ক্লিক গ্রহণ হয়েছে

    try:
        action, category, provider = query.data.split(":")
    except ValueError:
        await query.edit_message_text("⚠️ অবৈধ বাটন ডেটা।")
        return

    label = ai_provider.PROVIDER_LABELS.get(provider, provider)
    await query.edit_message_text(f"⏳ {label} দিয়ে '{category}' প্রসেস হচ্ছে...")

    try:
        items = news_fetcher.fetch_category(category, limit=1)
        if not items:
            await query.edit_message_text("এই মুহূর্তে নতুন কোনো খবর নেই।")
            return

        item = items[0]
        bangla_summary = ai_provider.summarize_to_bangla(
            provider, item["title"], item["summary"], category
        )

        if action == "summarize":
            text = telegram_bot.format_news_message(
                category, item["title"], bangla_summary, item["link"], item["source"]
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id, text=text, parse_mode=ParseMode.MARKDOWN_V2
            )

        elif action == "caption":
            fb_caption = ai_provider.generate_facebook_caption(
                provider, item["title"], bangla_summary, item["link"], category
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{label} দিয়ে তৈরি Facebook ক্যাপশন:\n\n{fb_caption}",
            )

        news_fetcher.mark_as_seen([item])
        await query.delete_message()

    except Exception as e:
        await context.bot.send_message(chat_id=query.message.chat_id, text=f"⚠️ একটি সমস্যা হয়েছে: {e}")
