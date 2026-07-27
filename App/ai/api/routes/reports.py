from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.report import InterviewReport
from app.core.exceptions import AppError
from app.utils.responses import ok
router=APIRouter(prefix='/reports',tags=['Reports'])
def data(r): return {'id':r.id,'session_id':r.session_id,'overall_score':r.overall_score,'performance_label':r.performance_label,'category_scores':r.category_scores,'executive_summary':r.executive_summary,'strengths':r.strengths,'growth_areas':r.growth_areas,'recommendations':r.recommendations,'responsible_ai_notice':'AI feedback is advisory and is not a hiring decision.'}
@router.get('')
def reports(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok([data(r) for r in db.scalars(select(InterviewReport).where(InterviewReport.user_id==user.id)).all()])
@router.get('/{report_id}')
def report(report_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 r=db.get(InterviewReport,report_id)
 if not r or r.user_id!=user.id: raise AppError('Report not found',404,'NOT_FOUND')
 return ok(data(r))
@router.get('/interviews/{session_id}')
def by_session(session_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 r=db.scalar(select(InterviewReport).where(InterviewReport.session_id==session_id,InterviewReport.user_id==user.id))
 if not r: raise AppError('Report not found',404,'NOT_FOUND')
 return ok(data(r))
