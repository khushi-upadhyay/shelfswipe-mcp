'use client';

const SHOP_EMOJIS: Record<string, string> = {
  'shelfswipe://fixtures/artisan_pottery': '🏺',
  'shelfswipe://fixtures/bakery_shop': '🥐',
  'shelfswipe://fixtures/home_garden': '🌿',
  'shelfswipe://fixtures/tech_gadgets': '💡',
  'shelfswipe://fixtures/bath_body': '🛁',
};

interface Shop {
  shop_url: string;
  shop_name: string;
  shop_id: string;
  product_count: number;
}

interface ShopTabsProps {
  shops: Shop[];
  activeShop: string;
  onSelect: (shopUrl: string) => void;
}

export default function ShopTabs({ shops, activeShop, onSelect }: ShopTabsProps) {
  return (
    <div className="relative">
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-hide">
        {/* All tab */}
        <button
          onClick={() => onSelect('')}
          className={`
            shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all duration-150
            ${activeShop === ''
              ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900 shadow-sm'
              : 'border border-gray-300 dark:border-[#3d3d50] text-gray-600 dark:text-gray-400 hover:bg-gray-900 hover:text-white dark:hover:bg-white dark:hover:text-gray-900 hover:border-transparent'
            }
          `}
        >
          <span>🛍</span>
          <span>All Shops</span>
        </button>

        {/* Per-shop tabs */}
        {shops.map((shop) => {
          const emoji = SHOP_EMOJIS[shop.shop_url] ?? '🏪';
          const isActive = activeShop === shop.shop_url;
          return (
            <button
              key={shop.shop_url}
              onClick={() => onSelect(shop.shop_url)}
              className={`
                shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium transition-all duration-150
                ${isActive
                  ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900 shadow-sm'
                  : 'border border-gray-300 dark:border-[#3d3d50] text-gray-600 dark:text-gray-400 hover:bg-gray-900 hover:text-white dark:hover:bg-white dark:hover:text-gray-900 hover:border-transparent'
                }
              `}
            >
              <span>{emoji}</span>
              <span className="whitespace-nowrap">{shop.shop_name}</span>
              <span className={`text-xs px-1.5 py-0.5 rounded-full tabular-nums ${isActive ? 'bg-white/20 dark:bg-black/20' : 'bg-gray-100 dark:bg-[#2a2a3d] text-gray-500 dark:text-gray-500'}`}>
                {shop.product_count}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
