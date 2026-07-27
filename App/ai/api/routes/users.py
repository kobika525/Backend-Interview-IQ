from fastapi import APIRouter,Depends,UploadFile,File
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User,UserProfile
from app.schemas.user import ProfileUpdate,OnboardingUpdate
from app.services.storage_service import StorageService
from app.services.user_service import UserService
from app.core.exceptions import AppError
from app.utils.responses import ok
router=APIRouter(prefix='/users',tags=['Users'])
@router.get('/me/profile')
def profile(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok(UserService(db).get_profile(user))
@router.patch('/me/profile')
def update_profile(payload:ProfileUpdate,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok(UserService(db).update(user,payload),'Profile updated')
@router.get('/me/onboarding')
def onboarding(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok(UserService(db).get_profile(user))
@router.put('/me/onboarding')
def put_onboarding(payload:OnboardingUpdate,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok(UserService(db).save_onboarding(user,payload),'Onboarding saved')
@router.post('/me/onboarding/complete')
def complete(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(UserProfile).where(UserProfile.user_id==user.id))
    if not row.career_goal or not row.experience_level: raise AppError('Career goal and experience level are required',400,'ONBOARDING_INCOMPLETE')
    row.onboarding_completed=True; db.commit(); return ok(UserService(db).get_profile(user),'Onboarding completed')
@router.post('/me/profile-image')
async def image(file:UploadFile=File(...),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    allowed={'image/jpeg':'.jpg','image/png':'.png','image/webp':'.webp'}
    if file.content_type not in allowed: raise AppError('Only JPG, PNG and WEBP images are supported',415,'UNSUPPORTED_MEDIA_TYPE')
    data=await file.read()
    if len(data)>5*1024*1024: raise AppError('Profile image exceeds 5 MB',413,'FILE_TOO_LARGE')
    signatures={'.jpg':(b'\xff\xd8\xff',),'.png':(b'\x89PNG\r\n\x1a\n',),'.webp':(b'RIFF',)}
    ext=allowed[file.content_type]
    if not any(data.startswith(sig) for sig in signatures[ext]): raise AppError('File content does not match its media type',415,'INVALID_FILE_SIGNATURE')
    key=StorageService.save_bytes('profile-images',file.filename or f'profile{ext}',data); row=db.scalar(select(UserProfile).where(UserProfile.user_id==user.id)); row.profile_image_key=key; db.commit(); return ok({'storage_key':key},'Profile image uploaded')
@router.delete('/me',status_code=204)
def delete(user:User=Depends(get_current_user),db:Session=Depends(get_db)): user.is_deleted=True; user.email=f'deleted-{user.id}-{user.email}'; db.commit()
