from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.platform import BillingRecord
from app.utils.responses import ok
router=APIRouter(prefix='/billing',tags=['Billing'])
@router.get('')
def list_items(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(BillingRecord).where(BillingRecord.user_id==user.id).order_by(BillingRecord.id.desc())).all()
    return ok([{'id':b.id,'description':b.description,'amount':float(b.amount),'currency':b.currency,'status':b.status,'created_at':b.created_at.isoformat()} for b in rows],'Records retrieved successfully')
