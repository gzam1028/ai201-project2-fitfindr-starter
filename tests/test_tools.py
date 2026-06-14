from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_empty_wardrobe

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_suggest_outfit_empty_wardrobe():
    # Create a simple fake item so we don't have to run search_listings first
    mock_item = {
        "title": "Fake Vintage Tee",
        "category": "tops",
        "size": "L",
        "price": 15.0,
        "platform": "depop",
        "style_tags": ["vintage", "graphic"],
        "colors": ["black"]
    }
    
    empty_wardrobe = get_empty_wardrobe()
    
    # Run the tool
    result = suggest_outfit(mock_item, empty_wardrobe)
    
    # It should not crash, and it should return a useful string of text
    assert isinstance(result, str)
    assert len(result) > 10 

def test_create_fit_card_empty_outfit():
    mock_item = {
        "title": "Fake Vintage Tee",
        "price": 15.0,
        "platform": "depop",
        "style_tags": ["vintage"]
    }
    
    # We pass an empty string ("") as the outfit suggestion
    result = create_fit_card("", mock_item)
    
    # It should catch the empty string and return our exact error message
    assert "Error:" in result
    assert "incomplete outfit details" in result