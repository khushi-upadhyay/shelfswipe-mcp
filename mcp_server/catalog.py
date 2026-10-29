"""
Fixture registry and resolution for ShelfSwipe MCP dummy shops.

Each dummy shop is a JSON file in the fixtures/ directory.
The shop_url acts as the stable identifier used by PayTrace's /onboard endpoint.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional

from mcp_server.schemas import ShopCatalog, ProductSchema

# All fixture files live next to this package
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

# Mapping of shop_url  →  fixture filename (without .json)
URL_TO_FIXTURE: dict[str, str] = {
    "shelfswipe://fixtures/artisan_pottery": "artisan_pottery",
    "shelfswipe://fixtures/bakery_shop":     "bakery_shop",
    "shelfswipe://fixtures/home_garden":     "home_garden",
    "shelfswipe://fixtures/tech_gadgets":    "tech_gadgets",
    "shelfswipe://fixtures/bath_body":       "bath_body",
}


def list_shops() -> list[dict]:
    """Return a lightweight summary of every registered dummy shop."""
    summaries = []
    for url, filename in URL_TO_FIXTURE.items():
        path = FIXTURES_DIR / f"{filename}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            summaries.append({
                "shop_url":   url,
                "shop_name":  data.get("shop_name", filename),
                "shop_id":    data.get("shop_id", filename),
                "description": data.get("description", ""),
                "product_count": len(data.get("products", [])),
            })
    return summaries


def load_catalog(shop_url: str) -> Optional[ShopCatalog]:
    """
    Load the full catalog for a given shop_url.
    Returns None if the URL is not registered or the fixture is missing.
    """
    filename = URL_TO_FIXTURE.get(shop_url)
    if not filename:
        return None
    path = FIXTURES_DIR / f"{filename}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return ShopCatalog(**data)


def search_catalog(
    shop_url: str,
    query: str,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
    in_stock_only: bool = True,
) -> list[ProductSchema]:
    """
    Keyword + filter search over a single shop's products.

    Ranking heuristic:
      - Each matching query term in name / category / description / tags → +10 pts
      - In-stock bonus → +5 pts
      - Cheaper items break ties (lower price = higher rank)
    """
    catalog = load_catalog(shop_url)
    if catalog is None:
        return []

    stop_words = {"the", "and", "for", "with", "a", "an", "of", "in", "to"}
    query_terms = {
        t for t in re.findall(r"[a-z0-9]+", query.lower())
        if len(t) > 2 and t not in stop_words
    }

    results: list[tuple[int, float, ProductSchema]] = []

    for product in catalog.products:
        if in_stock_only and product.stock <= 0:
            continue
        if max_price is not None and product.price > max_price:
            continue
        if category and category.lower() not in product.category.lower():
            continue

        # Score
        searchable = " ".join([
            product.name,
            product.category,
            product.description,
            " ".join(product.tags),
            product.why_matches or "",
        ]).lower()
        tokens = set(re.findall(r"[a-z0-9]+", searchable))

        score = 10 * len(query_terms & tokens)
        score += 5 if product.stock > 0 else 0

        # Include everything when no query terms provided
        if not query_terms or score > 0:
            results.append((score, product.price, product))

    # Sort: highest score first, then lowest price
    results.sort(key=lambda t: (-t[0], t[1]))
    return [r[2] for r in results]


def search_all_shops(
    query: str,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
    in_stock_only: bool = True,
    limit_per_shop: int = 5,
) -> list[ProductSchema]:
    """
    Search across ALL registered dummy shops and merge results.
    Returns up to `limit_per_shop` products per shop, interleaved by relevance.
    """
    all_results: list[ProductSchema] = []
    for shop_url in URL_TO_FIXTURE:
        shop_results = search_catalog(
            shop_url=shop_url,
            query=query,
            max_price=max_price,
            category=category,
            in_stock_only=in_stock_only,
        )
        all_results.extend(shop_results[:limit_per_shop])
    return all_results
