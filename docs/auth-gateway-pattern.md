# Auth Gateway Pattern

## Overview

Every protected frontend-to-backend request follows this flow:

```
Browser → Next.js Route Handler (proxy) → FastAPI Backend
              ↓                                  ↓
         iron-session cookie              X-User-Id header
         (decrypt, extract user)          X-Organization-Id header
                                           X-Internal-Token header
                                           (validated via dependency)
```

The frontend **never** communicates directly with the backend. All requests pass through Next.js API Route Handlers that act as an authenticated proxy. The backend validates an internal shared secret (`X-Internal-Token`) to ensure only the Next.js gateway can reach protected endpoints.

## Architecture Layers

### 1. Session Layer (`frontend/lib/session/`)

- Uses `iron-session` v8 with `getIronSession`
- Cookie: `synkra_session` (httpOnly, secure in production, sameSite=lax)
- Session data: `{ userId: string, isLoggedIn: boolean, organizationId: string }`
- Secret: `SESSION_SECRET` env var (32+ characters)

### 2. Gateway Layer (`frontend/lib/gateway/`)

Provides two main functions:

- `authenticatedGateway(request)` — requires valid session, forwards `X-User-Id`, `X-Organization-Id`, and `X-Internal-Token` to backend
- `publicGateway(request)` — no auth required, no user context forwarded

Helper functions:
- `withAuth(handler)` — wraps a route handler with authentication
- `proxyToBackend(request, authContext, options)` — low-level proxy function

The `AuthenticatedContext` carries both `userId` and `organizationId` extracted from the session.

### 3. Backend Auth Layer (`backend/application/security/auth.py`)

- `CurrentUser` dependency: `Annotated[AuthenticatedUser, Depends(require_authenticated_user)]`
- Validates `X-Internal-Token` against `BACKEND_INTERNAL_TOKEN` env var
- Reads `X-User-Id` and `X-Organization-Id` from request headers
- Raises 401 if token is missing, incorrect, or if identity headers are absent/empty

### 4. Trust Boundary

The `X-Internal-Token` mechanism ensures that only the Next.js gateway (which holds encrypted sessions) can call backend endpoints. Even if a client discovers the backend URL directly, requests without the correct internal token are rejected with 401.

```
Browser ──(cookie)──> Next.js Gateway ──(X-Internal-Token + X-User-Id + X-Organization-Id)──> FastAPI Backend
                         │                                                                    │
                    decrypts session                                                   validates token
                    extracts userId                                                    validates headers
                    extracts orgId                                                     returns user context
```

## Login Flow

### Login: `POST /api/auth/session`

```json
{ "username": "operator1", "password": "secret123" }
```

- Validates credentials against `OPERATOR_CREDENTIALS` env var
- Format: `user1:pass1,user2:pass2`
- On success, sets session: `{ userId: username, isLoggedIn: true, organizationId: "default" }`

### Check session: `GET /api/auth/session`

Returns current session state:
```json
{ "isLoggedIn": true, "userId": "operator1", "organizationId": "default" }
```

### Logout: `DELETE /api/auth/session`

Destroys the session cookie.

## How to Use

### Frontend: Create a protected route

All protected API calls automatically go through the catch-all gateway at `frontend/app/api/[...path]/route.ts`. No additional code needed for simple proxy routes.

For custom logic:

```typescript
// frontend/app/api/custom/route.ts
import { withAuth } from "@/lib/gateway";

export const POST = withAuth(async (request, authContext) => {
  // authContext.userId is available here
  // authContext.organizationId is available here
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
    # user.organization_id is the organization context
    return {"items": [], "operator": user.user_id, "org": user.organization_id}
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
| 401 | Authentication required or invalid internal token |
| 403 | Access denied |
| 500 | Internal server error (no details exposed) |
| 503 | Backend service unavailable |

## Environment Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `SESSION_SECRET` | Frontend | 32+ char secret for iron-session encryption |
| `BACKEND_URL` | Frontend | Backend service URL (default: `http://localhost:8000`) |
| `INTERNAL_TOKEN` | Frontend | Shared secret sent as `X-Internal-Token` to backend |
| `BACKEND_INTERNAL_TOKEN` | Backend | Expected value for `X-Internal-Token` (must match `INTERNAL_TOKEN`) |
| `OPERATOR_CREDENTIALS` | Frontend | Comma-separated `user:pass` pairs for operator login |
| `ALLOWED_ORIGINS` | Backend | CORS allowed origins |

## Security Guarantees

1. Frontend never has access to tokens — session is encrypted in httpOnly cookie
2. Backend never sees cookies — receives user identity via internal headers
3. Backend rejects requests without valid `X-Internal-Token` — prevents direct backend access
4. Login requires valid credentials from `OPERATOR_CREDENTIALS` — no arbitrary user creation
5. Organization context propagates through the entire stack
6. Unauthenticated requests to protected routes return 401 with no implementation details
7. All backend errors are caught and sanitized before reaching the frontend
8. Cookie is secure-only in production mode

## Organization Context

Every authenticated request carries `X-Organization-Id` from the session to the backend. The `AuthenticatedUser` object exposes `organization_id` for downstream use in data isolation and authorization decisions. Currently set to `"default"` upon login; future stories will integrate with an organization directory.
