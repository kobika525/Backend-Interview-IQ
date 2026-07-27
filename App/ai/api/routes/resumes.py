from fastapi import APIRouter,Depends,UploadFile,File,Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select,func
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume,ResumeAnalysis
from app.services.storage_service import StorageService
from app.services.resume_service import ResumeService
from app.core.exceptions import AppError
from app.config import settings
from app.utils.responses import ok,pagination
router=APIRouter(prefix='/resumes',tags=['Resumes'])
@router.post('',status_code=201)
async def upload(file:UploadFile=File(...),target_role_id:int|None=None,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 data=await file.read(); name=file.filename or ''; ext=name.lower().rsplit('.',1)[-1] if '.' in name else ''
 if ext not in ['pdf','docx']: raise AppError('Only PDF and DOCX files are supported',415,'UNSUPPORTED_MEDIA')
 if len(data)>settings.MAX_RESUME_SIZE_MB*1024*1024: raise AppError('Resume file is too large',413,'FILE_TOO_LARGE')
 if ext=='pdf' and not data.startswith(b'%PDF'): raise AppError('Invalid PDF signature',415,'INVALID_FILE')
 if ext=='docx' and not data.startswith(b'PK'): raise AppError('Invalid DOCX signature',415,'INVALID_FILE')
 key=StorageService.save_bytes('resumes',name,data); r=Resume(user_id=user.id,original_name=name,storage_key=key,mime_type=file.content_type or '',size_bytes=len(data),target_role_id=target_role_id); db.add(r); db.commit(); return ok({'id':r.id,'status':r.status},'Resume uploaded')
@router.post('/{resume_id}/analyze')
def analyze(resume_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 r=db.get(Resume,resume_id)
 if not r or r.user_id!=user.id or r.is_deleted: raise AppError('Resume not found',404,'NOT_FOUND')
 a=ResumeService.analyze(db,r); return ok({'resume_id':r.id,'ats_score':a.ats_score,'category_scores':a.category_scores,'strengths':a.strengths,'suggestions':a.suggestions,'disclaimer':a.disclaimer},'Resume analysis completed')
@router.post('/{resume_id}/reanalyze')
def reanalyze(resume_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return analyze(resume_id,user,db)
@router.get('')
def list_resumes(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 q=select(Resume).where(Resume.user_id==user.id,Resume.is_deleted==False); total=db.scalar(select(func.count()).select_from(q.subquery())); items=db.scalars(q.order_by(Resume.created_at.desc()).offset((page-1)*page_size).limit(page_size)).all(); return ok({'items':[{'id':x.id,'original_name':x.original_name,'status':x.status,'created_at':x.created_at} for x in items],'pagination':pagination(page,page_size,total)},'Records retrieved successfully')
@router.get('/{resume_id}')
def get_resume(resume_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 r=db.get(Resume,resume_id)
 if not r or r.user_id!=user.id or r.is_deleted: raise AppError('Resume not found',404,'NOT_FOUND')
 return ok({'id':r.id,'original_name':r.original_name,'status':r.status,'target_role_id':r.target_role_id,'created_at':r.created_at})
@router.get('/{resume_id}/analysis')
def analysis(resume_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 r=db.get(Resume,resume_id)
 if not r or r.user_id!=user.id: raise AppError('Resume not found',404,'NOT_FOUND')
 a=db.scalar(select(ResumeAnalysis).where(ResumeAnalysis.resume_id==r.id));
 if not a: raise AppError('Resume analysis not found',404,'NOT_FOUND')
 return ok({'ats_score':a.ats_score,'category_scores':a.category_scores,'strengths':a.strengths,'suggestions':a.suggestions,'sections':a.sections,'disclaimer':a.disclaimer})
@router.get('/{resume_id}/download')
def download(resume_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 r=db.get(Resume,resume_id)
 if not r or r.user_id!=user.id: raise AppError('Resume not found',404,'NOT_FOUND')
 return FileResponse(StorageService.path(r.storage_key),filename=r.original_name)
@router.delete('/{resume_id}',status_code=204)
def delete(resume_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 r=db.get(Resume,resume_id)
 if not r or r.user_id!=user.id: raise AppError('Resume not found',404,'NOT_FOUND')
 r.is_deleted=True; db.commit()
