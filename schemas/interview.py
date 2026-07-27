from pydantic import BaseModel,Field
from app.utils.enums import InterviewMode,InterviewType,Difficulty,ExperienceLevel
class InterviewCreate(BaseModel):
 target_role_id:int|None=None; resume_id:int|None=None; interview_type:InterviewType=InterviewType.MIXED; interview_mode:InterviewMode=InterviewMode.TEXT; experience_level:ExperienceLevel=ExperienceLevel.BEGINNER; difficulty:Difficulty=Difficulty.BEGINNER; duration:int=Field(20,ge=5,le=120); number_of_questions:int=Field(5,ge=1,le=30); question_categories:list[str]=[]; job_description:str|None=Field(None,max_length=10000); preferred_language:str='en'
class TextAnswer(BaseModel): question_id:int; answer_text:str=Field(min_length=1,max_length=20000)
