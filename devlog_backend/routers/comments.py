from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import database, models, schemas, auth_utils

router = APIRouter(prefix="/comments", tags=["comments"])

# PUBLIC_INTERFACE
@router.post("/{post_id}", response_model=schemas.CommentRead)
async def add_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user=Depends(auth_utils.get_current_user),
):
    """Add a comment to a post."""
    new_comment = models.Comment(
        content=comment.content,
        post_id=post_id,
        author_id=current_user.id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    # Real-time notification could be triggered here (see /realtime/ws)
    return new_comment

# PUBLIC_INTERFACE
@router.get("/post/{post_id}", response_model=List[schemas.CommentRead])
async def get_comments_for_post(
    post_id: int,
    db: AsyncSession = Depends(database.get_db),
):
    """List comments for a post."""
    q = await db.execute(select(models.Comment).where(models.Comment.post_id == post_id).order_by(models.Comment.created_at.asc()))
    return q.scalars().all()
