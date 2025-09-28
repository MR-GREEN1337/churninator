from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from ..dependencies import get_current_user
from backend.src.db.postgresql import get_session
from backend.src.db.models.user import User, UserRead, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user.
    """
    return current_user


@router.put("/me", response_model=UserRead)
async def update_user_me(
    *,
    session: AsyncSession = Depends(get_session),
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
):
    """
    Update the current authenticated user's profile.
    """
    # Get the user object from the database
    db_user = await session.get(User, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the update data from the request
    update_data = user_update.model_dump(exclude_unset=True)

    # Update the user object's attributes
    for key, value in update_data.items():
        setattr(db_user, key, value)

    # Add, commit, and refresh the session
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user
