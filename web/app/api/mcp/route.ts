import { NextRequest, NextResponse } from 'next/server';
import {
  getShopSummaries,
  loadFixtureByUrl,
  searchProducts,
} from '@/lib/catalog';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { tool, arguments: args = {} } = body as {
      tool: string;
      arguments: Record<string, unknown>;
    };

    switch (tool) {
      case 'list_shops': {
        const shops = getShopSummaries();
        return NextResponse.json({ tool, result: shops });
      }

      case 'fetch_catalog': {
        const shop_url = args.shop_url as string;
        if (!shop_url) {
          return NextResponse.json(
            { error: 'shop_url is required' },
            { status: 400 }
          );
        }
        const shop = loadFixtureByUrl(shop_url);
        if (!shop) {
          return NextResponse.json(
            { error: `Shop not found: ${shop_url}` },
            { status: 404 }
          );
        }
        return NextResponse.json({ tool, result: shop });
      }

      case 'search_shop': {
        const shop_url = args.shop_url as string;
        const query = (args.query as string) ?? '';
        const max_price = args.max_price as number | undefined;
        const category = args.category as string | undefined;
        if (!shop_url) {
          return NextResponse.json(
            { error: 'shop_url is required' },
            { status: 400 }
          );
        }
        const result = searchProducts({ query, max_price, category, shop_url });
        return NextResponse.json({ tool, result });
      }

      case 'search_all_shops': {
        const query = (args.query as string) ?? '';
        const max_price = args.max_price as number | undefined;
        const category = args.category as string | undefined;
        const limit_per_shop = (args.limit_per_shop as number) ?? 20;
        const result = searchProducts({
          query,
          max_price,
          category,
          limit_per_shop,
        });
        return NextResponse.json({ tool, result });
      }

      default:
        return NextResponse.json(
          { error: `Unknown tool: ${tool}` },
          { status: 400 }
        );
    }
  } catch (err) {
    console.error('[/api/mcp]', err);
    return NextResponse.json({ error: 'MCP call failed' }, { status: 500 });
  }
}
