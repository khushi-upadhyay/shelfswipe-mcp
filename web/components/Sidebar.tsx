'use client';

interface SidebarProps {
  currentTab: 'catalog' | 'tools';
  onTabChange: (tab: 'catalog' | 'tools') => void;
  isDark: boolean;
  onToggleTheme: () => void;
}

export default function Sidebar({ currentTab, onTabChange, isDark, onToggleTheme }: SidebarProps) {
  return (
    <aside className="w-16 md:w-20 shrink-0 flex flex-col items-center py-6 border-r border-slate-200/70 dark:border-white/[0.08] bg-white/70 dark:bg-[#0f1016]/80 backdrop-blur-xl justify-between">
      {/* Top action buttons */}
      <div className="flex flex-col items-center gap-6">
        {/* Plus / Brand button */}
        <button
          onClick={() => onTabChange('catalog')}
          aria-label="New session"
          className="w-10 h-10 rounded-full bg-slate-100 dark:bg-white/[0.08] hover:bg-slate-200 dark:hover:bg-white/[0.15] text-slate-800 dark:text-slate-100 flex items-center justify-center transition shadow-sm"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
        </button>

        {/* Nav Items */}
        <nav className="flex flex-col items-center gap-2">
          {/* Home / Catalog */}
          <button
            onClick={() => onTabChange('catalog')}
            aria-label="Storefronts & Catalog"
            title="Merchant Catalog"
            className={`w-10 h-10 rounded-2xl flex items-center justify-center transition ${
              currentTab === 'catalog'
                ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-md'
                : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/[0.06]'
            }`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
          </button>

          {/* Tools / MCP Terminal */}
          <button
            onClick={() => onTabChange('tools')}
            aria-label="MCP Agent Tools"
            title="MCP Tool Console"
            className={`w-10 h-10 rounded-2xl flex items-center justify-center transition ${
              currentTab === 'tools'
                ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-md'
                : 'text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/[0.06]'
            }`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </button>
        </nav>
      </div>

      {/* Bottom utilities */}
      <div className="flex flex-col items-center gap-4">
        {/* Real Theme Switcher Button */}
        <button
          onClick={onToggleTheme}
          aria-label="Toggle Theme"
          title={isDark ? "Switch to Light Theme" : "Switch to Dark Theme"}
          className="w-10 h-10 rounded-2xl border border-slate-200 dark:border-white/[0.1] bg-slate-50 dark:bg-white/[0.06] text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/[0.12] flex items-center justify-center transition shadow-sm"
        >
          {isDark ? (
            <svg className="w-4 h-4 text-amber-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <circle cx="12" cy="12" r="4" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 2v2m0 16v2m10-10h-2M4 12H2m15.07-7.07l-1.41 1.41M6.34 17.66l-1.41 1.41m12.73 0l-1.41-1.41M6.34 6.34L4.93 4.93" />
            </svg>
          ) : (
            <svg className="w-4 h-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          )}
        </button>

        {/* Minimal User Avatar */}
        <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-rose-400 p-[1.5px] shadow-sm">
          <div className="w-full h-full rounded-full bg-slate-900 text-white font-semibold text-xs flex items-center justify-center">
            SS
          </div>
        </div>
      </div>
    </aside>
  );
}

