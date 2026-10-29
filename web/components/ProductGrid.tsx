'use client';

import ProductCard, { Product } from './ProductCard';
import SkeletonCard from './SkeletonCard';

interface ProductGridProps {
  products: Product[];
  loading: boolean;
  query: string;
}

export default function ProductGrid({ products, loading, query }: ProductGridProps) {
  if (loading) {
    return (
      <div
        className="grid gap-5"
        style={{
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        }}
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4 text-center">
        <div className="text-5xl">🔍</div>
        <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300">
          No products found
        </h3>
        <p className="text-sm text-gray-400 dark:text-gray-500 max-w-xs">
          {query
            ? `No results match "${query}". Try adjusting your search or filters.`
            : 'No products match the current filters. Try resetting them.'}
        </p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          <span className="font-semibold text-gray-900 dark:text-gray-100">
            {products.length}
          </span>{' '}
          product{products.length !== 1 ? 's' : ''} found
          {query && (
            <>
              {' '}for{' '}
              <span className="font-medium text-indigo-600 dark:text-indigo-400">
                &ldquo;{query}&rdquo;
              </span>
            </>
          )}
        </p>
      </div>
      <div
        className="grid gap-5"
        style={{
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        }}
      >
        {products.map((product) => (
          <ProductCard key={`${product.shop_url}-${product.id}`} product={product} />
        ))}
      </div>
    </div>
  );
}
