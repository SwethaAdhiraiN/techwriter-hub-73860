from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from slugify import slugify
from .. import database, models, schemas, auth_utils

router = APIRouter(prefix="/posts", tags=["posts"])

# PUBLIC_INTERFACE
@router.post("/", response_model=schemas.PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: schemas.PostCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user=Depends(auth_utils.get_current_user),
):
    """Create a new blog post (markdown supported)."""
    new_post = models.Post(
        title=post.title,
        slug=slugify(post.title + "-" + current_user.username),
        content=post.content,
        author_id=current_user.id,
        tags=post.tags or "",
        published=True,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post

# PUBLIC_INTERFACE
@router.get("/", response_model=List[schemas.PostRead])
async def read_all_posts(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(database.get_db)):
    """Get all posts, paginated."""
    q = await db.execute(select(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit))
    return q.scalars().all()

# PUBLIC_INTERFACE
@router.get("/{slug}", response_model=schemas.PostRead)
async def read_post(slug: str, db: AsyncSession = Depends(database.get_db)):
    """Get a single post by slug."""
    q = await db.execute(select(models.Post).where(models.Post.slug == slug))
    post = q.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# PUBLIC_INTERFACE
@router.put("/{slug}", response_model=schemas.PostRead)
async def update_post(
    slug: str,
    updated: schemas.PostCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user=Depends(auth_utils.get_current_user),
):
    """Update a post (author only)."""
    q = await db.execute(select(models.Post).where(models.Post.slug == slug))
    post = q.scalars().first()
    if not post or post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update.")
    post.title = updated.title
    post.content = updated.content
    post.tags = updated.tags or ""
    await db.commit()
    await db.refresh(post)
    return post

# PUBLIC_INTERFACE
@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    slug: str,
    db: AsyncSession = Depends(database.get_db),
    current_user=Depends(auth_utils.get_current_user),
):
    """Delete a post (author only)."""
    q = await db.execute(select(models.Post).where(models.Post.slug == slug))
    post = q.scalars().first()
    if not post or post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete.")
    await db.delete(post)
    await db.commit()
    return None
