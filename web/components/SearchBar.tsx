'use client';

import { useState } from 'react';

interface SearchBarProps {
  query: string;
  maxPrice: string;
  category: string;
  onQueryChange: (v: string) => void;
  onMaxPriceChange: (v: string) => void;
  onCategoryChange: (v: string) => void;
  onSearch: () => void;
  onReset: () => void;
  loading: boolean;
}

export default function SearchBar({
  query,
  maxPrice,
  category,
  onQueryChange,
  onMaxPriceChange,
  onCategoryChange,
  onSearch,
  onReset,
  loading,
}: SearchBarProps) {
  const [showFilters, setShowFilters] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch();
    }
  };

  return (
    <div className="w-full space-y-3">
      {/* Main Pill Search Bar - styled like the bottom bar in reference image */}
      <div className="relative w-full rounded-full bg-white dark:bg-[#141622] border border-slate-200/90 dark:border-white/[0.1] shadow-[0_8px_30px_rgba(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgba(0,0,0,0.3)] transition-all p-1.5 pl-5 sm:pl-6 flex items-center gap-3">
        {/* Search icon */}
        <svg className="w-5 h-5 text-slate-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
        </svg>

        {/* Input */}
        <input
          type="text"
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search products across all merchant shops (e.g. coffee, vase, keyboard)..."
          className="flex-1 bg-transparent border-none outline-none text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-sm sm:text-base font-normal min-w-0"
        />

        {/* Filter toggle button */}
        <button
          type="button"
          onClick={() => setShowFilters(!showFilters)}
          className={`shrink-0 hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition ${
            maxPrice || category || showFilters
              ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
              : 'bg-slate-100 dark:bg-white/[0.06] text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/[0.12]'
          }`}
        >
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Filters {(maxPrice || category) && '•'}
        </button>

        {/* Clear query button if query exists */}
        {query && (
          <button
            type="button"
            onClick={() => onQueryChange('')}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-full text-xs"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}

        {/* Submit Arrow Button - round black button like reference screenshot */}
        <button
          type="button"
          onClick={onSearch}
          disabled={loading}
          aria-label="Submit search"
          className="w-10 h-10 sm:w-11 sm:h-11 rounded-full bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-200 text-white dark:text-slate-900 flex items-center justify-center transition shrink-0 shadow-sm active:scale-95 disabled:opacity-50"
        >
          {loading ? (
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          )}
        </button>
      </div>

      {/* Expandable clean filter pills row */}
      {showFilters && (
        <div className="flex flex-wrap items-center gap-2.5 px-4 pt-1 text-xs">
          <div className="flex items-center gap-1.5 bg-white dark:bg-[#141622] border border-slate-200 dark:border-white/[0.08] px-3 py-1.5 rounded-full shadow-sm">
            <span className="text-slate-400 font-medium">Max $</span>
            <input
              type="number"
              value={maxPrice}
              onChange={(e) => onMaxPriceChange(e.target.value)}
              placeholder="e.g. 50"
              min={0}
              className="w-16 bg-transparent outline-none text-slate-800 dark:text-slate-200 font-medium"
            />
          </div>

          <div className="flex items-center gap-1.5 bg-white dark:bg-[#141622] border border-slate-200 dark:border-white/[0.08] px-3 py-1.5 rounded-full shadow-sm">
            <span className="text-slate-400 font-medium">Category</span>
            <input
              type="text"
              value={category}
              onChange={(e) => onCategoryChange(e.target.value)}
              placeholder="e.g. Kitchen"
              className="w-24 bg-transparent outline-none text-slate-800 dark:text-slate-200 font-medium"
            />
          </div>

          {(query || maxPrice || category) && (
            <button
              type="button"
              onClick={onReset}
              className="text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 underline font-medium ml-1"
            >
              Reset all filters
            </button>
          )}
        </div>
      )}
    </div>
  );
}
