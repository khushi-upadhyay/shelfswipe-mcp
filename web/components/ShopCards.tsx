'use client';

interface Shop {
  shop_url: string;
  shop_name: string;
  shop_id: string;
  description: string;
  product_count: number;
}

interface ShopCardsProps {
  shops: Shop[];
  activeShop: string;
  onSelectShop: (url: string) => void;
}

const SHOP_METADATA: Record<string, { subtitle: string; category: string; gradient: string }> = {
  'shelfswipe://fixtures/artisan_pottery': {
    subtitle: 'Hand-thrown stoneware & raku ceramics',
    category: 'Ceramics & Kitchen',
    gradient: 'from-amber-500/10 to-orange-500/10 text-amber-600 dark:text-amber-400',
  },
  'shelfswipe://fixtures/bakery_shop': {
    subtitle: 'Small-batch baked goods & honey preserves',
    category: 'Gourmet Pantry',
    gradient: 'from-rose-500/10 to-amber-500/10 text-rose-600 dark:text-rose-400',
  },
  'shelfswipe://fixtures/home_garden': {
    subtitle: 'Indoor botanicals & artisanal planters',
    category: 'Botanicals & Home',
    gradient: 'from-emerald-500/10 to-teal-500/10 text-emerald-600 dark:text-emerald-400',
  },
  'shelfswipe://fixtures/tech_gadgets': {
    subtitle: 'Mechanical desk tools & developer accessories',
    category: 'Indie Hardware',
    gradient: 'from-blue-500/10 to-indigo-500/10 text-blue-600 dark:text-blue-400',
  },
  'shelfswipe://fixtures/bath_body': {
    subtitle: 'Organic cold-process care & aromatherapy',
    category: 'Wellness & Body',
    gradient: 'from-violet-500/10 to-pink-500/10 text-violet-600 dark:text-violet-400',
  },
};

export default function ShopCards({ shops, activeShop, onSelectShop }: ShopCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-3.5">
      {shops.map((shop) => {
        const meta = SHOP_METADATA[shop.shop_url] || {
          subtitle: shop.description,
          category: 'Merchant Store',
          gradient: 'from-slate-500/10 to-slate-500/10 text-slate-600 dark:text-slate-400',
        };
        const isSelected = activeShop === shop.shop_url;

        return (
          <button
            key={shop.shop_url}
            onClick={() => onSelectShop(isSelected ? '' : shop.shop_url)}
            className={`text-left p-4 rounded-3xl border transition-all duration-200 relative group flex flex-col justify-between h-[130px] ${
              isSelected
                ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-slate-900 dark:border-white shadow-lg ring-2 ring-slate-900/10 dark:ring-white/20'
                : 'bg-white/80 dark:bg-[#141622]/80 hover:bg-white dark:hover:bg-[#181a28] border-slate-200/80 dark:border-white/[0.08] hover:border-slate-300 dark:hover:border-white/[0.15] shadow-[0_4px_20px_-2px_rgba(0,0,0,0.03)] hover:shadow-md'
            }`}
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span
                  className={`text-[11px] font-semibold tracking-wide uppercase px-2 py-0.5 rounded-full ${
                    isSelected
                      ? 'bg-white/20 dark:bg-black/10 text-white dark:text-slate-900'
                      : meta.gradient
                  }`}
                >
                  {meta.category}
                </span>
                <span
                  className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                    isSelected
                      ? 'bg-white/20 dark:bg-black/10 text-white dark:text-slate-900'
                      : 'bg-slate-100 dark:bg-white/[0.06] text-slate-500 dark:text-slate-400'
                  }`}
                >
                  {shop.product_count} items
                </span>
              </div>
              <h3
                className={`font-bold text-sm tracking-tight leading-snug line-clamp-1 ${
                  isSelected ? 'text-white dark:text-slate-900' : 'text-slate-900 dark:text-slate-100'
                }`}
              >
                {shop.shop_name}
              </h3>
            </div>

            <p
              className={`text-xs line-clamp-1 leading-relaxed ${
                isSelected
                  ? 'text-white/80 dark:text-slate-700'
                  : 'text-slate-500 dark:text-slate-400'
              }`}
            >
              {meta.subtitle}
            </p>
          </button>
        );
      })}
    </div>
  );
}

