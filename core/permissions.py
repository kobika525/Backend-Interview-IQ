from app.core.exceptions import AppError
from app.models.user import User
from app.utils.enums import UserRole

def ensure_owner(owner_id:int,current_user:User):
    if owner_id != current_user.id and current_user.role != UserRole.ADMIN: raise AppError('You do not have access to this resource',403,'FORBIDDEN')

def ensure_admin(user:User):
    if user.role != UserRole.ADMIN: raise AppError('Administrator access required',403,'FORBIDDEN')
