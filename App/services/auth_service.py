from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User, RefreshToken, ActionToken
from app.models.platform import SubscriptionPlan, UserSubscription
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password, create_access_token, new_opaque_token, token_hash, new_family_id
from app.core.exceptions import AppError
from app.utils.enums import AccountStatus, SubscriptionStatus

class AuthService:
    def __init__(self, db: Session): self.db=db; self.users=UserRepository(db)
    @staticmethod
    def user_data(user: User):
        return {'id':user.id,'full_name':user.full_name,'email':user.email,'role':user.role.value,'account_status':user.account_status.value,'email_verified':user.email_verified}
    def _ensure_active(self, user: User):
        if user.is_deleted: raise AppError('Invalid email or password',401,'INVALID_CREDENTIALS')
        if user.account_status != AccountStatus.ACTIVE: raise AppError('Account is not active',403,'ACCOUNT_INACTIVE')
    def _issue_pair(self, user: User, family_id: str | None = None):
        access, expires_in = create_access_token(user.id, user.role.value)
        raw = new_opaque_token(); family_id = family_id or new_family_id()
        self.db.add(RefreshToken(user_id=user.id,token_hash=token_hash(raw),family_id=family_id,expires_at=datetime.utcnow()+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)))
        return {'access_token':access,'refresh_token':raw,'token_type':'bearer','expires_in':expires_in,'user':self.user_data(user)}
    def register(self, full_name: str, email: str, password: str):
        email=email.lower().strip()
        if self.users.by_email(email): raise AppError('An account with this email already exists',409,'DUPLICATE_EMAIL')
        user=self.users.create(full_name=full_name.strip(),email=email,password_hash=hash_password(password),account_status=AccountStatus.ACTIVE)
        plan=self.db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.name=='Free'))
        if plan: self.db.add(UserSubscription(user_id=user.id,plan_id=plan.id,status=SubscriptionStatus.ACTIVE))
        verification_token=self.create_action_token(user.id,'email_verification',24)
        self.db.commit()
        data=self.user_data(user)
        if settings.APP_ENV == 'development': data['development_verification_token']=verification_token
        return data
    def login(self, email: str, password: str):
        user=self.users.by_email(email)
        if not user or not verify_password(password,user.password_hash): raise AppError('Invalid email or password',401,'INVALID_CREDENTIALS')
        self._ensure_active(user); result=self._issue_pair(user); self.db.commit(); return result
    def refresh(self, raw: str):
        row=self.users.refresh_by_hash(token_hash(raw)); now=datetime.utcnow()
        if not row: raise AppError('Invalid refresh token',401,'INVALID_REFRESH_TOKEN')
        if row.revoked_at is not None:
            self.users.revoke_family(row.family_id); self.db.commit(); raise AppError('Refresh token reuse detected. Please sign in again',401,'REFRESH_TOKEN_REUSE')
        if row.expires_at <= now: row.revoked_at=now; self.db.commit(); raise AppError('Refresh token expired',401,'INVALID_REFRESH_TOKEN')
        user=self.users.by_id(row.user_id)
        if not user: raise AppError('Invalid refresh token',401,'INVALID_REFRESH_TOKEN')
        self._ensure_active(user)
        new_raw=new_opaque_token(); new_hash=token_hash(new_raw); row.revoked_at=now; row.replaced_by_hash=new_hash
        access, expires_in=create_access_token(user.id,user.role.value)
        self.db.add(RefreshToken(user_id=user.id,token_hash=new_hash,family_id=row.family_id,expires_at=now+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)))
        self.db.commit(); return {'access_token':access,'refresh_token':new_raw,'token_type':'bearer','expires_in':expires_in,'user':self.user_data(user)}
    def logout(self, raw: str):
        row=self.users.refresh_by_hash(token_hash(raw))
        if row and row.revoked_at is None: row.revoked_at=datetime.utcnow(); self.db.commit()
    def logout_all(self, user_id: int): self.users.revoke_all(user_id); self.db.commit()
    def create_action_token(self, user_id: int, purpose: str, hours: int):
        raw=new_opaque_token(); self.db.add(ActionToken(user_id=user_id,purpose=purpose,token_hash=token_hash(raw),expires_at=datetime.utcnow()+timedelta(hours=hours))); return raw
    def forgot_password(self, email: str):
        user=self.users.by_email(email)
        raw=None
        if user and not user.is_deleted:
            raw=self.create_action_token(user.id,'password_reset',1); self.db.commit()
        return raw
    def reset_password(self, raw: str, new_password: str):
        row=self.users.active_action_token(token_hash(raw),'password_reset')
        if not row or row.expires_at <= datetime.utcnow(): raise AppError('Invalid or expired reset token',400,'INVALID_TOKEN')
        user=self.users.by_id(row.user_id); user.password_hash=hash_password(new_password); row.used_at=datetime.utcnow(); self.users.revoke_all(user.id); self.db.commit()
    def change_password(self, user: User, current: str, new: str):
        if not verify_password(current,user.password_hash): raise AppError('Current password is incorrect',400,'INVALID_PASSWORD')
        user.password_hash=hash_password(new); self.users.revoke_all(user.id); self.db.commit()
    def verify_email(self, raw: str):
        row=self.users.active_action_token(token_hash(raw),'email_verification')
        if not row or row.expires_at <= datetime.utcnow(): raise AppError('Invalid or expired verification token',400,'INVALID_TOKEN')
        user=self.users.by_id(row.user_id); user.email_verified=True; row.used_at=datetime.utcnow(); self.db.commit(); return self.user_data(user)
    def resend_verification(self, email: str):
        user=self.users.by_email(email); raw=None
        if user and not user.email_verified and not user.is_deleted:
            raw=self.create_action_token(user.id,'email_verification',24); self.db.commit()
        return raw
