from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from .. import database, models, schemas, auth_utils

router = APIRouter(prefix="/auth", tags=["auth"])

# PUBLIC_INTERFACE
@router.post('/register', response_model=schemas.UserRead)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    """Register a new user."""
    db_user = await auth_utils.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth_utils.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

# PUBLIC_INTERFACE
@router.post('/token', response_model=schemas.Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(database.get_db)):
    """Authenticate user (login) and return JWT."""
    user = await auth_utils.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth_utils.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# PUBLIC_INTERFACE
@router.get('/me', response_model=schemas.UserRead)
async def read_current_user(current_user=Depends(auth_utils.get_current_user)):
    """Get details of the currently authenticated user."""
    return current_user
