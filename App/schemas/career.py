from pydantic import BaseModel
class MatchRequest(BaseModel): role_id:int|None=None
class SkillGapRequest(BaseModel): role_id:int
