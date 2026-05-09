# Auth Gateway Pattern

## Overview

Every protected frontend-to-backend request follows this flow:

```
Browser → Next.js Route Handler (proxy) → FastAPI Backend
              ↓                                  ↓
         iron-session cookie              X-User-Id header
         (decrypt, extract user)          (validated via dependency)
```

The frontend **never** communicates directly with the backend. All requests pass through Next.js API Route Handlers that act as an authenticated proxy.

## Architecture Layers

### 1. Session Layer (`frontend/lib/session/`)

- Uses `iron-session` v8 with `getIronSession`
- Cookie: `synkra_session` (httpOnly, secure in production, sameSite=lax)
- Session data: `{ userId: string, isLoggedIn: boolean }`
- Secret: `SESSION_SECRET` env var (32+ characters)

### 2. Gateway Layer (`frontend/lib/gateway/`)

Provides two main functions:

- `authenticatedGateway(request)` — requires valid session, forwards `X-User-Id` to backend
- `publicGateway(request)` — no auth required, no user context forwarded

Helper functions:
- `withAuth(handler)` — wraps a route handler with authentication
- `proxyToBackend(request, authContext, options)` — low-level proxy function

### 3. Backend Auth Layer (`backend/application/security/auth.py`)

- `CurrentUser` dependency: `Annotated[AuthenticatedUser, Depends(require_authenticated_user)]`
- Reads `X-User-Id` from request headers
- Raises 401 if header is missing or empty

## How to Use

### Frontend: Create a protected route

All protected API calls automatically go through the catch-all gateway at `frontend/app/api/[...path]/route.ts`. No additional code needed for simple proxy routes.

For custom logic:

```typescript
// frontend/app/api/custom/route.ts
import { withAuth } from "@/lib/gateway";

export const POST = withAuth(async (request, authContext) => {
  // authContext.userId is available here
  // custom logic...
});
```

### Backend: Create a protected endpoint

```python
# backend/api/routes/example.py
from fastapi import APIRouter
from application.security.auth import CurrentUser

router = APIRouter(prefix="/example", tags=["example"])

@router.get("/")
async def list_items(user: CurrentUser) -> dict:
    # user.user_id is the authenticated operator
    return {"items": [], "operator": user.user_id}
```

Then register the router in `backend/main.py`:

```python
from api.routes.example import router as example_router
app.include_router(example_router)
```

### Backend: Create a public endpoint

```python
@router.get("/public-data")
async def public_endpoint() -> dict:
    return {"data": "no auth needed"}
```

Simply do not use the `CurrentUser` dependency.

## Error Handling

All error responses follow a consistent format and never leak internals:

```json
{"error": "Human-readable message"}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid input) |
| 401 | Authentication required |
| 403 | Access denied |
| 500 | Internal server error (no details exposed) |
| 503 | Backend service unavailable |

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `SESSION_SECRET` | Frontend + Backend | 32+ char secret for iron-session encryption |
| `BACKEND_URL` | Frontend | Backend service URL (default: `http://localhost:8000`) |
| `ALLOWED_ORIGINS` | Backend | CORS allowed origins |

## Login/Logout

- **Login**: `POST /api/auth/session` with `{ "userId": "..." }`
- **Logout**: `DELETE /api/auth/session`

## Security Guarantees

1. Frontend never has access to tokens — session is encrypted in httpOnly cookie
2. Backend never sees cookies — receives user identity via internal `X-User-Id` header
3. Unauthenticated requests to protected routes return 401 with no implementation details
4. All backend errors are caught and sanitized before reaching the frontend
5. Cookie is secure-only in production mode
