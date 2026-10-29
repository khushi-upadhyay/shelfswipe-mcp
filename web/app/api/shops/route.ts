import { NextResponse } from 'next/server';
import { getShopSummaries } from '@/lib/catalog';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const shops = getShopSummaries();
    return NextResponse.json(shops);
  } catch (err) {
    console.error('[/api/shops]', err);
    return NextResponse.json({ error: 'Failed to load shops' }, { status: 500 });
  }
}
