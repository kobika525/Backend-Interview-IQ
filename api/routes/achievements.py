from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.platform import Achievement,UserAchievement
from app.utils.responses import ok
router=APIRouter(prefix='/achievements',tags=['Achievements'])
@router.get('')
def list_items(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    achievements=db.scalars(select(Achievement)).all()
    earned={ua.achievement_id:ua.awarded_at for ua in db.scalars(select(UserAchievement).where(UserAchievement.user_id==user.id)).all()}
    return ok([{'id':a.id,'code':a.code,'title':a.title,'description':a.description,'earned':a.id in earned,'awarded_at':earned[a.id].isoformat() if a.id in earned else None} for a in achievements],'Records retrieved successfully')
