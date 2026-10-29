'use client';

export default function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-[#1a1a24] rounded-2xl border border-gray-100 dark:border-[#2d2d3d] overflow-hidden">
      {/* Image placeholder */}
      <div className="shimmer h-[200px] w-full" />

      {/* Body */}
      <div className="p-4 space-y-3">
        {/* Shop badge */}
        <div className="shimmer h-4 w-24 rounded-full" />
        {/* Title */}
        <div className="space-y-1.5">
          <div className="shimmer h-5 w-full rounded-lg" />
          <div className="shimmer h-5 w-3/4 rounded-lg" />
        </div>
        {/* Description */}
        <div className="space-y-1">
          <div className="shimmer h-3.5 w-full rounded" />
          <div className="shimmer h-3.5 w-5/6 rounded" />
          <div className="shimmer h-3.5 w-4/5 rounded" />
        </div>
        {/* Price + category */}
        <div className="flex items-center justify-between pt-1">
          <div className="shimmer h-6 w-16 rounded-lg" />
          <div className="shimmer h-5 w-24 rounded-full" />
        </div>
        {/* Tags */}
        <div className="flex gap-1.5">
          <div className="shimmer h-5 w-12 rounded-full" />
          <div className="shimmer h-5 w-16 rounded-full" />
          <div className="shimmer h-5 w-10 rounded-full" />
        </div>
      </div>
    </div>
  );
}
