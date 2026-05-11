import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    service: 'nextjs-app',
    timestamp: new Date().toISOString()
  });
}
