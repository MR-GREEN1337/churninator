# backend/src/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.src.db.postgresql import get_session
from backend.src.db.models.user import User, UserCreate, UserRead
from backend.src.core.security import get_password_hash

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def create_user(
    *, session: AsyncSession = Depends(get_session), user_in: UserCreate
):
    """
    Create a new user. Basic public endpoint for signup.
    """
    # Check if user already exists
    existing_user = await session.exec(select(User).where(User.email == user_in.email))
    if existing_user.one_or_none():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    hashed_password = get_password_hash(user_in.password)
    db_user = User.model_validate(user_in, update={"hashed_password": hashed_password})
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.get("/me", response_model=UserRead)
async def read_users_me(
    session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_active_user) # This is what we'll use later
):
    """
    Get the current user.
    """
    # FOR NOW: We'll mock this by fetching the first user in the DB.
    # This allows us to build the frontend without implementing auth yet.
    user = await session.exec(select(User))
    current_user = user.first()
    if not current_user:
        raise HTTPException(status_code=404, detail="No users found to mock 'me'")
    return current_user
