from sqlalchemy import String,Text,Boolean,ForeignKey,Enum,Integer,DateTime,JSON,Numeric
from sqlalchemy.orm import Mapped,mapped_column
from datetime import datetime
from decimal import Decimal
from app.database import Base
from app.models.base import TimestampMixin
from app.utils.enums import NotificationType,SubscriptionStatus,InterviewMode
class Notification(Base,TimestampMixin):
 __tablename__='notifications'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); type:Mapped[NotificationType]=mapped_column(Enum(NotificationType)); title:Mapped[str]=mapped_column(String(160)); message:Mapped[str]=mapped_column(Text); is_read:Mapped[bool]=mapped_column(Boolean,default=False,index=True)
class SubscriptionPlan(Base,TimestampMixin):
 __tablename__='subscription_plans'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(40),unique=True); price_monthly:Mapped[Decimal]=mapped_column(Numeric(10,2),default=0); limits:Mapped[dict]=mapped_column(JSON); features:Mapped[list]=mapped_column(JSON); is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class UserSubscription(Base,TimestampMixin):
 __tablename__='user_subscriptions'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); plan_id:Mapped[int]=mapped_column(ForeignKey('subscription_plans.id')); status:Mapped[SubscriptionStatus]=mapped_column(Enum(SubscriptionStatus),default=SubscriptionStatus.ACTIVE); starts_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow); ends_at:Mapped[datetime|None]=mapped_column(DateTime)
class UsageRecord(Base,TimestampMixin):
 __tablename__='usage_records'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); feature:Mapped[str]=mapped_column(String(60),index=True); period_key:Mapped[str]=mapped_column(String(10),index=True); quantity:Mapped[int]=mapped_column(Integer,default=0)
class BillingRecord(Base,TimestampMixin):
 __tablename__='billing_records'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); description:Mapped[str]=mapped_column(String(255)); amount:Mapped[Decimal]=mapped_column(Numeric(10,2)); currency:Mapped[str]=mapped_column(String(3),default='LKR'); status:Mapped[str]=mapped_column(String(30),default='DEMO'); external_reference:Mapped[str|None]=mapped_column(String(100))
class SupportTicket(Base,TimestampMixin):
 __tablename__='support_tickets'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); category:Mapped[str]=mapped_column(String(50)); subject:Mapped[str]=mapped_column(String(180)); status:Mapped[str]=mapped_column(String(30),default='OPEN',index=True)
class SupportMessage(Base,TimestampMixin):
 __tablename__='support_messages'; id:Mapped[int]=mapped_column(primary_key=True); ticket_id:Mapped[int]=mapped_column(ForeignKey('support_tickets.id',ondelete='CASCADE'),index=True); sender_user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE')); message:Mapped[str]=mapped_column(Text)
class Achievement(Base,TimestampMixin):
 __tablename__='achievements'; id:Mapped[int]=mapped_column(primary_key=True); code:Mapped[str]=mapped_column(String(80),unique=True); title:Mapped[str]=mapped_column(String(120)); description:Mapped[str]=mapped_column(Text); condition:Mapped[dict]=mapped_column(JSON)
class UserAchievement(Base):
 __tablename__='user_achievements'; user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),primary_key=True); achievement_id:Mapped[int]=mapped_column(ForeignKey('achievements.id',ondelete='CASCADE'),primary_key=True); awarded_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class AuditLog(Base):
 __tablename__='audit_logs'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int|None]=mapped_column(ForeignKey('users.id',ondelete='SET NULL'),index=True); action:Mapped[str]=mapped_column(String(100),index=True); entity_type:Mapped[str]=mapped_column(String(60)); entity_id:Mapped[str|None]=mapped_column(String(60)); metadata_json:Mapped[dict]=mapped_column(JSON,default=dict); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True)
class ProcessingJob(Base,TimestampMixin):
 __tablename__='processing_jobs'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True); job_type:Mapped[str]=mapped_column(String(50)); entity_type:Mapped[str]=mapped_column(String(50)); entity_id:Mapped[int|None]; status:Mapped[str]=mapped_column(String(30),default='PROCESSING',index=True); progress:Mapped[int]=mapped_column(Integer,default=0); current_stage:Mapped[str]=mapped_column(String(160),default='Queued'); error_message:Mapped[str|None]=mapped_column(Text); started_at:Mapped[datetime|None]=mapped_column(DateTime); completed_at:Mapped[datetime|None]=mapped_column(DateTime)
