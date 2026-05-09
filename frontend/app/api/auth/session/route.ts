import { NextRequest, NextResponse } from "next/server";
import { getIronSession } from "iron-session";
import { cookies } from "next/headers";
import { sessionOptions, SessionData } from "@/lib/session";

function parseOperatorCredentials(): Map<string, string> {
  const raw = process.env.OPERATOR_CREDENTIALS || "";
  const map = new Map<string, string>();
  if (!raw) return map;
  for (const pair of raw.split(",")) {
    const trimmed = pair.trim();
    if (!trimmed) continue;
    const colonIndex = trimmed.indexOf(":");
    if (colonIndex === -1) continue;
    const username = trimmed.slice(0, colonIndex).trim();
    const password = trimmed.slice(colonIndex + 1).trim();
    if (username && password) {
      map.set(username, password);
    }
  }
  return map;
}

export async function GET() {
  const session = await getIronSession<SessionData>(
    await cookies(),
    sessionOptions
  );

  return NextResponse.json({
    isLoggedIn: session.isLoggedIn ?? false,
    userId: session.userId ?? "",
    organizationId: session.organizationId ?? "",
  });
}

export async function POST(request: NextRequest) {
  const session = await getIronSession<SessionData>(
    await cookies(),
    sessionOptions
  );

  try {
    const body = await request.json();
    const { username, password } = body;

    if (!username || typeof username !== "string" || !password || typeof password !== "string") {
      return NextResponse.json(
        { error: "Username and password are required" },
        { status: 400 }
      );
    }

    const credentials = parseOperatorCredentials();
    const expectedPassword = credentials.get(username);

    if (!expectedPassword || expectedPassword !== password) {
      return NextResponse.json(
        { error: "Invalid credentials" },
        { status: 401 }
      );
    }

    session.userId = username;
    session.isLoggedIn = true;
    session.organizationId = "default";
    await session.save();

    return NextResponse.json({ success: true }, { status: 200 });
  } catch {
    return NextResponse.json(
      { error: "Invalid request" },
      { status: 400 }
    );
  }
}

export async function DELETE() {
  const session = await getIronSession<SessionData>(
    await cookies(),
    sessionOptions
  );

  session.destroy();

  return NextResponse.json({ success: true }, { status: 200 });
}
