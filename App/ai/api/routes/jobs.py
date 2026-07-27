from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.platform import ProcessingJob
from app.core.exceptions import AppError
from app.utils.responses import ok
router=APIRouter(prefix='/jobs',tags=['Processing Jobs'])
@router.get('/{job_id}')
def get_job(job_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 j=db.get(ProcessingJob,job_id)
 if not j or j.user_id!=user.id: raise AppError('Job not found',404,'NOT_FOUND')
 return ok({'job_id':j.id,'status':j.status,'progress':j.progress,'current_stage':j.current_stage})
