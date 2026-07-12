"""
ai_provider.py
--------------
Gemini এবং Claude — দুটো AI প্রোভাইডারের জন্য একটাই common ইন্টারফেস।
handlers.py / main.py থেকে সরাসরি gemini_ai বা anthropic_ai কল না করে
এই ফাইলের মাধ্যমে কল করলে provider পরিবর্তন সহজ হয়।
"""

import gemini_ai
import anthropic_ai

PROVIDERS = {
    "gemini": gemini_ai,
    "claude": anthropic_ai,
}

PROVIDER_LABELS = {
    "gemini": "🟢 Gemini",
    "claude": "🟣 Claude",
}


def _resolve(provider: str):
    provider = (provider or "").lower()
    if provider not in PROVIDERS:
        raise ValueError(f"অজানা AI provider: '{provider}'. অপশন: {list(PROVIDERS.keys())}")
    return PROVIDERS[provider]


def summarize_to_bangla(provider: str, title: str, summary: str, category: str) -> str:
    module = _resolve(provider)
    return module.summarize_to_bangla(title, summary, category)


def generate_facebook_caption(provider: str, title: str, bangla_summary: str, link: str, category: str) -> str:
    module = _resolve(provider)
    return module.generate_facebook_caption(title, bangla_summary, link, category)
