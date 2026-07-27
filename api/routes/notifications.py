from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select,func
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.platform import Notification
from app.core.exceptions import AppError
from app.utils.responses import ok
router=APIRouter(prefix='/notifications',tags=['Notifications'])
def data(n): return {'id':n.id,'type':n.type,'title':n.title,'message':n.message,'is_read':n.is_read,'created_at':n.created_at.isoformat()}
@router.get('')
def list_items(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(Notification).where(Notification.user_id==user.id).order_by(Notification.id.desc())).all()
    return ok([data(n) for n in rows],'Records retrieved successfully')
@router.get('/unread-count')
def unread_count(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    count=db.scalar(select(func.count(Notification.id)).where(Notification.user_id==user.id,Notification.is_read==False)) or 0
    return ok({'count':count})
@router.patch('/{notification_id}/read')
def mark_read(notification_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    n=db.get(Notification,notification_id)
    if not n or n.user_id!=user.id: raise AppError('Notification not found',404,'NOT_FOUND')
    n.is_read=True; db.commit(); db.refresh(n)
    return ok(data(n),'Notification marked as read')
@router.patch('/read-all')
def mark_all_read(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(Notification).where(Notification.user_id==user.id,Notification.is_read==False)).all()
    for n in rows: n.is_read=True
    db.commit()
    return ok({'updated':len(rows)},'All notifications marked as read')
@router.delete('/{notification_id}')
def delete_notification(notification_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    n=db.get(Notification,notification_id)
    if not n or n.user_id!=user.id: raise AppError('Notification not found',404,'NOT_FOUND')
    db.delete(n); db.commit()
    return ok({'id':notification_id},'Notification deleted')
