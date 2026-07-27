from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.schemas.auth import RegisterRequest,LoginRequest,RefreshRequest,TokenRequest,EmailRequest,ResetPasswordRequest,ChangePasswordRequest
from app.services.auth_service import AuthService
from app.dependencies import get_current_user
from app.models.user import User
from app.utils.responses import ok
router=APIRouter(prefix='/auth',tags=['Authentication'])

def service(db: Session): return AuthService(db)
@router.post('/register',status_code=201)
def register(payload:RegisterRequest,db:Session=Depends(get_db)): return ok(service(db).register(payload.full_name,payload.email,payload.password),'Registration successful')
@router.post('/login')
def login(payload:LoginRequest,db:Session=Depends(get_db)): return ok(service(db).login(payload.email,payload.password),'Login successful')
@router.post('/refresh')
def refresh(payload:RefreshRequest,db:Session=Depends(get_db)): return ok(service(db).refresh(payload.refresh_token),'Token refreshed')
@router.post('/logout')
def logout(payload:RefreshRequest,db:Session=Depends(get_db)): service(db).logout(payload.refresh_token); return ok(message='Logout successful')
@router.post('/logout-all')
def logout_all(user:User=Depends(get_current_user),db:Session=Depends(get_db)): service(db).logout_all(user.id); return ok(message='Logged out from all devices')
@router.get('/me')
def me(user:User=Depends(get_current_user)): return ok(AuthService.user_data(user))
@router.post('/forgot-password')
def forgot(payload:EmailRequest,db:Session=Depends(get_db)):
    token=service(db).forgot_password(payload.email); data={}
    if token and settings.APP_ENV=='development': data['development_reset_token']=token
    return ok(data,'If the account exists, password-reset instructions have been created')
@router.post('/reset-password')
def reset(payload:ResetPasswordRequest,db:Session=Depends(get_db)): service(db).reset_password(payload.token,payload.new_password); return ok(message='Password reset successful')
@router.post('/change-password')
def change(payload:ChangePasswordRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)): service(db).change_password(user,payload.current_password,payload.new_password); return ok(message='Password changed successfully. Sign in again on other devices')
@router.post('/verify-email')
def verify(payload:TokenRequest,db:Session=Depends(get_db)): return ok(service(db).verify_email(payload.token),'Email verified successfully')
@router.post('/resend-verification')
def resend(payload:EmailRequest,db:Session=Depends(get_db)):
    token=service(db).resend_verification(payload.email); data={}
    if token and settings.APP_ENV=='development': data['development_verification_token']=token
    return ok(data,'If verification is required, new instructions have been created')
