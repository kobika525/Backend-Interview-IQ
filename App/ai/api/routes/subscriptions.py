from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.platform import SubscriptionPlan,UserSubscription,UsageRecord
from app.utils.responses import ok
router=APIRouter(prefix='/subscriptions',tags=['Subscriptions'])
@router.get('/plans')
def plans(db:Session=Depends(get_db)): return ok([{'id':p.id,'name':p.name,'price_monthly':float(p.price_monthly),'limits':p.limits,'features':p.features} for p in db.scalars(select(SubscriptionPlan).where(SubscriptionPlan.is_active==True)).all()])
@router.get('/current')
def current(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
 s=db.scalar(select(UserSubscription).where(UserSubscription.user_id==user.id).order_by(UserSubscription.created_at.desc())); p=db.get(SubscriptionPlan,s.plan_id) if s else None; return ok({'subscription_id':s.id if s else None,'status':s.status if s else None,'plan':{'id':p.id,'name':p.name,'limits':p.limits,'features':p.features} if p else None})
@router.get('/usage')
def usage(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ok([{'feature':u.feature,'period_key':u.period_key,'quantity':u.quantity} for u in db.scalars(select(UsageRecord).where(UsageRecord.user_id==user.id)).all()])
@router.post('/demo-upgrade')
def upgrade(plan_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)): s=db.scalar(select(UserSubscription).where(UserSubscription.user_id==user.id).order_by(UserSubscription.created_at.desc())); s.plan_id=plan_id; db.commit(); return ok({'demo':True,'plan_id':plan_id},'Demo upgrade completed; no payment was charged')
