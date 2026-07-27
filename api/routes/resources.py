from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.resource import LearningResource,UserResourceProgress
from app.core.exceptions import AppError
from app.utils.responses import ok
router=APIRouter(prefix='/resources',tags=['Resources'])
@router.get('')
def list_items(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    resources=db.scalars(select(LearningResource).where(LearningResource.is_active==True)).all()
    progress={p.resource_id:p for p in db.scalars(select(UserResourceProgress).where(UserResourceProgress.user_id==user.id)).all()}
    return ok([{'id':r.id,'title':r.title,'description':r.description,'resource_type':r.resource_type,'url':r.url,'premium_only':r.premium_only,'completed':bool(progress.get(r.id) and progress[r.id].completed_at),'bookmarked':bool(progress.get(r.id) and progress[r.id].bookmarked)} for r in resources],'Records retrieved successfully')
@router.post('/{resource_id}/complete')
def mark_complete(resource_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    from datetime import datetime
    r=db.get(LearningResource,resource_id)
    if not r: raise AppError('Resource not found',404,'NOT_FOUND')
    p=db.get(UserResourceProgress,(user.id,resource_id))
    if not p: p=UserResourceProgress(user_id=user.id,resource_id=resource_id); db.add(p)
    p.completed_at=datetime.utcnow(); db.commit()
    return ok({'resource_id':resource_id,'completed':True},'Resource marked as completed')
@router.post('/{resource_id}/bookmark')
def toggle_bookmark(resource_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    r=db.get(LearningResource,resource_id)
    if not r: raise AppError('Resource not found',404,'NOT_FOUND')
    p=db.get(UserResourceProgress,(user.id,resource_id))
    if not p: p=UserResourceProgress(user_id=user.id,resource_id=resource_id,bookmarked=True); db.add(p)
    else: p.bookmarked=not p.bookmarked
    db.commit()
    return ok({'resource_id':resource_id,'bookmarked':p.bookmarked},'Bookmark updated')
