"""
news_fetcher.py
----------------
বিভিন্ন RSS ফিড থেকে খবর সংগ্রহ করে।
"""

import feedparser
import hashlib
import json
import os
from datetime import datetime, timezone

import config

SEEN_FILE = "seen_items.json"  # আগে পোস্ট করা আইটেমের হ্যাশ রাখা হয় (ডুপ্লিকেট এড়াতে)


def _load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, OSError):
            return set()
    return set()


def _save_seen(seen: set) -> None:
    # সর্বোচ্চ ৫০০টা হ্যাশ রাখি, ফাইল যেন অসীম বড় না হয়
    trimmed = list(seen)[-500:]
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f)


def _hash_entry(entry) -> str:
    key = entry.get("link") or entry.get("title", "")
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def fetch_category(category: str, limit: int = None) -> list[dict]:
    """
    নির্দিষ্ট ক্যাটাগরির (news/defense/ai/space) সব RSS ফিড থেকে নতুন
    (আগে না দেখা) আইটেমগুলো ফেরত দেয়।
    """
    if category not in config.RSS_FEEDS:
        raise ValueError(f"অজানা ক্যাটাগরি: {category}. অপশন: {list(config.RSS_FEEDS.keys())}")

    limit = limit or config.MAX_ITEMS_PER_CATEGORY
    seen = _load_seen()
    results = []

    for feed_url in config.RSS_FEEDS[category]:
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"⚠️ ফিড লোড করতে ব্যর্থ: {feed_url} — {e}")
            continue

        for entry in parsed.entries:
            item_hash = _hash_entry(entry)
            if item_hash in seen:
                continue

            results.append({
                "title": entry.get("title", "শিরোনাম পাওয়া যায়নি"),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", datetime.now(timezone.utc).isoformat()),
                "source": parsed.feed.get("title", feed_url),
                "hash": item_hash,
            })

            if len(results) >= limit:
                break
        if len(results) >= limit:
            break

    return results


def mark_as_seen(items: list[dict]) -> None:
    """পোস্ট করা আইটেমগুলো 'দেখা হয়ে গেছে' হিসেবে সংরক্ষণ করে।"""
    seen = _load_seen()
    for item in items:
        seen.add(item["hash"])
    _save_seen(seen)


def fetch_all_categories() -> dict[str, list[dict]]:
    """সব ক্যাটাগরির খবর একসাথে ফেরত দেয়।"""
    return {cat: fetch_category(cat) for cat in config.RSS_FEEDS}
