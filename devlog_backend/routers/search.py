from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import database, models, schemas

router = APIRouter(prefix="/search", tags=["search"])

# PUBLIC_INTERFACE
@router.post("/", response_model=list[schemas.PostRead])
async def search_posts(
    query: schemas.SearchQuery,
    db: AsyncSession = Depends(database.get_db),
):
    """Search posts (by query string, author, tags)."""
    q = select(models.Post)
    if query.query:
        q = q.where(models.Post.title.ilike(f"%{query.query}%") | models.Post.content.ilike(f"%{query.query}%"))
    if query.tags:
        q = q.where(models.Post.tags.ilike(f"%{query.tags}%"))
    if query.author:
        q = q.join(models.User).where(models.User.username == query.author)
    result = await db.execute(q.order_by(models.Post.created_at.desc()))
    posts = result.scalars().all()
    return posts
