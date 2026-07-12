"""
bot.py
------
ঐচ্ছিক: যদি আপনি ২৪/৭ কোনো সার্ভার/PC/VPS-এ বট চালাতে চান (polling mode),
যাতে ইউজার লাইভ /news, /defense, /ai, /space, /post কমান্ড দিলে সাথে সাথে
রিপ্লাই পায় — তাহলে এই ফাইলটা চালান:

    python bot.py

GitHub Actions শিডিউলড মোডে এই ফাইলটার দরকার নেই, তখন main.py ব্যবহার হয়।
"""

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

import config
import handlers


def main() -> None:
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", handlers.start_command))
    app.add_handler(CommandHandler("news", handlers.category_command))
    app.add_handler(CommandHandler("defense", handlers.category_command))
    app.add_handler(CommandHandler("ai", handlers.category_command))
    app.add_handler(CommandHandler("space", handlers.category_command))
    app.add_handler(CommandHandler("post", handlers.post_command))
    # 🟢 Gemini / 🟣 Claude বাটনে ক্লিকের জন্য
    app.add_handler(CallbackQueryHandler(handlers.handle_provider_choice))

    print("🤖 বট চালু হয়েছে (polling mode)... বন্ধ করতে Ctrl+C চাপুন।")
    app.run_polling()


if __name__ == "__main__":
    main()
