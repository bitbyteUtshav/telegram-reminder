"""
main.py
-------
GitHub Actions থেকে শিডিউল অনুযায়ী চলে।
সব ক্যাটাগরি থেকে নতুন খবর ফেচ করে, Gemini দিয়ে বাংলায় সামারি বানিয়ে
Telegram-এ পোস্ট করে, এবং Facebook ক্যাপশন একটি ফাইলে সংরক্ষণ করে।

চালানোর নিয়ম:
    python main.py                 # সব ক্যাটাগরি
    python main.py --category ai   # শুধু একটি ক্যাটাগরি
"""

import argparse
import sys
import time

import config
import news_fetcher
import ai_provider
import telegram_bot

FACEBOOK_OUTPUT_FILE = "facebook_posts.md"


def process_category(category: str, provider: str) -> int:
    """একটি ক্যাটাগরির নতুন খবর প্রসেস করে। কতগুলো পোস্ট হলো তা ফেরত দেয়।"""
    print(f"\n🔍 '{category}' ক্যাটাগরির খবর খোঁজা হচ্ছে... (AI: {provider})")
    items = news_fetcher.fetch_category(category)

    if not items:
        print(f"   কোনো নতুন খবর পাওয়া যায়নি।")
        return 0

    posted_items = []
    facebook_posts = []

    for item in items:
        try:
            print(f"   ➜ প্রসেস হচ্ছে: {item['title'][:60]}...")

            bangla_summary = ai_provider.summarize_to_bangla(
                provider, item["title"], item["summary"], category
            )

            telegram_text = telegram_bot.format_news_message(
                category, item["title"], bangla_summary, item["link"], item["source"]
            )
            telegram_bot.send_message(telegram_text)
            print(f"   ✅ Telegram-এ পোস্ট হয়েছে")

            fb_caption = ai_provider.generate_facebook_caption(
                provider, item["title"], bangla_summary, item["link"], category
            )
            facebook_posts.append(f"## [{category}] {item['title']}\n\n{fb_caption}\n\n---\n")

            posted_items.append(item)
            time.sleep(2)  # Telegram / Gemini rate limit এর জন্য একটু বিরতি

        except Exception as e:
            print(f"   ❌ এই আইটেমে সমস্যা হয়েছে, স্কিপ করা হলো: {e}")
            continue

    if posted_items:
        news_fetcher.mark_as_seen(posted_items)

    if facebook_posts:
        with open(FACEBOOK_OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.writelines(facebook_posts)

    return len(posted_items)


def main():
    parser = argparse.ArgumentParser(description="AI News Bot — স্বয়ংক্রিয় নিউজ পোস্টার")
    parser.add_argument(
        "--category",
        choices=list(config.RSS_FEEDS.keys()) + ["all"],
        default="all",
        help="কোন ক্যাটাগরি প্রসেস করতে হবে (ডিফল্ট: all)",
    )
    parser.add_argument(
        "--provider",
        choices=["gemini", "claude"],
        default=config.DEFAULT_AI_PROVIDER,
        help="কোন AI দিয়ে সামারি/ক্যাপশন বানাতে হবে (ডিফল্ট: config.py এর DEFAULT_AI_PROVIDER)",
    )
    args = parser.parse_args()

    categories = list(config.RSS_FEEDS.keys()) if args.category == "all" else [args.category]

    total_posted = 0
    for category in categories:
        total_posted += process_category(category, args.provider)

    print(f"\n🎉 সম্পন্ন! মোট {total_posted}টি নতুন খবর পোস্ট করা হয়েছে।")
    return 0


if __name__ == "__main__":
    sys.exit(main())
