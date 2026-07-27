from app.database import SessionLocal
from app.models.career import CareerRole, Skill, RoleSkill
from app.models.interview import InterviewQuestion
from app.models.platform import SubscriptionPlan, Achievement
from app.models.resource import LearningResource
from app.utils.enums import ExperienceLevel, Difficulty, InterviewType

def register(client, email='user@example.com', password='Strong@123'):
    return client.post('/api/auth/register', json={'full_name': 'Demo User', 'email': email, 'password': password})

def login(client, email='user@example.com', password='Strong@123'):
    return client.post('/api/auth/login', json={'email': email, 'password': password})

def auth_headers(client, email='user@example.com', password='Strong@123'):
    register(client, email, password)
    token = login(client, email, password).json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}

def seed_career_role(title='Software Developer', slug='software-developer'):
    db = SessionLocal()
    try:
        role = CareerRole(title=title, slug=slug, description='Build software', responsibilities=['Develop', 'Test'], experience_level=ExperienceLevel.BEGINNER)
        db.add(role); db.commit(); db.refresh(role)
        return role.id
    finally:
        db.close()

def seed_skill_for_role(role_id, name='Python', required=True):
    db = SessionLocal()
    try:
        skill = Skill(name=name, category='Language')
        db.add(skill); db.flush()
        db.add(RoleSkill(role_id=role_id, skill_id=skill.id, required=required))
        db.commit()
        return skill.id
    finally:
        db.close()

def seed_interview_question(text='Tell me about yourself.', category='HR', itype=InterviewType.HR):
    db = SessionLocal()
    try:
        q = InterviewQuestion(question_text=text, category=category, difficulty=Difficulty.BEGINNER, interview_type=itype, expected_key_points=['background'], expected_keywords=['background'], is_active=True)
        db.add(q); db.commit(); db.refresh(q)
        return q.id
    finally:
        db.close()

def seed_subscription_plan(name='Free', price=0):
    db = SessionLocal()
    try:
        plan = SubscriptionPlan(name=name, price_monthly=price, limits={'text_interviews': 5}, features=['Basic reports'])
        db.add(plan); db.commit(); db.refresh(plan)
        return plan.id
    finally:
        db.close()

def seed_achievement(code='FIRST_INTERVIEW', title='First Interview'):
    db = SessionLocal()
    try:
        a = Achievement(code=code, title=title, description='Completed a first interview', condition={'interviews_completed': 1})
        db.add(a); db.commit(); db.refresh(a)
        return a.id
    finally:
        db.close()

def seed_learning_resource(title='REST API Design'):
    db = SessionLocal()
    try:
        r = LearningResource(title=title, description='Learn REST API design', resource_type='ARTICLE', url='https://example.com/rest', premium_only=False, is_active=True)
        db.add(r); db.commit(); db.refresh(r)
        return r.id
    finally:
        db.close()
