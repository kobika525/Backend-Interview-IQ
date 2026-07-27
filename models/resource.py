from sqlalchemy import String,Text,Boolean,ForeignKey,DateTime
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from app.database import Base
from app.models.base import TimestampMixin
class LearningResource(Base,TimestampMixin):
 __tablename__='learning_resources'; id:Mapped[int]=mapped_column(primary_key=True); title:Mapped[str]=mapped_column(String(180)); description:Mapped[str]=mapped_column(Text); resource_type:Mapped[str]=mapped_column(String(40)); url:Mapped[str]=mapped_column(String(500)); skill_id:Mapped[int|None]=mapped_column(ForeignKey('skills.id',ondelete='SET NULL')); premium_only:Mapped[bool]=mapped_column(Boolean,default=False); is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class UserResourceProgress(Base):
 __tablename__='user_resource_progress'; user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),primary_key=True); resource_id:Mapped[int]=mapped_column(ForeignKey('learning_resources.id',ondelete='CASCADE'),primary_key=True); completed_at:Mapped[datetime|None]=mapped_column(DateTime); bookmarked:Mapped[bool]=mapped_column(Boolean,default=False)
