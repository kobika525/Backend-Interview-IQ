from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select,func
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.interview import InterviewSession
from app.models.report import InterviewReport
from app.models.resume import ResumeAnalysis,Resume
from app.models.roadmap import LearningRoadmap
from app.utils.enums import InterviewStatus
from app.utils.responses import ok
router=APIRouter(prefix='/progress',tags=['Progress'])
@router.get('/dashboard')
def dashboard(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 total=db.scalar(select(func.count(InterviewSession.id)).where(InterviewSession.user_id==user.id,InterviewSession.status==InterviewStatus.COMPLETED)) or 0; avg=db.scalar(select(func.avg(InterviewReport.overall_score)).where(InterviewReport.user_id==user.id)) or 0; high=db.scalar(select(func.max(InterviewReport.overall_score)).where(InterviewReport.user_id==user.id)) or 0; resume_avg=db.scalar(select(func.avg(ResumeAnalysis.ats_score)).join(Resume,Resume.id==ResumeAnalysis.resume_id).where(Resume.user_id==user.id)) or 0; roadmap=db.scalar(select(func.avg(LearningRoadmap.progress_percentage)).where(LearningRoadmap.user_id==user.id)) or 0; return ok({'total_interviews':total,'average_score':round(float(avg),2),'highest_score':round(float(high),2),'resume_score_average':round(float(resume_avg),2),'roadmap_progress':round(float(roadmap),2),'advisory_notice':'Career readiness is an advisory estimate, not an employment decision.'})
@router.get('/summary')
def summary(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return dashboard(user,db)
