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

from mcp_server.catalog import list_shops, load_catalog, search_catalog, search_all_shops, URL_TO_FIXTURE

PORT = 8765

# ---------------------------------------------------------------------------
# HTML UI
# ---------------------------------------------------------------------------

HTML = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ShelfSwipe MCP — Dummy Shop Catalog</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root[data-theme="light"] {
    --bg: #f8fafc;
    --surface: #ffffff;
    --card: #ffffff;
    --border: #e2e8f0;
    --border-subtle: #f1f5f9;
    --text: #0f172a;
    --text-muted: #64748b;
    --accent: #4f46e5;
    --accent-hover: #4338ca;
    --accent-light: #eef2ff;
    --pill-active-bg: #0f172a;
    --pill-active-text: #ffffff;
    --pill-inactive-bg: #ffffff;
    --pill-inactive-text: #475569;
    --pill-inactive-border: #e2e8f0;
    --badge-bg: #f1f5f9;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
    --shadow-card: 0 4px 20px -2px rgba(15, 23, 42, 0.06);
    --shadow-card-hover: 0 12px 30px -4px rgba(15, 23, 42, 0.12);
    --green: #059669;
    --green-bg: #ecfdf5;
    --orange: #d97706;
    --orange-bg: #fffbeb;
    --code-bg: #090d16;
    --code-text: #34d399;
  }

  :root[data-theme="dark"] {
    --bg: #090a0f;
    --surface: #11131c;
    --card: #161824;
    --border: #232738;
    --border-subtle: #1c1f2e;
    --text: #f8fafc;
    --text-muted: #94a3b8;
    --accent: #6366f1;
    --accent-hover: #4f46e5;
    --accent-light: rgba(99, 102, 241, 0.15);
    --pill-active-bg: #ffffff;
    --pill-active-text: #090a0f;
    --pill-inactive-bg: #161824;
    --pill-inactive-text: #94a3b8;
    --pill-inactive-border: #232738;
    --badge-bg: #1c1f2e;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.4);
    --shadow-card: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    --shadow-card-hover: 0 12px 32px -4px rgba(99, 102, 241, 0.2);
    --green: #34d399;
    --green-bg: rgba(52, 211, 153, 0.12);
    --orange: #fbbf24;
    --orange-bg: rgba(251, 191, 36, 0.12);
    --code-bg: #090a0f;
    --code-text: #34d399;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    transition: background 0.2s ease, color 0.2s ease;
  }

  /* Header */
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
    backdrop-filter: blur(12px);
  }
  .header-inner {
    max-width: 1400px; margin: 0 auto;
    padding: 0 2rem;
    display: flex; align-items: center; justify-content: space-between;
    height: 70px;
  }
  .brand { display: flex; align-items: center; gap: 0.75rem; }
  .logo {
    font-size: 1.35rem; font-weight: 800; letter-spacing: -0.02em;
    color: var(--text);
    display: flex; align-items: center; gap: 0.5rem;
  }
  .badge {
    background: var(--accent); color: #fff;
    font-size: 0.65rem; font-weight: 700;
    padding: 3px 9px; border-radius: 9999px; letter-spacing: 0.06em;
  }
  .header-right { display: flex; align-items: center; gap: 1rem; }
  .stats-pill {
    font-size: 0.82rem; font-weight: 500; color: var(--text-muted);
    background: var(--badge-bg); padding: 5px 12px; border-radius: 9999px;
    border: 1px solid var(--border);
  }
  .theme-btn {
    background: var(--surface); border: 1px solid var(--border);
    color: var(--text); padding: 7px 14px; border-radius: 9999px;
    font-size: 0.85rem; font-weight: 600; cursor: pointer;
    display: flex; align-items: center; gap: 0.5rem;
    transition: all 0.2s;
  }
  .theme-btn:hover { border-color: var(--accent); transform: translateY(-1px); }

  /* Hero / Analytics Bar */
  .hero-container {
    max-width: 1400px; margin: 2rem auto 1.5rem; padding: 0 2rem;
  }
  .hero-title {
    font-size: 1.85rem; font-weight: 800; letter-spacing: -0.03em;
    margin-bottom: 0.35rem; color: var(--text);
  }
  .hero-subtitle {
    font-size: 0.95rem; color: var(--text-muted); margin-bottom: 1.5rem;
  }

  /* Metric cards - Wollo style */
  .metrics-row {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem; margin-bottom: 2rem;
  }
  .metric-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; padding: 1.25rem 1.5rem;
    box-shadow: var(--shadow-sm);
    display: flex; flex-direction: column; gap: 0.5rem;
  }
  .metric-label { font-size: 0.8rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
  .metric-value { font-size: 1.8rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
  .metric-pill { font-size: 0.72rem; font-weight: 700; border-radius: 9999px; padding: 2px 8px; width: fit-content; }

  /* Search bar */
  .search-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sm); display: flex; gap: 0.75rem; flex-wrap: wrap;
    align-items: center;
  }
  input {
    background: var(--bg); border: 1px solid var(--border); color: var(--text);
    border-radius: 12px; padding: 0.65rem 1.1rem; font-size: 0.9rem; font-family: inherit;
    outline: none; transition: border-color 0.2s, box-shadow 0.2s;
  }
  input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-light); }
  input[type="text"] { flex: 1; min-width: 220px; }
  input[type="number"] { width: 140px; }
  .btn-primary {
    background: var(--accent); color: #fff; border: none; border-radius: 12px;
    padding: 0.65rem 1.5rem; font-weight: 600; font-size: 0.9rem;
    cursor: pointer; transition: all 0.2s;
  }
  .btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }
  .btn-reset {
    background: var(--bg); border: 1px solid var(--border); color: var(--text-muted);
    border-radius: 12px; padding: 0.65rem 1.25rem; font-weight: 600; font-size: 0.9rem;
    cursor: pointer; transition: all 0.2s;
  }
  .btn-reset:hover { color: var(--text); border-color: var(--text-muted); }

  /* Pill Tabs - Wollo styled */
  .tabs-bar {
    max-width: 1400px; margin: 0 auto 1.5rem; padding: 0 2rem;
    display: flex; gap: 0.6rem; overflow-x: auto; padding-bottom: 0.5rem;
  }
  .tab-pill {
    background: var(--pill-inactive-bg);
    border: 1px solid var(--pill-inactive-border);
    color: var(--pill-inactive-text);
    border-radius: 9999px; padding: 0.55rem 1.25rem;
    font-size: 0.88rem; font-weight: 600; cursor: pointer;
    white-space: nowrap; transition: all 0.2s ease;
    box-shadow: var(--shadow-sm);
  }
  .tab-pill:hover { border-color: var(--text); color: var(--text); }
  .tab-pill.active {
    background: var(--pill-active-bg);
    border-color: var(--pill-active-bg);
    color: var(--pill-active-text);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }

  /* Grid */
  .grid-container {
    max-width: 1400px; margin: 0 auto; padding: 0 2rem 3rem;
  }
  .grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
    gap: 1.5rem;
  }

  /* Wollo style clean Cards */
  .product-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 20px; overflow: hidden;
    box-shadow: var(--shadow-card);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    display: flex; flex-direction: column;
  }
  .product-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-card-hover);
  }
  .card-img-wrap {
    width: 100%; height: 210px; background: var(--border-subtle);
    overflow: hidden; position: relative;
  }
  .product-card img {
    width: 100%; height: 100%; object-fit: cover;
    transition: transform 0.3s ease;
  }
  .product-card:hover img { transform: scale(1.03); }
  .card-body {
    padding: 1.25rem; flex: 1; display: flex; flex-direction: column; gap: 0.6rem;
  }
  .card-shop {
    font-size: 0.72rem; color: var(--accent); font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em;
  }
  .card-name {
    font-size: 1.05rem; font-weight: 700; color: var(--text);
    line-height: 1.35;
  }
  .card-desc {
    font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; flex: 1;
  }
  .why-box {
    font-size: 0.8rem; color: var(--text-muted); font-style: italic;
    padding: 0.5rem 0.75rem; background: var(--badge-bg);
    border-radius: 10px; border-left: 3px solid var(--accent);
  }
  .tag-list { display: flex; flex-wrap: wrap; gap: 4px; }
  .tag-item {
    font-size: 0.7rem; background: var(--badge-bg);
    border: 1px solid var(--border); color: var(--text-muted);
    border-radius: 6px; padding: 2px 7px;
  }
  .card-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding-top: 0.85rem; border-top: 1px solid var(--border);
    margin-top: auto;
  }
  .price { font-size: 1.25rem; font-weight: 800; color: var(--green); }
  .category-pill {
    font-size: 0.72rem; font-weight: 600;
    background: var(--accent-light); color: var(--accent);
    border-radius: 9999px; padding: 4px 10px;
  }

  /* MCP interactive panel */
  .mcp-container {
    max-width: 1400px; margin: 0 auto 2rem; padding: 0 2rem;
  }
  .mcp-box {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; padding: 1.5rem;
    box-shadow: var(--shadow-sm);
  }
  .mcp-head {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1rem;
  }
  .mcp-title {
    font-size: 1rem; font-weight: 700; color: var(--text);
    display: flex; align-items: center; gap: 0.5rem;
  }
  .mcp-btn-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-bottom: 1rem; }
  .mcp-btn {
    font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
    background: var(--bg); border: 1px solid var(--border); color: var(--text);
    border-radius: 10px; padding: 6px 12px; cursor: pointer;
    transition: all 0.15s; font-weight: 500;
  }
  .mcp-btn:hover { border-color: var(--accent); color: var(--accent); }
  .mcp-code {
    background: var(--code-bg); border: 1px solid var(--border);
    border-radius: 14px; padding: 1rem 1.25rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.82rem;
    color: var(--code-text); white-space: pre-wrap; max-height: 280px; overflow-y: auto;
  }

  /* Shimmer Skeleton Loaders */
  .skeleton-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; overflow: hidden; height: 380px;
    display: flex; flex-direction: column;
  }
  .shimmer {
    background: linear-gradient(90deg, var(--border-subtle) 25%, var(--badge-bg) 50%, var(--border-subtle) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
  }
  @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
  .skeleton-img { height: 200px; width: 100%; }
  .skeleton-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; flex: 1; }
  .skeleton-line { height: 16px; border-radius: 8px; width: 80%; }
  .skeleton-line.short { width: 40%; }
  .skeleton-line.half { width: 60%; }
