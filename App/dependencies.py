from fastapi import Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import AppError
from app.models.user import User
from app.utils.enums import UserRole,AccountStatus
bearer=HTTPBearer(auto_error=False)
def get_current_user(credentials:HTTPAuthorizationCredentials|None=Depends(bearer),db:Session=Depends(get_db))->User:
 if not credentials: raise AppError('Authentication required',401,'AUTH_REQUIRED')
 try: uid=int(decode_access_token(credentials.credentials)['sub'])
 except Exception: raise AppError('Invalid or expired access token',401,'INVALID_TOKEN')
 user=db.get(User,uid)
 if not user or user.is_deleted: raise AppError('User not found',401,'INVALID_TOKEN')
 if user.account_status!=AccountStatus.ACTIVE: raise AppError('Account is not active',403,'ACCOUNT_INACTIVE')
 return user
def require_admin(user:User=Depends(get_current_user))->User:
 if user.role!=UserRole.ADMIN: raise AppError('Administrator access required',403,'FORBIDDEN')
 return user
