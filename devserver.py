"""
ShelfSwipe MCP — Dev server with a visual browser UI.

Serves two things:
  1. GET /          → Visual HTML catalog browser (see all 5 shops + products)
  2. GET /api/shops → JSON list of all shops
  3. GET /api/catalog?shop_url=... → JSON full catalog
  4. GET /api/search?query=...&max_price=...&category=... → JSON search (all shops)
  5. POST /api/mcp  → Simulate an MCP tool call {tool, arguments}

Run: python devserver.py
Open: http://localhost:8765
"""
from __future__ import annotations
import json
import sys
import os

# Make sure mcp_server package is importable
sys.path.insert(0, os.path.dirname(__file__))

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from mcp_server.catalog import list_shops, load_catalog, search_catalog, search_all_shops

PORT = 8765

# ---------------------------------------------------------------------------
# HTML UI
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ShelfSwipe MCP — Dummy Shop Catalog</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0f0f13;
    --surface: #1a1a24;
    --card: #22222f;
    --border: #2e2e3e;
    --accent: #7c6aff;
    --accent2: #ff6a9b;
    --text: #e8e8f0;
    --muted: #7a7a9a;
    --green: #4ade80;
    --orange: #fb923c;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

  /* Header */
  header {
    background: linear-gradient(135deg, #1a1a30 0%, #12121e 100%);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    position: sticky; top: 0; z-index: 100;
    backdrop-filter: blur(10px);
  }
  .header-inner { max-width: 1400px; margin: 0 auto; display: flex; align-items: center; gap: 1rem; height: 64px; }
  .logo { font-size: 1.25rem; font-weight: 700; background: linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
  .badge { background: var(--accent); color: #fff; font-size: 0.65rem; font-weight: 600; padding: 2px 8px; border-radius: 20px; letter-spacing: 0.05em; }

  /* Search bar */
  .search-bar {
    max-width: 1400px; margin: 2rem auto 1.5rem; padding: 0 2rem;
    display: flex; gap: 0.75rem; flex-wrap: wrap;
  }
  input, select {
    background: var(--surface); border: 1px solid var(--border); color: var(--text);
    border-radius: 10px; padding: 0.6rem 1rem; font-size: 0.9rem; font-family: inherit;
    outline: none; transition: border-color 0.2s;
  }
  input:focus, select:focus { border-color: var(--accent); }
  input[type="text"] { flex: 1; min-width: 200px; }
  input[type="number"] { width: 130px; }
  button {
    background: linear-gradient(135deg, var(--accent), #5b4fcf);
    color: #fff; border: none; border-radius: 10px;
    padding: 0.6rem 1.4rem; font-weight: 600; font-size: 0.9rem;
    cursor: pointer; transition: opacity 0.2s, transform 0.1s;
  }
  button:hover { opacity: 0.9; transform: translateY(-1px); }
  button:active { transform: translateY(0); }
  .btn-reset { background: var(--surface); border: 1px solid var(--border); color: var(--muted); }

  /* Tabs */
  .tabs { max-width: 1400px; margin: 0 auto 1.5rem; padding: 0 2rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }
  .tab {
    background: var(--surface); border: 1px solid var(--border); color: var(--muted);
    border-radius: 8px; padding: 0.45rem 1rem; font-size: 0.85rem; font-weight: 500;
    cursor: pointer; transition: all 0.2s;
  }
  .tab:hover { border-color: var(--accent); color: var(--text); }
  .tab.active { background: var(--accent); border-color: var(--accent); color: #fff; }

  /* Grid */
  .grid { max-width: 1400px; margin: 0 auto; padding: 0 2rem 3rem; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.25rem; }

  /* Card */
  .card {
    background: var(--card); border: 1px solid var(--border); border-radius: 16px;
    overflow: hidden; transition: transform 0.2s, box-shadow 0.2s;
    display: flex; flex-direction: column;
  }
  .card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(124,106,255,0.15); }
  .card img { width: 100%; height: 200px; object-fit: cover; display: block; }
  .card-body { padding: 1rem; flex: 1; display: flex; flex-direction: column; gap: 0.5rem; }
  .card-shop { font-size: 0.7rem; color: var(--accent); font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
  .card-name { font-size: 1rem; font-weight: 600; color: var(--text); line-height: 1.35; }
  .card-desc { font-size: 0.82rem; color: var(--muted); line-height: 1.5; flex: 1; }
  .card-footer { display: flex; align-items: center; justify-content: space-between; margin-top: auto; padding-top: 0.75rem; border-top: 1px solid var(--border); }
  .price { font-size: 1.1rem; font-weight: 700; color: var(--green); }
  .category { font-size: 0.72rem; background: rgba(124,106,255,0.15); color: var(--accent); border-radius: 6px; padding: 3px 8px; }
  .stock { font-size: 0.75rem; color: var(--orange); }
  .why { font-size: 0.78rem; color: #a0a0c0; font-style: italic; margin-top: 0.25rem; padding: 0.4rem 0.6rem; background: rgba(255,255,255,0.04); border-radius: 6px; border-left: 2px solid var(--accent); }

  /* Tags */
  .tags { display: flex; flex-wrap: wrap; gap: 4px; }
  .tag { font-size: 0.68rem; background: var(--surface); border: 1px solid var(--border); color: var(--muted); border-radius: 4px; padding: 1px 6px; }

  /* MCP panel */
  .mcp-panel { max-width: 1400px; margin: 0 auto 1.5rem; padding: 0 2rem; }
  .mcp-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem; }
  .mcp-box h3 { font-size: 0.9rem; color: var(--accent); margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }
  .mcp-tools { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.75rem; }
  .mcp-tool { font-size: 0.78rem; background: var(--card); border: 1px solid var(--border); color: var(--text); border-radius: 6px; padding: 4px 10px; cursor: pointer; transition: all 0.15s; font-family: 'Courier New', monospace; }
  .mcp-tool:hover { border-color: var(--accent); color: var(--accent); }
  .mcp-output { background: #0a0a12; border: 1px solid var(--border); border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.78rem; font-family: 'Courier New', monospace; color: #a0f0c0; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }

  /* Stats bar */
  .stats { max-width: 1400px; margin: 0 auto 1rem; padding: 0 2rem; display: flex; gap: 1rem; align-items: center; }
  .stat-count { font-size: 0.85rem; color: var(--muted); }
  .stat-count span { color: var(--text); font-weight: 600; }

  /* Empty state */
  .empty { text-align: center; padding: 4rem 2rem; color: var(--muted); grid-column: 1/-1; }
  .empty h3 { font-size: 1.25rem; margin-bottom: 0.5rem; color: var(--text); }

  /* Spinner */
  .spinner { display: inline-block; width: 16px; height: 16px; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.6s linear infinite; vertical-align: middle; margin-right: 6px; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Tooltip */
  .id-badge { font-size: 0.65rem; color: var(--muted); font-family: monospace; margin-top: 2px; }
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="logo">🛍 ShelfSwipe MCP</div>
    <div class="badge">DEV SERVER</div>
    <div style="margin-left:auto; font-size:0.8rem; color:var(--muted);">5 dummy shops · 26 products · localhost:8765</div>
  </div>
</header>

<!-- Search bar -->
<div class="search-bar">
  <input type="text" id="query" placeholder="🔍  Search products (e.g. gift, coffee, handmade...)" oninput="debounceSearch()"/>
  <input type="number" id="maxPrice" placeholder="Max price $" min="0" step="5" oninput="debounceSearch()"/>
  <input type="text" id="category" placeholder="Category filter..." oninput="debounceSearch()"/>
  <button onclick="doSearch()">Search</button>
  <button class="btn-reset" onclick="resetSearch()">Reset</button>
</div>

<!-- Shop tabs -->
<div class="tabs" id="tabs">
  <div class="tab active" data-url="all" onclick="switchTab(this)">All Shops</div>
</div>

<!-- MCP Tool Tester -->
<div class="mcp-panel">
  <div class="mcp-box">
    <h3>⚡ MCP Tool Tester <span style="font-size:0.75rem;color:var(--muted);font-weight:400;">— call tools like an AI agent would</span></h3>
    <div class="mcp-tools">
      <div class="mcp-tool" onclick="callTool('list_shops', {})">list_shops()</div>
      <div class="mcp-tool" onclick="callTool('fetch_catalog', {shop_url: currentShopUrl()})">fetch_catalog(shop_url)</div>
      <div class="mcp-tool" onclick="callTool('search_shop', {shop_url: currentShopUrl(), query: document.getElementById('query').value || 'gift'})">search_shop(shop_url, query)</div>
      <div class="mcp-tool" onclick="callTool('search_all_shops', {query: document.getElementById('query').value || 'handmade gift'})">search_all_shops(query)</div>
    </div>
    <div class="mcp-output" id="mcpOutput">// Click a tool above to see its JSON response...\n// This is exactly what an LLM agent receives when it calls these tools.</div>
  </div>
</div>

<!-- Stats -->
<div class="stats">
  <div class="stat-count">Showing <span id="productCount">0</span> products</div>
</div>

<!-- Product grid -->
<div class="grid" id="grid">
  <div class="empty"><div class="spinner"></div> Loading...</div>
</div>

<script>
let allShops = [];
let debounceTimer = null;
let activeUrl = 'all';

async function init() {
  // Load shops for tabs
  const res = await fetch('/api/shops');
  allShops = await res.json();
  const tabs = document.getElementById('tabs');
  allShops.forEach(shop => {
    const t = document.createElement('div');
    t.className = 'tab';
    t.dataset.url = shop.shop_url;
    t.textContent = shop.shop_name + ' (' + shop.product_count + ')';
    t.onclick = () => switchTab(t);
    tabs.appendChild(t);
  });
  loadProducts();
}

function currentShopUrl() {
  return activeUrl === 'all' ? allShops[0]?.shop_url || '' : activeUrl;
}

function switchTab(el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  activeUrl = el.dataset.url;
  loadProducts();
}

function debounceSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(doSearch, 350);
}

function doSearch() { loadProducts(); }

function resetSearch() {
  document.getElementById('query').value = '';
  document.getElementById('maxPrice').value = '';
  document.getElementById('category').value = '';
  loadProducts();
}

async function loadProducts() {
  const query = document.getElementById('query').value.trim();
  const maxPrice = document.getElementById('maxPrice').value;
  const category = document.getElementById('category').value.trim();

  let url = '/api/search?query=' + encodeURIComponent(query || '');
  if (maxPrice) url += '&max_price=' + maxPrice;
  if (category) url += '&category=' + encodeURIComponent(category);
  if (activeUrl !== 'all') url += '&shop_url=' + encodeURIComponent(activeUrl);

  const grid = document.getElementById('grid');
  grid.innerHTML = '<div class="empty"><div class="spinner"></div> Loading...</div>';

  const res = await fetch(url);
  const data = await res.json();
  renderProducts(data.products);
}

function renderProducts(products) {
  const grid = document.getElementById('grid');
  document.getElementById('productCount').textContent = products.length;

  if (!products.length) {
    grid.innerHTML = '<div class="empty"><h3>No products found</h3><p>Try a different query or reset filters.</p></div>';
    return;
  }

  grid.innerHTML = products.map(p => `
    <div class="card">
      <img src="${p.image_url}" alt="${p.name}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=600&q=80'"/>
      <div class="card-body">
        <div class="card-shop">${p.source_shop || p.category}</div>
        <div class="card-name">${p.name}</div>
        <div class="id-badge">ID: ${p.id}</div>
        <div class="card-desc">${p.description}</div>
        ${p.why_matches ? `<div class="why">💡 ${p.why_matches}</div>` : ''}
        <div class="tags">${(p.tags||[]).map(t => `<span class="tag">${t}</span>`).join('')}</div>
        <div class="card-footer">
          <div>
            <div class="price">$${p.price.toFixed(2)}</div>
            <div class="stock">📦 ${p.stock} in stock</div>
          </div>
          <div class="category">${p.category}</div>
        </div>
      </div>
    </div>
  `).join('');
}

async function callTool(toolName, args) {
  const out = document.getElementById('mcpOutput');
  out.textContent = '// Calling ' + toolName + '...\n';
  try {
    const res = await fetch('/api/mcp', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({tool: toolName, arguments: args})
    });
    const data = await res.json();
    out.textContent = '// Tool: ' + toolName + '\\n// Arguments: ' + JSON.stringify(args) + '\\n\\n' + JSON.stringify(data, null, 2);
  } catch(e) {
    out.textContent = '// Error: ' + e.message;
  }
}

init();
</script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html):
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        if parsed.path == "/":
            self.send_html(HTML)

        elif parsed.path == "/api/shops":
            self.send_json(list_shops())

        elif parsed.path == "/api/catalog":
            shop_url = qs.get("shop_url", [None])[0]
            catalog = load_catalog(shop_url) if shop_url else None
            if catalog:
                self.send_json(catalog.model_dump())
            else:
                self.send_json({"error": "Shop not found"}, 404)

        elif parsed.path == "/api/search":
            query = qs.get("query", [""])[0]
            max_price = float(qs["max_price"][0]) if "max_price" in qs else None
            category = qs.get("category", [None])[0]
            shop_url = qs.get("shop_url", [None])[0]

            if shop_url:
                products = search_catalog(shop_url, query, max_price, category)
                # attach shop name
                catalog = load_catalog(shop_url)
                shop_name = catalog.shop_name if catalog else shop_url
                for p in products:
                    p.__dict__["source_shop"] = shop_name
            else:
                products = search_all_shops(query, max_price, category, limit_per_shop=20)

            self.send_json({
                "query": query,
                "total_matches": len(products),
                "products": [p.model_dump() for p in products],
            })

        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path == "/api/mcp":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            tool = body.get("tool", "")
            args = body.get("arguments", {})

            if tool == "list_shops":
                result = list_shops()
            elif tool == "fetch_catalog":
                c = load_catalog(args.get("shop_url", ""))
                result = c.model_dump() if c else {"error": "Not found"}
            elif tool == "search_shop":
                products = search_catalog(
                    args.get("shop_url", ""), args.get("query", ""),
                    args.get("max_price"), args.get("category"),
                )
                result = {"total_matches": len(products), "products": [p.model_dump() for p in products]}
            elif tool == "search_all_shops":
                products = search_all_shops(
                    args.get("query", ""), args.get("max_price"),
                    args.get("category"), limit_per_shop=args.get("limit_per_shop", 5),
                )
                result = {"total_matches": len(products), "products": [p.model_dump() for p in products]}
            else:
                result = {"error": f"Unknown tool: {tool}"}

            self.send_json(result)

        else:
            self.send_json({"error": "Not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    print(f"\n  [ShelfSwipe MCP Dev Server]")
    print(f"  ------------------------------")
    print(f"  Visual UI  -> http://localhost:{PORT}")
    print(f"  Shops API  -> http://localhost:{PORT}/api/shops")
    print(f"  Search     -> http://localhost:{PORT}/api/search?query=gift")
    print(f"  MCP tool   -> POST http://localhost:{PORT}/api/mcp")
    print(f"\n  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
