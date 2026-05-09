import { getSession, SessionData } from "@/lib/session";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";
const INTERNAL_TOKEN = process.env.INTERNAL_TOKEN || "";

interface GatewayOptions {
  requireAuth?: boolean;
}

interface AuthenticatedContext {
  userId: string;
  organizationId: string;
}

function createSafeErrorResponse(message: string, status: number): NextResponse {
  return NextResponse.json({ error: message }, { status });
}

export async function extractAuthenticatedUser(
  session: SessionData | Awaited<ReturnType<typeof getSession>>
): Promise<AuthenticatedContext | null> {
  if (!session.isLoggedIn || !session.userId) {
    return null;
  }
  return {
    userId: session.userId,
    organizationId: (session as unknown as SessionData).organizationId || "default",
  };
}

export async function withAuth(
  handler: (
    request: NextRequest,
    context: AuthenticatedContext
  ) => Promise<NextResponse>
) {
  return async (request: NextRequest): Promise<NextResponse> => {
    const session = await getSession();
    const authContext = await extractAuthenticatedUser(session as unknown as SessionData);

    if (!authContext) {
      return createSafeErrorResponse("Authentication required", 401);
    }

    return handler(request, authContext);
  };
}

export async function proxyToBackend(
  request: NextRequest,
  authContext: AuthenticatedContext | null,
  options: GatewayOptions = {}
): Promise<NextResponse> {
  const { requireAuth = true } = options;

  if (requireAuth && !authContext) {
    return createSafeErrorResponse("Authentication required", 401);
  }

  const path = request.nextUrl.pathname.replace(/^\/api/, "");
  const searchParams = request.nextUrl.search;
  const backendUrl = `${BACKEND_URL}${path}${searchParams}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (INTERNAL_TOKEN) {
    headers["X-Internal-Token"] = INTERNAL_TOKEN;
  }

  if (authContext) {
    headers["X-User-Id"] = authContext.userId;
    headers["X-Organization-Id"] = authContext.organizationId;
  }

  try {
    let body: string | undefined;
    if (request.method !== "GET" && request.method !== "HEAD") {
      const rawBody = await request.text();
      body = rawBody || undefined;
    }

    const response = await fetch(backendUrl, {
      method: request.method,
      headers,
      body,
    });

    const contentType = response.headers.get("content-type");
    if (contentType?.includes("application/json")) {
      const data = await response.json();
      return NextResponse.json(data, { status: response.status });
    }

    return new NextResponse(response.body, {
      status: response.status,
      statusText: response.statusText,
    });
  } catch {
    return createSafeErrorResponse("Service unavailable", 503);
  }
}

export async function authenticatedGateway(
  request: NextRequest
): Promise<NextResponse> {
  const session = await getSession();
  const sessionData = session as unknown as SessionData;
  const authContext = await extractAuthenticatedUser(sessionData);

  return proxyToBackend(request, authContext, { requireAuth: true });
}

export async function publicGateway(
  request: NextRequest
): Promise<NextResponse> {
  return proxyToBackend(request, null, { requireAuth: false });
}
