'use client';

export interface Product {
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
  source_shop: string;
  shop_url: string;
}

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const isLowStock = product.stock > 0 && product.stock <= 4;
  const isOutOfStock = product.stock <= 0;

  return (
    <article className="group bg-white dark:bg-[#141622] rounded-[24px] border border-slate-200/70 dark:border-white/[0.08] overflow-hidden shadow-[0_4px_20px_-2px_rgba(0,0,0,0.03)] hover:shadow-[0_16px_36px_-4px_rgba(0,0,0,0.08)] dark:hover:shadow-[0_16px_40px_-4px_rgba(0,0,0,0.4)] transition-all duration-300 hover:-translate-y-1 flex flex-col">
      {/* Image Container */}
      <div className="relative h-[200px] w-full bg-slate-100 dark:bg-white/[0.04] overflow-hidden">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
          onError={(e) => {
            (e.target as HTMLImageElement).src =
              'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80';
          }}
        />
        <div className="absolute top-3 left-3 bg-white/90 dark:bg-black/80 backdrop-blur-md px-2.5 py-1 rounded-full text-[10px] font-semibold tracking-wide text-slate-800 dark:text-slate-200 border border-black/5 dark:border-white/10 shadow-sm">
          {product.source_shop}
        </div>
      </div>

      {/* Card Content */}
      <div className="p-5 flex flex-col flex-1 gap-2.5">
        <div className="flex items-center justify-between gap-2">
          <span className="text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-white/[0.06] text-slate-600 dark:text-slate-400">
            {product.category}
          </span>
          <span className="text-[11px] font-mono text-slate-400">
            #{product.id}
          </span>
        </div>

        <h3 className="font-bold text-slate-900 dark:text-slate-100 text-base leading-snug line-clamp-1 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
          {product.name}
        </h3>

        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-2 flex-1">
          {product.description}
        </p>

        {product.why_matches && (
          <div className="text-[11px] text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-white/[0.04] border-l-2 border-indigo-500 px-2.5 py-1.5 rounded-r-lg italic">
            {product.why_matches}
          </div>
        )}

        {/* Footer info: Price & Stock */}
        <div className="pt-3 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between mt-auto">
          <div>
            <div className="text-lg font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
              ${product.price.toFixed(2)}
            </div>
            <div className="text-[11px] text-slate-400 font-medium">
              {isOutOfStock ? (
                <span className="text-rose-500">Out of stock</span>
              ) : isLowStock ? (
                <span className="text-amber-500">Only {product.stock} units left</span>
              ) : (
                <span>{product.stock} units in inventory</span>
              )}
            </div>
          </div>

          <div className="flex flex-wrap gap-1 max-w-[120px] justify-end">
            {(product.tags || []).slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="text-[10px] font-medium px-2 py-0.5 rounded-md bg-slate-100 dark:bg-white/[0.06] text-slate-500 dark:text-slate-400"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </article>
  );
}