</style>
</head>
<body>

<header>
  <div class="header-inner">
    <div class="brand">
      <div class="logo">ShelfSwipe</div>
      <div class="badge">MCP</div>
    </div>
    <div class="header-right">
      <div class="stats-pill" id="statsHeader">5 stores · 26 products</div>
      <button class="theme-btn" id="themeToggle" onclick="toggleTheme()">
        <span id="themeText">Dark Theme</span>
      </button>
    </div>
  </div>
</header>

<main class="hero-container">
  <h1 class="hero-title">Merchant Catalogs</h1>
  <p class="hero-subtitle">Registry of verified merchant fixtures and PayTrace onboarding bridge</p>

  <!-- Metric highlight cards like Wollo -->
  <div class="metrics-row">
    <div class="metric-card">
      <div class="metric-label">Registered Shops</div>
      <div class="metric-value">5</div>
      <div class="metric-pill" style="background:var(--green-bg); color:var(--green);">Active & Verified</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Total Inventory</div>
      <div class="metric-value">26</div>
      <div class="metric-pill" style="background:var(--accent-light); color:var(--accent);">In-Stock Fixtures</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">MCP Protocol</div>
      <div class="metric-value">v1.0</div>
      <div class="metric-pill" style="background:var(--orange-bg); color:var(--orange);">PayTrace Bridge</div>
    </div>
  </div>

  <!-- Search input bar -->
  <div class="search-card">
    <input type="text" id="query" placeholder="Search products across all merchant shops (e.g. coffee, vase, keyboard)..." oninput="debounceSearch()"/>
    <input type="number" id="maxPrice" placeholder="Max price $" min="0" step="5" oninput="debounceSearch()"/>
    <input type="text" id="category" placeholder="Category filter..." oninput="debounceSearch()"/>
    <button class="btn-primary" onclick="doSearch()">Search</button>
    <button class="btn-reset" onclick="resetSearch()">Reset</button>
  </div>
