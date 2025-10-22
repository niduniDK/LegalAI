// src/app/api/ask/route.js
import { NextResponse } from 'next/server';

export async function POST(req) {
  const body = await req.json();

  const backendRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const data = await backendRes.json();
  return NextResponse.json(data);
}
