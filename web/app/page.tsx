'use client';

import { useEffect, useState, useCallback } from 'react';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import GlassOrb from '@/components/GlassOrb';
import ShopCards from '@/components/ShopCards';
import SearchBar from '@/components/SearchBar';
import ProductCard, { Product } from '@/components/ProductCard';
import McpPanel from '@/components/McpPanel';

interface Shop {
  shop_url: string;
  shop_name: string;
  shop_id: string;
  description: string;
  product_count: number;
}

interface SearchResult {
  query: string;
  total_matches: number;
  products: Product[];
}

export default function CatalogPage() {
  const [currentTab, setCurrentTab] = useState<'catalog' | 'tools'>('catalog');
  const [isDark, setIsDark] = useState<boolean>(false);

  // Synchronize theme with DOM / localStorage
  useEffect(() => {
    const isDarkMode = document.documentElement.classList.contains('dark');
    setIsDark(isDarkMode);
  }, []);

  const handleToggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (nextDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('shelfswipe-theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('shelfswipe-theme', 'light');
    }
  };

  // Shops
  const [shops, setShops] = useState<Shop[]>([]);
  const [shopsLoading, setShopsLoading] = useState(true);
  const totalProducts = shops.reduce((sum, s) => sum + s.product_count, 0);

  // Search and filter state
  const [query, setQuery] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [category, setCategory] = useState('');
  const [activeShop, setActiveShop] = useState('');

  // Products
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);

  // Fetch shops
  useEffect(() => {
    fetch('/api/shops')
      .then((r) => r.json())
      .then((data: Shop[]) => {
        setShops(data);
        setShopsLoading(false);
      })
      .catch(() => setShopsLoading(false));
  }, []);

  // Fetch products
  const fetchProducts = useCallback(
    async (opts: {
      query: string;
      maxPrice: string;
      category: string;
      shopUrl: string;
    }) => {
      setProductsLoading(true);
      const params = new URLSearchParams();
      if (opts.query) params.set('query', opts.query);
      if (opts.maxPrice) params.set('max_price', opts.maxPrice);
      if (opts.category) params.set('category', opts.category);
      if (opts.shopUrl) params.set('shop_url', opts.shopUrl);

      try {
        const res = await fetch(`/api/search?${params.toString()}`);
        const data: SearchResult = await res.json();
        setProducts(data.products || []);
      } catch {
        setProducts([]);
      } finally {
        setProductsLoading(false);
      }
    },
    []
  );

  // Initial load
  useEffect(() => {
    fetchProducts({ query: '', maxPrice: '', category: '', shopUrl: '' });
  }, [fetchProducts]);

  const handleSearch = () => {
    fetchProducts({ query, maxPrice, category, shopUrl: activeShop });
  };

  const handleReset = () => {
    setQuery('');
    setMaxPrice('');
    setCategory('');
    setActiveShop('');
    fetchProducts({ query: '', maxPrice: '', category: '', shopUrl: '' });
  };

  const handleShopSelect = (shopUrl: string) => {
    setActiveShop(shopUrl);
    fetchProducts({ query, maxPrice, category, shopUrl });
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#eceff3] dark:bg-[#07080b] p-2 md:p-3 transition-colors duration-300">
      {/* Outer rounded window container (replicates the clean framing of reference screenshot) */}
      <div className="flex flex-1 w-full h-full rounded-[28px] md:rounded-[36px] bg-[#f8fafc] dark:bg-[#0c0d12] border border-slate-300/60 dark:border-white/[0.06] shadow-2xl overflow-hidden">
        {/* Left minimal navigation sidebar rail */}
        <Sidebar
          currentTab={currentTab}
          onTabChange={setCurrentTab}
          isDark={isDark}
          onToggleTheme={handleToggleTheme}
        />

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col h-full overflow-y-auto px-6 md:px-10 py-6">
          {/* Header */}
          <Header
            shopCount={shops.length}
            productCount={totalProducts}
            isDark={isDark}
            onToggleTheme={handleToggleTheme}
          />

          {/* Hero Greeting Section (Wollo / Reference Screenshot 2 style) */}
          <div className="py-4 md:py-6 flex items-center gap-4">
            <GlassOrb size={54} />
            <div>
              <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
                Explore Merchant Stores
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                {activeShop
                  ? `Filtering products for ${shops.find((s) => s.shop_url === activeShop)?.shop_name || 'selected shop'}`
                  : 'Select a merchant storefront below or search across all registered fixtures'}
              </p>
            </div>
          </div>

          {/* 5 Shop Storefront Cards */}
          <section className="mb-6">
            {!shopsLoading && shops.length > 0 && (
              <ShopCards
                shops={shops}
                activeShop={activeShop}
                onSelectShop={handleShopSelect}
              />
            )}
          </section>

          {/* Search Bar - Clean Pill input styled like Screenshot 2 */}
          <section className="mb-8">
            <SearchBar
              query={query}
              maxPrice={maxPrice}
              category={category}
              onQueryChange={setQuery}
              onMaxPriceChange={setMaxPrice}
              onCategoryChange={setCategory}
              onSearch={handleSearch}
              onReset={handleReset}
              loading={productsLoading}
            />
          </section>

          {/* Tab Content */}
          {currentTab === 'tools' ? (
            <section className="flex-1 pb-10">
              <McpPanel />
            </section>
          ) : (
            <section className="flex-1 pb-10">
              {/* Product Grid Header */}
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold tracking-wider uppercase text-slate-400 dark:text-slate-500">
                  Showing {products.length} {products.length === 1 ? 'Product' : 'Products'}
                </span>
                {activeShop && (
                  <button
                    onClick={() => handleShopSelect('')}
                    className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline font-semibold"
                  >
                    Clear Store Filter
                  </button>
                )}
              </div>

              {/* Shimmer Skeleton or Product Cards */}
              {productsLoading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                  {[...Array(8)].map((_, i) => (
                    <div
                      key={i}
                      className="rounded-[24px] bg-white dark:bg-[#141622] border border-slate-200/60 dark:border-white/[0.06] h-[360px] p-4 flex flex-col gap-3 shadow-sm"
                    >
                      <div className="w-full h-[180px] rounded-2xl shimmer" />
                      <div className="w-24 h-4 rounded-full shimmer" />
                      <div className="w-full h-5 rounded-md shimmer" />
                      <div className="w-2/3 h-4 rounded-md shimmer" />
                      <div className="mt-auto flex justify-between">
                        <div className="w-16 h-6 rounded-md shimmer" />
                        <div className="w-20 h-6 rounded-md shimmer" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : products.length === 0 ? (
                <div className="py-20 text-center rounded-[32px] border border-dashed border-slate-300 dark:border-white/[0.1] bg-white/40 dark:bg-white/[0.02]">
                  <p className="text-base font-semibold text-slate-700 dark:text-slate-300">
                    No matching products found
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Try adjusting your search terms or reset filters
                  </p>
                  <button
                    onClick={handleReset}
                    className="mt-4 px-4 py-2 rounded-full text-xs font-semibold bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-sm"
                  >
                    Reset Search
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                  {products.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              )}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
