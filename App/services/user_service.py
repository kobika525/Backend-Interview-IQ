from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.models.user import User, UserProfile
from app.models.career import CareerRole, Skill, UserSkill
from app.core.exceptions import AppError
class UserService:
    def __init__(self,db:Session): self.db=db
    def profile_data(self,user:User,profile:UserProfile):
        skills=self.db.scalars(select(Skill).join(UserSkill,UserSkill.skill_id==Skill.id).where(UserSkill.user_id==user.id)).all()
        return {'user_id':user.id,'full_name':user.full_name,'email':user.email,'career_goal':profile.career_goal,'experience_level':profile.experience_level,'target_role_id':profile.target_role_id,'preferred_interview_mode':profile.preferred_interview_mode,'weekly_learning_target':profile.weekly_learning_target,'summary':profile.summary,'profile_image_key':profile.profile_image_key,'onboarding_completed':profile.onboarding_completed,'current_skills':[s.name for s in skills]}
    def get_profile(self,user:User):
        profile=self.db.scalar(select(UserProfile).where(UserProfile.user_id==user.id))
        if not profile: profile=UserProfile(user_id=user.id); self.db.add(profile); self.db.commit()
        return self.profile_data(user,profile)
    def update(self,user:User,payload):
        profile=self.db.scalar(select(UserProfile).where(UserProfile.user_id==user.id)); data=payload.model_dump(exclude_unset=True)
        if 'full_name' in data: user.full_name=data.pop('full_name')
        if data.get('target_role_id') and not self.db.get(CareerRole,data['target_role_id']): raise AppError('Target career role not found',404,'CAREER_ROLE_NOT_FOUND')
        for key,value in data.items(): setattr(profile,key,value)
        self.db.commit(); return self.profile_data(user,profile)
    def save_onboarding(self,user:User,payload):
        profile=self.db.scalar(select(UserProfile).where(UserProfile.user_id==user.id)); data=payload.model_dump(exclude={'current_skills'},exclude_unset=True)
        if 'full_name' in data: user.full_name=data.pop('full_name')
        if data.get('target_role_id') and not self.db.get(CareerRole,data['target_role_id']): raise AppError('Target career role not found',404,'CAREER_ROLE_NOT_FOUND')
        for key,value in data.items(): setattr(profile,key,value)
        self.db.execute(delete(UserSkill).where(UserSkill.user_id==user.id))
        for name in payload.current_skills:
            skill=self.db.scalar(select(Skill).where(Skill.name==name))
            if not skill: skill=Skill(name=name,category='OTHER'); self.db.add(skill); self.db.flush()
            self.db.add(UserSkill(user_id=user.id,skill_id=skill.id,proficiency=1))
        self.db.commit(); return self.profile_data(user,profile)
