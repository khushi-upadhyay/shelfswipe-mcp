'use client';

import { useState } from 'react';

interface McpTool {
  name: string;
  label: string;
  args: Record<string, unknown>;
  description: string;
}

const TOOLS: McpTool[] = [
  {
    name: 'list_shops',
    label: 'list_shops()',
    args: {},
    description: 'Discover all registered dummy merchant storefronts',
  },
  {
    name: 'fetch_catalog',
    label: 'fetch_catalog(shop_url)',
    args: { shop_url: 'shelfswipe://fixtures/artisan_pottery' },
    description: 'Retrieve complete product catalog for one shop',
  },
  {
    name: 'search_shop',
    label: 'search_shop(shop_url, query)',
    args: { shop_url: 'shelfswipe://fixtures/tech_gadgets', query: 'keyboard' },
    description: 'Search within a specific shop catalog with query filters',
  },
  {
    name: 'search_all_shops',
    label: 'search_all_shops(query)',
    args: { query: 'gift', limit_per_shop: 4 },
    description: 'Cross-shop search across all 5 registered merchant stores',
  },
];

export default function McpPanel() {
  const [activeTool, setActiveTool] = useState<string>('list_shops');
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const callTool = async (tool: McpTool) => {
    setLoading(true);
    setActiveTool(tool.name);
    setResult(null);

    try {
      const res = await fetch('/api/mcp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool: tool.name, arguments: tool.args }),
      });
      const data = await res.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setResult(JSON.stringify({ error: String(e) }, null, 2));
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result) {
      navigator.clipboard.writeText(result);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-white dark:bg-[#141622] rounded-[28px] border border-slate-200/80 dark:border-white/[0.08] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.03)] space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="font-bold text-slate-900 dark:text-slate-100 text-lg">
              MCP Agent Protocol Console
            </h2>
            <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
              Live Bridge
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Simulate the exact tool calls an LLM agent executes to onboard products to PayTrace
          </p>
        </div>

        {/* Copy button */}
        {result && (
          <button
            onClick={handleCopy}
            className="self-start sm:self-center text-xs font-semibold px-3 py-1.5 rounded-xl border border-slate-200 dark:border-white/[0.1] bg-slate-50 dark:bg-white/[0.04] text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/[0.08] transition"
          >
            {copied ? 'Copied' : 'Copy JSON'}
          </button>
        )}
      </div>

      {/* Tool Buttons */}
      <div className="flex flex-wrap gap-2">
        {TOOLS.map((tool) => {
          const isSelected = activeTool === tool.name;
          return (
            <button
              key={tool.name}
              onClick={() => callTool(tool)}
              disabled={loading}
              className={`px-3.5 py-2 rounded-xl text-xs font-mono font-medium transition-all ${
                isSelected
                  ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-sm'
                  : 'bg-slate-100 dark:bg-white/[0.06] text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-white/[0.1]'
              } disabled:opacity-50`}
            >
              {tool.label}
            </button>
          );
        })}
      </div>

      {/* Response Box */}
      <div className="rounded-2xl bg-[#090a10] border border-white/[0.08] p-4 text-xs font-mono text-emerald-400 overflow-auto max-h-[360px] leading-relaxed">
        {loading ? (
          <div className="text-slate-400 flex items-center gap-2 py-6 justify-center">
            <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Calling {activeTool}...
          </div>
        ) : result ? (
          <pre>{result}</pre>
        ) : (
          <div className="text-slate-500 py-6 text-center">
            Click any tool above to execute and inspect live MCP response
          </div>
        )}
      </div>
    </div>
  );
}
