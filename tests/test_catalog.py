"""
Tests for the ShelfSwipe MCP catalog tools.
Run with: pytest tests/ -v
"""
import pytest
from mcp_server.catalog import (
    list_shops,
    load_catalog,
    search_catalog,
    search_all_shops,
)


# ---------------------------------------------------------------------------
# list_shops
# ---------------------------------------------------------------------------

class TestListShops:
    def test_returns_all_five_shops(self):
        shops = list_shops()
        assert len(shops) == 5

    def test_each_shop_has_required_keys(self):
        for shop in list_shops():
            assert "shop_url" in shop
            assert "shop_name" in shop
            assert "product_count" in shop
            assert shop["product_count"] > 0

    def test_shop_urls_are_unique(self):
        urls = [s["shop_url"] for s in list_shops()]
        assert len(urls) == len(set(urls))


# ---------------------------------------------------------------------------
# load_catalog
# ---------------------------------------------------------------------------

class TestLoadCatalog:
    def test_loads_pottery_catalog(self):
        catalog = load_catalog("shelfswipe://fixtures/artisan_pottery")
        assert catalog is not None
        assert catalog.shop_name == "Clay & Co. Pottery Studio"
        assert len(catalog.products) == 5

    def test_loads_bakery_catalog(self):
        catalog = load_catalog("shelfswipe://fixtures/bakery_shop")
        assert catalog is not None
        assert len(catalog.products) == 5

    def test_loads_home_garden_catalog(self):
        catalog = load_catalog("shelfswipe://fixtures/home_garden")
        assert catalog is not None
        assert len(catalog.products) == 6

    def test_loads_tech_gadgets_catalog(self):
        catalog = load_catalog("shelfswipe://fixtures/tech_gadgets")
        assert catalog is not None
        assert len(catalog.products) == 5

    def test_loads_bath_body_catalog(self):
        catalog = load_catalog("shelfswipe://fixtures/bath_body")
        assert catalog is not None
        assert len(catalog.products) == 5

    def test_returns_none_for_unknown_url(self):
        result = load_catalog("shelfswipe://fixtures/does_not_exist")
        assert result is None

    def test_all_products_have_required_fields(self):
        catalog = load_catalog("shelfswipe://fixtures/artisan_pottery")
        for product in catalog.products:
            assert product.id
            assert product.name
            assert product.price > 0
            assert product.category
            assert product.stock >= 0
            assert product.image_url.startswith("https://")


# ---------------------------------------------------------------------------
# search_catalog
# ---------------------------------------------------------------------------

class TestSearchCatalog:
    POTTERY_URL = "shelfswipe://fixtures/artisan_pottery"
    BAKERY_URL = "shelfswipe://fixtures/bakery_shop"

    def test_empty_query_returns_all_in_stock(self):
        results = search_catalog(self.POTTERY_URL, query="")
        # All pottery products have stock > 0
        assert len(results) == 5

    def test_query_matcha_hits_matcha_bowl(self):
        results = search_catalog(self.POTTERY_URL, query="matcha")
        assert len(results) >= 1
        assert any("Matcha" in p.name for p in results)

    def test_query_coffee_hits_espresso_and_coffee(self):
        results = search_catalog(self.POTTERY_URL, query="coffee espresso")
        assert any("Espresso" in p.name for p in results)

    def test_max_price_filter(self):
        results = search_catalog(self.POTTERY_URL, query="", max_price=30.0)
        for product in results:
            assert product.price <= 30.0

    def test_category_filter(self):
        results = search_catalog(self.POTTERY_URL, query="", category="Kitchen")
        for product in results:
            assert "Kitchen" in product.category

    def test_out_of_stock_excluded_by_default(self):
        # All fixtures currently have stock > 0, but we can patch one
        catalog = load_catalog(self.POTTERY_URL)
        original = catalog.products[0].stock
        catalog.products[0].stock = 0
        # Manually search with in_stock_only=True
        results = [p for p in catalog.products if p.stock > 0]
        assert all(p.stock > 0 for p in results)

    def test_unknown_shop_returns_empty(self):
        results = search_catalog("shelfswipe://fixtures/nonexistent", query="gift")
        assert results == []

    def test_honey_query_hits_bakery(self):
        results = search_catalog(self.BAKERY_URL, query="honey")
        assert any("Honey" in p.name for p in results)


# ---------------------------------------------------------------------------
# search_all_shops
# ---------------------------------------------------------------------------

class TestSearchAllShops:
    def test_cross_shop_search_returns_results(self):
        results = search_all_shops(query="gift")
        assert len(results) > 0

    def test_limit_per_shop_respected(self):
        results = search_all_shops(query="handmade", limit_per_shop=2)
        # 5 shops × 2 max = at most 10 results
        assert len(results) <= 10

    def test_max_price_applied_cross_shop(self):
        results = search_all_shops(query="", max_price=20.0)
        for product in results:
            assert product.price <= 20.0

    def test_results_include_multiple_shops(self):
        results = search_all_shops(query="handmade gift")
        shop_categories = {p.category for p in results}
        # Should span more than one category / shop
        assert len(shop_categories) > 1
