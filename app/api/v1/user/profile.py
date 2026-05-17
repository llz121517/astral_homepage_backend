# app/api/v1/user/profile.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/user", tags=["user"])

@router.get("/profile")
async def get_user_profile():
    """
    返回用户信息
    """
    return {
        "name": "example",
        "bio": "This is an example user bio.",
        "avatar_url": "/static/user/avatar.webp"
    }