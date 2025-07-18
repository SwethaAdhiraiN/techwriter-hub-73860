from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .. import database, models, schemas, auth_utils

router = APIRouter(prefix="/reactions", tags=["reactions"])

# PUBLIC_INTERFACE
@router.post("/{post_id}", response_model=schemas.ReactionRead)
async def react_to_post(
    post_id: int,
    reaction: schemas.ReactionCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user=Depends(auth_utils.get_current_user),
):
    """React (like/heart/etc) to a post. Only one reaction per user per post."""
    existing = await db.execute(select(models.Reaction).where(models.Reaction.post_id==post_id, models.Reaction.user_id==current_user.id))
    existing_reaction = existing.scalars().first()
    if existing_reaction:
        raise HTTPException(status_code=400, detail="Already reacted.")
    new_reaction = models.Reaction(user_id=current_user.id, post_id=post_id, type=reaction.type)
    db.add(new_reaction)
    await db.commit()
    await db.refresh(new_reaction)
    return new_reaction

# PUBLIC_INTERFACE
@router.delete("/{post_id}", status_code=204)
async def remove_reaction(
    post_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user=Depends(auth_utils.get_current_user),
):
    """Remove your reaction from a post."""
    existing = await db.execute(select(models.Reaction).where(models.Reaction.post_id==post_id, models.Reaction.user_id==current_user.id))
    reaction = existing.scalars().first()
    if not reaction:
        raise HTTPException(status_code=404, detail="No reaction to remove.")
    await db.delete(reaction)
    await db.commit()

# PUBLIC_INTERFACE
@router.get("/post/{post_id}")
async def get_reaction_summary(post_id: int, db: AsyncSession = Depends(database.get_db)):
    """Get all reactions for a post."""
    q = await db.execute(select(models.Reaction).where(models.Reaction.post_id==post_id))
    reactions = q.scalars().all()
    summary = {}
    for r in reactions:
        summary[r.type] = summary.get(r.type, 0) + 1
    return summary
