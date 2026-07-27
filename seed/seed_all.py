from sqlalchemy import select
from app.database import SessionLocal
from app.models import *
from app.core.security import hash_password
from app.config import settings
from app.utils.enums import *
def seed():
 db=SessionLocal()
 try:
  plans=[('Free',0,{'resume_analyses':2,'text_interviews':5,'voice_interviews':0,'video_interviews':0},['Basic reports']),('Pro',2500,{'resume_analyses':10,'text_interviews':30,'voice_interviews':10,'video_interviews':3},['Roadmaps','Voice interviews']),('Premium',5000,{'resume_analyses':50,'text_interviews':100,'voice_interviews':50,'video_interviews':20},['All features'])]
  for n,p,l,f in plans:
   if not db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.name==n)): db.add(SubscriptionPlan(name=n,price_monthly=p,limits=l,features=f))
  roles=[('Software Developer','software-developer','Build and maintain software applications',ExperienceLevel.BEGINNER),('Frontend Developer','frontend-developer','Build accessible web interfaces',ExperienceLevel.BEGINNER),('Backend Developer','backend-developer','Design APIs and data services',ExperienceLevel.INTERMEDIATE)]
  for title,slug,desc,level in roles:
   if not db.scalar(select(CareerRole).where(CareerRole.slug==slug)): db.add(CareerRole(title=title,slug=slug,description=desc,responsibilities=['Develop','Test','Collaborate'],experience_level=level))
  for n,c in [('Python','Language'),('JavaScript','Language'),('React','Framework'),('FastAPI','Framework'),('SQL','Database'),('MySQL','Database'),('Git','Tool'),('Docker','DevOps'),('Communication','Soft Skill')]:
   if not db.scalar(select(Skill).where(Skill.name==n)): db.add(Skill(name=n,category=c))
  qs=[('Tell me about yourself.','HR',InterviewType.HR,['background','skills','goal']),('Describe a challenging project and your contribution.','Behavioral',InterviewType.BEHAVIORAL,['situation','action','result']),('Explain REST API design principles.','Technical',InterviewType.TECHNICAL,['resource','http','status code','stateless']),('How do you secure a web API?','Technical',InterviewType.TECHNICAL,['authentication','authorization','validation','rate limit'])]
  for text,cat,typ,kw in qs:
   if not db.scalar(select(InterviewQuestion).where(InterviewQuestion.question_text==text)): db.add(InterviewQuestion(question_text=text,category=cat,difficulty=Difficulty.BEGINNER,interview_type=typ,expected_key_points=kw,expected_keywords=kw,is_active=True))
  resources=[('Mastering the STAR Method','A guide to structuring behavioral interview answers','ARTICLE','https://example.com/resources/star-method',False),('REST API Design Fundamentals','Core principles for designing clean, resource-oriented APIs','COURSE','https://example.com/resources/rest-api-design',False),('Advanced System Design','Deep dive into scalable backend architecture','COURSE','https://example.com/resources/system-design',True)]
  for title,desc,rtype,url,premium in resources:
   if not db.scalar(select(LearningResource).where(LearningResource.title==title)): db.add(LearningResource(title=title,description=desc,resource_type=rtype,url=url,premium_only=premium,is_active=True))
  achievements=[('FIRST_INTERVIEW','First Interview Completed','Completed your first mock interview session',{'interviews_completed':1}),('RESUME_UPLOADED','Resume Uploaded','Uploaded your first resume for analysis',{'resumes_uploaded':1}),('FIVE_INTERVIEWS','Interview Regular','Completed five mock interview sessions',{'interviews_completed':5})]
  for code,title,desc,cond in achievements:
   if not db.scalar(select(Achievement).where(Achievement.code==code)): db.add(Achievement(code=code,title=title,description=desc,condition=cond))
  if settings.ADMIN_PASSWORD and not db.scalar(select(User).where(User.email==settings.ADMIN_EMAIL)):
   u=User(full_name='Interview IQ Admin',email=settings.ADMIN_EMAIL,password_hash=hash_password(settings.ADMIN_PASSWORD),role=UserRole.ADMIN,account_status=AccountStatus.ACTIVE,email_verified=True); db.add(u); db.flush(); db.add(UserProfile(user_id=u.id,onboarding_completed=True))
  db.commit(); print('Seed completed successfully')
 finally: db.close()
if __name__=='__main__': seed()
