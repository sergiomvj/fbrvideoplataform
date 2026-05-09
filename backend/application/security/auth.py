import os

from fastapi import Depends, Request
from typing import Annotated

from application.errors import create_unauthorized_response


class AuthenticatedUser:
    def __init__(self, user_id: str, organization_id: str) -> None:
        self.user_id = user_id
        self.organization_id = organization_id


async def require_authenticated_user(request: Request) -> AuthenticatedUser:
    internal_token = request.headers.get("X-Internal-Token")
    expected_token = os.environ.get("BACKEND_INTERNAL_TOKEN", "")

    if not expected_token or internal_token != expected_token:
        raise create_unauthorized_response()

    user_id = request.headers.get("X-User-Id")
    organization_id = request.headers.get("X-Organization-Id")

    if not user_id or not user_id.strip():
        raise create_unauthorized_response()

    if not organization_id or not organization_id.strip():
        raise create_unauthorized_response()

    return AuthenticatedUser(
        user_id=user_id.strip(),
        organization_id=organization_id.strip(),
    )


CurrentUser = Annotated[AuthenticatedUser, Depends(require_authenticated_user)]
