from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.career import CareerRole,CareerMatch,SkillGapAnalysis
from app.schemas.career import MatchRequest,SkillGapRequest
from app.services.career_service import CareerService
from app.core.exceptions import AppError
from app.utils.responses import ok
router=APIRouter(prefix='/careers',tags=['Careers'])
@router.get('/roles')
def roles(db:Session=Depends(get_db)): return ok([{'id':r.id,'title':r.title,'slug':r.slug,'description':r.description,'experience_level':r.experience_level} for r in db.scalars(select(CareerRole).where(CareerRole.is_active==True)).all()])
@router.get('/roles/{role_id}')
def role(role_id:int,db:Session=Depends(get_db)):
 r=db.get(CareerRole,role_id)
 if not r: raise AppError('Career role not found',404,'NOT_FOUND')
 return ok({'id':r.id,'title':r.title,'slug':r.slug,'description':r.description,'responsibilities':r.responsibilities,'experience_level':r.experience_level})
@router.post('/matches/generate',status_code=201)
def generate(p:MatchRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 rid=p.role_id or 1; m=CareerService.match(db,user.id,rid); return ok({'id':m.id,'role_id':m.role_id,'match_percentage':m.score,'matched_skills':m.matched_skills,'missing_skills':m.missing_skills,'explanation':m.explanation},'Career match generated')
@router.get('/matches')
def matches(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok([{'id':m.id,'role_id':m.role_id,'match_percentage':m.score,'matched_skills':m.matched_skills,'missing_skills':m.missing_skills} for m in db.scalars(select(CareerMatch).where(CareerMatch.user_id==user.id).order_by(CareerMatch.created_at.desc())).all()])
@router.get('/matches/{match_id}')
def match(match_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 m=db.get(CareerMatch,match_id)
 if not m or m.user_id!=user.id: raise AppError('Career match not found',404,'NOT_FOUND')
 return ok({'id':m.id,'role_id':m.role_id,'match_percentage':m.score,'matched_skills':m.matched_skills,'missing_skills':m.missing_skills,'explanation':m.explanation})
@router.post('/skill-gap',status_code=201)
def skill_gap(p:SkillGapRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 m=CareerService.match(db,user.id,p.role_id); a=SkillGapAnalysis(user_id=user.id,role_id=p.role_id,readiness_score=m.score,matched_skills=m.matched_skills,missing_skills=m.missing_skills,priority_gaps=m.missing_skills[:5],suggestions=[f'Learn {x}' for x in m.missing_skills[:5]]); db.add(a); db.commit(); return ok({'id':a.id,'readiness_score':a.readiness_score,'matched_skills':a.matched_skills,'missing_skills':a.missing_skills,'priority_gaps':a.priority_gaps,'suggested_actions':a.suggestions})
@router.get('/skill-gap')
def gaps(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok([{'id':a.id,'role_id':a.role_id,'readiness_score':a.readiness_score,'missing_skills':a.missing_skills} for a in db.scalars(select(SkillGapAnalysis).where(SkillGapAnalysis.user_id==user.id)).all()])
