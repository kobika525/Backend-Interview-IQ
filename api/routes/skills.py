from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.career import Skill,UserSkill
from app.schemas.skill import UpsertUserSkillRequest
from app.utils.responses import ok
router=APIRouter(prefix='/skills',tags=['Skills'])
@router.get('')
def list_items(db:Session=Depends(get_db)):
    rows=db.scalars(select(Skill)).all()
    return ok([{'id':s.id,'name':s.name,'category':s.category} for s in rows],'Records retrieved successfully')
@router.get('/mine')
def my_skills(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(UserSkill).where(UserSkill.user_id==user.id)).all()
    return ok([{'skill_id':us.skill_id,'proficiency':us.proficiency} for us in rows])
@router.put('/mine/{skill_id}')
def upsert_my_skill(skill_id:int,payload:UpsertUserSkillRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(UserSkill).where(UserSkill.user_id==user.id,UserSkill.skill_id==skill_id))
    if not row: row=UserSkill(user_id=user.id,skill_id=skill_id,proficiency=payload.proficiency); db.add(row)
    else: row.proficiency=payload.proficiency
    db.commit()
    return ok({'skill_id':skill_id,'proficiency':payload.proficiency},'Skill proficiency updated')