</main>

<!-- Shop tabs -->
<div class="tabs-bar" id="tabs">
  <button class="tab-pill active" data-url="all" onclick="switchTab(this)">All Shops</button>
</div>

<!-- MCP Tool Tester -->
<div class="mcp-container">
  <div class="mcp-box">
    <div class="mcp-head">
      <div class="mcp-title">MCP Agent Protocol Console <span style="font-size:0.8rem; font-weight:400; color:var(--text-muted);">— simulate LLM agent tool calls</span></div>
    </div>
    <div class="mcp-btn-row">
      <button class="mcp-btn" onclick="callTool('list_shops', {})">list_shops()</button>
      <button class="mcp-btn" onclick="callTool('fetch_catalog', {shop_url: currentShopUrl()})">fetch_catalog(shop_url)</button>
      <button class="mcp-btn" onclick="callTool('search_shop', {shop_url: currentShopUrl(), query: document.getElementById('query').value || 'gift'})">search_shop(shop_url, query)</button>
      <button class="mcp-btn" onclick="callTool('search_all_shops', {query: document.getElementById('query').value || 'gift'})">search_all_shops(query)</button>
    </div>
    <pre class="mcp-code" id="mcpOutput">// Click a tool button above to test real-time tool execution JSON response.</pre>
  </div>
