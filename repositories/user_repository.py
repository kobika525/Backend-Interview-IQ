from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.user import User, UserProfile, RefreshToken, ActionToken

class UserRepository:
    def __init__(self, db: Session): self.db = db
    def by_email(self, email: str):
        return self.db.scalar(select(User).where(User.email == email.lower().strip()))
    def by_id(self, user_id: int): return self.db.get(User, user_id)
    def create(self, *, full_name: str, email: str, password_hash: str, account_status):
        user = User(full_name=full_name, email=email, password_hash=password_hash, account_status=account_status)
        self.db.add(user); self.db.flush(); self.db.add(UserProfile(user_id=user.id)); return user
    def profile(self, user_id: int):
        return self.db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    def refresh_by_hash(self, value: str):
        return self.db.scalar(select(RefreshToken).where(RefreshToken.token_hash == value))
    def revoke_family(self, family_id: str):
        self.db.execute(update(RefreshToken).where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None)).values(revoked_at=datetime.utcnow()))
    def revoke_all(self, user_id: int):
        self.db.execute(update(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)).values(revoked_at=datetime.utcnow()))
    def active_action_token(self, token_hash: str, purpose: str):
        return self.db.scalar(select(ActionToken).where(ActionToken.token_hash == token_hash, ActionToken.purpose == purpose, ActionToken.used_at.is_(None)))
