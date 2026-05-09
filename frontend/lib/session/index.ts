import { getIronSession } from "iron-session";
import { cookies } from "next/headers";

export interface SessionData {
  userId: string;
  isLoggedIn: boolean;
}

const COOKIE_NAME = "synkra_session";

function getSessionSecret(): string {
  const secret = process.env.SESSION_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error(
      "SESSION_SECRET must be set in environment variables with at least 32 characters"
    );
  }
  return secret;
}

export const sessionOptions = {
  get password() {
    return getSessionSecret();
  },
  cookieName: COOKIE_NAME,
  cookieOptions: {
    secure: process.env.NODE_ENV === "production",
    httpOnly: true,
    sameSite: "lax" as const,
    maxAge: 60 * 60 * 24,
    path: "/",
  },
};

export async function getSession() {
  const session = await getIronSession<SessionData>(
    await cookies(),
    sessionOptions
  );
  return session;
}

export function createEmptySession(): SessionData {
  return {
    userId: "",
    isLoggedIn: false,
  };
}