</div>

<!-- Grid -->
<div class="grid-container">
  <div style="font-size:0.9rem; font-weight:600; color:var(--text-muted); margin-bottom:1rem;">
    Showing <span id="productCount" style="color:var(--text); font-weight:700;">0</span> products
  </div>
  <div class="grid" id="grid"></div>
</div>

<script>
let allShops = [];
let debounceTimer = null;
let activeUrl = 'all';

// Theme management
function initTheme() {
  const saved = localStorage.getItem('shelfswipe-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeBtn(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('shelfswipe-theme', next);
  updateThemeBtn(next);
}

function updateThemeBtn(theme) {
  const text = document.getElementById('themeText');
  if (theme === 'dark') {
    text.textContent = 'Light Theme';
  } else {
    text.textContent = 'Dark Theme';
  }
}

async function init() {
  initTheme();
  renderSkeletons();
  try {
    const res = await fetch('/api/shops');
    if (!res.ok) throw new Error('Failed to load shops');
    allShops = await res.json();
    const tabs = document.getElementById('tabs');
    allShops.forEach(shop => {
      const btn = document.createElement('button');
      btn.className = 'tab-pill';
      btn.dataset.url = shop.shop_url;
      btn.textContent = `${shop.shop_name} (${shop.product_count})`;
      btn.onclick = () => switchTab(btn);
      tabs.appendChild(btn);
    });
      btn.dataset.url = shop.shop_url;
      const key = shop.shop_url.split('/').pop();
      const emoji = EMOJI_MAP[key] || '🛍️';
      btn.textContent = `${emoji} ${shop.shop_name} (${shop.product_count})`;
      btn.onclick = () => switchTab(btn);
      tabs.appendChild(btn);
    });
    await loadProducts();
  } catch(e) {
    document.getElementById('grid').innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:3rem; color:var(--text-muted);"><h3>Failed to connect</h3><p>${e.message}</p></div>`;
  }
}

function currentShopUrl() {
  return activeUrl === 'all' ? (allShops[0]?.shop_url || '') : activeUrl;
}

function switchTab(el) {
  document.querySelectorAll('.tab-pill').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  activeUrl = el.dataset.url;
  loadProducts();
}

function debounceSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(doSearch, 250);
}

function doSearch() { loadProducts(); }

function resetSearch() {
  document.getElementById('query').value = '';
  document.getElementById('maxPrice').value = '';
  document.getElementById('category').value = '';
  loadProducts();
}

