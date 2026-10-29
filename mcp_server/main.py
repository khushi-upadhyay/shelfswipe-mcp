"""
ShelfSwipe MCP Server — main entry point.

Exposes five MCP tools that an LLM agent (or PayTrace's /onboard endpoint)
can call to discover and ingest products from the dummy merchant fixtures:

  1. list_shops            — discover all registered dummy shops
  2. fetch_catalog         — load the full product list for one shop
  3. search_shop           — keyword + filter search within one shop
  4. search_all_shops      — cross-shop search (merged results)
  5. get_product           — fetch a single product by ID from a given shop

Run modes:
  • stdio  (default) — pipe-friendly; works with Claude Desktop / any MCP client
  • http              — FastAPI/SSE transport on localhost:8765
"""
from __future__ import annotations

import logging
from typing import Optional

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from mcp_server.catalog import (
    list_shops as _list_shops,
    load_catalog,
    search_catalog,
    search_all_shops as _search_all_shops,
)
from mcp_server.schemas import NormalizedProduct

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger("shelfswipe-mcp")

# ---------------------------------------------------------------------------
# Server bootstrap
# ---------------------------------------------------------------------------

server = Server("shelfswipe-mcp")


# ---------------------------------------------------------------------------
# Tool: list_shops
# ---------------------------------------------------------------------------

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_shops",
            description=(
                "Returns a summary of every registered dummy merchant shop available "
                "for ShelfSwipe onboarding. Each entry includes the shop_url (use this "
                "as the identifier for other tools), shop_name, description, and product_count."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="fetch_catalog",
            description=(
                "Fetches the full product catalog for a single dummy merchant shop identified "
                "by its shop_url. Returns shop metadata plus all products with id, name, price, "
                "category, description, image_url, stock, tags, and why_matches."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "shop_url": {
                        "type": "string",
                        "description": "The shop_url of the dummy merchant (e.g. 'shelfswipe://fixtures/artisan_pottery').",
                    }
                },
                "required": ["shop_url"],
            },
        ),
        types.Tool(
            name="search_shop",
            description=(
                "Keyword search within a single dummy shop. Ranks products by relevance to the "
                "query, with optional price ceiling and category filter. Returns ranked products."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "shop_url": {
                        "type": "string",
                        "description": "The shop_url to search within.",
                    },
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g. 'handmade gift under 30').",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Optional maximum price ceiling in USD.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter substring (e.g. 'Kitchen', 'Bath').",
                    },
                    "in_stock_only": {
                        "type": "boolean",
                        "description": "If true (default), exclude out-of-stock products.",
                        "default": True,
                    },
                },
                "required": ["shop_url", "query"],
            },
        ),
        types.Tool(
            name="search_all_shops",
            description=(
                "Cross-shop keyword search across ALL registered dummy shops. Returns up to "
                "`limit_per_shop` results per shop, merged and ranked by relevance. "
                "Great for building a diverse ShelfSwipe deck from multiple merchants."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query.",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Optional maximum price ceiling in USD.",
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter substring.",
                    },
                    "in_stock_only": {
                        "type": "boolean",
                        "description": "If true (default), exclude out-of-stock products.",
                        "default": True,
                    },
                    "limit_per_shop": {
                        "type": "integer",
                        "description": "Max products to return per shop (default: 5).",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_product",
            description=(
                "Fetches a single product by its ID from a specific dummy shop. "
                "Returns a NormalizedProduct ready to be forwarded to PayTrace's /shelfswipe/onboard."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "shop_url": {
                        "type": "string",
                        "description": "The shop_url containing the product.",
                    },
                    "product_id": {
                        "type": "string",
                        "description": "The product ID (e.g. 'pottery-001').",
                    },
                },
                "required": ["shop_url", "product_id"],
            },
        ),
    ]


# ---------------------------------------------------------------------------
# Tool call handler
# ---------------------------------------------------------------------------

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:

    import json

    if name == "list_shops":
        shops = _list_shops()
        return [types.TextContent(type="text", text=json.dumps(shops, indent=2))]

    elif name == "fetch_catalog":
        shop_url = arguments["shop_url"]
        catalog = load_catalog(shop_url)
        if catalog is None:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"No shop found for url: {shop_url}. "
                                          f"Call list_shops to see available shops."}),
            )]
        return [types.TextContent(type="text", text=catalog.model_dump_json(indent=2))]

    elif name == "search_shop":
        shop_url = arguments["shop_url"]
        query = arguments["query"]
        max_price: Optional[float] = arguments.get("max_price")
        category: Optional[str] = arguments.get("category")
        in_stock_only: bool = arguments.get("in_stock_only", True)

        results = search_catalog(
            shop_url=shop_url,
            query=query,
            max_price=max_price,
            category=category,
            in_stock_only=in_stock_only,
        )
        payload = {
            "shop_url": shop_url,
            "query": query,
            "total_matches": len(results),
            "products": [p.model_dump() for p in results],
        }
        return [types.TextContent(type="text", text=json.dumps(payload, indent=2))]

    elif name == "search_all_shops":
        query = arguments["query"]
        max_price: Optional[float] = arguments.get("max_price")
        category: Optional[str] = arguments.get("category")
        in_stock_only: bool = arguments.get("in_stock_only", True)
        limit_per_shop: int = arguments.get("limit_per_shop", 5)

        results = _search_all_shops(
            query=query,
            max_price=max_price,
            category=category,
            in_stock_only=in_stock_only,
            limit_per_shop=limit_per_shop,
        )
        payload = {
            "query": query,
            "total_matches": len(results),
            "products": [p.model_dump() for p in results],
        }
        return [types.TextContent(type="text", text=json.dumps(payload, indent=2))]

    elif name == "get_product":
        shop_url = arguments["shop_url"]
        product_id = arguments["product_id"]

        catalog = load_catalog(shop_url)
        if catalog is None:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Shop not found: {shop_url}"}),
            )]

        product = next((p for p in catalog.products if p.id == product_id), None)
        if product is None:
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": f"Product '{product_id}' not found in shop '{shop_url}'"}),
            )]

        normalized = NormalizedProduct(
            name=product.name,
            price=product.price,
            currency=product.currency,
            category=product.category,
            description=product.description,
            image_url=product.image_url,
            stock=product.stock,
            why_matches=product.why_matches or f"Sourced from {catalog.shop_name}",
            source_shop_url=shop_url,
            source_shop_name=catalog.shop_name,
        )
        return [types.TextContent(type="text", text=normalized.model_dump_json(indent=2))]

    else:
        return [types.TextContent(
            type="text",
            text=json.dumps({"error": f"Unknown tool: {name}"}),
        )]


# ---------------------------------------------------------------------------
# Entry point — stdio transport (default)
# ---------------------------------------------------------------------------

async def main():
    logger.info("Starting ShelfSwipe MCP server (stdio transport)...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
