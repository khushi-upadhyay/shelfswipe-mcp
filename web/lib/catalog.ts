import path from 'path';
import fs from 'fs';

export interface ShopFixture {
  shop_id: string;
  shop_name: string;
  shop_url: string;
  contact_email: string;
  description: string;
  products: ProductFixture[];
}

export interface ProductFixture {
  id: string;
  name: string;
  price: number;
  currency: string;
  category: string;
  description: string;
  image_url: string;
  stock: number;
  tags: string[];
  why_matches?: string;
}

export interface Product extends ProductFixture {
  source_shop: string;
  shop_url: string;
  score?: number;
}

// Fixture file names
const FIXTURE_FILES = [
  'artisan_pottery.json',
  'bakery_shop.json',
  'home_garden.json',
  'tech_gadgets.json',
  'bath_body.json',
];

export function getFixturePath(filename: string): string {
  return path.join(process.cwd(), 'fixtures', filename);
}

export function loadAllFixtures(): ShopFixture[] {
  return FIXTURE_FILES.map((file) => {
    const filePath = getFixturePath(file);
    const raw = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(raw) as ShopFixture;
  });
}

export function loadFixtureByUrl(shopUrl: string): ShopFixture | null {
  const all = loadAllFixtures();
  return all.find((s) => s.shop_url === shopUrl) ?? null;
}

const STOPWORDS = new Set(['the', 'and', 'for', 'with', 'a', 'an', 'of', 'in', 'to']);

function extractTerms(query: string): string[] {
  return query
    .toLowerCase()
    .split(/\s+/)
    .map((t) => t.replace(/[^a-z0-9]/g, ''))
    .filter((t) => t.length > 2 && !STOPWORDS.has(t));
}

function scoreProduct(product: ProductFixture, terms: string[]): number {
  if (terms.length === 0) return product.stock > 0 ? 5 : 0;

  const haystack = [
    product.name,
    product.category,
    product.description,
    ...(product.tags ?? []),
    product.why_matches ?? '',
  ]
    .join(' ')
    .toLowerCase();

  let score = 0;
  for (const term of terms) {
    if (haystack.includes(term)) score += 10;
  }
  if (product.stock > 0) score += 5;
  return score;
}

export interface SearchOptions {
  query?: string;
  max_price?: number;
  category?: string;
  in_stock_only?: boolean;
  shop_url?: string;
  limit_per_shop?: number;
}

export interface SearchResult {
  query: string;
  total_matches: number;
  products: Product[];
}

export function searchProducts(options: SearchOptions): SearchResult {
  const {
    query = '',
    max_price,
    category,
    in_stock_only = false,
    shop_url,
    limit_per_shop = 20,
  } = options;

  const terms = extractTerms(query);
  const shops = loadAllFixtures();
  const targetShops = shop_url
    ? shops.filter((s) => s.shop_url === shop_url)
    : shops;

  const results: Product[] = [];

  for (const shop of targetShops) {
    let shopProducts: Product[] = shop.products.map((p) => ({
      ...p,
      source_shop: shop.shop_name,
      shop_url: shop.shop_url,
    }));

    // Apply filters
    shopProducts = shopProducts.filter((p) => {
      if (max_price !== undefined && p.price > max_price) return false;
      if (category && !p.category.toLowerCase().includes(category.toLowerCase()))
        return false;
      if (in_stock_only && p.stock <= 0) return false;
      return true;
    });

    // Score
    shopProducts = shopProducts.map((p) => ({
      ...p,
      score: scoreProduct(p, terms),
    }));

    // If there's a query, filter out zero-score items
    if (terms.length > 0) {
      shopProducts = shopProducts.filter((p) => (p.score ?? 0) > 0);
    }

    // Sort: highest score first, then lowest price
    shopProducts.sort((a, b) => {
      const scoreDiff = (b.score ?? 0) - (a.score ?? 0);
      if (scoreDiff !== 0) return scoreDiff;
      return a.price - b.price;
    });

    // Limit per shop for cross-shop search
    if (!shop_url) {
      shopProducts = shopProducts.slice(0, limit_per_shop);
    }

    results.push(...shopProducts);
  }

  // Final sort across shops
  results.sort((a, b) => {
    const scoreDiff = (b.score ?? 0) - (a.score ?? 0);
    if (scoreDiff !== 0) return scoreDiff;
    return a.price - b.price;
  });

  return {
    query,
    total_matches: results.length,
    products: results,
  };
}

export function getShopSummaries() {
  const shops = loadAllFixtures();
  return shops.map((s) => ({
    shop_url: s.shop_url,
    shop_name: s.shop_name,
    shop_id: s.shop_id,
    description: s.description,
    product_count: s.products.length,
  }));
}
