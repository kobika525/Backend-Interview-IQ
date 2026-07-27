from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Enum, Integer
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.database import Base
from app.models.base import TimestampMixin
from app.utils.enums import UserRole,AccountStatus,ExperienceLevel,InterviewMode
class User(Base,TimestampMixin):
    __tablename__='users'
    id:Mapped[int]=mapped_column(primary_key=True)
    full_name:Mapped[str]=mapped_column(String(120))
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(String(255))
    role:Mapped[UserRole]=mapped_column(Enum(UserRole),default=UserRole.USER,index=True)
    account_status:Mapped[AccountStatus]=mapped_column(Enum(AccountStatus),default=AccountStatus.ACTIVE,index=True)
    email_verified:Mapped[bool]=mapped_column(Boolean,default=False)
    is_deleted:Mapped[bool]=mapped_column(Boolean,default=False,index=True)
    profile:Mapped['UserProfile|None']=relationship(back_populates='user',uselist=False,cascade='all, delete-orphan')
class UserProfile(Base,TimestampMixin):
    __tablename__='user_profiles'
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),unique=True,index=True)
    career_goal:Mapped[str|None]=mapped_column(String(255))
    experience_level:Mapped[ExperienceLevel|None]=mapped_column(Enum(ExperienceLevel))
    target_role_id:Mapped[int|None]=mapped_column(ForeignKey('career_roles.id',ondelete='SET NULL'))
    preferred_interview_mode:Mapped[InterviewMode|None]=mapped_column(Enum(InterviewMode))
    weekly_learning_target:Mapped[int]=mapped_column(Integer,default=5)
    summary:Mapped[str|None]=mapped_column(Text)
    profile_image_key:Mapped[str|None]=mapped_column(String(255))
    onboarding_completed:Mapped[bool]=mapped_column(Boolean,default=False)
    user:Mapped[User]=relationship(back_populates='profile')
class RefreshToken(Base):
    __tablename__='refresh_tokens'
    id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True)
    token_hash:Mapped[str]=mapped_column(String(64),unique=True,index=True); family_id:Mapped[str]=mapped_column(String(36),index=True)
    expires_at:Mapped[datetime]=mapped_column(DateTime,index=True); revoked_at:Mapped[datetime|None]=mapped_column(DateTime); replaced_by_hash:Mapped[str|None]=mapped_column(String(64)); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class ActionToken(Base):
    __tablename__='action_tokens'
    id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True)
    purpose:Mapped[str]=mapped_column(String(40),index=True); token_hash:Mapped[str]=mapped_column(String(64),unique=True,index=True)
    expires_at:Mapped[datetime]=mapped_column(DateTime,index=True); used_at:Mapped[datetime|None]=mapped_column(DateTime); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
