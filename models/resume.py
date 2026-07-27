from sqlalchemy import String,Text,ForeignKey,Enum,Float,JSON,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from app.database import Base
from app.models.base import TimestampMixin
from app.utils.enums import ResumeStatus
class Resume(Base,TimestampMixin):
 __tablename__='resumes'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); original_name:Mapped[str]=mapped_column(String(255)); storage_key:Mapped[str]=mapped_column(String(255),unique=True); mime_type:Mapped[str]=mapped_column(String(120)); size_bytes:Mapped[int]; target_role_id:Mapped[int|None]=mapped_column(ForeignKey('career_roles.id',ondelete='SET NULL')); status:Mapped[ResumeStatus]=mapped_column(Enum(ResumeStatus),default=ResumeStatus.UPLOADED,index=True); extracted_text:Mapped[str|None]=mapped_column(Text); is_deleted:Mapped[bool]=mapped_column(Boolean,default=False,index=True)
class ResumeAnalysis(Base,TimestampMixin):
 __tablename__='resume_analyses'; id:Mapped[int]=mapped_column(primary_key=True); resume_id:Mapped[int]=mapped_column(ForeignKey('resumes.id',ondelete='CASCADE'),unique=True,index=True); ats_score:Mapped[float]=mapped_column(Float); category_scores:Mapped[dict]=mapped_column(JSON); strengths:Mapped[list]=mapped_column(JSON); suggestions:Mapped[list]=mapped_column(JSON); sections:Mapped[dict]=mapped_column(JSON); scoring_version:Mapped[str]=mapped_column(String(40),default='ats-v1'); disclaimer:Mapped[str]=mapped_column(String(255),default='Estimated AI-assisted ATS readiness score')
class ResumeSkill(Base):
 __tablename__='resume_skills'; resume_id:Mapped[int]=mapped_column(ForeignKey('resumes.id',ondelete='CASCADE'),primary_key=True); skill_id:Mapped[int]=mapped_column(ForeignKey('skills.id',ondelete='CASCADE'),primary_key=True); confidence:Mapped[float]=mapped_column(Float,default=1.0)
