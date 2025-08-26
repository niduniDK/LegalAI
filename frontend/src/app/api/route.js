// src/app/api/ask/route.js
import { NextResponse } from "next/server";

export async function POST(req) {
  const body = await req.json();

  const backendRes = await fetch("http://localhost:8000/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await backendRes.json();
  return NextResponse.json(data);
}
