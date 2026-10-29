# shelfswipe-mcp

> **MCP server** that gives LLM agents access to dummy merchant shop catalogs for ShelfSwipe product onboarding : Try [ShelfSwipe MCP](https://shelfswipe-mcp.vercel.app/)

---

## What this is

ShelfSwipe's `/onboard` endpoint normally pretends to load a merchant's store — it just returns a hardcoded demo catalog. This MCP server replaces that fiction with real tool calls:

1. An LLM agent **calls `list_shops`** to discover available dummy merchants.
2. It **calls `search_all_shops`** with a buyer's query to find relevant products.
3. It **posts the results** to PayTrace's `/api/v1/shelfswipe/onboard` to seed the swipe deck.

```
LLM Agent
  │
  ├─ list_shops()            → which dummy shops exist?
  ├─ search_all_shops(query) → find products matching buyer intent
  └─ get_product(id)         → normalised product ready for PayTrace
        │
        ▼
  PayTrace /shelfswipe/onboard   →   DB seed   →   swipe deck
```

---

## Dummy Shops (Fixtures)

| Shop | URL | Products |
|---|---|---|
| Clay & Co. Pottery Studio | `shelfswipe://fixtures/artisan_pottery` | 5 |
| Morning Crust Artisan Bakery | `shelfswipe://fixtures/bakery_shop` | 5 |
| Green Haven Home & Garden | `shelfswipe://fixtures/home_garden` | 6 |
| TinkerLab Indie Gadgets | `shelfswipe://fixtures/tech_gadgets` | 5 |
| Bloom Bath & Body Co. | `shelfswipe://fixtures/bath_body` | 5 |

---

## MCP Tools

| Tool | Description |
|---|---|
| `list_shops` | Discover all registered dummy shops |
| `fetch_catalog` | Full product list for one shop |
| `search_shop` | Keyword + price + category filter within one shop |
| `search_all_shops` | Cross-shop search — best for building mixed decks |
| `get_product` | Single product by ID, normalized for PayTrace `/onboard` |

---

## Setup

```bash
# From this directory
pip install -e ".[dev]"
```

---

## Running the MCP server

### stdio (default — works with Claude Desktop, any MCP client)

```bash
python -m mcp_server.main
```

### Claude Desktop config (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "shelfswipe": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "/absolute/path/to/shelfswipe-mcp"
    }
  }
}
```

### Antigravity / Cursor MCP config

```json
{
  "mcpServers": {
    "shelfswipe-mcp": {
      "command": "python",
      "args": ["-m", "mcp_server.main"],
      "cwd": "C:\\Users\\HP5CD\\OneDrive\\Desktop\\shelfswipe-mcp"
    }
  }
}
```

---

## Running Tests

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_catalog.py::TestListShops::test_returns_all_five_shops         PASSED
tests/test_catalog.py::TestListShops::test_each_shop_has_required_keys    PASSED
tests/test_catalog.py::TestLoadCatalog::test_loads_pottery_catalog        PASSED
... (all green)
```

---

## Project Structure

```
shelfswipe-mcp/
├── fixtures/
│   ├── artisan_pottery.json   # Clay & Co. Pottery Studio
│   ├── bakery_shop.json       # Morning Crust Artisan Bakery
│   ├── home_garden.json       # Green Haven Home & Garden
│   ├── tech_gadgets.json      # TinkerLab Indie Gadgets
│   └── bath_body.json         # Bloom Bath & Body Co.
├── mcp_server/
│   ├── __init__.py
│   ├── main.py                # MCP server + tool handlers
│   ├── catalog.py             # Fixture registry, load/search logic
│   └── schemas.py             # Pydantic models (ProductSchema, NormalizedProduct)
├── tests/
│   └── test_catalog.py        # pytest suite
├── pyproject.toml
└── README.md
```

---

## Adding a New Dummy Shop

1. Create `fixtures/my_new_shop.json` following the same schema as existing fixtures.
2. Add an entry to `URL_TO_FIXTURE` in `mcp_server/catalog.py`:
   ```python
   "shelfswipe://fixtures/my_new_shop": "my_new_shop",
   ```
3. Run `pytest` — `TestListShops::test_returns_all_five_shops` will need updating to reflect the new count.

---

## Connecting to PayTrace

To wire this MCP server to the live `/onboard` endpoint, have your LLM agent:

```python
import httpx, asyncio

# 1. Get products from MCP (via tool calls)
products = search_all_shops(query="birthday gift under 50")

# 2. POST to PayTrace onboard
async with httpx.AsyncClient() as client:
    resp = await client.post(
        "http://localhost:8000/api/v1/shelfswipe/onboard",
        json={"shop_url": "shelfswipe://fixtures/artisan_pottery",
              "shop_name": "Clay & Co. Pottery Studio"},
        headers={"Authorization": "Bearer <token>"},
    )
```
