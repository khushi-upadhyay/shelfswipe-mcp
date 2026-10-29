'use client';

interface HeaderProps {
  shopCount: number;
  productCount: number;
  isDark: boolean;
  onToggleTheme: () => void;
}

export default function Header({ shopCount, productCount, isDark, onToggleTheme }: HeaderProps) {
  return (
    <header className="w-full flex items-center justify-between pb-6 pt-2">
      {/* Left: Brand title & status */}
      <div className="flex items-center gap-3">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">
              ShelfSwipe
            </h1>
            <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded-full bg-slate-900 text-white dark:bg-white dark:text-slate-900">
              MCP
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Merchant shop catalog registry & PayTrace onboarding bridge
          </p>
        </div>
      </div>

      {/* Right: Live stats & theme toggle */}
      <div className="flex items-center gap-2.5">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white dark:bg-[#141622] border border-slate-200/80 dark:border-white/[0.08] text-xs font-medium text-slate-600 dark:text-slate-300 shadow-sm">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>{shopCount} Stores</span>
          <span className="text-slate-300 dark:text-slate-600">•</span>
          <span>{productCount} Items</span>
        </div>

        {/* Theme Switcher Button */}
        <button
          onClick={onToggleTheme}
          aria-label="Toggle Theme"
          className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-slate-200/80 dark:border-white/[0.08] bg-white dark:bg-[#141622] text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-white/[0.06] transition shadow-sm"
        >
          {isDark ? (
            <>
              <svg className="w-3.5 h-3.5 text-amber-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <circle cx="12" cy="12" r="4" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 2v2m0 16v2m10-10h-2M4 12H2m15.07-7.07l-1.41 1.41M6.34 17.66l-1.41 1.41m12.73 0l-1.41-1.41M6.34 6.34L4.93 4.93" />
              </svg>
              <span>Light Mode</span>
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
              <span>Dark Mode</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
}
