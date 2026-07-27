from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.resume import Resume,ResumeAnalysis,ResumeSkill
from app.models.career import Skill,RoleSkill
from app.services.storage_service import StorageService
from app.ai.resume.text_extractor import extract_text
from app.ai.resume.section_detector import detect_sections
from app.ai.resume.skill_extractor import extract_skills
from app.ai.resume.ats_scorer import score
from app.utils.enums import ResumeStatus
from app.core.exceptions import AppError
class ResumeService:
 @staticmethod
 def analyze(db:Session,resume:Resume):
  resume.status=ResumeStatus.PROCESSING; db.commit()
  try:
   text=extract_text(StorageService.path(resume.storage_key)); skills=db.scalars(select(Skill)).all(); found=extract_skills(text,[s.name for s in skills]); smap={s.name:s for s in skills}; required=[]
   if resume.target_role_id: required=[x.skill_id for x in db.scalars(select(RoleSkill).where(RoleSkill.role_id==resume.target_role_id,RoleSkill.required==True)).all()]
   found_ids=[smap[n].id for n in found]; sections=detect_sections(text); ats,cats=score(text,sections,len(set(found_ids)&set(required)),len(required));
   db.query(ResumeSkill).filter(ResumeSkill.resume_id==resume.id).delete(); [db.add(ResumeSkill(resume_id=resume.id,skill_id=sid,confidence=1.0)) for sid in found_ids]
   old=db.scalar(select(ResumeAnalysis).where(ResumeAnalysis.resume_id==resume.id)); strengths=[k.replace('_',' ').title() for k,v in cats.items() if v>=75]; suggestions=[f'Improve {k.replace("_"," ")}' for k,v in cats.items() if v<60]
   if old: old.ats_score=ats; old.category_scores=cats; old.strengths=strengths; old.suggestions=suggestions; old.sections=sections
   else: db.add(ResumeAnalysis(resume_id=resume.id,ats_score=ats,category_scores=cats,strengths=strengths,suggestions=suggestions,sections=sections))
   resume.extracted_text=text; resume.status=ResumeStatus.COMPLETED; db.commit(); return db.scalar(select(ResumeAnalysis).where(ResumeAnalysis.resume_id==resume.id))
  except Exception:
   resume.status=ResumeStatus.FAILED; db.commit(); raise
