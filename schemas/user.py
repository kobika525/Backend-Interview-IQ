from pydantic import BaseModel, Field, field_validator
from app.utils.enums import ExperienceLevel, InterviewMode
class ProfileUpdate(BaseModel):
    full_name:str|None=Field(None,min_length=2,max_length=120)
    career_goal:str|None=Field(None,max_length=255)
    experience_level:ExperienceLevel|None=None
    target_role_id:int|None=Field(None,gt=0)
    preferred_interview_mode:InterviewMode|None=None
    weekly_learning_target:int|None=Field(None,ge=1,le=40)
    summary:str|None=Field(None,max_length=2000)
    @field_validator('full_name')
    @classmethod
    def clean_name(cls,v): return ' '.join(v.split()) if v else v
class OnboardingUpdate(ProfileUpdate):
    current_skills:list[str]=Field(default_factory=list,max_length=100)
    @field_validator('current_skills')
    @classmethod
    def clean_skills(cls, values):
        cleaned=[]
        for value in values:
            value=' '.join(value.split()).strip()
            if value and value.lower() not in [x.lower() for x in cleaned]: cleaned.append(value)
        return cleaned
