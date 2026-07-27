from sqlalchemy import String,Text,Boolean,Enum,ForeignKey,Float,JSON,Integer
from sqlalchemy.orm import Mapped,mapped_column
from app.database import Base
from app.models.base import TimestampMixin
from app.utils.enums import ExperienceLevel
class CareerRole(Base,TimestampMixin):
 __tablename__='career_roles'; id:Mapped[int]=mapped_column(primary_key=True); title:Mapped[str]=mapped_column(String(120),unique=True); slug:Mapped[str]=mapped_column(String(140),unique=True,index=True); description:Mapped[str]=mapped_column(Text); responsibilities:Mapped[dict]=mapped_column(JSON,default=list); experience_level:Mapped[ExperienceLevel]=mapped_column(Enum(ExperienceLevel)); is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class Skill(Base,TimestampMixin):
 __tablename__='skills'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(100),unique=True,index=True); category:Mapped[str]=mapped_column(String(60),index=True)
class RoleSkill(Base):
 __tablename__='role_skills'; role_id:Mapped[int]=mapped_column(ForeignKey('career_roles.id',ondelete='CASCADE'),primary_key=True); skill_id:Mapped[int]=mapped_column(ForeignKey('skills.id',ondelete='CASCADE'),primary_key=True); required:Mapped[bool]=mapped_column(Boolean,default=True); weight:Mapped[float]=mapped_column(Float,default=1.0)
class UserSkill(Base,TimestampMixin):
 __tablename__='user_skills'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); skill_id:Mapped[int]=mapped_column(ForeignKey('skills.id',ondelete='CASCADE')); proficiency:Mapped[int]=mapped_column(Integer,default=1)
class CareerMatch(Base,TimestampMixin):
 __tablename__='career_matches'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); role_id:Mapped[int]=mapped_column(ForeignKey('career_roles.id')); score:Mapped[float]=mapped_column(Float); matched_skills:Mapped[list]=mapped_column(JSON); missing_skills:Mapped[list]=mapped_column(JSON); explanation:Mapped[str]=mapped_column(Text); model_version:Mapped[str]=mapped_column(String(40),default='rules-v1')
class SkillGapAnalysis(Base,TimestampMixin):
 __tablename__='skill_gap_analyses'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); role_id:Mapped[int]=mapped_column(ForeignKey('career_roles.id')); readiness_score:Mapped[float]=mapped_column(Float); matched_skills:Mapped[list]=mapped_column(JSON); missing_skills:Mapped[list]=mapped_column(JSON); priority_gaps:Mapped[list]=mapped_column(JSON); suggestions:Mapped[list]=mapped_column(JSON); scoring_version:Mapped[str]=mapped_column(String(40),default='gap-v1')
