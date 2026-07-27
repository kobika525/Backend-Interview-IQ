from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.platform import SupportTicket,SupportMessage
from app.schemas.support import CreateTicketRequest,AddMessageRequest
from app.core.exceptions import AppError
from app.utils.responses import ok
router=APIRouter(prefix='/support',tags=['Support'])
def ticket_data(t): return {'id':t.id,'subject':t.subject,'category':t.category,'status':t.status,'created_at':t.created_at.isoformat()}
def message_data(m): return {'id':m.id,'ticket_id':m.ticket_id,'sender_user_id':m.sender_user_id,'message':m.message,'created_at':m.created_at.isoformat()}
@router.get('')
def list_items(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(SupportTicket).where(SupportTicket.user_id==user.id).order_by(SupportTicket.id.desc())).all()
    return ok([ticket_data(t) for t in rows],'Records retrieved successfully')
@router.post('',status_code=201)
def create_ticket(payload:CreateTicketRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    t=SupportTicket(user_id=user.id,subject=payload.subject,category=payload.category,status='OPEN')
    db.add(t); db.flush()
    m=SupportMessage(ticket_id=t.id,sender_user_id=user.id,message=payload.message)
    db.add(m); db.commit(); db.refresh(t)
    return ok(ticket_data(t),'Support ticket created')
@router.get('/{ticket_id}')
def get_ticket(ticket_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    t=db.get(SupportTicket,ticket_id)
    if not t or t.user_id!=user.id: raise AppError('Support ticket not found',404,'NOT_FOUND')
    msgs=db.scalars(select(SupportMessage).where(SupportMessage.ticket_id==t.id).order_by(SupportMessage.id.asc())).all()
    return ok({**ticket_data(t),'messages':[message_data(m) for m in msgs]})
@router.post('/{ticket_id}/messages',status_code=201)
def add_message(ticket_id:int,payload:AddMessageRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    t=db.get(SupportTicket,ticket_id)
    if not t or t.user_id!=user.id: raise AppError('Support ticket not found',404,'NOT_FOUND')
    m=SupportMessage(ticket_id=t.id,sender_user_id=user.id,message=payload.message)
    db.add(m); db.commit(); db.refresh(m)
    return ok(message_data(m),'Message added')
