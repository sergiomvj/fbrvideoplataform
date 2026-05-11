from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/session")
async def login(request: dict):
    username = request.get("username", "")
    password = request.get("password", "")

    if username == "admin" and password == "admin":
        return {
            "user_id": "admin",
            "organization_id": "org-1",
            "token": "session-token-123"
        }

    return {"error": "Invalid credentials"}, 401