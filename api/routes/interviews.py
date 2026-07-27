from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select,func
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.interview import InterviewSession,SessionQuestion,InterviewQuestion
from app.schemas.interview import InterviewCreate,TextAnswer
from app.services.interview_service import InterviewService
from app.core.exceptions import AppError
from app.utils.enums import InterviewStatus
from app.utils.responses import ok,pagination
router=APIRouter(prefix='/interviews',tags=['Interviews'])
@router.post('',status_code=201)
def create(p:InterviewCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)): s=InterviewService.create(db,user.id,p); return ok({'id':s.id,'status':s.status},'Interview created')
@router.get('')
def listing(page:int=1,page_size:int=20,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 q=select(InterviewSession).where(InterviewSession.user_id==user.id); total=db.scalar(select(func.count()).select_from(q.subquery())); items=db.scalars(q.order_by(InterviewSession.created_at.desc()).offset((page-1)*page_size).limit(min(page_size,100))).all(); return ok({'items':[{'id':s.id,'status':s.status,'mode':s.mode,'interview_type':s.interview_type,'created_at':s.created_at} for s in items],'pagination':pagination(page,min(page_size,100),total)})
@router.post('/{session_id}/start')
def start(session_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 s=db.get(InterviewSession,session_id)
 if not s or s.user_id!=user.id: raise AppError('Interview session not found',404,'NOT_FOUND')
 if s.status!=InterviewStatus.READY: raise AppError('Interview cannot be started',409,'INVALID_STATE')
 s.status=InterviewStatus.IN_PROGRESS; db.commit(); return current(session_id,user,db)
@router.get('/{session_id}/current-question')
def current(session_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 s=db.get(InterviewSession,session_id)
 if not s or s.user_id!=user.id: raise AppError('Interview session not found',404,'NOT_FOUND')
 sq=db.scalar(select(SessionQuestion).where(SessionQuestion.session_id==s.id,SessionQuestion.order_no==s.current_order+1));
 if not sq: return ok({'completed':True})
 q=db.get(InterviewQuestion,sq.question_id); return ok({'completed':False,'question':{'id':q.id,'order':sq.order_no,'text':q.question_text,'category':q.category,'difficulty':q.difficulty}})
@router.get('/{session_id}/questions/{question_order}')
def q_by_order(session_id:int,question_order:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 s=db.get(InterviewSession,session_id)
 if not s or s.user_id!=user.id: raise AppError('Interview session not found',404,'NOT_FOUND')
 sq=db.scalar(select(SessionQuestion).where(SessionQuestion.session_id==s.id,SessionQuestion.order_no==question_order));
 if not sq: raise AppError('Question not found',404,'NOT_FOUND')
 q=db.get(InterviewQuestion,sq.question_id); return ok({'id':q.id,'order':sq.order_no,'text':q.question_text,'category':q.category})
@router.post('/{session_id}/answers/text')
def answer(session_id:int,p:TextAnswer,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok(InterviewService.submit_text(db,user.id,session_id,p),'Answer evaluated')
@router.post('/{session_id}/complete')
def complete(session_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)): r=InterviewService.complete(db,user.id,session_id); return ok({'report_id':r.id,'overall_score':r.overall_score,'performance_label':r.performance_label},'Interview completed')
@router.post('/{session_id}/cancel')
def cancel(session_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 s=db.get(InterviewSession,session_id)
 if not s or s.user_id!=user.id: raise AppError('Interview session not found',404,'NOT_FOUND')
 s.status=InterviewStatus.CANCELLED; db.commit(); return ok(message='Interview cancelled')
@router.get('/{session_id}/status')
def status(session_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 s=db.get(InterviewSession,session_id)
 if not s or s.user_id!=user.id: raise AppError('Interview session not found',404,'NOT_FOUND')
 return ok({'id':s.id,'status':s.status,'current_order':s.current_order})
