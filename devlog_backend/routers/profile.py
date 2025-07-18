from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import database, models, schemas, auth_utils

router = APIRouter(prefix="/profile", tags=["profile"])

# PUBLIC_INTERFACE
@router.get("/{username}", response_model=schemas.UserRead)
async def get_user_profile(username: str, db: AsyncSession = Depends(database.get_db)):
    """Get profile for user by username."""
    q = await db.execute(select(models.User).where(models.User.username == username))
    user = q.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# PUBLIC_INTERFACE
@router.put("/", response_model=schemas.UserRead)
async def update_profile(
    update: schemas.ProfileUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user=Depends(auth_utils.get_current_user),
):
    """Update bio or avatar for current user."""
    if update.bio is not None:
        current_user.bio = update.bio
    if update.avatar_url is not None:
        current_user.avatar_url = update.avatar_url
    await db.commit()
    await db.refresh(current_user)
    return current_user
