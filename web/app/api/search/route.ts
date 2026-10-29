import { NextRequest, NextResponse } from 'next/server';
import { searchProducts } from '@/lib/catalog';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('query') ?? '';
    const max_price_raw = searchParams.get('max_price');
    const category = searchParams.get('category') ?? '';
    const shop_url = searchParams.get('shop_url') ?? '';
    const in_stock_only = searchParams.get('in_stock_only') === 'true';

    const max_price =
      max_price_raw && !isNaN(Number(max_price_raw))
        ? Number(max_price_raw)
        : undefined;

    const result = searchProducts({
      query,
      max_price,
      category: category || undefined,
      shop_url: shop_url || undefined,
      in_stock_only,
    });

    return NextResponse.json(result);
  } catch (err) {
    console.error('[/api/search]', err);
    return NextResponse.json({ error: 'Search failed' }, { status: 500 });
  }
}
