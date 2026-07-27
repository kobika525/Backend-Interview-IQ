from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select,func
from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.interview import InterviewQuestion,InterviewSession
from app.models.resume import ResumeAnalysis
from app.models.platform import UserSubscription
from app.utils.responses import ok
router=APIRouter(prefix='/admin',tags=['Admin'])
@router.get('/dashboard')
def dashboard(admin:User=Depends(require_admin),db:Session=Depends(get_db)): return ok({'total_users':db.scalar(select(func.count(User.id))) or 0,'completed_interviews':db.scalar(select(func.count(InterviewSession.id)).where(InterviewSession.status=='COMPLETED')) or 0,'resume_analyses':db.scalar(select(func.count(ResumeAnalysis.id))) or 0,'active_subscriptions':db.scalar(select(func.count(UserSubscription.id)).where(UserSubscription.status=='ACTIVE')) or 0})
@router.get('/users')
def users(admin:User=Depends(require_admin),db:Session=Depends(get_db)): return ok([{'id':u.id,'full_name':u.full_name,'email':u.email,'role':u.role,'account_status':u.account_status} for u in db.scalars(select(User).limit(100)).all()])
@router.get('/questions')
def questions(admin:User=Depends(require_admin),db:Session=Depends(get_db)): return ok([{'id':q.id,'question_text':q.question_text,'category':q.category,'difficulty':q.difficulty,'interview_type':q.interview_type,'is_active':q.is_active} for q in db.scalars(select(InterviewQuestion)).all()])
