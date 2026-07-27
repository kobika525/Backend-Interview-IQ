from sqlalchemy import ForeignKey,Float,JSON,Text,String
from sqlalchemy.orm import Mapped,mapped_column
from app.database import Base
from app.models.base import TimestampMixin
class InterviewReport(Base,TimestampMixin):
 __tablename__='interview_reports'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); session_id:Mapped[int]=mapped_column(ForeignKey('interview_sessions.id',ondelete='CASCADE'),unique=True,index=True); overall_score:Mapped[float]=mapped_column(Float); performance_label:Mapped[str]=mapped_column(String(40)); category_scores:Mapped[dict]=mapped_column(JSON); executive_summary:Mapped[str]=mapped_column(Text); strengths:Mapped[list]=mapped_column(JSON); growth_areas:Mapped[list]=mapped_column(JSON); question_feedback:Mapped[list]=mapped_column(JSON); recommendations:Mapped[list]=mapped_column(JSON); pdf_storage_key:Mapped[str|None]=mapped_column(String(255)); scoring_version:Mapped[str]=mapped_column(String(40),default='report-v1')
