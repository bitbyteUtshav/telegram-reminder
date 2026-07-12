# 🤖 AI News Assistant

RSS ফিড থেকে খবর সংগ্রহ করে, Gemini AI দিয়ে বাংলায় সামারি বানিয়ে
Telegram চ্যানেলে অটো-পোস্ট করে এবং Facebook-এর জন্য ক্যাপশন তৈরি করে।

## ✨ ফিচার

- 📰 `/news` — সাধারণ খবর
- 🛡️ `/defense` — প্রতিরক্ষা সংক্রান্ত খবর
- 🤖 `/ai` — এআই সংক্রান্ত খবর
- 🚀 `/space` — মহাকাশ সংক্রান্ত খবর
- 📱 বাংলা ভাষায় Facebook ক্যাপশন জেনারেশন
- ⏰ GitHub Actions দিয়ে সম্পূর্ণ ফ্রি, সার্ভার ছাড়া অটো-শিডিউলিং
- 🔁 ডুপ্লিকেট খবর এড়ানোর ব্যবস্থা (`seen_items.json`)
- 🟢🟣 **দুটো AI প্রোভাইডার:** Gemini ও Claude — polling mode-এ ইউজার প্রতিবার
  Telegram বাটনে বেছে নিতে পারবেন কোনটা দিয়ে উত্তর চান; শিডিউলড মোডে
  GitHub Actions "Run workflow" থেকে বেছে নেওয়া যায় (ডিফল্ট: Gemini)

## 📂 প্রজেক্ট স্ট্রাকচার

```
ai-news-bot/
├── main.py              # GitHub Actions থেকে চলে (শিডিউলড অটো-পোস্ট)
├── bot.py                # ঐচ্ছিক: ২৪/৭ সার্ভারে polling mode চালাতে
├── handlers.py           # polling mode এর কমান্ড হ্যান্ডলার
├── config.py             # সব সেটিংস ও environment variable
├── news_fetcher.py       # RSS থেকে খবর সংগ্রহ
├── gemini_ai.py          # Gemini API দিয়ে বাংলা সামারি/ক্যাপশন
├── anthropic_ai.py       # Claude API দিয়ে বাংলা সামারি/ক্যাপশন
├── ai_provider.py        # Gemini/Claude এর মধ্যে রাউটিং (common ইন্টারফেস)
├── telegram_bot.py       # Telegram মেসেজ পাঠানোর হেল্পার
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── .github/workflows/news.yml   # শিডিউলড অটো-পোস্ট workflow
```

## 🚀 সেটআপ (ধাপে ধাপে)

### ১. রিপোজিটরি তৈরি
এই কোড একটি নতুন GitHub রিপোতে পুশ করুন (public বা private, দুটোই চলবে)।

### ২. Repository Secrets যোগ করুন
GitHub রিপোতে যান: **Settings → Secrets and variables → Actions → New repository secret**

তিনটা secret যোগ করুন:

| Secret নাম | মান |
|---|---|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) থেকে পাওয়া টোকেন |
| `TELEGRAM_CHAT_ID` | যে চ্যানেল/গ্রুপে পোস্ট হবে তার আইডি (নিচে দেখুন) |
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) থেকে পাওয়া কী |
| `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/settings/keys) থেকে পাওয়া কী |

**Chat ID বের করার উপায়:** আপনার বটকে চ্যানেলে অ্যাডমিন বানান, তারপর চ্যানেলে একটা মেসেজ পাঠান এবং এই URL ভিজিট করুন:
`https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` — সেখানে `"chat":{"id": ...}` পাবেন। চ্যানেলের আইডি সাধারণত `-100` দিয়ে শুরু হয়।

### ৩. শিডিউল কনফিগার করুন (ঐচ্ছিক)
`.github/workflows/news.yml` ফাইলে cron টাইম পরিবর্তন করুন:
```yaml
- cron: "0 */3 * * *"   # প্রতি ৩ ঘণ্টায় একবার (UTC)
```

### ৪. ম্যানুয়ালি টেস্ট করুন
GitHub রিপোর **Actions** ট্যাবে গিয়ে "AI News Auto-Poster" workflow সিলেক্ট করে **Run workflow** চাপুন।

## 💻 লোকালি টেস্ট করা

```bash
git clone <your-repo-url>
cd ai-news-bot
pip install -r requirements.txt
cp .env.example .env    # তারপর .env এ আসল কী/টোকেন বসান
python main.py --category ai   # শুধু একটা ক্যাটাগরি টেস্ট করতে
```

## 🟢🟣 Gemini নাকি Claude — কীভাবে বেছে নেবেন

**Polling mode (`bot.py`):** `/news`, `/defense`, `/ai`, `/space`, বা `/post <category>`
কমান্ড দিলে বট প্রথমে দুটো ইনলাইন বাটন দেখাবে — 🟢 Gemini আর 🟣 Claude।
যেটাতে ক্লিক করবেন সেটা দিয়েই সামারি/ক্যাপশন তৈরি হবে। প্রতিবার আলাদা করে বেছে নেওয়া যায়।

**Scheduled mode (`main.py` / GitHub Actions):** এখানে লাইভ ইউজার নেই, তাই
GitHub Actions-এর **Actions → Run workflow** বাটনে ক্লিক করলে একটা ড্রপডাউন
আসবে যেখানে `gemini` বা `claude` বেছে নেওয়া যাবে। কিছু না বেছে নিলে ডিফল্ট
হিসেবে `gemini` ব্যবহৃত হবে (`config.py` তে `DEFAULT_AI_PROVIDER` দিয়ে এটা
পরিবর্তনও করা যায়)। কমান্ড লাইন থেকেও সরাসরি নির্দিষ্ট করা যায়:

```bash
python main.py --category ai --provider claude
```

## 🔄 ২৪/৭ সার্ভারে চালানো (ঐচ্ছিক, লাইভ কমান্ডের জন্য)

GitHub Actions শুধু শিডিউল অনুযায়ী চলে — কেউ Telegram-এ `/news` টাইপ করলে
সাথে সাথে রিপ্লাই দিতে পারে না। যদি লাইভ কমান্ড রিপ্লাই চান, তাহলে
`bot.py` কোনো VPS/সার্ভারে (Railway, Render, একটা ছোট cloud VM ইত্যাদি) চালাতে হবে:

```bash
python bot.py
```

## ⚠️ গুরুত্বপূর্ণ নোট

- RSS ফিড লিংকগুলো (`config.py` এর `RSS_FEEDS`) উদাহরণস্বরূপ দেওয়া হয়েছে — আপনার
  পছন্দমতো যেকোনো RSS সোর্স দিয়ে পরিবর্তন করতে পারবেন।
- Gemini ও Telegram এর নিজস্ব rate limit আছে — খুব ছোট ইন্টারভ্যালে (যেমন প্রতি
  মিনিটে) শিডিউল না রাখাই ভালো।
- `MAX_ITEMS_PER_CATEGORY` (ডিফল্ট ৩) দিয়ে প্রতি রানে কতগুলো খবর প্রসেস হবে
  নিয়ন্ত্রণ করা যায় — `.env` বা GitHub Actions ভ্যারিয়েবলে পরিবর্তন করুন।

## 📄 লাইসেন্স

MIT — স্বাধীনভাবে ব্যবহার, পরিবর্তন ও বিতরণ করতে পারবেন।
