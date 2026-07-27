from sqlalchemy import String,Text,ForeignKey,Enum,Integer,Float,Boolean
from sqlalchemy.orm import Mapped,mapped_column
from app.database import Base
from app.models.base import TimestampMixin
from app.utils.enums import RoadmapStatus,Difficulty
class LearningRoadmap(Base,TimestampMixin):
 __tablename__='learning_roadmaps'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); role_id:Mapped[int]=mapped_column(ForeignKey('career_roles.id')); title:Mapped[str]=mapped_column(String(160)); status:Mapped[RoadmapStatus]=mapped_column(Enum(RoadmapStatus),default=RoadmapStatus.ACTIVE); progress_percentage:Mapped[float]=mapped_column(Float,default=0)
class RoadmapItem(Base,TimestampMixin):
 __tablename__='roadmap_items'; id:Mapped[int]=mapped_column(primary_key=True); roadmap_id:Mapped[int]=mapped_column(ForeignKey('learning_roadmaps.id',ondelete='CASCADE'),index=True); title:Mapped[str]=mapped_column(String(160)); description:Mapped[str]=mapped_column(Text); item_type:Mapped[str]=mapped_column(String(50)); difficulty:Mapped[Difficulty]=mapped_column(Enum(Difficulty)); order_no:Mapped[int]=mapped_column(Integer); estimated_hours:Mapped[float]=mapped_column(Float); resource_id:Mapped[int|None]=mapped_column(ForeignKey('learning_resources.id',ondelete='SET NULL')); completed:Mapped[bool]=mapped_column(Boolean,default=False); progress_percentage:Mapped[float]=mapped_column(Float,default=0); premium_only:Mapped[bool]=mapped_column(Boolean,default=False)
