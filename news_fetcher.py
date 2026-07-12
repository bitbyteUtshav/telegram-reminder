"""
news_fetcher.py
----------------
বিভিন্ন RSS ফিড থেকে খবর সংগ্রহ করে।
"""

import feedparser
import hashlib
import json
import os
import requests
from datetime import datetime, timezone

import config

SEEN_FILE = "seen_items.json"  # আগে পোস্ট করা আইটেমের হ্যাশ রাখা হয় (ডুপ্লিকেট এড়াতে)
FEED_TIMEOUT_SECONDS = 15  # কোনো ফিড সার্ভার সাড়া না দিলে এতক্ষণ পর ছেড়ে দেওয়া হবে
HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AI-News-Bot/1.0)"}


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


def _fetch_feed(feed_url: str):
    """
    RSS ফিড HTTP দিয়ে (টাইমআউটসহ) আনে, তারপর feedparser দিয়ে পার্স করে।
    feedparser.parse(url) সরাসরি ব্যবহার করলে টাইমআউট সেট করার উপায় নেই —
    কোনো সার্ভার সাড়া না দিলে পুরো স্ক্রিপ্ট চিরকাল আটকে থাকতে পারে।
    তাই আগে requests দিয়ে (টাইমআউটসহ) ডাউনলোড করে, তারপর পার্স করা হয়।
    """
    try:
        response = requests.get(feed_url, headers=HTTP_HEADERS, timeout=FEED_TIMEOUT_SECONDS)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except requests.exceptions.RequestException as e:
        print(f"⚠️ ফিড লোড করতে ব্যর্থ (timeout/network): {feed_url} — {e}")
        return None
    except Exception as e:
        print(f"⚠️ ফিড পার্স করতে ব্যর্থ: {feed_url} — {e}")
        return None


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
        parsed = _fetch_feed(feed_url)
        if parsed is None:
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
