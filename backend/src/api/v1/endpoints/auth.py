# backend/src/api/v1/endpoints/auth.py
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Dict

from backend.src.db.postgresql import get_session
from backend.src.db.models.user import User, UserCreate, UserRead
from backend.src.db.models.oauth_account import OAuthAccount
from backend.src.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from backend.src.core.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def register_user(
    user_in: UserCreate, session: AsyncSession = Depends(get_session)
):
    # ... (code for registration from previous step, it's correct)
    # ... (ensure it returns the created user for immediate login)
    existing_user_result = await session.execute(
        select(User).where(User.email == user_in.email)
    )
    if existing_user_result.one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    if not user_in.password:
        raise HTTPException(
            status_code=400, detail="Password is required for email registration"
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = User.model_validate(user_in, update={"hashed_password": hashed_password})
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.post("/token")
async def login_for_access_token(
    # ... (code for token login, it's correct)
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    # ...
    user_result = await session.execute(
        select(User).where(User.email == form_data.username)
    )
    user = user_result.scalar_one_or_none()
    if (
        not user
        or not user.hashed_password
        or not verify_password(form_data.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/token/refresh")
async def refresh_access_token(
    refresh_token: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    user_id = verify_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_oauth_user_profile(provider: str, token: str) -> Dict:
    """Fetch user profile from an OAuth provider."""
    profile_urls = {
        "google": "https://www.googleapis.com/oauth2/v3/userinfo",
        "github": "https://api.github.com/user",
    }
    url = profile_urls.get(provider)
    if not url:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        profile = response.json()

        if provider == "google":
            return {
                "email": profile["email"],
                "provider_user_id": profile["sub"],
                "full_name": profile.get("name"),
                "avatar_url": profile.get("picture"),
            }
        elif provider == "github":
            return {
                "email": profile["email"],  # May be null, handle this
                "provider_user_id": str(profile["id"]),
                "full_name": profile.get("name"),
                "avatar_url": profile.get("avatar_url"),
            }
    return {}


@router.post("/oauth/{provider}")
async def oauth_login(
    provider: str,
    token: str = Body(..., embed=True),
    session: AsyncSession = Depends(get_session),
):
    """
    This endpoint is called by NextAuth after it gets a token from the provider.
    It finds or creates a user, links the OAuth account, and returns our own JWTs.
    """
    try:
        profile = await get_oauth_user_profile(provider, token)
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=400, detail="Invalid OAuth token")

    if not profile or not profile.get("email"):
        raise HTTPException(
            status_code=400, detail="Could not retrieve email from provider"
        )

    # Find or create user logic (Upsert)
    user_result = await session.execute(
        select(User).where(User.email == profile["email"])
    )
    user = user_result.scalar_one_or_none()

    if not user:
        user = User(
            email=profile["email"],
            full_name=profile.get("full_name"),
            avatar_url=profile.get("avatar_url"),
        )
        session.add(user)
    else:  # User exists, update details if needed
        user.full_name = user.full_name or profile.get("full_name")
        user.avatar_url = user.avatar_url or profile.get("avatar_url")

    # Check if this specific OAuth account is already linked
    oauth_account_result = await session.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == profile["provider_user_id"],
        )
    )
    if not oauth_account_result.scalar_one_or_none():
        oauth_account = OAuthAccount(
            provider=provider,
            provider_user_id=profile["provider_user_id"],
            access_token=token,
            user=user,
        )
        session.add(oauth_account)

    await session.commit()
    await session.refresh(user)

    # Issue our own tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
