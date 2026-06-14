"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import re

from tools import search_listings, suggest_outfit, create_fit_card


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    # Step 1 — initialize session
    session = _new_session(query, wardrobe)

    # Step 2 — parse query with regex
    # Extract max_price: "under $30", "under 30", "less than $45", "max $20"
    price_match = re.search(
        r'(?:under|less than|below|max(?:imum)?)\s*\$?\s*(\d+(?:\.\d+)?)',
        query,
        re.IGNORECASE,
    )
    max_price = float(price_match.group(1)) if price_match else None

    # Extract size: "size M", "size US 8", "size XL", or bare codes like "W30"
    size_match = re.search(
        r'\bsize\s+([A-Za-z0-9/]+(?:\s*[A-Za-z0-9/]+)?)',
        query,
        re.IGNORECASE,
    )
    size = size_match.group(1).strip() if size_match else None

    # Description: strip price and size phrases, use the rest as keywords
    description = query
    if price_match:
        description = description[:price_match.start()] + description[price_match.end():]
    if size_match:
        description = description[:size_match.start()] + description[size_match.end():]
    description = re.sub(r'\s+', ' ', description).strip(" ,.")

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # Step 3 — search listings; exit early if nothing matches
    results = search_listings(description, size, max_price)
    session["search_results"] = results

    if not results:
        session["error"] = (
            "No items matched your search. Try broadening your description, "
            "adjusting the size, or raising the price limit."
        )
        return session

    # Step 4 — select top result
    session["selected_item"] = results[0]

    # Step 5 — generate outfit suggestion
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )

    # Step 6 — generate fit card caption
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )

    # Step 7 — return completed session
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
