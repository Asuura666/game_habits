import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Log to console (visible in docker logs)
    console.error(JSON.stringify({
      level: 'error',
      source: 'frontend',
      timestamp: body.timestamp || new Date().toISOString(),
      error: body.error,
      stack: body.stack,
      componentStack: body.componentStack,
      url: body.url,
      userAgent: body.userAgent,
    }));
    
    return NextResponse.json({ success: true });
  } catch (e) {
    return NextResponse.json({ success: false }, { status: 500 });
  }
}
