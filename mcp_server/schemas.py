"""
Pydantic schemas for the ShelfSwipe MCP server.
These mirror the ShelfProduct shape expected by PayTrace's /shelfswipe/onboard endpoint.
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class ProductSchema(BaseModel):
    """A single product as stored in a fixture or returned by MCP tools."""
    id: str
    name: str
    price: float
    currency: str = "USD"
    category: str
    description: str
    image_url: str
    stock: int
    tags: list[str] = Field(default_factory=list)
    why_matches: Optional[str] = None


class ShopCatalog(BaseModel):
    """Full catalog response from a dummy merchant shop fixture."""
    shop_id: str
    shop_name: str
    shop_url: str
    contact_email: str
    description: str
    products: list[ProductSchema]


class SearchResult(BaseModel):
    """Filtered/ranked search results from a catalog."""
    shop_url: str
    shop_name: str
    query: str
    total_matches: int
    products: list[ProductSchema]


class NormalizedProduct(BaseModel):
    """
    PayTrace-compatible shape ready to POST to /shelfswipe/onboard.
    Maps fixture fields onto what the ShelfSwipe backend expects.
    """
    name: str
    price: float
    currency: str
    category: str
    description: str
    image_url: str
    stock: int
    why_matches: str
    source_shop_url: str
    source_shop_name: str
