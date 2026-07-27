from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.career import CareerRole
from app.models.roadmap import LearningRoadmap,RoadmapItem
from app.services.career_service import CareerService
from app.schemas.roadmap import GenerateRoadmapRequest
from app.core.exceptions import AppError
from app.utils.enums import RoadmapStatus,Difficulty
from app.utils.responses import ok
router=APIRouter(prefix='/roadmaps',tags=['Roadmaps'])
DEFAULT_TOPICS=['Programming fundamentals','Framework practice','Database design','API development','Testing','Portfolio project','Interview preparation']
def item_data(i): return {'id':i.id,'title':i.title,'description':i.description,'item_type':i.item_type,'difficulty':i.difficulty,'order_no':i.order_no,'estimated_hours':i.estimated_hours,'completed':i.completed,'progress_percentage':i.progress_percentage}
def roadmap_data(r,db): return {'id':r.id,'title':r.title,'role_id':r.role_id,'status':r.status,'progress_percentage':r.progress_percentage,'items':[item_data(i) for i in db.scalars(select(RoadmapItem).where(RoadmapItem.roadmap_id==r.id).order_by(RoadmapItem.order_no)).all()]}
@router.get('')
def list_items(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(LearningRoadmap).where(LearningRoadmap.user_id==user.id)).all()
    return ok([roadmap_data(r,db) for r in rows],'Records retrieved successfully')
@router.post('/generate',status_code=201)
def generate(payload:GenerateRoadmapRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    role=db.get(CareerRole,payload.role_id)
    if not role: raise AppError('Career role not found',404,'NOT_FOUND')
    match=CareerService.match(db,user.id,role.id)
    topics=match.missing_skills or DEFAULT_TOPICS
    roadmap=LearningRoadmap(user_id=user.id,role_id=role.id,title=f'{role.title} Learning Roadmap',status=RoadmapStatus.ACTIVE,progress_percentage=0)
    db.add(roadmap); db.flush()
    for order_no,topic in enumerate(topics,1):
        db.add(RoadmapItem(roadmap_id=roadmap.id,title=str(topic).title(),description=f'Learn, practise and build a small task using {topic}.',item_type='COURSE',difficulty=Difficulty.BEGINNER,order_no=order_no,estimated_hours=3))
    db.commit(); db.refresh(roadmap)
    return ok(roadmap_data(roadmap,db),'Roadmap generated')
@router.get('/{roadmap_id}')
def get_roadmap(roadmap_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    r=db.get(LearningRoadmap,roadmap_id)
    if not r or r.user_id!=user.id: raise AppError('Roadmap not found',404,'NOT_FOUND')
    return ok(roadmap_data(r,db))
@router.post('/{roadmap_id}/items/{item_id}/complete')
def complete_item(roadmap_id:int,item_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    r=db.get(LearningRoadmap,roadmap_id)
    if not r or r.user_id!=user.id: raise AppError('Roadmap not found',404,'NOT_FOUND')
    i=db.get(RoadmapItem,item_id)
    if not i or i.roadmap_id!=roadmap_id: raise AppError('Roadmap item not found',404,'NOT_FOUND')
    i.completed=True; i.progress_percentage=100
    items=db.scalars(select(RoadmapItem).where(RoadmapItem.roadmap_id==roadmap_id)).all()
    r.progress_percentage=round(100*sum(1 for x in items if x.completed)/max(1,len(items)),2)
    if r.progress_percentage>=100: r.status=RoadmapStatus.COMPLETED
    db.commit()
    return ok(roadmap_data(r,db),'Roadmap item marked as completed')
