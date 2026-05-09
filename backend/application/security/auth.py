from fastapi import Depends, Request
from typing import Annotated


class AuthenticatedUser:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id


async def require_authenticated_user(request: Request) -> AuthenticatedUser:
    user_id = request.headers.get("X-User-Id")

    if not user_id or not user_id.strip():
        from application.errors import create_unauthorized_response

        raise create_unauthorized_response()

    return AuthenticatedUser(user_id=user_id.strip())


CurrentUser = Annotated[AuthenticatedUser, Depends(require_authenticated_user)]
