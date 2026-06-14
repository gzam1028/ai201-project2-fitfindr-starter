"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    listings = load_listings()

    # Filter by max_price
    if max_price is not None:
        listings = [item for item in listings if item["price"] <= max_price]

    # Filter by size (case-insensitive substring match so "M" hits "S/M", "M/L", etc.)
    if size is not None:
        size_lower = size.lower()
        listings = [item for item in listings if size_lower in item["size"].lower()]

    # Score by keyword overlap across title, description, and style_tags
    keywords = description.lower().split()

    def _score(item: dict) -> int:
        searchable = (
            item["title"].lower()
            + " "
            + item["description"].lower()
            + " "
            + " ".join(item["style_tags"]).lower()
        )
        return sum(1 for kw in keywords if kw in searchable)

    scored = [(item, _score(item)) for item in listings]
    scored = [(item, score) for item, score in scored if score > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [item for item, _ in scored]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    client = _get_groq_client()

    item_summary = (
        f"'{new_item['title']}' — {new_item['category']}, "
        f"size {new_item['size']}, ${new_item['price']:.2f} on {new_item['platform']}. "
        f"Style tags: {', '.join(new_item['style_tags'])}. "
        f"Colors: {', '.join(new_item['colors'])}."
    )

    wardrobe_items = wardrobe.get("items", [])

    if not wardrobe_items:
        prompt = (
            f"A thrifted item just dropped: {item_summary}\n\n"
            "The user doesn't have a saved wardrobe yet. Give 1–2 specific outfit ideas "
            "that would work well with this piece — suggest the kinds of items (bottoms, "
            "shoes, outerwear, etc.) that complement it, referencing its style and colors. "
            "Keep it casual, concrete, and under 150 words."
        )
    else:
        wardrobe_lines = "\n".join(
            f"- {w['name']} ({w['category']}, colors: {', '.join(w['colors'])})"
            for w in wardrobe_items
        )
        prompt = (
            f"A thrifted item just dropped: {item_summary}\n\n"
            f"The user's current wardrobe:\n{wardrobe_lines}\n\n"
            "Suggest 1–2 complete outfits that pair the new item with specific pieces "
            "from the wardrobe above. Name each wardrobe item you use. Keep it casual, "
            "specific, and under 150 words."
        )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return (
            "Error: cannot generate fit card due to incomplete outfit details. "
            "Try widening your search!"
        )

    client = _get_groq_client()

    item_summary = (
        f"'{new_item['title']}' — ${new_item['price']:.2f} on {new_item['platform']}. "
        f"Style tags: {', '.join(new_item['style_tags'])}."
    )

    prompt = (
        f"Item details: {item_summary}\n\n"
        f"Outfit suggestion: {outfit}\n\n"
        "Write a 2–4 sentence Instagram/TikTok caption for this thrift find and outfit. "
        "Rules: sound like a real person posting their OOTD (not a product description), "
        "mention the item name, price, and platform once each naturally, capture the vibe "
        "in specific terms, and use emojis. Be authentic and fun — not corporate."
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()
