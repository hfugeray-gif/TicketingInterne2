from fastapi import APIRouter, Header

from app.schemas.me import MeResponse

router = APIRouter()


@router.get("/me", response_model=MeResponse)
def get_me(
    x_demo_user: str | None = Header(default=None),
    x_demo_role: str | None = Header(default=None),
):
    username = x_demo_user or "demo_user"
    role = x_demo_role or "Utilisateur"

    return MeResponse(
        username=username,
        email=f"{username}@beam.local",
        role=role,
        authenticated=True,
    )