function renderSkeletons() {
  const grid = document.getElementById('grid');
  let html = '';
  for (let i = 0; i < 6; i++) {
    html += `
      <div class="skeleton-card">
        <div class="skeleton-img shimmer"></div>
        <div class="skeleton-body">
          <div class="skeleton-line short shimmer"></div>
          <div class="skeleton-line shimmer"></div>
          <div class="skeleton-line half shimmer"></div>
        </div>
      </div>
    `;
  }
  grid.innerHTML = html;
}

async function loadProducts() {
  renderSkeletons();
  const query = document.getElementById('query').value.trim();
  const maxPrice = document.getElementById('maxPrice').value;
  const category = document.getElementById('category').value.trim();

  let url = '/api/search?query=' + encodeURIComponent(query || '');
  if (maxPrice) url += '&max_price=' + maxPrice;
  if (category) url += '&category=' + encodeURIComponent(category);
  if (activeUrl !== 'all') url += '&shop_url=' + encodeURIComponent(activeUrl);

  try {
    const res = await fetch(url);
    const data = await res.json();
    renderProducts(data.products || []);
  } catch(e) {
    document.getElementById('grid').innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:3rem; color:var(--text-muted);"><h3>Error loading products</h3><p>${e.message}</p></div>`;
  }
}

function renderProducts(products) {
  const grid = document.getElementById('grid');
  document.getElementById('productCount').textContent = products.length;

  if (!products.length) {
    grid.innerHTML = `
      <div style="grid-column:1/-1; text-align:center; padding:4rem 2rem; color:var(--text-muted);">
        <h3 style="font-size:1.3rem; margin-bottom:0.5rem; color:var(--text);">No matching products</h3>
        <p>Try searching for gifts, ceramics, sourdough, or clearing filters.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = products.map(p => `
    <div class="product-card">
      <div class="card-img-wrap">
        <img src="${p.image_url}" alt="${p.name}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=600&q=80'"/>
      </div>
      <div class="card-body">
        <div class="card-shop">${p.source_shop || p.category}</div>
        <div class="card-name">${p.name}</div>
        <div style="font-size:0.7rem; color:var(--text-muted); font-family:monospace;">ID: ${p.id}</div>
        <div class="card-desc">${p.description}</div>
        ${p.why_matches ? `<div class="why-box">${p.why_matches}</div>` : ''}
        <div class="tag-list">${(p.tags||[]).map(t => `<span class="tag-item">${t}</span>`).join('')}</div>
        <div class="card-footer">
          <div>
            <div class="price">$${p.price.toFixed(2)}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">${p.stock} in stock</div>
          </div>
          <div class="category-pill">${p.category}</div>
        </div>
      </div>
    </div>
  `).join('');
}

async function callTool(toolName, args) {
  const out = document.getElementById('mcpOutput');
  out.textContent = `// Executing ${toolName}...\\n`;
  try {
    const res = await fetch('/api/mcp', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({tool: toolName, arguments: args})
    });
    const data = await res.json();
    out.textContent = `// Tool: ${toolName}\\n// Arguments: ${JSON.stringify(args, null, 2)}\\n\\n` + JSON.stringify(data, null, 2);
  } catch(e) {
    out.textContent = '// Execution error: ' + e.message;
  }
}

window.addEventListener('DOMContentLoaded', init);
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
                # attach shop name — Pydantic v2 models are immutable; use dict merge
                catalog_obj = load_catalog(shop_url)
                shop_name = catalog_obj.shop_name if catalog_obj else shop_url
                product_dicts = [dict(p.model_dump(), source_shop=shop_name) for p in products]
                self.send_json({
                    "query": query,
                    "total_matches": len(product_dicts),
                    "products": product_dicts,
                })
                return
            else:
                all_product_dicts = []
                for s_url in URL_TO_FIXTURE:
                    cat = load_catalog(s_url)
                    s_name = cat.shop_name if cat else s_url
                    cat_products = search_catalog(s_url, query, max_price, category)
                    for p in cat_products[:20]:
                        all_product_dicts.append(dict(p.model_dump(), source_shop=s_name))
                self.send_json({
                    "query": query,
                    "total_matches": len(all_product_dicts),
                    "products": all_product_dicts,
                })
                return

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
