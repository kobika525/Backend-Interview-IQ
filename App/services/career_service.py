from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.career import *
class CareerService:
 @staticmethod
 def match(db:Session,user_id:int,role_id:int):
  required=db.execute(select(Skill.name,RoleSkill.required).join(RoleSkill,Skill.id==RoleSkill.skill_id).where(RoleSkill.role_id==role_id)).all(); user=db.scalars(select(Skill.name).join(UserSkill,Skill.id==UserSkill.skill_id).where(UserSkill.user_id==user_id)).all(); us=set(user); req={n for n,r in required if r}; rec={n for n,r in required if not r}; matched=sorted((req|rec)&us); missing=sorted(req-us); score=round(100*(.75*len(req&us)/max(len(req),1)+.25*len(rec&us)/max(len(rec),1)),2); m=CareerMatch(user_id=user_id,role_id=role_id,score=score,matched_skills=matched,missing_skills=missing,explanation='Weighted skill coverage with deterministic fallback scoring.'); db.add(m); db.commit(); return m
